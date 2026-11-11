using System.Net;
using System.Text.Json;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Infrastructure.Mensajeria;
using BuildingBlocks.Tests.Soporte;

namespace BuildingBlocks.Tests.Infraestructura;

public class BusDeEventosHttpTests
{
    private sealed class ManejadorFalso(Func<HttpRequestMessage, HttpResponseMessage> responder) : HttpMessageHandler
    {
        public HttpRequestMessage? Peticion { get; private set; }
        public string? Cuerpo { get; private set; }
        public long? LongitudDeclarada { get; private set; }

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            Peticion = request;
            LongitudDeclarada = request.Content!.Headers.ContentLength;
            Cuerpo = await request.Content!.ReadAsStringAsync(cancellationToken);
            return responder(request);
        }
    }

    private static SobreDeEvento Sobre() => new(
        Guid.Parse("22222222-2222-4222-8222-222222222222"), "intervenciones.orden-de-trabajo-cerrada.v1",
        Escenario.Inicio, Guid.NewGuid(), JsonSerializer.SerializeToElement(new { ordenId = "x" }));

    private static BusDeEventosHttp Crear(ManejadorFalso manejador) =>
        new(new HttpClient(manejador) { BaseAddress = new Uri("http://event-bus:5100/") });

    [Fact]
    public async Task Publica_con_POST_a_BUS_URL_publish_y_el_sobre_del_contrato()
    {
        var manejador = new ManejadorFalso(_ => new HttpResponseMessage(HttpStatusCode.OK));

        await Crear(manejador).PublicarAsync(Sobre());

        Assert.Equal(HttpMethod.Post, manejador.Peticion!.Method);
        Assert.Equal("http://event-bus:5100/publish", manejador.Peticion.RequestUri!.ToString());
        using var json = JsonDocument.Parse(manejador.Cuerpo!);
        var raiz = json.RootElement;
        Assert.Equal("22222222-2222-4222-8222-222222222222", raiz.GetProperty("eventId").GetString());
        Assert.Equal("intervenciones.orden-de-trabajo-cerrada.v1", raiz.GetProperty("topic").GetString());
        Assert.True(raiz.TryGetProperty("occurredOn", out _));
        Assert.True(raiz.TryGetProperty("correlationId", out _));
        Assert.Equal("x", raiz.GetProperty("payload").GetProperty("ordenId").GetString());
    }

    [Fact]
    public async Task El_cuerpo_declara_su_longitud_porque_el_bus_no_acepta_transferencia_fragmentada()
    {
        var manejador = new ManejadorFalso(_ => new HttpResponseMessage(HttpStatusCode.OK));

        await Crear(manejador).PublicarAsync(Sobre());

        Assert.Equal(System.Text.Encoding.UTF8.GetByteCount(manejador.Cuerpo!), manejador.LongitudDeclarada);
    }

    [Fact]
    public async Task Una_respuesta_no_exitosa_es_un_fallo_de_publicacion()
    {
        var manejador = new ManejadorFalso(_ => new HttpResponseMessage(HttpStatusCode.ServiceUnavailable));

        var ex = await Assert.ThrowsAsync<FalloDePublicacionException>(() => Crear(manejador).PublicarAsync(Sobre()));

        Assert.Contains("503", ex.Message);
    }

    [Fact]
    public async Task Un_error_de_red_es_un_fallo_de_publicacion()
    {
        var manejador = new ManejadorFalso(_ => throw new HttpRequestException("sin red"));

        await Assert.ThrowsAsync<FalloDePublicacionException>(() => Crear(manejador).PublicarAsync(Sobre()));
    }
}
