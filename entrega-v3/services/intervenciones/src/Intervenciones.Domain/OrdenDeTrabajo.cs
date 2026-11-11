using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class OrdenDeTrabajo : AggregateRoot<Guid>, IOriginador<OrdenDeTrabajo, OrdenDeTrabajoMemento>
{
    private readonly List<TareaEjecutada> _tareas = [];
    private readonly List<ConsumoDeRepuesto> _consumos = [];
    private readonly List<Hallazgo> _hallazgos = [];

    private OrdenDeTrabajo(
        Guid id, Guid paradaId, string dronId, TipoDeOrden tipo, bool esTrabajoMayor,
        EstadoDeLaOrden estado, DateTimeOffset abiertaEn)
        : base(Guard.NoVacio(id, nameof(id)))
    {
        ParadaId = Guard.NoVacio(paradaId, nameof(paradaId));
        DronId = Guard.Texto(dronId, nameof(dronId), 50);
        Tipo = Guard.Definido(tipo, nameof(tipo));
        EsTrabajoMayor = esTrabajoMayor;
        Estado = Guard.NoNulo(estado, nameof(estado));
        AbiertaEn = Guard.NoPorDefecto(abiertaEn, nameof(abiertaEn));
    }

    public Guid ParadaId { get; }

    public string DronId { get; }

    public TipoDeOrden Tipo { get; }

    public bool EsTrabajoMayor { get; }

    public EstadoDeLaOrden Estado { get; private set; }

    public DateTimeOffset AbiertaEn { get; }

    public string? Tecnico { get; private set; }

    public string? MotivoDeEspera { get; private set; }

    public DateTimeOffset? CerradaEn { get; private set; }

    public VueloDePrueba? VueloDePrueba { get; private set; }

    public Liberacion? Liberacion { get; private set; }

    public IReadOnlyList<TareaEjecutada> Tareas => _tareas;

    public IReadOnlyList<ConsumoDeRepuesto> Consumos => _consumos;

    public IReadOnlyList<Hallazgo> Hallazgos => _hallazgos;

    public HorasHombre? HorasHombreTotales =>
        _tareas.Count == 0 ? null : _tareas.Select(t => t.Horas).Aggregate((a, b) => a.Sumar(b));

    public static OrdenDeTrabajo Abrir(
        Guid id, Guid paradaId, bool paradaExiste, string dronId, TipoDeOrden tipo, bool esTrabajoMayor, DateTimeOffset ahora)
    {
        BusinessRules.Check(new ParadaInexistente(paradaExiste));
        var orden = new OrdenDeTrabajo(id, paradaId, dronId, tipo, esTrabajoMayor, EstadoDeLaOrden.Abierta, ahora);
        orden.Raise(new OrdenDeTrabajoAbierta(id, paradaId, orden.DronId, tipo, esTrabajoMayor, ahora));
        return orden;
    }

    public void AsignarTecnico(string tecnico, DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlAsignarTecnico());
        Tecnico = Guard.Texto(tecnico, nameof(tecnico), 100);
        Estado = siguiente;
        Raise(new TecnicoAsignado(Id, Tecnico, ahora));
    }

    public void RegistrarEjecucionDeTarea(
        Guid tareaId, string descripcion, string resultado, string ejecutadaPor, HorasHombre horas, DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlRegistrarTarea());
        var tarea = new TareaEjecutada(tareaId, descripcion, resultado, ejecutadaPor, horas, ahora);
        _tareas.Add(tarea);
        MotivoDeEspera = null;
        Estado = siguiente;
        Raise(new EjecucionDeTareaRegistrada(Id, tarea.Id, tarea.EjecutadaPor, horas.Valor, ahora));
    }

    public void RegistrarConsumoDeRepuesto(
        Guid consumoId, string referencia, int cantidad, bool requiereSerie,
        string? serieRetirada, string? serieInstalada, HoraDeCorte? horaDeCorte, DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlRegistrarConsumo());
        var consumo = new ConsumoDeRepuesto(consumoId, referencia, cantidad, requiereSerie, serieRetirada, serieInstalada, horaDeCorte);
        CheckRule(new SerieFaltante(consumo));
        _consumos.Add(consumo);
        MotivoDeEspera = null;
        Estado = siguiente;
        Raise(new ConsumoDeRepuestoRegistrado(Id, consumo.Id, consumo.Referencia, consumo.Cantidad, consumo.SerieInstalada, ahora));
    }

    public void RegistrarHallazgo(string descripcion, DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlRegistrarHallazgo());
        var hallazgo = new Hallazgo(descripcion, ahora);
        _hallazgos.Add(hallazgo);
        Estado = siguiente;
        Raise(new HallazgoRegistrado(Id, hallazgo.Descripcion, ahora));
    }

    public void RegistrarVueloDePrueba(VueloDePrueba vuelo, DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlRegistrarVueloDePrueba());
        VueloDePrueba = Guard.NoNulo(vuelo, nameof(vuelo));
        Estado = siguiente;
        Raise(new VueloDePruebaRegistrado(Id, vuelo.Aprobado, ahora));
    }

    public void LiberarDron(Guid liberacionId, string liberadaPor, DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlLiberar());
        CheckRule(new LiberaElMismoQueEjecuto(EsTrabajoMayor, Guard.Texto(liberadaPor, nameof(liberadaPor), 100), _tareas));
        if (EsTrabajoMayor && VueloDePrueba is not { Aprobado: true })
            throw new DomainException("En trabajos mayores la liberación exige un vuelo de prueba aprobado.");

        Liberacion = new Liberacion(liberacionId, liberadaPor, ahora, VueloDePrueba);
        Estado = siguiente;
        Raise(new DronLiberado(Id, DronId, Liberacion.LiberadaPor, ahora));
    }

    public void Cerrar(DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlCerrar());
        foreach (var consumo in _consumos)
            CheckRule(new SerieFaltante(consumo));

        CerradaEn = Guard.NoPorDefecto(ahora, nameof(ahora));
        Estado = siguiente;
        var consumos = _consumos
            .Select(c => new ConsumoCerrado(c.Referencia, c.Cantidad, c.SerieInstalada, c.HoraDeCorte?.Horas))
            .ToList();
        Raise(new OrdenDeTrabajoCerrada(Id, ParadaId, DronId, HorasHombreTotales?.Valor ?? 0m, consumos, ahora));
    }

    public void PonerEnEspera(string motivo, DateTimeOffset ahora)
    {
        var siguiente = Transicionar(e => e.AlPonerEnEspera());
        MotivoDeEspera = Guard.Texto(motivo, nameof(motivo), 250);
        Estado = siguiente;
        Raise(new OrdenDeTrabajoPuestaEnEspera(Id, MotivoDeEspera, ahora));
    }

    public OrdenDeTrabajoMemento CrearMemento() => new(
        Id, ParadaId, DronId, Tipo.ToString(), EsTrabajoMayor, Estado.Nombre, AbiertaEn, Tecnico, MotivoDeEspera, CerradaEn,
        _tareas.Select(t => new TareaEjecutadaMemento(t.Id, t.Descripcion, t.Resultado, t.EjecutadaPor, t.Horas.Valor, t.EjecutadaEn)).ToList(),
        _consumos.Select(c => new ConsumoDeRepuestoMemento(
            c.Id, c.Referencia, c.Cantidad, c.RequiereSerie, c.SerieRetirada, c.SerieInstalada, c.HoraDeCorte?.Horas)).ToList(),
        _hallazgos.Select(h => new HallazgoMemento(h.Descripcion, h.RegistradoEn)).ToList(),
        VueloDePrueba is null ? null : AMemento(VueloDePrueba),
        Liberacion is null ? null : new LiberacionMemento(
            Liberacion.Id, Liberacion.LiberadaPor, Liberacion.FirmadaEn,
            Liberacion.VueloDePrueba is null ? null : AMemento(Liberacion.VueloDePrueba)));

    public static OrdenDeTrabajo RestaurarDesde(OrdenDeTrabajoMemento memento)
    {
        Guard.NoNulo(memento, nameof(memento));
        if (!Enum.TryParse<TipoDeOrden>(memento.Tipo, out var tipo))
            throw new DomainException($"El tipo de orden '{memento.Tipo}' no es válido.");

        var orden = new OrdenDeTrabajo(
            memento.Id, memento.ParadaId, memento.DronId, tipo, memento.EsTrabajoMayor,
            EstadoDeLaOrden.Desde(memento.Estado), memento.AbiertaEn)
        {
            Tecnico = memento.Tecnico is null ? null : Guard.Texto(memento.Tecnico, nameof(memento.Tecnico), 100),
            MotivoDeEspera = memento.MotivoDeEspera is null ? null : Guard.Texto(memento.MotivoDeEspera, nameof(memento.MotivoDeEspera), 250),
            CerradaEn = memento.CerradaEn,
            VueloDePrueba = memento.VueloDePrueba is null ? null : DesdeMemento(memento.VueloDePrueba),
            Liberacion = memento.Liberacion is null ? null : new Liberacion(
                memento.Liberacion.Id, memento.Liberacion.LiberadaPor, memento.Liberacion.FirmadaEn,
                memento.Liberacion.VueloDePrueba is null ? null : DesdeMemento(memento.Liberacion.VueloDePrueba))
        };

        orden._tareas.AddRange(memento.Tareas.Select(t =>
            new TareaEjecutada(t.Id, t.Descripcion, t.Resultado, t.EjecutadaPor, new HorasHombre(t.Horas), t.EjecutadaEn)));
        orden._consumos.AddRange(memento.Consumos.Select(c => new ConsumoDeRepuesto(
            c.Id, c.Referencia, c.Cantidad, c.RequiereSerie, c.SerieRetirada, c.SerieInstalada,
            c.HoraDeCorte is null ? null : new HoraDeCorte(c.HoraDeCorte.Value))));
        orden._hallazgos.AddRange(memento.Hallazgos.Select(h => new Hallazgo(h.Descripcion, h.RegistradoEn)));
        return orden;
    }

    private EstadoDeLaOrden Transicionar(Func<EstadoDeLaOrden, EstadoDeLaOrden> transicion)
    {
        CheckRule(new OrdenCerradaInmutable(Estado));
        return transicion(Estado);
    }

    private static VueloDePruebaMemento AMemento(VueloDePrueba v) =>
        new(v.RealizadoEn, v.DuracionEnMinutos, v.Aprobado, v.Observaciones);

    private static VueloDePrueba DesdeMemento(VueloDePruebaMemento v) =>
        new(v.RealizadoEn, v.DuracionEnMinutos, v.Aprobado, v.Observaciones);
}
