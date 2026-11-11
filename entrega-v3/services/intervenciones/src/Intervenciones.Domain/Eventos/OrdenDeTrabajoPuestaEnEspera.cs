using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record OrdenDeTrabajoPuestaEnEspera(Guid OrdenId, string Motivo, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
