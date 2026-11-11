using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Persistencia;

namespace BuildingBlocks.Infrastructure.Persistencia;

/// <summary>Implementación en memoria del almacén y de las bandejas, para pruebas herméticas.</summary>
public sealed class AlmacenDeDocumentosEnMemoria : IAlmacenDeDocumentos, IAlmacenDeMensajeria
{
    private readonly object _candado = new();
    private readonly Dictionary<(string Coleccion, string Id), (string Json, long Version)> _documentos = [];
    private readonly Dictionary<Guid, MensajeDeSalida> _salida = [];
    private readonly HashSet<Guid> _entrada = [];

    public Task<Documento?> ObtenerAsync(string coleccion, string id, CancellationToken cancellationToken = default)
    {
        lock (_candado)
        {
            return Task.FromResult(_documentos.TryGetValue((coleccion, id), out var d)
                ? new Documento(coleccion, id, d.Json, d.Version)
                : null);
        }
    }

    public Task<IReadOnlyList<Documento>> ListarAsync(string coleccion, CancellationToken cancellationToken = default)
    {
        lock (_candado)
        {
            IReadOnlyList<Documento> lista = _documentos
                .Where(p => p.Key.Coleccion == coleccion)
                .Select(p => new Documento(coleccion, p.Key.Id, p.Value.Json, p.Value.Version))
                .ToList();
            return Task.FromResult(lista);
        }
    }

    public Task ConfirmarAsync(LoteDeEscritura lote, CancellationToken cancellationToken = default)
    {
        lock (_candado)
        {
            foreach (var escritura in lote.Documentos)
            {
                var versionActual = _documentos.TryGetValue((escritura.Coleccion, escritura.Id), out var actual) ? actual.Version : 0;
                if (versionActual != escritura.VersionEsperada)
                    throw new ConflictoDeConcurrenciaException(
                        $"El documento '{escritura.Coleccion}/{escritura.Id}' fue modificado por otra operación.");
            }

            if (lote.MensajesEntrantes.Any(_entrada.Contains) || lote.MensajesEntrantes.Distinct().Count() != lote.MensajesEntrantes.Count)
                throw new ConflictoDeConcurrenciaException("El mensaje entrante ya fue procesado.");

            foreach (var escritura in lote.Documentos)
                _documentos[(escritura.Coleccion, escritura.Id)] = (escritura.Json, escritura.VersionEsperada + 1);
            foreach (var mensaje in lote.Mensajes)
                _salida[mensaje.Id] = mensaje;
            foreach (var entrante in lote.MensajesEntrantes)
                _entrada.Add(entrante);
        }

        return Task.CompletedTask;
    }

    public Task<bool> ExisteMensajeEntranteAsync(Guid eventId, CancellationToken cancellationToken = default)
    {
        lock (_candado)
            return Task.FromResult(_entrada.Contains(eventId));
    }

    public Task<IReadOnlyList<MensajeDeSalida>> ObtenerMensajesPendientesAsync(
        DateTimeOffset ahora, int maximo, int maximoIntentos, CancellationToken cancellationToken = default)
    {
        lock (_candado)
        {
            IReadOnlyList<MensajeDeSalida> pendientes = _salida.Values
                .Where(m => m.PublicadoEn is null && m.Intentos < maximoIntentos && m.ProximoIntentoEn <= ahora)
                .OrderBy(m => m.OcurrioEn)
                .Take(maximo)
                .ToList();
            return Task.FromResult(pendientes);
        }
    }

    public Task MarcarMensajePublicadoAsync(Guid id, DateTimeOffset publicadoEn, CancellationToken cancellationToken = default)
    {
        lock (_candado)
            _salida[id] = _salida[id] with { PublicadoEn = publicadoEn };
        return Task.CompletedTask;
    }

    public Task RegistrarIntentoFallidoAsync(
        Guid id, string error, DateTimeOffset proximoIntentoEn, CancellationToken cancellationToken = default)
    {
        lock (_candado)
        {
            var mensaje = _salida[id];
            _salida[id] = mensaje with { Intentos = mensaje.Intentos + 1, UltimoError = error, ProximoIntentoEn = proximoIntentoEn };
        }

        return Task.CompletedTask;
    }

    public IReadOnlyList<MensajeDeSalida> MensajesDeSalida
    {
        get
        {
            lock (_candado)
                return _salida.Values.OrderBy(m => m.OcurrioEn).ToList();
        }
    }
}
