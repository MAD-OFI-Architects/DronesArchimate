using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Excepciones;
using Intervenciones.Domain;

namespace Intervenciones.Application.Consultas;

public sealed class ObtenerOrdenDeTrabajoManejador(IOrdenDeTrabajoRepository ordenes)
    : IManejadorDeConsulta<ObtenerOrdenDeTrabajoConsulta, OrdenDeTrabajoDto>
{
    public async Task<OrdenDeTrabajoDto> ManejarAsync(ObtenerOrdenDeTrabajoConsulta consulta, CancellationToken cancellationToken)
    {
        var orden = await ordenes.ObtenerAsync(consulta.OrdenId, cancellationToken)
            ?? throw new RecursoNoEncontradoException("la orden de trabajo", consulta.OrdenId);

        return OrdenDeTrabajoMapeador.ADto(orden);
    }
}
