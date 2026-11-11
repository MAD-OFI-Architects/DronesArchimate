using System.Text.Json;

namespace BuildingBlocks.Application.Integracion;

/// <summary>Evento listo para salir del servicio: conserva el Id del evento de dominio.</summary>
public sealed record EventoDeIntegracion(Guid Id, string Topico, object Contrato, DateTimeOffset OcurrioEn);

/// <summary>Sobre del bus (ver contrato-bus.md).</summary>
public sealed record SobreDeEvento(
    Guid EventId,
    string Topic,
    DateTimeOffset OccurredOn,
    Guid CorrelationId,
    JsonElement Payload);

public sealed record ContextoDeMensaje(Guid EventId, Guid CorrelationId, string Topico, DateTimeOffset OcurrioEn);

/// <summary>Consumidor de un contrato publicado por otro contexto.</summary>
public interface IManejadorDeEventoDeIntegracion<in TMensaje>
{
    Task ManejarAsync(TMensaje mensaje, ContextoDeMensaje contexto, CancellationToken cancellationToken);
}

public interface IBusDeEventos
{
    Task PublicarAsync(SobreDeEvento sobre, CancellationToken cancellationToken = default);
}

public sealed class FalloDePublicacionException(string mensaje, Exception? interna = null) : Exception(mensaje, interna);
