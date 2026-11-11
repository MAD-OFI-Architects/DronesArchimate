namespace BuildingBlocks.Domain;

public static class BusinessRules
{
    public static void Check(IBusinessRule rule)
    {
        ArgumentNullException.ThrowIfNull(rule);
        if (rule.IsBroken())
            throw new BusinessRuleViolationException(rule);
    }
}
