using System.Diagnostics;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Application.Cqrs;

/// <summary>Eslabón 1 (externo): registra el resultado de cada solicitud.</summary>
public sealed class RegistroComportamiento<TSolicitud, TRespuesta>(
    ILogger<RegistroComportamiento<TSolicitud, TRespuesta>> logger)
    : IComportamientoDePipeline<TSolicitud, TRespuesta> where TSolicitud : ISolicitud<TRespuesta>
{
    public async Task<TRespuesta> ManejarAsync(
        TSolicitud solicitud, SiguienteEnElPipeline<TRespuesta> siguiente, CancellationToken cancellationToken)
    {
        var nombre = typeof(TSolicitud).Name;
        var reloj = Stopwatch.StartNew();
        try
        {
            var respuesta = await siguiente();
            logger.LogInformation("Solicitud {Solicitud} completada en {Milisegundos} ms", nombre, reloj.ElapsedMilliseconds);
            return respuesta;
        }
        catch (Exception ex)
        {
            logger.LogWarning("Solicitud {Solicitud} rechazada: {Motivo}", nombre, ex.Message);
            throw;
        }
    }
}
