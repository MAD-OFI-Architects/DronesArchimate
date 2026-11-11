using BuildingBlocks.Application.Tiempo;

namespace BuildingBlocks.Infrastructure.Tiempo;

public sealed class RelojDelSistema : IClock
{
    public DateTimeOffset Now => DateTimeOffset.UtcNow;
}

/// <summary>Reloj controlable para probar vencimientos y reintentos sin esperar.</summary>
public sealed class RelojSimulado(DateTimeOffset inicio) : IClock
{
    public DateTimeOffset Now { get; private set; } = inicio;

    public void Avanzar(TimeSpan intervalo) => Now += intervalo;
}
