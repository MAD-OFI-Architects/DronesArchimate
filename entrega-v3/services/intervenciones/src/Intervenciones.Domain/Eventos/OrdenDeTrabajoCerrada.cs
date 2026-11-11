using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record OrdenDeTrabajoCerrada(Guid OrdenId, Guid ParadaId, string DronId, decimal HorasHombre, IReadOnlyList<ConsumoCerrado> Consumos, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
