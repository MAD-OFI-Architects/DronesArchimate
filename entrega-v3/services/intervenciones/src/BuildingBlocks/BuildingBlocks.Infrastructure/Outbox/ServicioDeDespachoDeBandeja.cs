using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Infrastructure.Outbox;

/// <summary>Servicio en segundo plano que vacía la bandeja de salida cada cierto intervalo.</summary>
public sealed class ServicioDeDespachoDeBandeja(
    IServiceScopeFactory scopes,
    ILogger<ServicioDeDespachoDeBandeja> logger) : BackgroundService
{
    private static readonly TimeSpan Intervalo = TimeSpan.FromMilliseconds(100);

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var temporizador = new PeriodicTimer(Intervalo);
        while (await temporizador.WaitForNextTickAsync(stoppingToken))
        {
            try
            {
                await using var scope = scopes.CreateAsyncScope();
                await scope.ServiceProvider.GetRequiredService<DespachadorDeBandejaDeSalida>()
                    .DespacharPendientesAsync(stoppingToken);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                logger.LogError(ex, "Falló el despacho de la bandeja de salida");
            }
        }
    }
}
