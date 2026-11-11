using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record EjecucionDeTareaRegistrada(Guid OrdenId, Guid TareaId, string EjecutadaPor, decimal HorasHombre, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
