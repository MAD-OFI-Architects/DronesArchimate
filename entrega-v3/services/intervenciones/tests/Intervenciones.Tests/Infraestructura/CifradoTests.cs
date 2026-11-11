using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text.Json;
using Intervenciones.Infrastructure.Cifrado;
using Intervenciones.Infrastructure.Persistencia;
using Intervenciones.Tests.Soporte;

namespace Intervenciones.Tests.Infraestructura;

public class CifradoTests
{
    private static CifradorAes Cifrador => new(ServidorDeIntervenciones.ClaveBase64);

    [Theory]
    [InlineData("Ana")]
    [InlineData("José Núñez — líder")]
    [InlineData("")]
    public void Cifrar_y_descifrar_devuelve_el_texto_original(string texto)
    {
        var cifrado = Cifrador.Cifrar(texto);

        Assert.NotEqual(texto, cifrado);
        Assert.Equal(texto, Cifrador.Descifrar(cifrado));
    }

    [Fact]
    public void El_mismo_texto_da_el_mismo_cifrado_y_textos_distintos_dan_cifrados_distintos()
    {
        Assert.Equal(Cifrador.Cifrar("Ana"), Cifrador.Cifrar("Ana"));
        Assert.NotEqual(Cifrador.Cifrar("Ana"), Cifrador.Cifrar("Beto"));
    }

    [Fact]
    public void Un_texto_alterado_no_se_descifra()
    {
        var bytes = Convert.FromBase64String(Cifrador.Cifrar("Ana"));
        bytes[^1] ^= 0xFF;

        Assert.ThrowsAny<CryptographicException>(() => Cifrador.Descifrar(Convert.ToBase64String(bytes)));
    }

    [Fact]
    public void Otra_clave_no_descifra()
    {
        var otra = new CifradorAes(Convert.ToBase64String(new byte[32]));

        Assert.ThrowsAny<CryptographicException>(() => otra.Descifrar(Cifrador.Cifrar("Ana")));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("no-es-base64")]
    [InlineData("AAAA")]
    public void Una_clave_ausente_o_invalida_se_rechaza(string? clave) =>
        Assert.Throws<InvalidOperationException>(() => new CifradorAes(clave));

    [Fact]
    public void Una_clave_de_longitud_no_estandar_pero_suficiente_se_deriva_a_32_bytes()
    {
        var clave = Convert.ToBase64String(Enumerable.Range(1, 35).Select(i => (byte)i).ToArray());
        var cifrador = new CifradorAes(clave);

        Assert.Equal("Ana", cifrador.Descifrar(cifrador.Cifrar("Ana")));
    }

    [Fact]
    public async Task Los_datos_de_personas_se_guardan_cifrados_y_se_leen_descifrados()
    {
        await using var servidor = await ServidorDeIntervenciones.IniciarAsync();
        var abrir = await servidor.Cliente.PostAsJsonAsync("/api/orden-de-trabajo", new
        {
            paradaId = EscenarioDeIntervenciones.Parada, paradaProgramada = true, dronId = "ADV-03", tipo = "Preventiva", esTrabajoMayor = false
        });
        var id = (await abrir.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetGuid();
        await servidor.Cliente.PostAsJsonAsync($"/api/orden-de-trabajo/{id}/asignar-tecnico", new { tecnico = "Ana Pérez" });
        await servidor.Cliente.PostAsJsonAsync($"/api/orden-de-trabajo/{id}/registrar-ejecucion-de-tarea",
            new { tareaId = Guid.NewGuid(), descripcion = "Cambio", resultado = "Realizada", ejecutadaPor = "Ana Pérez", horas = 2 });
        await servidor.Cliente.PostAsJsonAsync($"/api/orden-de-trabajo/{id}/liberar-dron",
            new { liberacionId = Guid.NewGuid(), liberadaPor = "Beto Gómez" });

        var documento = await servidor.Almacen.ObtenerAsync(RepositorioOrdenDeTrabajo.NombreDeColeccion, id.ToString());
        var orden = await servidor.Cliente.GetFromJsonAsync<JsonElement>($"/api/orden-de-trabajo/{id}");

        Assert.DoesNotContain("Ana", documento!.Json);
        Assert.DoesNotContain("Beto", documento.Json);
        Assert.Equal("Ana Pérez", orden.GetProperty("tecnico").GetString());
        Assert.Equal("Beto Gómez", orden.GetProperty("liberacion").GetProperty("liberadaPor").GetString());
    }
}
