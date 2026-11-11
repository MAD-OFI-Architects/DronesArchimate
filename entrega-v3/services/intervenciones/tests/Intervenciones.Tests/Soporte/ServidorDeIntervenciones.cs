using BuildingBlocks.Api.DependencyInjection;
using BuildingBlocks.Infrastructure.DependencyInjection;
using BuildingBlocks.Infrastructure.Mensajeria;
using BuildingBlocks.Infrastructure.Persistencia;
using Intervenciones.Api;
using Intervenciones.Application.Puertos;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace Intervenciones.Tests.Soporte;

/// <summary>El servicio real (rutas, mediador, repositorio, cifrado) sobre TestServer con adaptadores en memoria.</summary>
public sealed class ServidorDeIntervenciones : IAsyncDisposable
{
    public static readonly string ClaveBase64 = Convert.ToBase64String("0123456789abcdef0123456789abcdef"u8.ToArray());

    private readonly WebApplication _app;

    private ServidorDeIntervenciones(WebApplication app, HabilitacionFija habilitacion)
    {
        _app = app;
        Habilitacion = habilitacion;
        Cliente = app.GetTestClient();
    }

    public HttpClient Cliente { get; }

    public HabilitacionFija Habilitacion { get; }

    public AlmacenDeDocumentosEnMemoria Almacen => _app.Services.GetRequiredService<AlmacenDeDocumentosEnMemoria>();

    public BusDeEventosEnMemoria Bus => (BusDeEventosEnMemoria)_app.Services.GetRequiredService<BuildingBlocks.Application.Integracion.IBusDeEventos>();

    public static async Task<ServidorDeIntervenciones> IniciarAsync()
    {
        var builder = WebApplication.CreateBuilder(new WebApplicationOptions { EnvironmentName = "Testing" });
        builder.WebHost.UseTestServer();
        builder.Logging.ClearProviders();

        var opciones = new OpcionesDeMicroservicio
        {
            Nombre = "intervenciones-pruebas",
            SimulatorsUrl = "http://simuladores.test",
            CifradoClave = ClaveBase64
        };
        builder.Services.AgregarIntervenciones(opciones);
        var habilitacion = new HabilitacionFija();
        builder.Services.AddSingleton<IConsultaDeHabilitacion>(habilitacion);

        var app = builder.Build();
        app.UsarBloquesDeApi();
        app.MapearModulosDeEndpoints();
        await app.StartAsync();
        return new ServidorDeIntervenciones(app, habilitacion);
    }

    public async ValueTask DisposeAsync()
    {
        Cliente.Dispose();
        await _app.DisposeAsync();
    }

    public sealed class HabilitacionFija : IConsultaDeHabilitacion
    {
        public bool Habilitado { get; set; } = true;

        public Task<bool> EstaHabilitadoAsync(string tecnico, CancellationToken cancellationToken = default) =>
            Task.FromResult(Habilitado);
    }
}
