using System.Collections.Concurrent;
using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Infrastructure.Persistencia;

/// <summary>Caché en memoria de instantáneas (mementos) de órdenes con vencimiento por TTL.</summary>
public sealed class CacheDeOrdenes(IClock reloj, TimeSpan? ttl = null)
{
    public static readonly TimeSpan TtlPorDefecto = TimeSpan.FromSeconds(60);

    private readonly ConcurrentDictionary<Guid, (OrdenDeTrabajoMemento Memento, DateTimeOffset VenceEn)> _entradas = new();
    private readonly TimeSpan _ttl = ttl ?? TtlPorDefecto;

    public bool TryObtener(Guid id, out OrdenDeTrabajoMemento? memento)
    {
        if (_entradas.TryGetValue(id, out var entrada) && entrada.VenceEn > reloj.Now)
        {
            memento = entrada.Memento;
            return true;
        }

        _entradas.TryRemove(id, out _);
        memento = null;
        return false;
    }

    public void Guardar(Guid id, OrdenDeTrabajoMemento memento) => _entradas[id] = (memento, reloj.Now + _ttl);

    public void Invalidar(Guid id) => _entradas.TryRemove(id, out _);

    public void InvalidarTodo() => _entradas.Clear();
}
