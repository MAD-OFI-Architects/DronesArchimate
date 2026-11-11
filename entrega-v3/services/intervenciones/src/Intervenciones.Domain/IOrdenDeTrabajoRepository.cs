namespace Intervenciones.Domain;

public interface IOrdenDeTrabajoRepository
{
    Task<OrdenDeTrabajo?> ObtenerAsync(Guid id, CancellationToken cancellationToken = default);

    Task<OrdenDeTrabajo?> ObtenerPorParadaAsync(Guid paradaId, CancellationToken cancellationToken = default);

    Task GuardarAsync(OrdenDeTrabajo orden, CancellationToken cancellationToken = default);
}
