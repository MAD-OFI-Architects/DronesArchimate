using System.Net;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using BuildingBlocks.Api.DependencyInjection;
using BuildingBlocks.Tests.Soporte;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Tests.Api;

public class EventosEntrantesEndpointsTests : IAsyncLifetime
{
    private WebApplication _app = null!;
    private HttpClient _cliente = null!;
    private Escenario _escenario = null!;

    public async Task InitializeAsync()
    {
        _escenario = new Escenario();
        var builder = WebApplication.CreateBuilder(new WebApplicationOptions { EnvironmentName = "Testing" });
        builder.WebHost.UseTestServer();
        builder.Logging.ClearProviders();
        _app = Construir(builder);
        await _app.StartAsync();
        _cliente = _app.GetTestClient();
    }

    private WebApplication Construir(WebApplicationBuilder builder)
    {
        builder.Services.AddSingleton(_escenario.Proveedor.GetRequiredService<BuildingBlocks.Infrastructure.Mensajeria.ProcesadorDeMensajeEntrante>());
        builder.Services.AgregarBloquesDeApi();
        builder.Services.AddScoped<BuildingBlocks.Application.Correlacion.IContextoDeCorrelacion, BuildingBlocks.Application.Correlacion.ContextoDeCorrelacion>();
        var app = builder.Build();
        app.UsarBloquesDeApi();
        app.MapearModulosDeEndpoints();
        return app;
    }

    public async Task DisposeAsync()
    {
        _cliente.Dispose();
        await _app.DisposeAsync();
        await _escenario.DisposeAsync();
    }

    private static object Sobre(Guid eventId, string topico = CuentaExternaConsumidor.NombreDelTopico) => new
    {
        eventId, topic = topico, occurredOn = Escenario.Inicio, correlationId = Guid.NewGuid(),
        payload = new { cuentaId = Guid.NewGuid(), titular = "Ana" }
    };

    [Fact]
    public async Task Responde_200_al_procesar_y_200_si_ya_lo_habia_procesado()
    {
        var sobre = Sobre(Guid.NewGuid());

        var primera = await _cliente.PostAsJsonAsync($"/events/{CuentaExternaConsumidor.NombreDelTopico}", sobre);
        var segunda = await _cliente.PostAsJsonAsync($"/events/{CuentaExternaConsumidor.NombreDelTopico}", sobre);

        Assert.Equal(HttpStatusCode.OK, primera.StatusCode);
        Assert.Equal("procesado", (await primera.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("estado").GetString());
        Assert.Equal(HttpStatusCode.OK, segunda.StatusCode);
        Assert.Equal("duplicado", (await segunda.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("estado").GetString());
        Assert.Single(_escenario.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Un_topico_sin_consumidor_responde_404_problem_json()
    {
        var respuesta = await _cliente.PostAsJsonAsync("/events/otro.v1", Sobre(Guid.NewGuid(), "otro.v1"));

        Assert.Equal(HttpStatusCode.NotFound, respuesta.StatusCode);
        Assert.Equal("application/problem+json", respuesta.Content.Headers.ContentType!.MediaType);
    }

    [Theory]
    [InlineData("no es json")]
    [InlineData("{\"eventId\":\"00000000-0000-0000-0000-000000000000\",\"topic\":\"externo.cuenta-creada.v1\",\"payload\":{}}")]
    public async Task Un_sobre_invalido_responde_400(string cuerpo)
    {
        var contenido = new StringContent(cuerpo, Encoding.UTF8, "application/json");

        var respuesta = await _cliente.PostAsync($"/events/{CuentaExternaConsumidor.NombreDelTopico}", contenido);

        Assert.Equal(HttpStatusCode.BadRequest, respuesta.StatusCode);
        Assert.Equal("application/problem+json", respuesta.Content.Headers.ContentType!.MediaType);
    }

    [Fact]
    public async Task Cada_respuesta_devuelve_el_encabezado_de_correlacion()
    {
        var respuesta = await _cliente.PostAsJsonAsync($"/events/{CuentaExternaConsumidor.NombreDelTopico}", Sobre(Guid.NewGuid()));

        Assert.True(respuesta.Headers.Contains("X-Correlation-Id"));
    }
}
