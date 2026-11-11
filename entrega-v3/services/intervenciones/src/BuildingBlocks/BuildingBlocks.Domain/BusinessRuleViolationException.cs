namespace BuildingBlocks.Domain;

/// <summary>Regla de negocio con nombre propio que se incumplió.</summary>
public sealed class BusinessRuleViolationException(IBusinessRule brokenRule)
    : DomainException(brokenRule.Message)
{
    public IBusinessRule BrokenRule { get; } = brokenRule;
}
