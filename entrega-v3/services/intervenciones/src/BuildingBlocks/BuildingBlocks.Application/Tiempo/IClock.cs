namespace BuildingBlocks.Application.Tiempo;

public interface IClock
{
    DateTimeOffset Now { get; }
}
