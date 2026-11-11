using System.Collections.Concurrent;
using Microsoft.Extensions.DependencyInjection;

namespace BuildingBlocks.Application.Cqrs;

public sealed class Mediador(IServiceProvider servicios) : IMediador
{
    private static readonly ConcurrentDictionary<(Type Solicitud, Type Respuesta), object> Envoltorios = new();

    public Task<TRespuesta> EnviarAsync<TRespuesta>(
        ISolicitud<TRespuesta> solicitud,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(solicitud);

        var envoltorio = (EnvoltorioDeSolicitud<TRespuesta>)Envoltorios.GetOrAdd(
            (solicitud.GetType(), typeof(TRespuesta)),
            clave => Activator.CreateInstance(
                typeof(EnvoltorioDeSolicitud<,>).MakeGenericType(clave.Solicitud, clave.Respuesta))!);

        return envoltorio.ManejarAsync(solicitud, servicios, cancellationToken);
    }
}

internal abstract class EnvoltorioDeSolicitud<TRespuesta>
{
    public abstract Task<TRespuesta> ManejarAsync(
        ISolicitud<TRespuesta> solicitud, IServiceProvider servicios, CancellationToken cancellationToken);
}

internal sealed class EnvoltorioDeSolicitud<TSolicitud, TRespuesta> : EnvoltorioDeSolicitud<TRespuesta>
    where TSolicitud : ISolicitud<TRespuesta>
{
    public override Task<TRespuesta> ManejarAsync(
        ISolicitud<TRespuesta> solicitud, IServiceProvider servicios, CancellationToken cancellationToken)
    {
        var manejador = servicios.GetService<IManejadorDeSolicitud<TSolicitud, TRespuesta>>()
            ?? throw new InvalidOperationException($"No hay un manejador registrado para {typeof(TSolicitud).Name}.");
        var tipada = (TSolicitud)solicitud;

        SiguienteEnElPipeline<TRespuesta> cadena = () => manejador.ManejarAsync(tipada, cancellationToken);
        foreach (var comportamiento in servicios.GetServices<IComportamientoDePipeline<TSolicitud, TRespuesta>>().Reverse())
        {
            var siguiente = cadena;
            cadena = () => comportamiento.ManejarAsync(tipada, siguiente, cancellationToken);
        }

        return cadena();
    }
}
