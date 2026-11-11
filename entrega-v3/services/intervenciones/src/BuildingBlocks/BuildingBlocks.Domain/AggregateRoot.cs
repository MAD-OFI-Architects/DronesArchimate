namespace BuildingBlocks.Domain;

/// <summary>Entidad principal de un agregado: única puerta de cambio y origen de sus eventos de dominio.</summary>
public abstract class AggregateRoot<TId>(TId id) : Entity<TId>(id), IAggregateRoot where TId : notnull
{
    private readonly List<IDomainEvent> _domainEvents = [];

    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected void Raise(IDomainEvent domainEvent)
    {
        ArgumentNullException.ThrowIfNull(domainEvent);
        _domainEvents.Add(domainEvent);
    }

    public void ClearDomainEvents() => _domainEvents.Clear();
}
