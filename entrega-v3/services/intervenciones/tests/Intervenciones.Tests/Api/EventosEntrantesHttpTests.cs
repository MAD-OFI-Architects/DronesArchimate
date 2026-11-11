using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Intervenciones.Contracts;
using Intervenciones.Tests.Soporte;

namespace Intervenciones.Tests.Api;

public class EventosEntrantesHttpTests : IAsyncLifetime
{
    private ServidorDeIntervenciones _servidor = null!;

    public async Task InitializeAsync() => _servidor = await ServidorDeIntervenciones.IniciarAsync();

    public Task DisposeAsync() => _servidor.DisposeAsync().AsTask();

    private static object Sobre(Guid eventId, string topico, object payload) => new
    {
        eventId, topic = topico, occurredOn = EscenarioDeIntervenciones.Inicio, correlationId = Guid.NewGuid(), payload
    };

    private static object ParadaProgramada => new
    {
        paradaId = EscenarioDeIntervenciones.Parada, dronId = "ADV-03", fechaProgramada = EscenarioDeIntervenciones.Inicio,
        tareas = Array.Empty<object>()
    };

    [Fact]
    public async Task Un_evento_repetido_se_procesa_una_sola_vez()
    {
        var sobre = Sobre(Guid.NewGuid(), IntervencionesTopicos.ParadaProgramada, ParadaProgramada);
        var ruta = $"/events/{IntervencionesTopicos.ParadaProgramada}";

        var primera = await _servidor.Cliente.PostAsJsonAsync(ruta, sobre);
        var segunda = await _servidor.Cliente.PostAsJsonAsync(ruta, sobre);

        Assert.Equal("procesado", (await primera.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("estado").GetString());
        Assert.Equal("duplicado", (await segunda.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("estado").GetString());
        Assert.Single(await _servidor.Almacen.ListarAsync(Intervenciones.Infrastructure.Persistencia.RepositorioOrdenDeTrabajo.NombreDeColeccion));
    }

    [Fact]
    public async Task Parada_programada_abre_la_orden_y_faltante_detectado_la_pone_en_espera()
    {
        await _servidor.Cliente.PostAsJsonAsync($"/events/{IntervencionesTopicos.ParadaProgramada}",
            Sobre(Guid.NewGuid(), IntervencionesTopicos.ParadaProgramada, ParadaProgramada));

        var faltante = await _servidor.Cliente.PostAsJsonAsync($"/events/{IntervencionesTopicos.FaltanteDetectado}",
            Sobre(Guid.NewGuid(), IntervencionesTopicos.FaltanteDetectado,
                new { paradaId = EscenarioDeIntervenciones.Parada, referencia = "HEL-T40", cantidadFaltante = 1 }));

        Assert.Equal(HttpStatusCode.OK, faltante.StatusCode);
        var documento = Assert.Single(await _servidor.Almacen.ListarAsync(Intervenciones.Infrastructure.Persistencia.RepositorioOrdenDeTrabajo.NombreDeColeccion));
        Assert.Contains("EnEspera", documento.Json);
    }

    [Fact]
    public async Task Un_topico_desconocido_responde_404()
    {
        var respuesta = await _servidor.Cliente.PostAsJsonAsync("/events/otro.v1", Sobre(Guid.NewGuid(), "otro.v1", new { }));

        Assert.Equal(HttpStatusCode.NotFound, respuesta.StatusCode);
    }
}
