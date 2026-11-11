using BuildingBlocks.Domain;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Application.EventosDeDominio;

public interface IManejadorDeEventoDeDominio
{
    Type TipoDeEvento { get; }

    Task ManejarAsync(IDomainEvent evento, CancellationToken cancellationToken);
}

/// <summary>Observador de un evento de dominio dentro del mismo servicio, ejecutado tras confirmar.</summary>
public abstract class ManejadorDeEventoDeDominio<TEvento> : IManejadorDeEventoDeDominio where TEvento : IDomainEvent
{
    public Type TipoDeEvento => typeof(TEvento);

    public Task ManejarAsync(IDomainEvent evento, CancellationToken cancellationToken) =>
        evento is TEvento tipado ? AlOcurrirAsync(tipado, cancellationToken) : Task.CompletedTask;

    protected abstract Task AlOcurrirAsync(TEvento evento, CancellationToken cancellationToken);
}

public interface IDespachadorDeEventosDeDominio
{
    Task DespacharAsync(IEnumerable<IDomainEvent> eventos, CancellationToken cancellationToken = default);
}

public sealed class DespachadorDeEventosDeDominio(
    IEnumerable<IManejadorDeEventoDeDominio> manejadores,
    ILogger<DespachadorDeEventosDeDominio> logger) : IDespachadorDeEventosDeDominio
{
    public async Task DespacharAsync(IEnumerable<IDomainEvent> eventos, CancellationToken cancellationToken = default)
    {
        foreach (var evento in eventos)
        foreach (var manejador in manejadores.Where(m => m.TipoDeEvento.IsInstanceOfType(evento)))
        {
            try
            {
                await manejador.ManejarAsync(evento, cancellationToken);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                logger.LogError(ex, "El observador {Observador} falló con {Evento}; el cambio ya estaba confirmado",
                    manejador.GetType().Name, evento.GetType().Name);
            }
        }
    }
}
