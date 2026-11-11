using BuildingBlocks.Domain;

namespace BuildingBlocks.Application.Integracion;

public interface ITraductorDeEventoDeDominio
{
    Type TipoDeEvento { get; }

    EventoDeIntegracion Traducir(IDomainEvent evento);
}

/// <summary>Convierte un evento de dominio en el contrato público que sale hacia otros contextos.</summary>
public abstract class TraductorDeEventoDeDominio<TEvento> : ITraductorDeEventoDeDominio where TEvento : IDomainEvent
{
    public Type TipoDeEvento => typeof(TEvento);

    protected abstract string Topico { get; }

    public EventoDeIntegracion Traducir(IDomainEvent evento) =>
        evento is TEvento tipado
            ? new EventoDeIntegracion(tipado.EventoId, Topico, CrearContrato(tipado), tipado.OcurrioEn)
            : throw new ArgumentException($"Se esperaba {typeof(TEvento).Name} y llegó {evento.GetType().Name}.", nameof(evento));

    protected abstract object CrearContrato(TEvento evento);
}
