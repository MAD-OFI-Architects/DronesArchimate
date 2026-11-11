using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record HallazgoRegistrado(Guid OrdenId, string Descripcion, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
