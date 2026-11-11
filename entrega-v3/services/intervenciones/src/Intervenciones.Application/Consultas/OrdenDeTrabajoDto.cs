namespace Intervenciones.Application.Consultas;

public sealed record OrdenDeTrabajoDto(
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
    decimal HorasHombre,
    IReadOnlyList<TareaEjecutadaDto> Tareas,
    IReadOnlyList<ConsumoDeRepuestoDto> Consumos,
    IReadOnlyList<HallazgoDto> Hallazgos,
    VueloDePruebaDto? VueloDePrueba,
    LiberacionDto? Liberacion);

public sealed record TareaEjecutadaDto(Guid Id, string Descripcion, string Resultado, string EjecutadaPor, decimal Horas, DateTimeOffset EjecutadaEn);

public sealed record ConsumoDeRepuestoDto(
    Guid Id, string Referencia, int Cantidad, bool RequiereSerie, string? SerieRetirada, string? SerieInstalada, decimal? HoraDeCorte);

public sealed record HallazgoDto(string Descripcion, DateTimeOffset RegistradoEn);

public sealed record VueloDePruebaDto(DateTimeOffset RealizadoEn, int DuracionEnMinutos, bool Aprobado, string Observaciones);

public sealed record LiberacionDto(Guid Id, string LiberadaPor, DateTimeOffset FirmadaEn);
