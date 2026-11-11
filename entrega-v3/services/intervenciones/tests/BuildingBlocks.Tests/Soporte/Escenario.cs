using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.DependencyInjection;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Tiempo;
using BuildingBlocks.Infrastructure.DependencyInjection;
using BuildingBlocks.Infrastructure.Persistencia;
using BuildingBlocks.Infrastructure.Tiempo;
using Microsoft.Extensions.DependencyInjection;

namespace BuildingBlocks.Tests.Soporte;

/// <summary>Servicio completo y hermético: aplicación + infraestructura con almacén y bus en memoria.</summary>
public sealed class Escenario : IAsyncDisposable
{
    public static readonly DateTimeOffset Inicio = new(2026, 11, 20, 8, 0, 0, TimeSpan.Zero);

    public Escenario(Action<IServiceCollection>? configurar = null)
    {
        var servicios = new ServiceCollection();
        servicios.AddLogging();
        servicios.AddSingleton<IClock>(Reloj);
        servicios.AgregarBloquesDeAplicacion(typeof(Cuenta).Assembly);
        servicios.AgregarBloquesDeInfraestructura(new OpcionesDeMicroservicio { Nombre = "pruebas" });
        servicios.AddScoped<IRepositorioDeCuentas, RepositorioDeCuentas>();
        servicios.AgregarConsumidor<CuentaExternaV1, CuentaExternaConsumidor>(CuentaExternaConsumidor.NombreDelTopico);
        configurar?.Invoke(servicios);
        Proveedor = servicios.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = false });
    }

    public ServiceProvider Proveedor { get; }

    public RelojSimulado Reloj { get; } = new(Inicio);

    public AlmacenDeDocumentosEnMemoria Almacen => (AlmacenDeDocumentosEnMemoria)Proveedor.GetRequiredService<BuildingBlocks.Application.Persistencia.IAlmacenDeDocumentos>();

    public async Task<TRespuesta> EnviarAsync<TRespuesta>(ISolicitud<TRespuesta> solicitud)
    {
        await using var alcance = Proveedor.CreateAsyncScope();
        return await alcance.ServiceProvider.GetRequiredService<IMediador>().EnviarAsync(solicitud);
    }

    public ValueTask DisposeAsync() => Proveedor.DisposeAsync();
}
