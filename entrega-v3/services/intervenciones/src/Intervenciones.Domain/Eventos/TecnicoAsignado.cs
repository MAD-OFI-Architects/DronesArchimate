using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record TecnicoAsignado(Guid OrdenId, string Tecnico, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
