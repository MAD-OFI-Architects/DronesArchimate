using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Serializacion;
using BuildingBlocks.Infrastructure.Persistencia;
using Intervenciones.Application.Puertos;
using Intervenciones.Domain;
using Intervenciones.Infrastructure.Cifrado;

namespace Intervenciones.Infrastructure.Persistencia;

/// <summary>Guarda la orden como documento (su memento) en MongoDB; el kernel la escribe junto a la bandeja de salida
/// en una transacción. Los datos de personas se cifran antes de llegar al almacén.</summary>
public sealed class RepositorioOrdenDeTrabajo(
    IAlmacenDeDocumentos almacen,
    UnidadDeTrabajoDocumental unidadDeTrabajo,
    ISerializadorJson serializador,
    Cifrador cifrador)
    : RepositorioDocumentalBase<OrdenDeTrabajo, Guid, OrdenDeTrabajoMemento>(
            almacen, unidadDeTrabajo, new SerializadorDeOrdenCifrado(serializador, cifrador)),
        IOrdenDeTrabajoRepository
{
    public const string NombreDeColeccion = "ordenes-de-trabajo";

    protected override string Coleccion => NombreDeColeccion;

    protected override string ClaveDe(Guid id) => id.ToString();

    public Task<OrdenDeTrabajo?> ObtenerAsync(Guid id, CancellationToken cancellationToken = default) =>
        ObtenerPorIdAsync(id, cancellationToken);

    /// <summary>Busca primero por la identidad determinista de la parada (lectura directa); solo si no está recorre
    /// la colección, para las órdenes abiertas antes de que la identidad se derivara de la parada.</summary>
    public async Task<OrdenDeTrabajo?> ObtenerPorParadaAsync(Guid paradaId, CancellationToken cancellationToken = default) =>
        await ObtenerPorIdAsync(IdentidadDeOrden.DeParada(paradaId), cancellationToken)
        ?? (await BuscarAsync(m => m.ParadaId == paradaId, cancellationToken)).FirstOrDefault();

    public async Task GuardarAsync(OrdenDeTrabajo orden, CancellationToken cancellationToken = default)
    {
        if (await ObtenerPorIdAsync(orden.Id, cancellationToken) is null)
            await AgregarAsync(orden, cancellationToken);
        else
            await ActualizarAsync(orden, cancellationToken);
    }
}
