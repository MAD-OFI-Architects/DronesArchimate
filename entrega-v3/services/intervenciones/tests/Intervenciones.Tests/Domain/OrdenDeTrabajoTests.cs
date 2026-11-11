using BuildingBlocks.Domain;
using Intervenciones.Domain;

namespace Intervenciones.Tests.Domain;

public class OrdenDeTrabajoTests
{
    private static readonly DateTimeOffset Ahora = new(2026, 11, 20, 8, 0, 0, TimeSpan.Zero);
    private static readonly Guid Parada = Guid.Parse("11111111-1111-4111-8111-111111111111");

    private static OrdenDeTrabajo Abierta(bool mayor = false) =>
        OrdenDeTrabajo.Abrir(Guid.NewGuid(), Parada, true, "ADV-03", TipoDeOrden.Preventiva, mayor, Ahora);

    private static void Ejecutar(OrdenDeTrabajo orden, string quien = "Ana") =>
        orden.RegistrarEjecucionDeTarea(Guid.NewGuid(), "Cambio de hélices", "Realizada", quien, new HorasHombre(3.5m), Ahora);

    private static VueloDePrueba VueloOk() => new(Ahora, 7, true, "Sin vibraciones");

    private static TEvento Unico<TEvento>(OrdenDeTrabajo orden) where TEvento : IDomainEvent =>
        Assert.IsType<TEvento>(Assert.Single(orden.DomainEvents));

    private static void RomperRegla<TRegla>(Action accion) where TRegla : IBusinessRule
    {
        var error = Assert.Throws<BusinessRuleViolationException>(accion);
        Assert.IsType<TRegla>(error.BrokenRule);
    }

    [Fact]
    public void Abrir_levanta_orden_de_trabajo_abierta()
    {
        var orden = Abierta();

        var evento = Unico<OrdenDeTrabajoAbierta>(orden);
        Assert.Equal(orden.Id, evento.OrdenId);
        Assert.Equal(EstadoDeLaOrden.Abierta, orden.Estado);
    }

    [Fact]
    public void Abrir_sin_parada_rompe_ParadaInexistente() =>
        RomperRegla<ParadaInexistente>(() =>
            OrdenDeTrabajo.Abrir(Guid.NewGuid(), Parada, false, "ADV-03", TipoDeOrden.Correctiva, false, Ahora));

    [Fact]
    public void AsignarTecnico_levanta_tecnico_asignado()
    {
        var orden = Abierta();
        orden.ClearDomainEvents();

        orden.AsignarTecnico("Ana", Ahora);

        Assert.Equal("Ana", Unico<TecnicoAsignado>(orden).Tecnico);
    }

    [Fact]
    public void AsignarTecnico_en_orden_cerrada_rompe_OrdenCerradaInmutable() =>
        RomperRegla<OrdenCerradaInmutable>(() => Cerrada().AsignarTecnico("Ana", Ahora));

    [Fact]
    public void RegistrarEjecucionDeTarea_levanta_evento_y_pasa_a_en_ejecucion()
    {
        var orden = Abierta();
        orden.ClearDomainEvents();

        Ejecutar(orden);

        Assert.Equal(3.5m, Unico<EjecucionDeTareaRegistrada>(orden).HorasHombre);
        Assert.Equal(EstadoDeLaOrden.EnEjecucion, orden.Estado);
    }

    [Fact]
    public void RegistrarEjecucionDeTarea_en_orden_cerrada_rompe_OrdenCerradaInmutable() =>
        RomperRegla<OrdenCerradaInmutable>(() => Ejecutar(Cerrada()));

    [Fact]
    public void RegistrarConsumoDeRepuesto_levanta_evento_con_la_serie()
    {
        var orden = Abierta();
        orden.ClearDomainEvents();

        orden.RegistrarConsumoDeRepuesto(Guid.NewGuid(), "MOT-T40", 1, true, "M-1", "M-2", new HoraDeCorte(180), Ahora);

        Assert.Equal("M-2", Unico<ConsumoDeRepuestoRegistrado>(orden).NumeroDeSerie);
    }

