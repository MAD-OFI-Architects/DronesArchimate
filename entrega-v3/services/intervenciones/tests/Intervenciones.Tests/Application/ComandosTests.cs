using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Persistencia;
using Microsoft.Extensions.DependencyInjection;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Domain;
using Intervenciones.Application.Comandos;
using Intervenciones.Application.Consultas;
using Intervenciones.Application.Reglas;
using Intervenciones.Contracts;
using Intervenciones.Domain;
using Intervenciones.Tests.Soporte;

namespace Intervenciones.Tests.Application;

public class ComandosTests
{
    private static readonly DateTimeOffset Ahora = EscenarioDeIntervenciones.Inicio;

    private static async Task<(EscenarioDeIntervenciones Escenario, Guid Id)> ConOrdenAsync(bool mayor = false, bool habilitado = true)
    {
        var escenario = new EscenarioDeIntervenciones(habilitado);
        return (escenario, await escenario.AbrirAsync(mayor));
    }

    private static Task EjecutarAsync(EscenarioDeIntervenciones e, Guid id, string quien = "Ana") =>
        e.EnviarAsync(new RegistrarEjecucionDeTareaComando(id, Guid.NewGuid(), "Cambio de hélices", "Realizada", quien, 3.5m));

    [Fact]
    public async Task Abrir_persiste_la_orden_abierta_sin_publicar_nada()
    {
        await using var e = new EscenarioDeIntervenciones();

        var id = await e.AbrirAsync();

        var memento = await e.MementoAsync(id);
        Assert.Equal("Abierta", memento.Estado);
        Assert.Equal(EscenarioDeIntervenciones.Parada, memento.ParadaId);
        Assert.Empty(e.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Abrir_dos_veces_la_misma_parada_devuelve_la_misma_orden()
    {
        await using var e = new EscenarioDeIntervenciones();

        var primera = await e.AbrirAsync();
        var segunda = await e.AbrirAsync();

        Assert.Equal(primera, segunda);
        Assert.Single(await e.OrdenesAsync());
    }

    [Fact]
    public async Task Dos_aperturas_simultaneas_de_la_misma_parada_no_duplican_la_orden()
    {
        await using var e = new EscenarioDeIntervenciones();
        var comando = new AbrirOrdenDeTrabajoComando(EscenarioDeIntervenciones.Parada, true, "ADV-03", "Preventiva", false);
        await using var a = e.Proveedor.CreateAsyncScope();
        await using var b = e.Proveedor.CreateAsyncScope();

        // Ambas leen "no existe" antes de que cualquiera confirme: es el entrelazado que duplicaba órdenes.
        var idA = await a.ServiceProvider.GetRequiredService<IManejadorDeSolicitud<AbrirOrdenDeTrabajoComando, Guid>>().ManejarAsync(comando, default);
        var idB = await b.ServiceProvider.GetRequiredService<IManejadorDeSolicitud<AbrirOrdenDeTrabajoComando, Guid>>().ManejarAsync(comando, default);
        await a.ServiceProvider.GetRequiredService<IUnidadDeTrabajo>().ConfirmarAsync();

        Assert.Equal(idA, idB);
        await Assert.ThrowsAsync<ConflictoDeConcurrenciaException>(() => b.ServiceProvider.GetRequiredService<IUnidadDeTrabajo>().ConfirmarAsync());
        Assert.Single(await e.OrdenesAsync());
        Assert.Equal(idA, await e.AbrirAsync());                                   // el reintento del perdedor devuelve la existente
    }

    [Fact]
    public void La_identidad_de_la_orden_es_estable_y_distinta_por_parada() =>
        Assert.True(IdentidadDeOrden.DeParada(EscenarioDeIntervenciones.Parada) == IdentidadDeOrden.DeParada(EscenarioDeIntervenciones.Parada)
            && IdentidadDeOrden.DeParada(EscenarioDeIntervenciones.Parada) != IdentidadDeOrden.DeParada(Guid.NewGuid()));

    [Fact]
    public async Task Abrir_sin_parada_programada_rompe_ParadaInexistente()
    {
        await using var e = new EscenarioDeIntervenciones();

        var error = await Assert.ThrowsAsync<BusinessRuleViolationException>(() =>
            e.EnviarAsync(new AbrirOrdenDeTrabajoComando(EscenarioDeIntervenciones.Parada, false, "ADV-03", "Preventiva", false)));

        Assert.IsType<ParadaInexistente>(error.BrokenRule);
        Assert.Empty(await e.OrdenesAsync());
    }

    [Fact]
    public async Task Asignar_tecnico_persiste_al_tecnico_habilitado()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;

        await e.EnviarAsync(new AsignarTecnicoComando(id, "Ana"));

        Assert.Equal("Ana", (await e.MementoAsync(id)).Tecnico);
        Assert.Empty(e.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Asignar_tecnico_no_habilitado_rompe_TecnicoNoHabilitado()
    {
        var (e, id) = await ConOrdenAsync(habilitado: false);
        await using var _ = e;

        var error = await Assert.ThrowsAsync<BusinessRuleViolationException>(() =>
            e.EnviarAsync(new AsignarTecnicoComando(id, "Ana")));

        Assert.IsType<TecnicoNoHabilitado>(error.BrokenRule);
        Assert.Null((await e.MementoAsync(id)).Tecnico);
    }

    [Fact]
    public async Task Registrar_ejecucion_de_tarea_persiste_la_tarea_y_pasa_a_en_ejecucion()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;

        await EjecutarAsync(e, id);

        var memento = await e.MementoAsync(id);
        Assert.Equal("EnEjecucion", memento.Estado);
        var tarea = Assert.Single(memento.Tareas);
        Assert.Equal(("Ana", 3.5m), (tarea.EjecutadaPor, tarea.Horas));
        Assert.Empty(e.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Registrar_consumo_persiste_el_consumo()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;

        await e.EnviarAsync(new RegistrarConsumoDeRepuestoComando(id, Guid.NewGuid(), "HEL-T40", 2, false, null, null, null));

        var consumo = Assert.Single((await e.MementoAsync(id)).Consumos);
        Assert.Equal(("HEL-T40", 2), (consumo.Referencia, consumo.Cantidad));
        Assert.Empty(e.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Registrar_consumo_que_requiere_serie_sin_serie_rompe_SerieFaltante()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;

        var error = await Assert.ThrowsAsync<BusinessRuleViolationException>(() =>
            e.EnviarAsync(new RegistrarConsumoDeRepuestoComando(id, Guid.NewGuid(), "MOT-01", 1, true, null, null, 12m)));

        Assert.IsType<SerieFaltante>(error.BrokenRule);
        Assert.Empty((await e.MementoAsync(id)).Consumos);
    }

    [Fact]
    public async Task Registrar_hallazgo_persiste_el_hallazgo()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;

        await e.EnviarAsync(new RegistrarHallazgoComando(id, "Fisura en el brazo 3"));

        Assert.Equal("Fisura en el brazo 3", Assert.Single((await e.MementoAsync(id)).Hallazgos).Descripcion);
        Assert.Empty(e.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Registrar_vuelo_de_prueba_persiste_el_vuelo_y_pasa_a_ejecutada()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;
        await EjecutarAsync(e, id);

        await e.EnviarAsync(new RegistrarVueloDePruebaComando(id, Ahora, 7, true, "Sin vibraciones"));

        var memento = await e.MementoAsync(id);
        Assert.Equal("Ejecutada", memento.Estado);
        Assert.True(memento.VueloDePrueba!.Aprobado);
    }

    [Fact]
    public async Task Liberar_dron_persiste_la_liberacion()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;
        await EjecutarAsync(e, id);

        await e.EnviarAsync(new LiberarDronComando(id, Guid.NewGuid(), "Beto"));

        var memento = await e.MementoAsync(id);
        Assert.Equal("Liberada", memento.Estado);
        Assert.Equal("Beto", memento.Liberacion!.LiberadaPor);
    }

    [Fact]
    public async Task Liberar_el_mismo_que_ejecuto_en_trabajo_mayor_rompe_LiberaElMismoQueEjecuto()
    {
        var (e, id) = await ConOrdenAsync(mayor: true);
        await using var _ = e;
        await EjecutarAsync(e, id);
        await e.EnviarAsync(new RegistrarVueloDePruebaComando(id, Ahora, 7, true, "Sin vibraciones"));

        var error = await Assert.ThrowsAsync<BusinessRuleViolationException>(() =>
            e.EnviarAsync(new LiberarDronComando(id, Guid.NewGuid(), "ana")));

        Assert.IsType<LiberaElMismoQueEjecuto>(error.BrokenRule);
    }

    [Fact]
    public async Task Cerrar_persiste_la_orden_y_deja_orden_de_trabajo_cerrada_en_la_bandeja()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;
        await EjecutarAsync(e, id);
        await e.EnviarAsync(new RegistrarConsumoDeRepuestoComando(id, Guid.NewGuid(), "HEL-T40", 2, false, null, null, null));
        await e.EnviarAsync(new LiberarDronComando(id, Guid.NewGuid(), "Beto"));

        await e.EnviarAsync(new CerrarOrdenDeTrabajoComando(id));

        Assert.Equal("Cerrada", (await e.MementoAsync(id)).Estado);
        var mensaje = Assert.Single(e.Almacen.MensajesDeSalida);
        Assert.Equal(IntervencionesTopicos.OrdenDeTrabajoCerrada, mensaje.Topico);
        Assert.Contains(id.ToString(), mensaje.PayloadJson);
        Assert.Contains("\"horasHombre\":3.5", mensaje.PayloadJson);
        Assert.Contains("HEL-T40", mensaje.PayloadJson);
    }

    [Fact]
    public async Task La_orden_cerrada_informa_instalaciones_y_retiros_con_su_hora_de_corte()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;
        await EjecutarAsync(e, id);
        await e.EnviarAsync(new RegistrarConsumoDeRepuestoComando(id, Guid.NewGuid(), "BAT-22K", 1, true, "BAT-0377", "BAT-0412", 112.5m));
        await e.EnviarAsync(new LiberarDronComando(id, Guid.NewGuid(), "Beto"));

        await e.EnviarAsync(new CerrarOrdenDeTrabajoComando(id));

        var contrato = System.Text.Json.JsonSerializer.Deserialize<OrdenDeTrabajoCerradaV1>(
            Assert.Single(e.Almacen.MensajesDeSalida).PayloadJson, new System.Text.Json.JsonSerializerOptions(System.Text.Json.JsonSerializerDefaults.Web))!;
        var consumo = Assert.Single(contrato.Consumos);
        Assert.Equal(("BAT-22K", 1, "BAT-0412", "BAT-0377", 112.5m), (consumo.Referencia, consumo.Cantidad, consumo.NumeroSerie, consumo.SerieRetirada, consumo.HoraDeCorte));
    }

    [Fact]
    public async Task Cerrada_la_orden_rechaza_cualquier_modificacion()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;
        await EjecutarAsync(e, id);
        await e.EnviarAsync(new LiberarDronComando(id, Guid.NewGuid(), "Beto"));
        await e.EnviarAsync(new CerrarOrdenDeTrabajoComando(id));

        var error = await Assert.ThrowsAsync<BusinessRuleViolationException>(() =>
            e.EnviarAsync(new RegistrarHallazgoComando(id, "Otro")));

        Assert.IsType<OrdenCerradaInmutable>(error.BrokenRule);
    }

