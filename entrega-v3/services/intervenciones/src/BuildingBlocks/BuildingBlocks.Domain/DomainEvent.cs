namespace BuildingBlocks.Domain;

/// <summary>Registro inmutable de algo que ya ocurrió; su EventoId viaja hasta el mensaje de integración.</summary>
public abstract record DomainEvent(DateTimeOffset OcurrioEn) : IDomainEvent
{
    public Guid EventoId { get; init; } = Guid.NewGuid();
}