    [Fact]
    public void RegistrarConsumoDeRepuesto_sin_serie_rompe_SerieFaltante() =>
        RomperRegla<SerieFaltante>(() =>
            Abierta().RegistrarConsumoDeRepuesto(Guid.NewGuid(), "MOT-T40", 1, true, "M-1", null, null, Ahora));

    [Fact]
    public void RegistrarHallazgo_levanta_hallazgo_registrado()
    {
        var orden = Abierta();
        orden.ClearDomainEvents();

        orden.RegistrarHallazgo("Manguera con rajadura incipiente", Ahora);

        Assert.Equal("Manguera con rajadura incipiente", Unico<HallazgoRegistrado>(orden).Descripcion);
    }

    [Fact]
    public void RegistrarHallazgo_en_orden_cerrada_rompe_OrdenCerradaInmutable() =>
        RomperRegla<OrdenCerradaInmutable>(() => Cerrada().RegistrarHallazgo("Nuevo", Ahora));

    [Fact]
    public void RegistrarVueloDePrueba_levanta_evento_y_pasa_a_ejecutada()
    {
        var orden = Abierta(true);
        Ejecutar(orden);
        orden.ClearDomainEvents();

        orden.RegistrarVueloDePrueba(VueloOk(), Ahora);

        Assert.True(Unico<VueloDePruebaRegistrado>(orden).Aprobado);
        Assert.Equal(EstadoDeLaOrden.Ejecutada, orden.Estado);
    }

    [Fact]
    public void RegistrarVueloDePrueba_en_orden_cerrada_rompe_OrdenCerradaInmutable() =>
        RomperRegla<OrdenCerradaInmutable>(() => Cerrada().RegistrarVueloDePrueba(VueloOk(), Ahora));

    [Fact]
    public void LiberarDron_levanta_dron_liberado()
    {
        var orden = Abierta(true);
        Ejecutar(orden, "Ana");
        orden.RegistrarVueloDePrueba(VueloOk(), Ahora);
        orden.ClearDomainEvents();

        orden.LiberarDron(Guid.NewGuid(), "Pompilio", Ahora);

        Assert.Equal("Pompilio", Unico<DronLiberado>(orden).LiberadaPor);
        Assert.Equal(EstadoDeLaOrden.Liberada, orden.Estado);
    }

    [Fact]
    public void LiberarDron_por_quien_ejecuto_en_trabajo_mayor_rompe_LiberaElMismoQueEjecuto()
    {
        var orden = Abierta(true);
        Ejecutar(orden, "Ana");
        orden.RegistrarVueloDePrueba(VueloOk(), Ahora);

        RomperRegla<LiberaElMismoQueEjecuto>(() => orden.LiberarDron(Guid.NewGuid(), "ana", Ahora));
    }

    [Fact]
    public void LiberarDron_en_trabajo_menor_permite_al_mismo_que_ejecuto()
    {
        var orden = Abierta();
        Ejecutar(orden, "Ana");

        orden.LiberarDron(Guid.NewGuid(), "Ana", Ahora);

        Assert.Equal(EstadoDeLaOrden.Liberada, orden.Estado);
    }

    [Fact]
    public void LiberarDron_en_trabajo_mayor_sin_vuelo_aprobado_se_rechaza()
    {
        var orden = Abierta(true);
        Ejecutar(orden, "Ana");

        Assert.Throws<DomainException>(() => orden.LiberarDron(Guid.NewGuid(), "Pompilio", Ahora));
    }

    [Fact]
    public void Cerrar_levanta_orden_cerrada_con_horas_y_consumos()
    {
        var orden = Liberada();
        orden.ClearDomainEvents();

        orden.Cerrar(Ahora);

        var evento = Unico<OrdenDeTrabajoCerrada>(orden);
        Assert.Equal(3.5m, evento.HorasHombre);
        Assert.Equal("M-2", Assert.Single(evento.Consumos).NumeroDeSerie);
        Assert.True(orden.Estado.EsTerminal);
    }

