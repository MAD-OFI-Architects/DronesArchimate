using BuildingBlocks.Domain;

namespace BuildingBlocks.Tests.Dominio;

public class EspecificacionTests
{
    private sealed class Par : Especificacion<int>
    {
        public override bool EsSatisfechaPor(int candidato) => candidato % 2 == 0;
    }

    private sealed class Mayor(int limite) : Especificacion<int>
    {
        public override bool EsSatisfechaPor(int candidato) => candidato > limite;
    }

    [Theory]
    [InlineData(12, true)]
    [InlineData(4, false)]
    [InlineData(13, false)]
    public void Y_exige_ambas(int valor, bool esperado) =>
        Assert.Equal(esperado, new Par().Y(new Mayor(10)).EsSatisfechaPor(valor));

    [Theory]
    [InlineData(4, true)]
    [InlineData(13, true)]
    [InlineData(7, false)]
    public void O_exige_alguna(int valor, bool esperado) =>
        Assert.Equal(esperado, new Par().O(new Mayor(10)).EsSatisfechaPor(valor));

    [Fact]
    public void No_invierte_el_resultado()
    {
        Assert.True(new Par().No().EsSatisfechaPor(3));
        Assert.False(new Par().No().EsSatisfechaPor(4));
    }

    [Fact]
    public void Se_pueden_componer_en_cadena() =>
        Assert.True(new Par().Y(new Mayor(10).No()).EsSatisfechaPor(8));
}
