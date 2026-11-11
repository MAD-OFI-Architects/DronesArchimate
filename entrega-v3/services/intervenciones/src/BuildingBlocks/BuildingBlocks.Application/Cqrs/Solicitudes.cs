namespace BuildingBlocks.Application.Cqrs;

public interface ISolicitud<TRespuesta>;

/// <summary>Cambia el estado: el pipeline confirma la transacción al terminar.</summary>
public interface IComando<TRespuesta> : ISolicitud<TRespuesta>;

/// <summary>Solo lee: nunca abre transacción.</summary>
public interface IConsulta<TRespuesta> : ISolicitud<TRespuesta>;

/// <summary>El «void» de las respuestas.</summary>
public readonly record struct Unidad
{
    public static readonly Unidad Valor = new();
}