    [Fact]
    public void Cerrar_dos_veces_rompe_OrdenCerradaInmutable() =>
        RomperRegla<OrdenCerradaInmutable>(() => Cerrada().Cerrar(Ahora));

    [Fact]
    public void Cerrar_sin_liberar_se_rechaza()
    {
        var orden = Abierta();
        Ejecutar(orden);

        Assert.Throws<DomainException>(() => orden.Cerrar(Ahora));
    }

    [Fact]
    public void PonerEnEspera_levanta_evento_y_pasa_a_en_espera()
    {
        var orden = Abierta();
        orden.ClearDomainEvents();

        orden.PonerEnEspera("Falta HEL-T40", Ahora);

        Assert.Equal("Falta HEL-T40", Unico<OrdenDeTrabajoPuestaEnEspera>(orden).Motivo);
        Assert.Equal(EstadoDeLaOrden.EnEspera, orden.Estado);
    }

    [Fact]
    public void PonerEnEspera_en_orden_cerrada_rompe_OrdenCerradaInmutable() =>
        RomperRegla<OrdenCerradaInmutable>(() => Cerrada().PonerEnEspera("Motivo", Ahora));

    [Fact]
    public void Una_orden_en_espera_retoma_la_ejecucion()
    {
        var orden = Abierta();
        orden.PonerEnEspera("Falta repuesto", Ahora);

        Ejecutar(orden);

        Assert.Equal(EstadoDeLaOrden.EnEjecucion, orden.Estado);
        Assert.Null(orden.MotivoDeEspera);
    }

    [Fact]
    public void Memento_ida_y_vuelta_conserva_el_estado()
    {
        var orden = Liberada();
        orden.RegistrarHallazgo("Manguera rajada", Ahora);

        var memento = orden.CrearMemento();
        var restaurada = OrdenDeTrabajo.RestaurarDesde(memento);

        Assert.Equal(memento.Estado, restaurada.CrearMemento().Estado);
        Assert.Equal(memento.Hallazgos, restaurada.CrearMemento().Hallazgos);
        Assert.Equal(memento.Consumos, restaurada.CrearMemento().Consumos);
        Assert.Equal(memento.VueloDePrueba, restaurada.CrearMemento().VueloDePrueba);
        Assert.Equal(orden.Estado, restaurada.Estado);
        Assert.Equal(orden.Tareas.Count, restaurada.Tareas.Count);
        Assert.Equal(orden.Consumos.Single().SerieInstalada, restaurada.Consumos.Single().SerieInstalada);
        Assert.Equal(orden.Liberacion!.LiberadaPor, restaurada.Liberacion!.LiberadaPor);
        Assert.Empty(restaurada.DomainEvents);
    }

    [Fact]
    public void Restaurar_desde_un_memento_invalido_vuelve_a_validar()
    {
        var memento = Abierta().CrearMemento() with { Estado = "Inexistente" };

        Assert.Throws<DomainException>(() => OrdenDeTrabajo.RestaurarDesde(memento));
    }

    private static OrdenDeTrabajo Liberada()
    {
        var orden = Abierta(true);
        Ejecutar(orden, "Ana");
        orden.RegistrarConsumoDeRepuesto(Guid.NewGuid(), "MOT-T40", 1, true, "M-1", "M-2", new HoraDeCorte(180), Ahora);
        orden.RegistrarVueloDePrueba(VueloOk(), Ahora);
        orden.LiberarDron(Guid.NewGuid(), "Pompilio", Ahora);
        return orden;
    }

    private static OrdenDeTrabajo Cerrada()
    {
        var orden = Liberada();
        orden.Cerrar(Ahora);
        return orden;
    }
}
