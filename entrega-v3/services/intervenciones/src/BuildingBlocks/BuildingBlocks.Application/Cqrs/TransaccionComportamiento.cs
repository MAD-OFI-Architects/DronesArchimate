using BuildingBlocks.Application.Persistencia;

namespace BuildingBlocks.Application.Cqrs;

/// <summary>Eslabón 3 (interno): confirma la unidad de trabajo tras un comando; las consultas pasan sin transacción.</summary>
public sealed class TransaccionComportamiento<TSolicitud, TRespuesta>(IUnidadDeTrabajo unidadDeTrabajo)
    : IComportamientoDePipeline<TSolicitud, TRespuesta> where TSolicitud : ISolicitud<TRespuesta>
{
    private static readonly bool EsComando = typeof(IComando<TRespuesta>).IsAssignableFrom(typeof(TSolicitud));

    public async Task<TRespuesta> ManejarAsync(
        TSolicitud solicitud, SiguienteEnElPipeline<TRespuesta> siguiente, CancellationToken cancellationToken)
    {
        var respuesta = await siguiente();
        if (EsComando)
            await unidadDeTrabajo.ConfirmarAsync(cancellationToken);

        return respuesta;
    }
}
