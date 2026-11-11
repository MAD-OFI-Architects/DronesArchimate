using System.Net;
using System.Text.Json;
using BuildingBlocks.Application.Integracion;
using Intervenciones.Infrastructure.Habilitacion;
using Intervenciones.Infrastructure.Mensajeria;

namespace Intervenciones.Tests.Infraestructura;

public class AdaptadoresHttpTests
{
    private static HttpClient Cliente(Func<HttpRequestMessage, Task<HttpResponseMessage>> respuesta) =>
        new(new ManejadorFalso(respuesta)) { BaseAddress = new Uri("http://externo.test/") };

    private static HttpResponseMessage Json(string json, HttpStatusCode estado = HttpStatusCode.OK) =>
        new(estado) { Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json") };

    [Theory]
    [InlineData("{\"habilitado\":true,\"ruta\":\"x\"}", true)]
    [InlineData("{\"habilitado\":false}", false)]
    public async Task La_ACL_traduce_la_respuesta_externa_a_si_o_no(string cuerpo, bool esperado)
    {
        HttpRequestMessage? enviada = null;
        var adapter = new ConsultaDeHabilitacionAdapter(Cliente(p => { enviada = p; return Task.FromResult(Json(cuerpo)); }));

        var habilitado = await adapter.EstaHabilitadoAsync("Ana");

        Assert.Equal(esperado, habilitado);
        Assert.Equal(HttpMethod.Post, enviada!.Method);
        Assert.Equal("/api/habilitacion-de-personal/consulta-de-habilitacion", enviada.RequestUri!.AbsolutePath);
    }

    [Theory]
    [InlineData(HttpStatusCode.InternalServerError, "{}")]
    [InlineData(HttpStatusCode.OK, "{\"otra\":1}")]
    [InlineData(HttpStatusCode.OK, "no es json")]
    public async Task La_ACL_falla_con_una_excepcion_propia_si_el_externo_no_responde_bien(HttpStatusCode estado, string cuerpo)
    {
        var adapter = new ConsultaDeHabilitacionAdapter(Cliente(_ => Task.FromResult(Json(cuerpo, estado))));

        await Assert.ThrowsAsync<HabilitacionNoDisponibleException>(() => adapter.EstaHabilitadoAsync("Ana"));
    }

    [Fact]
    public async Task La_ACL_falla_si_el_externo_no_es_alcanzable()
    {
        var adapter = new ConsultaDeHabilitacionAdapter(Cliente(_ => throw new HttpRequestException("sin red")));

        await Assert.ThrowsAsync<HabilitacionNoDisponibleException>(() => adapter.EstaHabilitadoAsync("Ana"));
    }

    [Fact]
    public async Task El_publicador_hace_POST_del_sobre_en_publish()
    {
        HttpRequestMessage? enviada = null;
        string? cuerpo = null;
        var publicador = new PublicadorDeEventosHttp(Cliente(async p =>
        {
            enviada = p;
            cuerpo = await p.Content!.ReadAsStringAsync();
            return new HttpResponseMessage(HttpStatusCode.Accepted);
        }));
        var sobre = new SobreDeEvento(Guid.NewGuid(), "intervenciones.orden-de-trabajo-cerrada.v1", DateTimeOffset.UtcNow, Guid.NewGuid(),
            JsonDocument.Parse("{\"ordenId\":\"x\"}").RootElement);

        await publicador.PublicarAsync(sobre);

        Assert.Equal(HttpMethod.Post, enviada!.Method);
        Assert.Equal("/publish", enviada.RequestUri!.AbsolutePath);
        Assert.Contains(sobre.EventId.ToString(), cuerpo);
        Assert.Contains("\"topic\":\"intervenciones.orden-de-trabajo-cerrada.v1\"", cuerpo);
    }

    [Fact]
    public async Task El_publicador_falla_si_el_bus_rechaza_el_evento()
    {
        var publicador = new PublicadorDeEventosHttp(Cliente(_ => Task.FromResult(new HttpResponseMessage(HttpStatusCode.BadGateway))));
        var sobre = new SobreDeEvento(Guid.NewGuid(), "t.v1", DateTimeOffset.UtcNow, Guid.NewGuid(), JsonDocument.Parse("{}").RootElement);

        await Assert.ThrowsAsync<FalloDePublicacionException>(() => publicador.PublicarAsync(sobre));
    }

    private sealed class ManejadorFalso(Func<HttpRequestMessage, Task<HttpResponseMessage>> respuesta) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) =>
            respuesta(request);
    }
}
