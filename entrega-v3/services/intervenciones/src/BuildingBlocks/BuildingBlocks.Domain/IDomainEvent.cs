namespace BuildingBlocks.Domain;

public interface IDomainEvent
{
    Guid EventoId { get; }

    DateTimeOffset OcurrioEn { get; }
}
