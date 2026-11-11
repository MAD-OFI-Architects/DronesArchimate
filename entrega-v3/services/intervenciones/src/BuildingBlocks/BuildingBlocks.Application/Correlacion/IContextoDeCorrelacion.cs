namespace BuildingBlocks.Application.Correlacion;

/// <summary>Identificador que sigue una operación entre servicios.</summary>
public interface IContextoDeCorrelacion
{
    Guid Id { get; set; }
}

public sealed class ContextoDeCorrelacion : IContextoDeCorrelacion
{
    public Guid Id { get; set; } = Guid.NewGuid();
}
