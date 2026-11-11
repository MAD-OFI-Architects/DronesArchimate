using System.Security.Cryptography;
using System.Text;
using Intervenciones.Application.Puertos;

namespace Intervenciones.Infrastructure.Cifrado;

/// <summary>AES-GCM con la clave de CIFRADO_CLAVE (base64 de al menos 16 bytes; las de 16, 24 o 32 se usan tal cual y
/// las demás se reducen a 32 bytes con SHA-256). El nonce se deriva del texto con
/// HMAC-SHA256, de modo que el mismo texto produce el mismo cifrado y el documento no cambia si los datos no cambian.</summary>
public sealed class CifradorAes : Cifrador
{
    private const int TamanoDeNonce = 12;
    private const int TamanoDeEtiqueta = 16;
    private const int TamanoMinimoDeClave = 16;

    private readonly byte[] _clave;

    public CifradorAes(string? claveBase64)
    {
        if (string.IsNullOrWhiteSpace(claveBase64))
            throw new InvalidOperationException("Falta la clave de cifrado (CIFRADO_CLAVE).");

        try
        {
            _clave = Convert.FromBase64String(claveBase64);
        }
        catch (FormatException ex)
        {
            throw new InvalidOperationException("CIFRADO_CLAVE no es base64 válido.", ex);
        }

        if (_clave.Length < TamanoMinimoDeClave)
            throw new InvalidOperationException("CIFRADO_CLAVE debe decodificar a al menos 16 bytes.");

        if (_clave.Length is not (16 or 24 or 32))
            _clave = SHA256.HashData(_clave);
    }

    public string Cifrar(string textoPlano)
    {
        ArgumentNullException.ThrowIfNull(textoPlano);

        var plano = Encoding.UTF8.GetBytes(textoPlano);
        var nonce = HMACSHA256.HashData(_clave, plano)[..TamanoDeNonce];
        var cifrado = new byte[plano.Length];
        var etiqueta = new byte[TamanoDeEtiqueta];

        using var aes = new AesGcm(_clave, TamanoDeEtiqueta);
        aes.Encrypt(nonce, plano, cifrado, etiqueta);

        return Convert.ToBase64String([.. nonce, .. etiqueta, .. cifrado]);
    }

    public string Descifrar(string textoCifrado)
    {
        ArgumentNullException.ThrowIfNull(textoCifrado);

        var datos = Convert.FromBase64String(textoCifrado);
        if (datos.Length < TamanoDeNonce + TamanoDeEtiqueta)
            throw new CryptographicException("El texto cifrado es demasiado corto.");

        var nonce = datos[..TamanoDeNonce];
        var etiqueta = datos[TamanoDeNonce..(TamanoDeNonce + TamanoDeEtiqueta)];
        var cifrado = datos[(TamanoDeNonce + TamanoDeEtiqueta)..];
        var plano = new byte[cifrado.Length];

        using var aes = new AesGcm(_clave, TamanoDeEtiqueta);
        aes.Decrypt(nonce, cifrado, etiqueta, plano);

        return Encoding.UTF8.GetString(plano);
    }
}
