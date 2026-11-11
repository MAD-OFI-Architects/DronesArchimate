namespace BuildingBlocks.Application.Cqrs;

public delegate Task<TRespuesta> SiguienteEnElPipeline<TRespuesta>();

/// <summary>Eslabón de la cadena que envuelve a cada caso de uso (Chain of Responsibility).</summary>
public interface IComportamientoDePipeline<in TSolicitud, TRespuesta> where TSolicitud : ISolicitud<TRespuesta>
{
    Task<TRespuesta> ManejarAsync(
        TSolicitud solicitud,
        SiguienteEnElPipeline<TRespuesta> siguiente,
        CancellationToken cancellationToken);
}
