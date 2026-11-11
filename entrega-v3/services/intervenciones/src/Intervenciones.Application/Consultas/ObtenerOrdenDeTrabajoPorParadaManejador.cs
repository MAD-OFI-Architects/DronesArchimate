using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Excepciones;
using Intervenciones.Domain;

namespace Intervenciones.Application.Consultas;

public sealed class ObtenerOrdenDeTrabajoPorParadaManejador(IOrdenDeTrabajoRepository ordenes)
    : IManejadorDeConsulta<ObtenerOrdenDeTrabajoPorParadaConsulta, OrdenDeTrabajoDto>
{
    public async Task<OrdenDeTrabajoDto> ManejarAsync(ObtenerOrdenDeTrabajoPorParadaConsulta consulta, CancellationToken cancellationToken)
    {
        var orden = await ordenes.ObtenerPorParadaAsync(consulta.ParadaId, cancellationToken)
            ?? throw new RecursoNoEncontradoException("la orden de trabajo de la parada", consulta.ParadaId);

        return OrdenDeTrabajoMapeador.ADto(orden);
    }
}
