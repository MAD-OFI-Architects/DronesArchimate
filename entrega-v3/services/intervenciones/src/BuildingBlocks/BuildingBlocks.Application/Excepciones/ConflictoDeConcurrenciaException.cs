namespace BuildingBlocks.Application.Excepciones;

/// <summary>Dos operaciones modificaron lo mismo a la vez (HTTP 409).</summary>
public sealed class ConflictoDeConcurrenciaException(string mensaje) : Exception(mensaje);
