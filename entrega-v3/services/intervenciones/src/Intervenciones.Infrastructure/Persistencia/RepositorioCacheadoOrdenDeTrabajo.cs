using Intervenciones.Domain;

namespace Intervenciones.Infrastructure.Persistencia;

/// <summary>Decorador de lectura: la segunda lectura de una orden dentro del TTL no toca el repositorio.
/// Entrega siempre una copia restaurada del memento, nunca una instancia compartida entre peticiones.
/// Pensado para consultas; los comandos usan el repositorio sin caché.</summary>
public sealed class RepositorioCacheadoOrdenDeTrabajo(IOrdenDeTrabajoRepository interno, CacheDeOrdenes cache)
    : IOrdenDeTrabajoRepository
{
    public async Task<OrdenDeTrabajo?> ObtenerAsync(Guid id, CancellationToken cancellationToken = default)
    {
        if (cache.TryObtener(id, out var memento))
            return OrdenDeTrabajo.RestaurarDesde(memento!);

        var orden = await interno.ObtenerAsync(id, cancellationToken);
        if (orden is not null)
            cache.Guardar(id, orden.CrearMemento());

        return orden;
    }

    public Task<OrdenDeTrabajo?> ObtenerPorParadaAsync(Guid paradaId, CancellationToken cancellationToken = default) =>
        interno.ObtenerPorParadaAsync(paradaId, cancellationToken);

    public async Task GuardarAsync(OrdenDeTrabajo orden, CancellationToken cancellationToken = default)
    {
        await interno.GuardarAsync(orden, cancellationToken);
        cache.Invalidar(orden.Id);
    }
}
