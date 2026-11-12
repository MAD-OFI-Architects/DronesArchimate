namespace BuildingBlocks.Application.Excepciones;

/// <summary>Un sistema del que depende la operación (otro servicio, un proveedor externo) no respondió o respondió algo inválido (HTTP 503).
/// Las capas anticorrupción lanzan un subtipo de esta excepción para que el fallo del otro contexto no se vea como un error propio.</summary>
public class DependenciaNoDisponibleException(string dependencia, string mensaje, Exception? interna = null) : Exception(mensaje, interna)
{
    public string Dependencia { get; } = dependencia;
}
