namespace BuildingBlocks.Application.Cqrs;

public interface IManejadorDeSolicitud<in TSolicitud, TRespuesta> where TSolicitud : ISolicitud<TRespuesta>
{
    Task<TRespuesta> ManejarAsync(TSolicitud solicitud, CancellationToken cancellationToken);
}

public interface IManejadorDeComando<in TComando, TRespuesta> : IManejadorDeSolicitud<TComando, TRespuesta>
    where TComando : IComando<TRespuesta>;

public interface IManejadorDeConsulta<in TConsulta, TRespuesta> : IManejadorDeSolicitud<TConsulta, TRespuesta>
    where TConsulta : IConsulta<TRespuesta>;
