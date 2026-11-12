using System.Text.Json;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Tiempo;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Infrastructure.Outbox;

public sealed class OpcionesDeDespacho
{
    public int TamanoDeLote { get; init; } = 50;
    public int MaximoDeIntentos { get; init; } = 10;
    public TimeSpan EsperaBase { get; init; } = TimeSpan.FromMilliseconds(200);
    public TimeSpan EsperaMaxima { get; init; } = TimeSpan.FromSeconds(30);
}

/// <summary>Publica los mensajes pendientes; si el bus falla, reintenta con espera exponencial.</summary>
public sealed class DespachadorDeBandejaDeSalida(
    IAlmacenDeMensajeria almacen,
    IBusDeEventos bus,
    IClock reloj,
    OpcionesDeDespacho opciones,
    ILogger<DespachadorDeBandejaDeSalida> logger)
{
    public async Task<int> DespacharPendientesAsync(CancellationToken cancellationToken = default)
    {
        var pendientes = await almacen.ObtenerMensajesPendientesAsync(
            reloj.Now, opciones.TamanoDeLote, opciones.MaximoDeIntentos, cancellationToken);

        var publicados = 0;
        foreach (var mensaje in pendientes)
        {
            try
            {
                using var payload = JsonDocument.Parse(mensaje.PayloadJson);
                await bus.PublicarAsync(
                    new SobreDeEvento(mensaje.Id, mensaje.Topico, mensaje.OcurrioEn, mensaje.CorrelacionId, payload.RootElement.Clone()),
                    cancellationToken);
                await almacen.MarcarMensajePublicadoAsync(mensaje.Id, reloj.Now, cancellationToken);
                publicados++;
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                var intento = mensaje.Intentos + 1;
                logger.LogWarning(ex, "No se pudo publicar {Topico} ({Id}); intento {Intento}", mensaje.Topico, mensaje.Id, intento);
                await almacen.RegistrarIntentoFallidoAsync(mensaje.Id, ex.Message, reloj.Now + Espera(intento), cancellationToken);
                if (intento >= opciones.MaximoDeIntentos)
                    logger.LogError("El mensaje {Topico} ({Id}) agotó sus {Intentos} intentos y no se volverá a publicar sin intervención", mensaje.Topico, mensaje.Id, intento);
            }
        }

        return publicados;
    }

    private TimeSpan Espera(int intento)
    {
        var milisegundos = opciones.EsperaBase.TotalMilliseconds * Math.Pow(2, Math.Min(intento - 1, 20));
        return TimeSpan.FromMilliseconds(Math.Min(milisegundos, opciones.EsperaMaxima.TotalMilliseconds));
    }
}
