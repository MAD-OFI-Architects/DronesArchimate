using System.Text.Json;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Infrastructure.Mensajeria;
using Intervenciones.Application.Comandos;
using Intervenciones.Contracts;
using Intervenciones.Domain;
using Intervenciones.Tests.Soporte;
using Microsoft.Extensions.DependencyInjection;

namespace Intervenciones.Tests.Application;

public class ConsumidoresTests
{
    private static SobreDeEvento Sobre(string topico, object payload, Guid? eventId = null) =>
        new(eventId ?? Guid.NewGuid(), topico, EscenarioDeIntervenciones.Inicio, Guid.NewGuid(),
            JsonSerializer.SerializeToElement(payload, new JsonSerializerOptions(JsonSerializerDefaults.Web)));

    private static object Parada() => new
    {
        paradaId = EscenarioDeIntervenciones.Parada,
        dronId = "ADV-03",
        fechaProgramada = "2026-11-20T08:00:00Z",
        tareas = new[] { new { tareaId = "T-101", descripcion = "Cambio de hélices", repuestos = new[] { new { referencia = "HEL-T40", cantidad = 2 } } } }
    };

    private static object Faltante() => new { paradaId = EscenarioDeIntervenciones.Parada, referencia = "HEL-T40", cantidadFaltante = 1 };

    private static ProcesadorDeMensajeEntrante Procesador(EscenarioDeIntervenciones e) =>
        e.Proveedor.GetRequiredService<ProcesadorDeMensajeEntrante>();

    [Fact]
    public async Task Parada_programada_abre_la_orden_de_la_parada()
    {
        await using var e = new EscenarioDeIntervenciones();

        var resultado = await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.ParadaProgramada, Parada()));

        Assert.Equal(ResultadoDeProcesamiento.Procesado, resultado);
        var orden = Assert.Single(await e.OrdenesAsync());
        var memento = await e.MementoAsync(Guid.Parse(orden.Id));
        Assert.Equal((EscenarioDeIntervenciones.Parada, "ADV-03", "Abierta"), (memento.ParadaId, memento.DronId, memento.Estado));
    }

    [Fact]
    public async Task Parada_programada_es_idempotente_por_evento_y_por_parada()
    {
        await using var e = new EscenarioDeIntervenciones();
        var eventId = Guid.NewGuid();

        await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.ParadaProgramada, Parada(), eventId));
        var repetido = await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.ParadaProgramada, Parada(), eventId));
        await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.ParadaProgramada, Parada()));

        Assert.Equal(ResultadoDeProcesamiento.Duplicado, repetido);
        Assert.Single(await e.OrdenesAsync());
    }

    [Fact]
    public async Task Faltante_detectado_pone_la_orden_en_espera()
    {
        await using var e = new EscenarioDeIntervenciones();
        var id = await e.AbrirAsync();

        await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.FaltanteDetectado, Faltante()));

        var memento = await e.MementoAsync(id);
        Assert.Equal("EnEspera", memento.Estado);
        Assert.Contains("HEL-T40", memento.MotivoDeEspera);
    }

    [Fact]
    public async Task Faltante_detectado_es_idempotente_por_evento_y_por_estado()
    {
        await using var e = new EscenarioDeIntervenciones();
        var id = await e.AbrirAsync();
        var eventId = Guid.NewGuid();

        await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.FaltanteDetectado, Faltante(), eventId));
        var repetido = await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.FaltanteDetectado, Faltante(), eventId));
        var otroEvento = await Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.FaltanteDetectado, Faltante()));

        Assert.Equal(ResultadoDeProcesamiento.Duplicado, repetido);
        Assert.Equal(ResultadoDeProcesamiento.Procesado, otroEvento);
        Assert.Equal("EnEspera", (await e.MementoAsync(id)).Estado);
    }

    [Fact]
    public async Task Cerrada_la_orden_el_faltante_ya_no_la_modifica()
    {
        await using var e = new EscenarioDeIntervenciones();
        var id = await e.AbrirAsync();
        await e.EnviarAsync(new RegistrarEjecucionDeTareaComando(id, Guid.NewGuid(), "Revisión", "Realizada", "Ana", 1m));
        await e.EnviarAsync(new LiberarDronComando(id, Guid.NewGuid(), "Beto"));
        await e.EnviarAsync(new CerrarOrdenDeTrabajoComando(id));

        await Assert.ThrowsAsync<BuildingBlocks.Domain.BusinessRuleViolationException>(() =>
            Procesador(e).ProcesarAsync(Sobre(IntervencionesTopicos.FaltanteDetectado, Faltante())));

        Assert.Equal("Cerrada", (await e.MementoAsync(id)).Estado);
    }
}
