using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record VueloDePruebaRegistrado(Guid OrdenId, bool Aprobado, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
