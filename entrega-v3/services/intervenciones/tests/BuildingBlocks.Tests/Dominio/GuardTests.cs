using BuildingBlocks.Domain;

namespace BuildingBlocks.Tests.Dominio;

public class GuardTests
{
    private enum Color { Rojo = 1 }

    [Fact]
    public void NoNulo_rechaza_nulo_con_DomainException()
    {
        var ex = Assert.Throws<DomainException>(() => Guard.NoNulo<string>(null, "nombre"));
        Assert.Equal("El campo 'nombre' es obligatorio.", ex.Message);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void Texto_rechaza_vacios(string? valor) =>
        Assert.Throws<DomainException>(() => Guard.Texto(valor, "motivo"));

    [Fact]
    public void Texto_recorta_y_valida_longitud()
    {
        Assert.Equal("hola", Guard.Texto("  hola ", "motivo", 10));
        Assert.Throws<DomainException>(() => Guard.Texto(new string('a', 11), "motivo", 10));
    }

    [Fact]
    public void NoVacio_y_NoPorDefecto_rechazan_valores_por_defecto()
    {
        Assert.Throws<DomainException>(() => Guard.NoVacio(Guid.Empty, "id"));
        Assert.Throws<DomainException>(() => Guard.NoPorDefecto(default(DateTimeOffset), "fecha"));
        var id = Guid.NewGuid();
        Assert.Equal(id, Guard.NoVacio(id, "id"));
    }

    [Theory]
    [InlineData(0, false)]
    [InlineData(1, true)]
    [InlineData(5, true)]
    [InlineData(6, false)]
    public void EnRango_valida_limites_inclusivos(int valor, bool valido)
    {
        if (valido)
            Assert.Equal(valor, Guard.EnRango(valor, 1, 5, "cantidad"));
        else
            Assert.Throws<DomainException>(() => Guard.EnRango(valor, 1, 5, "cantidad"));
    }

    [Fact]
    public void Positivo_y_NoNegativo()
    {
        Assert.Throws<DomainException>(() => Guard.Positivo(0, "horas"));
        Assert.Throws<DomainException>(() => Guard.Positivo(0m, "horas"));
        Assert.Throws<DomainException>(() => Guard.NoNegativo(-0.1m, "saldo"));
        Assert.Equal(0m, Guard.NoNegativo(0m, "saldo"));
    }

    [Fact]
    public void Definido_rechaza_enums_fuera_de_rango() =>
        Assert.Throws<DomainException>(() => Guard.Definido((Color)99, "color"));

    [Fact]
    public void Getters_lanzan_InvalidOperationException_si_no_se_asigno()
    {
        Assert.Throws<InvalidOperationException>(() => Guard.Inicializado<string>(null, "titular"));
        Assert.Throws<InvalidOperationException>(() => Guard.Asignado(Guid.Empty, "id"));
        Assert.Equal("x", Guard.Inicializado("x", "titular"));
    }
}
