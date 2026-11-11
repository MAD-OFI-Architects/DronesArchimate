using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Serializacion;
using BuildingBlocks.Domain;

namespace BuildingBlocks.Infrastructure.Persistencia;

/// <summary>Repositorio genérico: guarda cualquier agregado como documento a través de su memento; el concreto solo
/// indica la colección y la clave. Mantiene un mapa de identidad y deja la escritura a la unidad de trabajo.</summary>
public abstract class RepositorioDocumentalBase<TAgregado, TId, TMemento>(
    IAlmacenDeDocumentos almacen,
    UnidadDeTrabajoDocumental unidadDeTrabajo,
    ISerializadorJson serializador)
    where TAgregado : AggregateRoot<TId>, IOriginador<TAgregado, TMemento>
    where TId : notnull
{
    protected abstract string Coleccion { get; }

    protected abstract string ClaveDe(TId id);

    public Task AgregarAsync(TAgregado agregado, CancellationToken cancellationToken = default)
    {
        Rastrear(agregado, version: 0);
        return Task.CompletedTask;
    }

    public Task ActualizarAsync(TAgregado agregado, CancellationToken cancellationToken = default) =>
        unidadDeTrabajo.TryObtener<TAgregado>(Coleccion, ClaveDe(agregado.Id), out _)
            ? Task.CompletedTask
            : throw new InvalidOperationException("Solo se pueden actualizar agregados obtenidos o agregados en esta unidad de trabajo.");

    protected async Task<TAgregado?> ObtenerPorIdAsync(TId id, CancellationToken cancellationToken = default)
    {
        var clave = ClaveDe(id);
        if (unidadDeTrabajo.TryObtener<TAgregado>(Coleccion, clave, out var rastreado))
            return rastreado;

        var documento = await almacen.ObtenerAsync(Coleccion, clave, cancellationToken);
        return documento is null ? null : Materializar(documento);
    }

    protected async Task<IReadOnlyList<TAgregado>> BuscarAsync(Func<TMemento, bool> filtro, CancellationToken cancellationToken = default)
    {
        var resultado = new List<TAgregado>();
        foreach (var documento in await almacen.ListarAsync(Coleccion, cancellationToken))
        {
            if (unidadDeTrabajo.TryObtener<TAgregado>(Coleccion, documento.Id, out var rastreado))
            {
                if (filtro(rastreado!.CrearMemento()))
                    resultado.Add(rastreado);
                continue;
            }

            if (filtro(serializador.Deserializar<TMemento>(documento.Json)))
                resultado.Add(Materializar(documento));
        }

        return resultado;
    }

    private TAgregado Materializar(Documento documento)
    {
        var agregado = TAgregado.RestaurarDesde(serializador.Deserializar<TMemento>(documento.Json));
        Rastrear(agregado, documento.Version);
        return agregado;
    }

    private void Rastrear(TAgregado agregado, long version) =>
        unidadDeTrabajo.Rastrear(
            Coleccion,
            ClaveDe(agregado.Id),
            agregado,
            () => serializador.Serializar(agregado.CrearMemento()),
            version);
}
