using BuildingBlocks.Domain;
using BuildingBlocks.Tests.Soporte;

namespace BuildingBlocks.Tests.Dominio;

public class AggregateRootTests
{
    private static readonly DateTimeOffset Ahora = Escenario.Inicio;

    [Fact]
    public void El_agregado_levanta_sus_eventos_con_EventoId_unico()
    {
        var cuenta = Cuenta.Abrir(Guid.NewGuid(), "Ana", Ahora);
        cuenta.Depositar(10, Ahora);

        Assert.Collection(cuenta.DomainEvents,
            e => Assert.IsType<CuentaAbierta>(e),
            e => Assert.IsType<DepositoRealizado>(e));
        Assert.Equal(2, cuenta.DomainEvents.Select(e => e.EventoId).Distinct().Count());
        Assert.All(cuenta.DomainEvents, e => Assert.Equal(Ahora, e.OcurrioEn));
    }

    [Fact]
    public void ClearDomainEvents_vacia_la_coleccion()
    {
        var cuenta = Cuenta.Abrir(Guid.NewGuid(), "Ana", Ahora);
        cuenta.ClearDomainEvents();
        Assert.Empty(cuenta.DomainEvents);
    }

    [Fact]
    public void Un_evento_rechazado_por_regla_no_queda_levantado()
    {
        var cuenta = Cuenta.Abrir(Guid.NewGuid(), "Ana", Ahora);
        cuenta.ClearDomainEvents();

        Assert.Throws<BusinessRuleViolationException>(() => cuenta.Depositar(0, Ahora));
        Assert.Empty(cuenta.DomainEvents);
        Assert.Equal(0, cuenta.Saldo);
    }

    [Fact]
    public void Las_entidades_se_igualan_por_tipo_e_Id()
    {
        var id = Guid.NewGuid();
        Assert.Equal(Cuenta.Abrir(id, "Ana", Ahora), Cuenta.Abrir(id, "Otra", Ahora));
        Assert.NotEqual(Cuenta.Abrir(id, "Ana", Ahora), Cuenta.Abrir(Guid.NewGuid(), "Ana", Ahora));
    }

    [Fact]
    public void El_Id_vacio_se_rechaza() =>
        Assert.Throws<DomainException>(() => Cuenta.Abrir(Guid.Empty, "Ana", Ahora));

    [Fact]
    public void El_memento_restaura_el_agregado_validando()
    {
        var cuenta = Cuenta.Abrir(Guid.NewGuid(), "Ana", Ahora);
        cuenta.Depositar(25, Ahora);

        var restaurada = Cuenta.RestaurarDesde(cuenta.CrearMemento());

        Assert.Equal(cuenta.CrearMemento(), restaurada.CrearMemento());
        Assert.Empty(restaurada.DomainEvents);
        Assert.Throws<DomainException>(() => Cuenta.RestaurarDesde(new CuentaMemento(Guid.NewGuid(), "Ana", -1)));
    }
}
