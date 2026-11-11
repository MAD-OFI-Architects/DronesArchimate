using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Persistencia;
using MongoDB.Bson;
using MongoDB.Bson.IO;
using MongoDB.Driver;

namespace BuildingBlocks.Infrastructure.Persistencia;

/// <summary>Almacén MongoDB: los documentos, la bandeja de salida y la de entrada se escriben en una transacción
/// (requiere replica set).</summary>
public sealed class AlmacenDeDocumentosMongo(IMongoClient cliente, IMongoDatabase baseDeDatos)
    : IAlmacenDeDocumentos, IAlmacenDeMensajeria
{
    public const string ColeccionBandejaDeSalida = "bandeja_salida";
    public const string ColeccionBandejaDeEntrada = "bandeja_entrada";

    private static readonly JsonWriterSettings AjustesJson = new() { OutputMode = JsonOutputMode.RelaxedExtendedJson };

    public async Task<Documento?> ObtenerAsync(string coleccion, string id, CancellationToken cancellationToken = default)
    {
        var bson = await Coleccion(coleccion).Find(new BsonDocument("_id", id)).FirstOrDefaultAsync(cancellationToken);
        return bson is null ? null : ADocumento(coleccion, bson);
    }

    public async Task<IReadOnlyList<Documento>> ListarAsync(string coleccion, CancellationToken cancellationToken = default)
    {
        var todos = await Coleccion(coleccion).Find(FilterDefinition<BsonDocument>.Empty).ToListAsync(cancellationToken);
        return todos.Select(b => ADocumento(coleccion, b)).ToList();
    }

    public async Task ConfirmarAsync(LoteDeEscritura lote, CancellationToken cancellationToken = default)
    {
        using var sesion = await cliente.StartSessionAsync(cancellationToken: cancellationToken);
        sesion.StartTransaction();
        try
        {
            foreach (var escritura in lote.Documentos)
                await EscribirDocumentoAsync(sesion, escritura, cancellationToken);

            if (lote.Mensajes.Count > 0)
                await Coleccion(ColeccionBandejaDeSalida)
                    .InsertManyAsync(sesion, lote.Mensajes.Select(AMensajeBson), cancellationToken: cancellationToken);

            if (lote.MensajesEntrantes.Count > 0)
                await Coleccion(ColeccionBandejaDeEntrada).InsertManyAsync(
                    sesion,
                    lote.MensajesEntrantes.Select(id => new BsonDocument("_id", id.ToString())),
                    cancellationToken: cancellationToken);

            await sesion.CommitTransactionAsync(cancellationToken);
        }
        catch (Exception ex) when (EsConflictoDeEscritura(ex))
        {
            await sesion.AbortTransactionAsync(CancellationToken.None);
            throw new ConflictoDeConcurrenciaException("El documento o el mensaje ya fue escrito por otra operación.");
        }
        catch
        {
            if (sesion.IsInTransaction)
                await sesion.AbortTransactionAsync(CancellationToken.None);
            throw;
        }
    }

    public async Task<bool> ExisteMensajeEntranteAsync(Guid eventId, CancellationToken cancellationToken = default) =>
        await Coleccion(ColeccionBandejaDeEntrada).CountDocumentsAsync(
            new BsonDocument("_id", eventId.ToString()), cancellationToken: cancellationToken) > 0;

    public async Task<IReadOnlyList<MensajeDeSalida>> ObtenerMensajesPendientesAsync(
        DateTimeOffset ahora, int maximo, int maximoIntentos, CancellationToken cancellationToken = default)
    {
        var filtro = Builders<BsonDocument>.Filter.And(
            Builders<BsonDocument>.Filter.Eq("publicadoEn", BsonNull.Value),
            Builders<BsonDocument>.Filter.Lt("intentos", maximoIntentos),
            Builders<BsonDocument>.Filter.Lte("proximoIntentoEn", ahora.UtcDateTime));

        var pendientes = await Coleccion(ColeccionBandejaDeSalida)
            .Find(filtro).SortBy(b => b["ocurrioEn"]).Limit(maximo).ToListAsync(cancellationToken);
        return pendientes.Select(ADominio).ToList();
    }

    public Task MarcarMensajePublicadoAsync(Guid id, DateTimeOffset publicadoEn, CancellationToken cancellationToken = default) =>
        Coleccion(ColeccionBandejaDeSalida).UpdateOneAsync(
            new BsonDocument("_id", id.ToString()),
            Builders<BsonDocument>.Update.Set("publicadoEn", publicadoEn.UtcDateTime),
            cancellationToken: cancellationToken);

    public Task RegistrarIntentoFallidoAsync(
        Guid id, string error, DateTimeOffset proximoIntentoEn, CancellationToken cancellationToken = default) =>
        Coleccion(ColeccionBandejaDeSalida).UpdateOneAsync(
            new BsonDocument("_id", id.ToString()),
            Builders<BsonDocument>.Update
                .Inc("intentos", 1)
                .Set("ultimoError", error)
                .Set("proximoIntentoEn", proximoIntentoEn.UtcDateTime),
            cancellationToken: cancellationToken);

    private async Task EscribirDocumentoAsync(IClientSessionHandle sesion, EscrituraDeDocumento escritura, CancellationToken ct)
    {
        var coleccion = Coleccion(escritura.Coleccion);
        var nuevo = new BsonDocument
        {
            { "_id", escritura.Id },
            { "version", escritura.VersionEsperada + 1 },
            { "datos", BsonDocument.Parse(escritura.Json) }
        };

        if (escritura.VersionEsperada == 0)
        {
            await coleccion.InsertOneAsync(sesion, nuevo, cancellationToken: ct);
            return;
        }

        var filtro = new BsonDocument { { "_id", escritura.Id }, { "version", escritura.VersionEsperada } };
        var resultado = await coleccion.ReplaceOneAsync(sesion, filtro, nuevo, cancellationToken: ct);
        if (resultado.MatchedCount == 0)
            throw new ConflictoDeConcurrenciaException(
                $"El documento '{escritura.Coleccion}/{escritura.Id}' fue modificado por otra operación.");
    }

    private IMongoCollection<BsonDocument> Coleccion(string nombre) => baseDeDatos.GetCollection<BsonDocument>(nombre);

    private static Documento ADocumento(string coleccion, BsonDocument bson) =>
        new(coleccion, bson["_id"].AsString, bson["datos"].AsBsonDocument.ToJson(AjustesJson), bson["version"].ToInt64());

    private static BsonDocument AMensajeBson(MensajeDeSalida m) => new()
    {
        { "_id", m.Id.ToString() },
        { "topico", m.Topico },
        { "payload", m.PayloadJson },
        { "ocurrioEn", m.OcurrioEn.UtcDateTime },
        { "correlacionId", m.CorrelacionId.ToString() },
        { "intentos", m.Intentos },
        { "proximoIntentoEn", m.ProximoIntentoEn.UtcDateTime },
        { "publicadoEn", BsonNull.Value }
    };

    private static MensajeDeSalida ADominio(BsonDocument b) => new()
    {
        Id = Guid.Parse(b["_id"].AsString),
        Topico = b["topico"].AsString,
        PayloadJson = b["payload"].AsString,
        OcurrioEn = new DateTimeOffset(b["ocurrioEn"].ToUniversalTime(), TimeSpan.Zero),
        CorrelacionId = Guid.Parse(b["correlacionId"].AsString),
        Intentos = b["intentos"].ToInt32(),
        ProximoIntentoEn = new DateTimeOffset(b["proximoIntentoEn"].ToUniversalTime(), TimeSpan.Zero),
        UltimoError = b.GetValue("ultimoError", BsonNull.Value).IsBsonNull ? null : b["ultimoError"].AsString
    };

    /// <summary>Dos transacciones que escriben el mismo documento chocan como clave duplicada (si una ya confirmó)
    /// o como conflicto de escritura transitorio (si siguen abiertas): en ambos casos otra operación ganó.</summary>
    private static bool EsConflictoDeEscritura(Exception ex) => ex switch
    {
        MongoWriteException e => e.WriteError.Category == ServerErrorCategory.DuplicateKey,
        MongoBulkWriteException e => e.WriteErrors.Any(w => w.Category == ServerErrorCategory.DuplicateKey),
        MongoException e => e.HasErrorLabel("TransientTransactionError"),
        _ => false
    };
}
