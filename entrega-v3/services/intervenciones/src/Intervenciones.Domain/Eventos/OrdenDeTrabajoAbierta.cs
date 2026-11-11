using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record OrdenDeTrabajoAbierta(Guid OrdenId, Guid ParadaId, string DronId, TipoDeOrden Tipo, bool EsTrabajoMayor, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
