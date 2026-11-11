using BuildingBlocks.Application.Correlacion;
using BuildingBlocks.Application.EventosDeDominio;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Serializacion;
using BuildingBlocks.Domain;
using BuildingBlocks.Infrastructure.Outbox;

namespace BuildingBlocks.Infrastructure.Persistencia;

/// <summary>Unit of Work con Outbox: guarda en una transacción los agregados cambiados, los eventos traducidos
/// y la marca del mensaje entrante; después limpia y despacha los eventos de dominio.</summary>
public sealed class UnidadDeTrabajoDocumental(
    BandejaDeSalida bandeja,
    IEnumerable<ITraductorDeEventoDeDominio> traductores,
    IDespachadorDeEventosDeDominio despachador,
    IContextoDeCorrelacion correlacion,
    ISerializadorJson serializador) : IUnidadDeTrabajo
{
    private readonly Dictionary<(string Coleccion, string Id), Rastreado> _rastreados = [];
    private readonly List<Guid> _mensajesEntrantes = [];
    private readonly Dictionary<Type, ITraductorDeEventoDeDominio> _traductores = traductores.ToDictionary(t => t.TipoDeEvento);

    public bool TryObtener<TAgregado>(string coleccion, string id, out TAgregado? agregado) where TAgregado : class, IAggregateRoot
    {
        agregado = _rastreados.TryGetValue((coleccion, id), out var r) ? r.Agregado as TAgregado : null;
        return agregado is not null;
    }

    public void Rastrear(string coleccion, string id, IAggregateRoot agregado, Func<string> serializar, long version)
    {
        if (_rastreados.ContainsKey((coleccion, id)))
            throw new InvalidOperationException($"El documento '{coleccion}/{id}' ya está rastreado en esta unidad de trabajo.");

        _rastreados[(coleccion, id)] = new Rastreado(agregado, serializar, version == 0 ? null : serializar(), version);
    }

    public void RegistrarMensajeEntrante(Guid eventId) => _mensajesEntrantes.Add(eventId);

    public async Task ConfirmarAsync(CancellationToken cancellationToken = default)
    {
        var escrituras = new List<(Rastreado Rastreado, EscrituraDeDocumento Escritura)>();
        foreach (var ((coleccion, id), rastreado) in _rastreados)
        {
            var json = rastreado.Serializar();
            if (json != rastreado.JsonOriginal)
                escrituras.Add((rastreado, new EscrituraDeDocumento(coleccion, id, json, rastreado.Version)));
        }

        var eventos = _rastreados.Values.SelectMany(r => r.Agregado.DomainEvents).ToList();
        var mensajes = eventos.Select(CrearMensaje).OfType<MensajeDeSalida>().ToList();

        var lote = new LoteDeEscritura(escrituras.Select(e => e.Escritura).ToList(), mensajes, _mensajesEntrantes.ToList());
        if (lote.EstaVacio)
            return;

        await bandeja.GuardarAsync(lote, cancellationToken);

        foreach (var (rastreado, escritura) in escrituras)
        {
            rastreado.JsonOriginal = escritura.Json;
            rastreado.Version = escritura.VersionEsperada + 1;
        }

        _mensajesEntrantes.Clear();
        foreach (var rastreado in _rastreados.Values)
            rastreado.Agregado.ClearDomainEvents();

        await despachador.DespacharAsync(eventos, cancellationToken);
    }

    private MensajeDeSalida? CrearMensaje(IDomainEvent evento)
    {
        if (!_traductores.TryGetValue(evento.GetType(), out var traductor))
            return null;

        var integracion = traductor.Traducir(evento);
        return new MensajeDeSalida
        {
            Id = integracion.Id,
            Topico = integracion.Topico,
            PayloadJson = serializador.Serializar(integracion.Contrato),
            OcurrioEn = integracion.OcurrioEn,
            CorrelacionId = correlacion.Id
        };
    }

    private sealed class Rastreado(IAggregateRoot agregado, Func<string> serializar, string? jsonOriginal, long version)
    {
        public IAggregateRoot Agregado { get; } = agregado;
        public Func<string> Serializar { get; } = serializar;
        public string? JsonOriginal { get; set; } = jsonOriginal;
        public long Version { get; set; } = version;
    }
}
