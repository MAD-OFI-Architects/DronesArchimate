using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Infrastructure.Mensajeria;
using BuildingBlocks.Infrastructure.Outbox;
using BuildingBlocks.Infrastructure.Persistencia;
using BuildingBlocks.Infrastructure.Tiempo;
using BuildingBlocks.Tests.Soporte;
using Microsoft.Extensions.Logging.Abstractions;

namespace BuildingBlocks.Tests.Infraestructura;

public class DespachadorDeBandejaDeSalidaTests
{
    private sealed class BusQueFalla(int fallos) : IBusDeEventos
    {
        private int _restantes = fallos;

        public List<SobreDeEvento> Publicados { get; } = [];

        public Task PublicarAsync(SobreDeEvento sobre, CancellationToken cancellationToken = default)
        {
            if (_restantes-- > 0)
                throw new FalloDePublicacionException("bus caído");

            Publicados.Add(sobre);
            return Task.CompletedTask;
        }
    }

    private static async Task<(AlmacenDeDocumentosEnMemoria Almacen, MensajeDeSalida Mensaje)> ConUnMensajeAsync()
    {
        var almacen = new AlmacenDeDocumentosEnMemoria();
        var mensaje = new MensajeDeSalida
        {
            Id = Guid.NewGuid(), Topico = "t.v1", PayloadJson = "{\"a\":1}", OcurrioEn = Escenario.Inicio, CorrelacionId = Guid.NewGuid()
        };
        await almacen.ConfirmarAsync(new LoteDeEscritura([], [mensaje], []));
        return (almacen, mensaje);
    }

    private sealed class LoggerQueRegistra<T> : Microsoft.Extensions.Logging.ILogger<T>
    {
        public List<(Microsoft.Extensions.Logging.LogLevel Nivel, string Texto)> Entradas { get; } = [];

        public IDisposable? BeginScope<TState>(TState estado) where TState : notnull => null;

        public bool IsEnabled(Microsoft.Extensions.Logging.LogLevel nivel) => true;

        public void Log<TState>(Microsoft.Extensions.Logging.LogLevel nivel, Microsoft.Extensions.Logging.EventId id, TState estado, Exception? ex, Func<TState, Exception?, string> formato) =>
            Entradas.Add((nivel, formato(estado, ex)));
    }

    private static DespachadorDeBandejaDeSalida Crear(AlmacenDeDocumentosEnMemoria almacen, IBusDeEventos bus, RelojSimulado reloj, int maximo = 10) =>
        new(almacen, bus, reloj, new OpcionesDeDespacho { MaximoDeIntentos = maximo }, NullLogger<DespachadorDeBandejaDeSalida>.Instance);

    [Fact]
    public async Task Publica_el_sobre_con_el_Id_del_evento_y_marca_el_mensaje()
    {
        var (almacen, mensaje) = await ConUnMensajeAsync();
        var bus = new BusDeEventosEnMemoria();

        var publicados = await Crear(almacen, bus, new RelojSimulado(Escenario.Inicio)).DespacharPendientesAsync();

        var sobre = Assert.Single(bus.Publicados);
        Assert.Equal(1, publicados);
        Assert.Equal(mensaje.Id, sobre.EventId);
        Assert.Equal(mensaje.CorrelacionId, sobre.CorrelationId);
        Assert.Equal(1, sobre.Payload.GetProperty("a").GetInt32());
        Assert.NotNull(almacen.MensajesDeSalida.Single().PublicadoEn);
        Assert.Equal(0, await Crear(almacen, bus, new RelojSimulado(Escenario.Inicio)).DespacharPendientesAsync());
    }

    [Fact]
    public async Task Reintenta_con_espera_creciente_hasta_que_el_bus_responde()
    {
        var (almacen, _) = await ConUnMensajeAsync();
        var bus = new BusQueFalla(fallos: 2);
        var reloj = new RelojSimulado(Escenario.Inicio);
        var despachador = Crear(almacen, bus, reloj);

        Assert.Equal(0, await despachador.DespacharPendientesAsync());
        Assert.Equal(1, almacen.MensajesDeSalida.Single().Intentos);
        Assert.Equal(0, await despachador.DespacharPendientesAsync());
        Assert.Empty(bus.Publicados);

        reloj.Avanzar(TimeSpan.FromMilliseconds(250));
        Assert.Equal(0, await despachador.DespacharPendientesAsync());
        Assert.Equal(2, almacen.MensajesDeSalida.Single().Intentos);

        reloj.Avanzar(TimeSpan.FromMilliseconds(500));
        Assert.Equal(1, await despachador.DespacharPendientesAsync());
        Assert.Single(bus.Publicados);
        Assert.Equal("bus caído", almacen.MensajesDeSalida.Single().UltimoError);
    }

    [Fact]
    public async Task Deja_de_reintentar_al_agotar_los_intentos()
    {
        var (almacen, _) = await ConUnMensajeAsync();
        var bus = new BusQueFalla(fallos: int.MaxValue);
        var reloj = new RelojSimulado(Escenario.Inicio);
        var despachador = Crear(almacen, bus, reloj, maximo: 2);

        for (var i = 0; i < 5; i++)
        {
            await despachador.DespacharPendientesAsync();
            reloj.Avanzar(TimeSpan.FromMinutes(1));
        }

        Assert.Equal(2, almacen.MensajesDeSalida.Single().Intentos);
    }

    [Fact]
    public async Task Al_agotar_los_intentos_lo_deja_como_error_para_que_no_se_pierda_en_silencio()
    {
        var (almacen, mensaje) = await ConUnMensajeAsync();
        var log = new LoggerQueRegistra<DespachadorDeBandejaDeSalida>();
        var reloj = new RelojSimulado(Escenario.Inicio);
        var despachador = new DespachadorDeBandejaDeSalida(almacen, new BusQueFalla(int.MaxValue), reloj, new OpcionesDeDespacho { MaximoDeIntentos = 2 }, log);

        for (var i = 0; i < 4; i++)
        {
            await despachador.DespacharPendientesAsync();
            reloj.Avanzar(TimeSpan.FromMinutes(1));
        }

        var error = Assert.Single(log.Entradas, e => e.Nivel == Microsoft.Extensions.Logging.LogLevel.Error);
        Assert.Contains(mensaje.Id.ToString(), error.Texto);
        Assert.Contains("agotó", error.Texto);
    }
}
