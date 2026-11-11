using System.Xml.Linq;

namespace Intervenciones.Tests;

public class ReglaDeDependenciasTests
{
    private static readonly string Raiz = LocalizarRaiz();

    private static string LocalizarRaiz()
    {
        var directorio = new DirectoryInfo(AppContext.BaseDirectory);
        while (directorio is not null && !File.Exists(Path.Combine(directorio.FullName, "Intervenciones.sln")))
            directorio = directorio.Parent;

        return directorio?.FullName ?? throw new InvalidOperationException("No se encontró Intervenciones.sln.");
    }

    private static IReadOnlySet<string> Referencias(string proyecto)
    {
        var ruta = Directory.GetFiles(Path.Combine(Raiz, "src"), proyecto + ".csproj", SearchOption.AllDirectories).Single();
        return XDocument.Load(ruta).Descendants("ProjectReference")
            .Select(r => Path.GetFileNameWithoutExtension(((string)r.Attribute("Include")!).Replace('\\', '/')))
            .ToHashSet();
    }

    [Theory]
    [InlineData("Intervenciones.Domain", new[] { "BuildingBlocks.Domain" })]
    [InlineData("Intervenciones.Contracts", new string[0])]
    [InlineData("Intervenciones.Application", new[] { "BuildingBlocks.Application", "Intervenciones.Domain", "Intervenciones.Contracts" })]
    [InlineData("Intervenciones.Infrastructure", new[] { "BuildingBlocks.Infrastructure", "Intervenciones.Application", "Intervenciones.Domain", "Intervenciones.Contracts" })]
    [InlineData("BuildingBlocks.Domain", new string[0])]
    [InlineData("BuildingBlocks.Application", new[] { "BuildingBlocks.Domain" })]
    [InlineData("BuildingBlocks.Infrastructure", new[] { "BuildingBlocks.Application", "BuildingBlocks.Domain" })]
    public void Cada_proyecto_referencia_solo_las_capas_permitidas(string proyecto, string[] permitidas) =>
        Assert.Subset(permitidas.ToHashSet(), Referencias(proyecto).ToHashSet());

    [Fact]
    public void Api_conoce_todas_las_capas_del_servicio()
    {
        var referencias = Referencias("Intervenciones.Api");

        foreach (var capa in new[] { "Domain", "Application", "Contracts", "Infrastructure" })
            Assert.Contains($"Intervenciones.{capa}", referencias);
    }

    [Fact]
    public void Domain_no_referencia_paquetes()
    {
        var ruta = Directory.GetFiles(Path.Combine(Raiz, "src"), "Intervenciones.Domain.csproj", SearchOption.AllDirectories).Single();

        Assert.Empty(XDocument.Load(ruta).Descendants("PackageReference"));
    }
}
