using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Validacion;

namespace BuildingBlocks.Application.Cqrs;

/// <summary>Eslabón 2: valida la forma de la solicitud antes de tocar el dominio.</summary>
public sealed class ValidacionComportamiento<TSolicitud, TRespuesta>(IEnumerable<IValidador<TSolicitud>> validadores)
    : IComportamientoDePipeline<TSolicitud, TRespuesta> where TSolicitud : ISolicitud<TRespuesta>
{
    public Task<TRespuesta> ManejarAsync(
        TSolicitud solicitud, SiguienteEnElPipeline<TRespuesta> siguiente, CancellationToken cancellationToken)
    {
        var errores = validadores.SelectMany(v => v.Validar(solicitud)).ToList();
        return errores.Count > 0 ? throw new ValidacionException(errores) : siguiente();
    }
}
