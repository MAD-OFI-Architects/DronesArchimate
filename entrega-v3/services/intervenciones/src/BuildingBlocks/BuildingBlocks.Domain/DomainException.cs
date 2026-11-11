namespace BuildingBlocks.Domain;

/// <summary>Dato inválido para el dominio.</summary>
public class DomainException(string message) : Exception(message);
