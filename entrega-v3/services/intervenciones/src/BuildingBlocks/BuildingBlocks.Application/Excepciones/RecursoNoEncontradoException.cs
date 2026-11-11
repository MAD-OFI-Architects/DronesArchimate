namespace BuildingBlocks.Application.Excepciones;

/// <summary>Recurso inexistente (HTTP 404).</summary>
public sealed class RecursoNoEncontradoException(string recurso, object clave)
    : Exception($"No existe {recurso} '{clave}'.");
