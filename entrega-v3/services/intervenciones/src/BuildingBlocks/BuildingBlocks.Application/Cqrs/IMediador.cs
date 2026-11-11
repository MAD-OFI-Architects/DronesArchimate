namespace BuildingBlocks.Application.Cqrs;

public interface IMediador
{
    Task<TRespuesta> EnviarAsync<TRespuesta>(ISolicitud<TRespuesta> solicitud, CancellationToken cancellationToken = default);
}
