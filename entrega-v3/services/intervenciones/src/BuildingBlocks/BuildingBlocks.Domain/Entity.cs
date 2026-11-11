namespace BuildingBlocks.Domain;

/// <summary>Objeto que se distingue por su identidad y no por sus datos.</summary>
public abstract class Entity<TId> : IEquatable<Entity<TId>> where TId : notnull
{
    private TId? _id;
    private bool _tieneId;

    protected Entity(TId id) => Id = id;

    public TId Id
    {
        get => _tieneId
            ? _id!
            : throw new InvalidOperationException("La entidad no tiene un identificador asignado.");
        protected set
        {
            if (EqualityComparer<TId>.Default.Equals(value, default!))
                throw new DomainException("El identificador de la entidad no puede estar vacío.");

            _id = value;
            _tieneId = true;
        }
    }

    protected static void CheckRule(IBusinessRule rule) => BusinessRules.Check(rule);

    public bool Equals(Entity<TId>? other) =>
        other is not null
        && GetType() == other.GetType()
        && EqualityComparer<TId>.Default.Equals(Id, other.Id);

    public override bool Equals(object? obj) => Equals(obj as Entity<TId>);

    public override int GetHashCode() => HashCode.Combine(GetType(), Id);
}
