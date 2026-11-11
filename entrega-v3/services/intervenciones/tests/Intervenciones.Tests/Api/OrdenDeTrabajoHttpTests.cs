using System.Net;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using Intervenciones.Tests.Soporte;

namespace Intervenciones.Tests.Api;

public class OrdenDeTrabajoHttpTests : IAsyncLifetime
{
    private const string Base = "/api/orden-de-trabajo";
    private static readonly Guid Parada = EscenarioDeIntervenciones.Parada;
    private static readonly DateTimeOffset Ahora = EscenarioDeIntervenciones.Inicio;

    private ServidorDeIntervenciones _servidor = null!;

    private HttpClient Cliente => _servidor.Cliente;

    public async Task InitializeAsync() => _servidor = await ServidorDeIntervenciones.IniciarAsync();

    public Task DisposeAsync() => _servidor.DisposeAsync().AsTask();

    private static object CuerpoAbrir(bool paradaProgramada = true, bool mayor = false) => new
    {
        paradaId = Parada, paradaProgramada, dronId = "ADV-03", tipo = "Preventiva", esTrabajoMayor = mayor
    };

    private async Task<Guid> AbrirAsync(bool mayor = false)
    {
        var respuesta = await Cliente.PostAsJsonAsync(Base, CuerpoAbrir(mayor: mayor));
        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
        return (await respuesta.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetGuid();
    }

    private Task<HttpResponseMessage> PostAsync(Guid id, string comando, object? cuerpo = null) =>
        Cliente.PostAsJsonAsync($"{Base}/{id}/{comando}", cuerpo ?? new { });

    private Task<HttpResponseMessage> EjecutarAsync(Guid id, string quien = "Ana") => PostAsync(id, "registrar-ejecucion-de-tarea",
        new { tareaId = Guid.NewGuid(), descripcion = "Cambio de hélices", resultado = "Realizada", ejecutadaPor = quien, horas = 3.5 });

    private Task<HttpResponseMessage> LiberarAsync(Guid id, string quien = "Beto") =>
        PostAsync(id, "liberar-dron", new { liberacionId = Guid.NewGuid(), liberadaPor = quien });

    private async Task<JsonElement> ObtenerAsync(Guid id)
    {
        var respuesta = await Cliente.GetAsync($"{Base}/{id}");
        Assert.Equal(HttpStatusCode.OK, respuesta.StatusCode);
        return await respuesta.Content.ReadFromJsonAsync<JsonElement>();
    }

    private async Task<Guid> CerradaAsync()
    {
        var id = await AbrirAsync();
        await EjecutarAsync(id);
        await LiberarAsync(id);
        Assert.Equal(HttpStatusCode.NoContent, (await PostAsync(id, "cerrar-orden-de-trabajo")).StatusCode);
        return id;
    }

    private static async Task AssertProblemaAsync(HttpResponseMessage respuesta, HttpStatusCode estado, string? regla = null)
    {
        Assert.Equal(estado, respuesta.StatusCode);
        Assert.Equal("application/problem+json", respuesta.Content.Headers.ContentType!.MediaType);
        if (regla is not null)
            Assert.Equal(regla, (await respuesta.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("regla").GetString());
    }

    [Fact]
    public async Task Health_responde_ok()
    {
        var respuesta = await Cliente.GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, respuesta.StatusCode);
    }

    [Fact]
    public async Task AbrirOrdenDeTrabajoComando_responde_201_con_ubicacion_y_la_orden_queda_abierta()
    {
        var respuesta = await Cliente.PostAsJsonAsync(Base, CuerpoAbrir());
        var id = (await respuesta.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetGuid();

        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
        Assert.Equal($"{Base}/{id}", respuesta.Headers.Location!.OriginalString);
        Assert.Equal("Abierta", (await ObtenerAsync(id)).GetProperty("estado").GetString());
    }

    [Fact]
    public async Task Obtener_por_parada_devuelve_la_orden_abierta_para_esa_parada()
    {
        var id = await AbrirAsync();

        var respuesta = await Cliente.GetAsync($"{Base}/por-parada/{Parada}");

        Assert.Equal(HttpStatusCode.OK, respuesta.StatusCode);
        Assert.Equal(id, (await respuesta.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetGuid());
    }

    [Fact]
    public async Task Obtener_por_parada_sin_orden_responde_404()
    {
        var respuesta = await Cliente.GetAsync($"{Base}/por-parada/{Guid.NewGuid()}");

        await AssertProblemaAsync(respuesta, HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task AbrirOrdenDeTrabajoComando_sin_parada_programada_responde_422()
    {
        var respuesta = await Cliente.PostAsJsonAsync(Base, CuerpoAbrir(paradaProgramada: false));

        await AssertProblemaAsync(respuesta, HttpStatusCode.UnprocessableEntity, "ParadaInexistente");
    }

    [Fact]
    public async Task AsignarTecnicoComando_asigna_al_tecnico_habilitado()
    {
        var id = await AbrirAsync();

        var respuesta = await PostAsync(id, "asignar-tecnico", new { tecnico = "Ana" });

        Assert.Equal(HttpStatusCode.NoContent, respuesta.StatusCode);
        Assert.Equal("Ana", (await ObtenerAsync(id)).GetProperty("tecnico").GetString());
    }

    [Fact]
    public async Task AsignarTecnicoComando_no_habilitado_responde_422()
    {
        var id = await AbrirAsync();
        _servidor.Habilitacion.Habilitado = false;

        var respuesta = await PostAsync(id, "asignar-tecnico", new { tecnico = "Ana" });

        await AssertProblemaAsync(respuesta, HttpStatusCode.UnprocessableEntity, "TecnicoNoHabilitado");
    }

    [Fact]
    public async Task RegistrarEjecucionDeTareaComando_registra_la_tarea()
    {
        var id = await AbrirAsync();

        var respuesta = await EjecutarAsync(id);

        Assert.Equal(HttpStatusCode.NoContent, respuesta.StatusCode);
        var orden = await ObtenerAsync(id);
        Assert.Equal("EnEjecucion", orden.GetProperty("estado").GetString());
        Assert.Equal("Ana", orden.GetProperty("tareas")[0].GetProperty("ejecutadaPor").GetString());
    }

    [Fact]
    public async Task RegistrarConsumoDeRepuestoComando_registra_el_consumo()
    {
        var id = await AbrirAsync();

        var respuesta = await PostAsync(id, "registrar-consumo-de-repuesto", new
        {
            consumoId = Guid.NewGuid(), referencia = "HEL-T40", cantidad = 2, requiereSerie = false
        });

        Assert.Equal(HttpStatusCode.NoContent, respuesta.StatusCode);
        Assert.Equal("HEL-T40", (await ObtenerAsync(id)).GetProperty("consumos")[0].GetProperty("referencia").GetString());
    }

    [Fact]
    public async Task RegistrarConsumoDeRepuestoComando_que_requiere_serie_sin_serie_responde_422()
    {
        var id = await AbrirAsync();

        var respuesta = await PostAsync(id, "registrar-consumo-de-repuesto", new
        {
            consumoId = Guid.NewGuid(), referencia = "MOT-01", cantidad = 1, requiereSerie = true, horaDeCorte = 12
        });

        await AssertProblemaAsync(respuesta, HttpStatusCode.UnprocessableEntity, "SerieFaltante");
    }

    [Fact]
    public async Task RegistrarHallazgoComando_registra_el_hallazgo()
    {
        var id = await AbrirAsync();

        var respuesta = await PostAsync(id, "registrar-hallazgo", new { descripcion = "Fisura en el brazo 3" });

        Assert.Equal(HttpStatusCode.NoContent, respuesta.StatusCode);
        Assert.Equal("Fisura en el brazo 3", (await ObtenerAsync(id)).GetProperty("hallazgos")[0].GetProperty("descripcion").GetString());
    }

    [Fact]
    public async Task RegistrarVueloDePruebaComando_registra_el_vuelo()
    {
        var id = await AbrirAsync();
        await EjecutarAsync(id);

        var respuesta = await PostAsync(id, "registrar-vuelo-de-prueba",
            new { realizadoEn = Ahora, duracionEnMinutos = 7, aprobado = true, observaciones = "Sin vibraciones" });

        Assert.Equal(HttpStatusCode.NoContent, respuesta.StatusCode);
        var orden = await ObtenerAsync(id);
        Assert.Equal("Ejecutada", orden.GetProperty("estado").GetString());
        Assert.True(orden.GetProperty("vueloDePrueba").GetProperty("aprobado").GetBoolean());
    }

    [Fact]
    public async Task LiberarDronComando_libera_el_dron()
    {
        var id = await AbrirAsync();
        await EjecutarAsync(id);

        var respuesta = await LiberarAsync(id);

        Assert.Equal(HttpStatusCode.NoContent, respuesta.StatusCode);
        var orden = await ObtenerAsync(id);
        Assert.Equal("Liberada", orden.GetProperty("estado").GetString());
        Assert.Equal("Beto", orden.GetProperty("liberacion").GetProperty("liberadaPor").GetString());
    }

    [Fact]
    public async Task LiberarDronComando_el_mismo_que_ejecuto_en_trabajo_mayor_responde_422()
    {
        var id = await AbrirAsync(mayor: true);
        await EjecutarAsync(id);
        await PostAsync(id, "registrar-vuelo-de-prueba",
            new { realizadoEn = Ahora, duracionEnMinutos = 7, aprobado = true, observaciones = "ok" });

        var respuesta = await LiberarAsync(id, "ANA");

        await AssertProblemaAsync(respuesta, HttpStatusCode.UnprocessableEntity, "LiberaElMismoQueEjecuto");
    }

    [Fact]
    public async Task CerrarOrdenDeTrabajoComando_cierra_la_orden_y_deja_el_evento_en_la_bandeja()
    {
        var id = await CerradaAsync();

        Assert.Equal("Cerrada", (await ObtenerAsync(id)).GetProperty("estado").GetString());
        Assert.Single(_servidor.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task PonerOrdenEnEsperaComando_pone_la_orden_en_espera()
    {
        var id = await AbrirAsync();

        var respuesta = await PostAsync(id, "poner-orden-en-espera", new { motivo = "Falta HEL-T40" });

        Assert.Equal(HttpStatusCode.NoContent, respuesta.StatusCode);
        var orden = await ObtenerAsync(id);
        Assert.Equal("EnEspera", orden.GetProperty("estado").GetString());
        Assert.Equal("Falta HEL-T40", orden.GetProperty("motivoDeEspera").GetString());
    }

    [Theory]
    [InlineData("asignar-tecnico", "{\"tecnico\":\"Ana\"}")]
    [InlineData("registrar-ejecucion-de-tarea", "{\"tareaId\":\"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa\",\"descripcion\":\"x\",\"resultado\":\"y\",\"ejecutadaPor\":\"Ana\",\"horas\":1}")]
    [InlineData("registrar-consumo-de-repuesto", "{\"consumoId\":\"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa\",\"referencia\":\"R\",\"cantidad\":1,\"requiereSerie\":false}")]
    [InlineData("registrar-hallazgo", "{\"descripcion\":\"x\"}")]
    [InlineData("registrar-vuelo-de-prueba", "{\"realizadoEn\":\"2026-11-20T08:00:00Z\",\"duracionEnMinutos\":5,\"aprobado\":true,\"observaciones\":\"ok\"}")]
    [InlineData("liberar-dron", "{\"liberacionId\":\"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa\",\"liberadaPor\":\"Beto\"}")]
    [InlineData("cerrar-orden-de-trabajo", "{}")]
    [InlineData("poner-orden-en-espera", "{\"motivo\":\"x\"}")]
    public async Task Cada_comando_sobre_una_orden_cerrada_responde_422(string comando, string cuerpo)
    {
        var id = await CerradaAsync();

        var respuesta = await Cliente.PostAsync($"{Base}/{id}/{comando}", new StringContent(cuerpo, Encoding.UTF8, "application/json"));

        await AssertProblemaAsync(respuesta, HttpStatusCode.UnprocessableEntity, "OrdenCerradaInmutable");
    }

    [Fact]
    public async Task Un_cuerpo_invalido_responde_400_problem_json()
    {
        var id = await AbrirAsync();

        var vacio = await PostAsync(id, "asignar-tecnico", new { tecnico = " " });
        var roto = await Cliente.PostAsync($"{Base}/{id}/asignar-tecnico", new StringContent("{no es json", Encoding.UTF8, "application/json"));

        await AssertProblemaAsync(vacio, HttpStatusCode.BadRequest);
        await AssertProblemaAsync(roto, HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task Una_orden_inexistente_responde_404_problem_json()
    {
        var lectura = await Cliente.GetAsync($"{Base}/{Guid.NewGuid()}");
        var comando = await PostAsync(Guid.NewGuid(), "registrar-hallazgo", new { descripcion = "x" });

        await AssertProblemaAsync(lectura, HttpStatusCode.NotFound);
        await AssertProblemaAsync(comando, HttpStatusCode.NotFound);
    }
}
