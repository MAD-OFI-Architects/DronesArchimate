using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.DependencyInjection;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Serializacion;
using BuildingBlocks.Application.Tiempo;
using BuildingBlocks.Infrastructure.DependencyInjection;
using BuildingBlocks.Infrastructure.Persistencia;
using Intervenciones.Application.Comandos;
using Intervenciones.Application.Consumidores;
using Intervenciones.Application.Puertos;
using Intervenciones.Contracts;
using Intervenciones.Domain;
using Microsoft.Extensions.DependencyInjection;

namespace Intervenciones.Tests.Soporte;

/// <summary>Aplicación completa con adaptadores en memoria: mediador, pipeline, outbox y consumidores reales.</summary>
public sealed class EscenarioDeIntervenciones : IAsyncDisposable
{
    public static readonly DateTimeOffset Inicio = new(2026, 11, 20, 8, 0, 0, TimeSpan.Zero);
    public static readonly Guid Parada = Guid.Parse("11111111-1111-4111-8111-111111111111");

    public EscenarioDeIntervenciones(bool tecnicoHabilitado = true)
    {
        var servicios = new ServiceCollection();
        servicios.AddLogging();
        servicios.AddSingleton<IClock>(new RelojFijo(Inicio));
        servicios.AddSingleton<IConsultaDeHabilitacion>(new HabilitacionFija(tecnicoHabilitado));
        servicios.AgregarBloquesDeAplicacion(typeof(AbrirOrdenDeTrabajoComando).Assembly);
        servicios.AgregarBloquesDeInfraestructura(new OpcionesDeMicroservicio { Nombre = "pruebas" });
        servicios.AddScoped<IOrdenDeTrabajoRepository, RepositorioDeOrdenesEnMemoria>();
        servicios.AgregarConsumidor<ParadaProgramadaV1, ParadaProgramadaConsumidor>(IntervencionesTopicos.ParadaProgramada);
        servicios.AgregarConsumidor<FaltanteDetectadoV1, FaltanteDetectadoConsumidor>(IntervencionesTopicos.FaltanteDetectado);
        Proveedor = servicios.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true });
    }

    public ServiceProvider Proveedor { get; }

    public AlmacenDeDocumentosEnMemoria Almacen => Proveedor.GetRequiredService<AlmacenDeDocumentosEnMemoria>();

    public async Task<TRespuesta> EnviarAsync<TRespuesta>(ISolicitud<TRespuesta> solicitud)
    {
        await using var alcance = Proveedor.CreateAsyncScope();
        return await alcance.ServiceProvider.GetRequiredService<IMediador>().EnviarAsync(solicitud);
    }

    public Task<Guid> AbrirAsync(bool trabajoMayor = false) =>
        EnviarAsync(new AbrirOrdenDeTrabajoComando(Parada, true, "ADV-03", "Preventiva", trabajoMayor));

    public async Task<OrdenDeTrabajoMemento> MementoAsync(Guid ordenId)
    {
        var documento = await Almacen.ObtenerAsync(RepositorioDeOrdenesEnMemoria.NombreDeColeccion, ordenId.ToString());
        return Proveedor.GetRequiredService<ISerializadorJson>().Deserializar<OrdenDeTrabajoMemento>(documento!.Json);
    }

    public Task<IReadOnlyList<Documento>> OrdenesAsync() =>
        Almacen.ListarAsync(RepositorioDeOrdenesEnMemoria.NombreDeColeccion);

    public ValueTask DisposeAsync() => Proveedor.DisposeAsync();

    private sealed class RelojFijo(DateTimeOffset ahora) : IClock
    {
        public DateTimeOffset Now => ahora;
    }

    private sealed class HabilitacionFija(bool habilitado) : IConsultaDeHabilitacion
    {
        public Task<bool> EstaHabilitadoAsync(string tecnico, CancellationToken cancellationToken = default) =>
            Task.FromResult(habilitado);
    }
}

public sealed class RepositorioDeOrdenesEnMemoria(
    IAlmacenDeDocumentos almacen, UnidadDeTrabajoDocumental unidadDeTrabajo, ISerializadorJson serializador)
    : RepositorioDocumentalBase<OrdenDeTrabajo, Guid, OrdenDeTrabajoMemento>(almacen, unidadDeTrabajo, serializador),
        IOrdenDeTrabajoRepository
{
    public const string NombreDeColeccion = "ordenes-de-trabajo";

    protected override string Coleccion => NombreDeColeccion;

    protected override string ClaveDe(Guid id) => id.ToString();

    public Task<OrdenDeTrabajo?> ObtenerAsync(Guid id, CancellationToken cancellationToken = default) =>
        ObtenerPorIdAsync(id, cancellationToken);

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