    [Fact]
    public async Task Poner_en_espera_persiste_el_motivo()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;

        await e.EnviarAsync(new PonerOrdenEnEsperaComando(id, "Falta HEL-T40"));

        var memento = await e.MementoAsync(id);
        Assert.Equal("EnEspera", memento.Estado);
        Assert.Equal("Falta HEL-T40", memento.MotivoDeEspera);
        Assert.Empty(e.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Comando_sobre_orden_inexistente_da_recurso_no_encontrado()
    {
        await using var e = new EscenarioDeIntervenciones();

        await Assert.ThrowsAsync<RecursoNoEncontradoException>(() =>
            e.EnviarAsync(new CerrarOrdenDeTrabajoComando(Guid.NewGuid())));
    }

    public static TheoryData<object> ComandosInvalidos => new()
    {
        new AbrirOrdenDeTrabajoComando(Guid.Empty, true, "ADV-03", "Preventiva", false),
        new AbrirOrdenDeTrabajoComando(EscenarioDeIntervenciones.Parada, true, "ADV-03", "Inventada", false),
        new AsignarTecnicoComando(Guid.NewGuid(), " "),
        new RegistrarEjecucionDeTareaComando(Guid.NewGuid(), Guid.NewGuid(), "x", "y", "Ana", 0m),
        new RegistrarConsumoDeRepuestoComando(Guid.NewGuid(), Guid.NewGuid(), "HEL", 0, false, null, null, null),
        new RegistrarHallazgoComando(Guid.NewGuid(), ""),
        new RegistrarVueloDePruebaComando(Guid.NewGuid(), Ahora, 30, true, "ok"),
        new LiberarDronComando(Guid.NewGuid(), Guid.NewGuid(), ""),
        new CerrarOrdenDeTrabajoComando(Guid.Empty),
        new PonerOrdenEnEsperaComando(Guid.NewGuid(), "")
    };

    [Theory]
    [MemberData(nameof(ComandosInvalidos))]
    public async Task Comando_invalido_se_rechaza_con_validacion_y_no_persiste(object comando)
    {
        await using var e = new EscenarioDeIntervenciones();

        var error = await Assert.ThrowsAsync<ValidacionException>(() => EnviarDinamicoAsync(e, comando));

        Assert.NotEmpty(error.Errores);
        Assert.Empty(await e.OrdenesAsync());
    }

    private static Task EnviarDinamicoAsync(EscenarioDeIntervenciones e, object comando) => comando switch
    {
        AbrirOrdenDeTrabajoComando c => e.EnviarAsync(c),
        IComandoDeOrden c => e.EnviarAsync(c),
        _ => throw new ArgumentException("Comando desconocido.", nameof(comando))
    };

    [Fact]
    public async Task Obtener_devuelve_el_dto_de_la_orden()
    {
        var (e, id) = await ConOrdenAsync();
        await using var _ = e;
        await EjecutarAsync(e, id);

        var dto = await e.EnviarAsync(new ObtenerOrdenDeTrabajoConsulta(id));

        Assert.Equal(id, dto.Id);
        Assert.Equal("EnEjecucion", dto.Estado);
        Assert.Equal(3.5m, dto.HorasHombre);
        Assert.Single(dto.Tareas);
    }

    [Fact]
    public async Task Obtener_orden_inexistente_da_recurso_no_encontrado()
    {
        await using var e = new EscenarioDeIntervenciones();

        await Assert.ThrowsAsync<RecursoNoEncontradoException>(() =>
            e.EnviarAsync(new ObtenerOrdenDeTrabajoConsulta(Guid.NewGuid())));
    }
}
