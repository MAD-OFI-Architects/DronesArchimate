namespace BuildingBlocks.Application.Persistencia;

public interface IUnidadDeTrabajo
{
    /// <summary>Guarda en una sola operación los agregados modificados y los mensajes por publicar.</summary>
    Task ConfirmarAsync(CancellationToken cancellationToken = default);
}
