using BuildingBlocks.Domain;
using BuildingBlocks.Tests.Soporte;

namespace BuildingBlocks.Tests.Dominio;

public class ReglasDeNegocioTests
{
    [Fact]
    public void Check_no_hace_nada_si_la_regla_se_cumple() =>
        BusinessRules.Check(new DepositoDebeSerPositivo(5));

    [Fact]
    public void Check_lanza_BusinessRuleViolation_con_la_regla_rota()
    {
        var ex = Assert.Throws<BusinessRuleViolationException>(() => BusinessRules.Check(new DepositoDebeSerPositivo(0)));

        Assert.IsType<DepositoDebeSerPositivo>(ex.BrokenRule);
        Assert.Equal("El depósito debe ser positivo.", ex.Message);
    }

    [Fact]
    public void La_violacion_de_regla_es_una_DomainException() =>
        Assert.IsAssignableFrom<DomainException>(new BusinessRuleViolationException(new DepositoDebeSerPositivo(0)));
}
