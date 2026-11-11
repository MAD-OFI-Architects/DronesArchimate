using System.Net.Http.Json;
using System.Text.Json;
using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;
using Intervenciones.Infrastructure.Persistencia;
using Intervenciones.Tests.Soporte;

namespace Intervenciones.Tests.Infraestructura;

public class RepositorioCacheadoTests
{
    private static readonly DateTimeOffset Inicio = EscenarioDeIntervenciones.Inicio;

    private static OrdenDeTrabajo NuevaOrden() =>
        OrdenDeTrabajo.Abrir(Guid.NewGuid(), EscenarioDeIntervenciones.Parada, true, "ADV-03", TipoDeOrden.Preventiva, false, Inicio);

    [Fact]
    public async Task La_segunda_lectura_no_toca_el_repositorio()
    {
        var orden = NuevaOrden();
        var interno = new RepositorioContador(orden);
        var cacheado = new RepositorioCacheadoOrdenDeTrabajo(interno, new CacheDeOrdenes(new RelojManual(Inicio)));

        var primera = await cacheado.ObtenerAsync(orden.Id);
        var segunda = await cacheado.ObtenerAsync(orden.Id);

        Assert.Equal(1, interno.Lecturas);
        Assert.Equal((primera!.Id, primera.Estado), (segunda!.Id, segunda.Estado));
        Assert.NotSame(primera, segunda);
    }

    [Fact]
    public async Task Guardar_invalida_la_entrada()
    {
        var orden = NuevaOrden();
        var interno = new RepositorioContador(orden);
        var cacheado = new RepositorioCacheadoOrdenDeTrabajo(interno, new CacheDeOrdenes(new RelojManual(Inicio)));
        await cacheado.ObtenerAsync(orden.Id);

        await cacheado.GuardarAsync(orden);
        await cacheado.ObtenerAsync(orden.Id);

        Assert.Equal(2, interno.Lecturas);
    }

    [Fact]
    public async Task La_entrada_vence_pasado_el_ttl_de_60_segundos()
    {
        var orden = NuevaOrden();
        var reloj = new RelojManual(Inicio);
        var interno = new RepositorioContador(orden);
        var cacheado = new RepositorioCacheadoOrdenDeTrabajo(interno, new CacheDeOrdenes(reloj));
        await cacheado.ObtenerAsync(orden.Id);

        reloj.Avanzar(TimeSpan.FromSeconds(59));
        await cacheado.ObtenerAsync(orden.Id);
        reloj.Avanzar(TimeSpan.FromSeconds(2));
        await cacheado.ObtenerAsync(orden.Id);

        Assert.Equal(2, interno.Lecturas);
    }

    [Fact]
    public async Task Una_orden_inexistente_no_se_cachea()
    {
        var interno = new RepositorioContador(null);
        var cacheado = new RepositorioCacheadoOrdenDeTrabajo(interno, new CacheDeOrdenes(new RelojManual(Inicio)));

        Assert.Null(await cacheado.ObtenerAsync(Guid.NewGuid()));
        Assert.Null(await cacheado.ObtenerAsync(Guid.NewGuid()));

        Assert.Equal(2, interno.Lecturas);
    }

    [Fact]
    public async Task Un_comando_confirmado_invalida_la_lectura_cacheada_por_http()
    {
        await using var servidor = await ServidorDeIntervenciones.IniciarAsync();
        var abrir = await servidor.Cliente.PostAsJsonAsync("/api/orden-de-trabajo", new
        {
            paradaId = EscenarioDeIntervenciones.Parada, paradaProgramada = true, dronId = "ADV-03", tipo = "Preventiva", esTrabajoMayor = false
        });
        var id = (await abrir.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetGuid();
        await servidor.Cliente.GetAsync($"/api/orden-de-trabajo/{id}");

        await servidor.Cliente.PostAsJsonAsync($"/api/orden-de-trabajo/{id}/registrar-hallazgo", new { descripcion = "Fisura" });
        var orden = await servidor.Cliente.GetFromJsonAsync<JsonElement>($"/api/orden-de-trabajo/{id}");

        Assert.Equal(1, orden.GetProperty("hallazgos").GetArrayLength());
    }

    private sealed class RelojManual(DateTimeOffset ahora) : IClock
    {
        private DateTimeOffset _ahora = ahora;

        public DateTimeOffset Now => _ahora;

        public void Avanzar(TimeSpan tiempo) => _ahora += tiempo;
    }

    private sealed class RepositorioContador(OrdenDeTrabajo? orden) : IOrdenDeTrabajoRepository
    {
        public int Lecturas { get; private set; }

        public Task<OrdenDeTrabajo?> ObtenerAsync(Guid id, CancellationToken cancellationToken = default)
        {
            Lecturas++;
            return Task.FromResult(orden);
        }

        public Task<OrdenDeTrabajo?> ObtenerPorParadaAsync(Guid paradaId, CancellationToken cancellationToken = default) =>
            Task.FromResult(orden);

        public Task GuardarAsync(OrdenDeTrabajo ordenAGuardar, CancellationToken cancellationToken = default) => Task.CompletedTask;
    }
}
