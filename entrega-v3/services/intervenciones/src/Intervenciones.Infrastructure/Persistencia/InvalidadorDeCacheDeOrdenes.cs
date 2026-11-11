using BuildingBlocks.Application.EventosDeDominio;
using BuildingBlocks.Domain;

namespace Intervenciones.Infrastructure.Persistencia;

/// <summary>Tras confirmar cualquier cambio de una orden (ya con la transacción guardada) vacía la caché de lectura.</summary>
public sealed class InvalidadorDeCacheDeOrdenes(CacheDeOrdenes cache) : IManejadorDeEventoDeDominio
{
    public Type TipoDeEvento => typeof(IDomainEvent);

    public Task ManejarAsync(IDomainEvent evento, CancellationToken cancellationToken)
    {
        cache.InvalidarTodo();
        return Task.CompletedTask;
    }
}
