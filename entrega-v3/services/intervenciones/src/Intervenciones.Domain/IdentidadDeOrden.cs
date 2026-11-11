using System.Security.Cryptography;
using System.Text;

namespace Intervenciones.Domain;

/// <summary>La orden de una parada tiene una identidad determinista (UUID v5 sobre la parada): dos aperturas
/// simultáneas de la misma parada producen el mismo id y el almacén rechaza la segunda, en vez de duplicar la orden.</summary>
public static class IdentidadDeOrden
{
    private static readonly Guid Espacio = new("6f1d6a3e-2b0c-5c1e-9a3d-0f6b7c4e5a21");

    public static Guid DeParada(Guid paradaId)
    {
        var entrada = Espacio.ToByteArray().Concat(Encoding.UTF8.GetBytes(paradaId.ToString("D"))).ToArray();
        var hash = SHA1.HashData(entrada);
        var bytes = hash[..16];
        bytes[6] = (byte)((bytes[6] & 0x0F) | 0x50);
        bytes[8] = (byte)((bytes[8] & 0x3F) | 0x80);
        return new Guid(bytes);
    }
}
