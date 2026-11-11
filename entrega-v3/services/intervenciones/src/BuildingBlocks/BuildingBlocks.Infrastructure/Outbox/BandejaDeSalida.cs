using BuildingBlocks.Application.Persistencia;

namespace BuildingBlocks.Infrastructure.Outbox;

/// <summary>Outbox transaccional: guarda los agregados y los mensajes por publicar en una sola operación atómica.</summary>
public sealed class BandejaDeSalida(IAlmacenDeDocumentos almacen)
{
    public Task GuardarAsync(LoteDeEscritura lote, CancellationToken cancellationToken = default) =>
        lote.EstaVacio ? Task.CompletedTask : almacen.ConfirmarAsync(lote, cancellationToken);
}
