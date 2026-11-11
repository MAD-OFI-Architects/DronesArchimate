using BuildingBlocks.Application.Correlacion;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Serializacion;
using BuildingBlocks.Infrastructure.Persistencia;
using Microsoft.Extensions.DependencyInjection;

namespace BuildingBlocks.Infrastructure.Mensajeria;

public enum ResultadoDeProcesamiento
{
    Procesado,
    Duplicado,
    TopicoNoSuscrito
}

/// <summary>Consumidor registrado para un tópico: sabe deserializar el contrato y llamar a su manejador.</summary>
public sealed class ConsumidorRegistrado(
    string topico,
    Func<IServiceProvider, SobreDeEvento, ContextoDeMensaje, CancellationToken, Task> manejar)
{
    public string Topico { get; } = topico;

    public Task ManejarAsync(IServiceProvider servicios, SobreDeEvento sobre, ContextoDeMensaje contexto, CancellationToken ct) =>
        manejar(servicios, sobre, contexto, ct);

    public static ConsumidorRegistrado Para<TMensaje>(string topico) =>
        new(topico, (servicios, sobre, contexto, ct) =>
        {
            var mensaje = servicios.GetRequiredService<ISerializadorJson>().Deserializar<TMensaje>(sobre.Payload.GetRawText());
            return servicios.GetRequiredService<IManejadorDeEventoDeIntegracion<TMensaje>>().ManejarAsync(mensaje, contexto, ct);
        });
}

/// <summary>Recibe mensajes del bus y descarta los repetidos: procesar uno dos veces da el mismo resultado.</summary>
public sealed class ProcesadorDeMensajeEntrante(IServiceScopeFactory scopes, IEnumerable<ConsumidorRegistrado> consumidores)
{
    private readonly Dictionary<string, ConsumidorRegistrado> _consumidores = consumidores.ToDictionary(c => c.Topico);

    public async Task<ResultadoDeProcesamiento> ProcesarAsync(SobreDeEvento sobre, CancellationToken cancellationToken = default)
    {
        if (!_consumidores.TryGetValue(sobre.Topic, out var consumidor))
            return ResultadoDeProcesamiento.TopicoNoSuscrito;

        await using var scope = scopes.CreateAsyncScope();
        var servicios = scope.ServiceProvider;
        servicios.GetRequiredService<IContextoDeCorrelacion>().Id = sobre.CorrelationId;

        var mensajeria = servicios.GetRequiredService<IAlmacenDeMensajeria>();
        if (await mensajeria.ExisteMensajeEntranteAsync(sobre.EventId, cancellationToken))
            return ResultadoDeProcesamiento.Duplicado;

        var unidadDeTrabajo = servicios.GetRequiredService<UnidadDeTrabajoDocumental>();
        unidadDeTrabajo.RegistrarMensajeEntrante(sobre.EventId);
        try
        {
            var contexto = new ContextoDeMensaje(sobre.EventId, sobre.CorrelationId, sobre.Topic, sobre.OccurredOn);
            await consumidor.ManejarAsync(servicios, sobre, contexto, cancellationToken);
            await unidadDeTrabajo.ConfirmarAsync(cancellationToken);
        }
        catch (ConflictoDeConcurrenciaException)
        {
            if (await mensajeria.ExisteMensajeEntranteAsync(sobre.EventId, cancellationToken))
                return ResultadoDeProcesamiento.Duplicado;
            throw;
        }

        return ResultadoDeProcesamiento.Procesado;
    }
}
