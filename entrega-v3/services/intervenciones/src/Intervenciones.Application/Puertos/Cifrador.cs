namespace Intervenciones.Application.Puertos;

/// <summary>Cifrado simple de datos personales.</summary>
public interface Cifrador
{
    string Cifrar(string textoPlano);

    string Descifrar(string textoCifrado);
}
