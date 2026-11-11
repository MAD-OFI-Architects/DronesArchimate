using System.Text.Json;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Infrastructure.Mensajeria;
using BuildingBlocks.Tests.Soporte;
using Microsoft.Extensions.DependencyInjection;

namespace BuildingBlocks.Tests.Infraestructura;

public class ProcesadorDeMensajeEntranteTests
{
    private static SobreDeEvento Sobre(Guid eventId, Guid cuentaId, Guid? correlacion = null, string topico = CuentaExternaConsumidor.NombreDelTopico) =>
        new(eventId, topico, Escenario.Inicio, correlacion ?? Guid.NewGuid(),
            JsonSerializer.SerializeToElement(new { cuentaId, titular = "Ana" }));

    [Fact]
    public async Task Procesa_el_mensaje_una_vez_aunque_llegue_repetido()
    {
        await using var escenario = new Escenario();
        var procesador = escenario.Proveedor.GetRequiredService<ProcesadorDeMensajeEntrante>();
        var sobre = Sobre(Guid.NewGuid(), Guid.NewGuid());

        Assert.Equal(ResultadoDeProcesamiento.Procesado, await procesador.ProcesarAsync(sobre));
        Assert.Equal(ResultadoDeProcesamiento.Duplicado, await procesador.ProcesarAsync(sobre));
        Assert.Equal(ResultadoDeProcesamiento.Duplicado, await procesador.ProcesarAsync(sobre));

        Assert.Single(escenario.Almacen.MensajesDeSalida);
        Assert.True(await escenario.Almacen.ExisteMensajeEntranteAsync(sobre.EventId));
    }

    [Fact]
    public async Task Mensajes_distintos_se_procesan_cada_uno()
    {
        await using var escenario = new Escenario();
        var procesador = escenario.Proveedor.GetRequiredService<ProcesadorDeMensajeEntrante>();

        await procesador.ProcesarAsync(Sobre(Guid.NewGuid(), Guid.NewGuid()));
        await procesador.ProcesarAsync(Sobre(Guid.NewGuid(), Guid.NewGuid()));

        Assert.Equal(2, escenario.Almacen.MensajesDeSalida.Count);
    }

    [Fact]
    public async Task La_correlacion_del_mensaje_viaja_a_los_eventos_que_origina()
    {
        await using var escenario = new Escenario();
        var correlacion = Guid.NewGuid();

        await escenario.Proveedor.GetRequiredService<ProcesadorDeMensajeEntrante>()
            .ProcesarAsync(Sobre(Guid.NewGuid(), Guid.NewGuid(), correlacion));

        Assert.Equal(correlacion, escenario.Almacen.MensajesDeSalida.Single().CorrelacionId);
    }

    [Fact]
    public async Task Un_topico_sin_consumidor_se_informa_y_no_marca_nada()
    {
        await using var escenario = new Escenario();
        var sobre = Sobre(Guid.NewGuid(), Guid.NewGuid(), topico: "otro.v1");

        var resultado = await escenario.Proveedor.GetRequiredService<ProcesadorDeMensajeEntrante>().ProcesarAsync(sobre);

        Assert.Equal(ResultadoDeProcesamiento.TopicoNoSuscrito, resultado);
        Assert.False(await escenario.Almacen.ExisteMensajeEntranteAsync(sobre.EventId));
    }

    [Fact]
    public async Task Si_el_manejador_falla_el_mensaje_no_queda_marcado_y_puede_reintentarse()
    {
        await using var escenario = new Escenario();
        var procesador = escenario.Proveedor.GetRequiredService<ProcesadorDeMensajeEntrante>();
        var malo = Sobre(Guid.NewGuid(), Guid.Empty);

        await Assert.ThrowsAsync<BuildingBlocks.Application.Excepciones.ValidacionException>(() => procesador.ProcesarAsync(malo));

        Assert.False(await escenario.Almacen.ExisteMensajeEntranteAsync(malo.EventId));
        Assert.Empty(escenario.Almacen.MensajesDeSalida);
    }
}
