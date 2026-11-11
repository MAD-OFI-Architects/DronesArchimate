using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record ConsumoDeRepuestoRegistrado(Guid OrdenId, Guid ConsumoId, string Referencia, int Cantidad, string? NumeroDeSerie, DateTimeOffset OcurrioEn) : DomainEvent(OcurrioEn);
