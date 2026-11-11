namespace BuildingBlocks.Application.Persistencia;

/// <summary>Documento guardado; Version permite concurrencia optimista (0 = aún no existe).</summary>
public sealed record Documento(string Coleccion, string Id, string Json, long Version);

public sealed record EscrituraDeDocumento(string Coleccion, string Id, string Json, long VersionEsperada);

public sealed record MensajeDeSalida
{
    public required Guid Id { get; init; }
    public required string Topico { get; init; }
    public required string PayloadJson { get; init; }
    public required DateTimeOffset OcurrioEn { get; init; }
    public required Guid CorrelacionId { get; init; }
    public int Intentos { get; init; }
    public DateTimeOffset ProximoIntentoEn { get; init; }
    public DateTimeOffset? PublicadoEn { get; init; }
    public string? UltimoError { get; init; }
}

/// <summary>Todo lo que debe persistirse junto: documentos, mensajes de salida y marcas de mensajes entrantes.</summary>
public sealed record LoteDeEscritura(
    IReadOnlyList<EscrituraDeDocumento> Documentos,
    IReadOnlyList<MensajeDeSalida> Mensajes,
    IReadOnlyList<Guid> MensajesEntrantes)
{
    public bool EstaVacio => Documentos.Count == 0 && Mensajes.Count == 0 && MensajesEntrantes.Count == 0;
}

/// <summary>Puerto de persistencia documental; el dominio no conoce la base de datos.</summary>
public interface IAlmacenDeDocumentos
{
    Task<Documento?> ObtenerAsync(string coleccion, string id, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<Documento>> ListarAsync(string coleccion, CancellationToken cancellationToken = default);

    /// <summary>Atómico: o se guarda todo el lote o nada. Lanza ConflictoDeConcurrenciaException si la versión no coincide.</summary>
    Task ConfirmarAsync(LoteDeEscritura lote, CancellationToken cancellationToken = default);
}

/// <summary>Puerto de las bandejas de salida y entrada.</summary>
public interface IAlmacenDeMensajeria
{
    Task<bool> ExisteMensajeEntranteAsync(Guid eventId, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<MensajeDeSalida>> ObtenerMensajesPendientesAsync(
        DateTimeOffset ahora, int maximo, int maximoIntentos, CancellationToken cancellationToken = default);

    Task MarcarMensajePublicadoAsync(Guid id, DateTimeOffset publicadoEn, CancellationToken cancellationToken = default);

    Task RegistrarIntentoFallidoAsync(
        Guid id, string error, DateTimeOffset proximoIntentoEn, CancellationToken cancellationToken = default);
}
