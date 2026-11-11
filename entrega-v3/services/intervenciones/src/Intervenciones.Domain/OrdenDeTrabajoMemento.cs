namespace Intervenciones.Domain;

public sealed record OrdenDeTrabajoMemento(
    Guid Id,
    Guid ParadaId,
    string DronId,
    string Tipo,
    bool EsTrabajoMayor,
    string Estado,
    DateTimeOffset AbiertaEn,
    string? Tecnico,
    string? MotivoDeEspera,
    DateTimeOffset? CerradaEn,
    IReadOnlyList<TareaEjecutadaMemento> Tareas,
    IReadOnlyList<ConsumoDeRepuestoMemento> Consumos,
    IReadOnlyList<HallazgoMemento> Hallazgos,
    VueloDePruebaMemento? VueloDePrueba,
    LiberacionMemento? Liberacion);

public sealed record TareaEjecutadaMemento(
    Guid Id, string Descripcion, string Resultado, string EjecutadaPor, decimal Horas, DateTimeOffset EjecutadaEn);

public sealed record ConsumoDeRepuestoMemento(
    Guid Id, string Referencia, int Cantidad, bool RequiereSerie,
    string? SerieRetirada, string? SerieInstalada, decimal? HoraDeCorte);

public sealed record HallazgoMemento(string Descripcion, DateTimeOffset RegistradoEn);

public sealed record VueloDePruebaMemento(DateTimeOffset RealizadoEn, int DuracionEnMinutos, bool Aprobado, string Observaciones);

public sealed record LiberacionMemento(Guid Id, string LiberadaPor, DateTimeOffset FirmadaEn, VueloDePruebaMemento? VueloDePrueba);
