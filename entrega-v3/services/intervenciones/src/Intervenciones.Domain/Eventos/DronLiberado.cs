using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record DronLiberado(Guid OrdenId, string DronId, string LiberadaPor, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
