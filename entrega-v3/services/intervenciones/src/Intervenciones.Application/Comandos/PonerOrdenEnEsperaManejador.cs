using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class PonerOrdenEnEsperaManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : ManejadorDeComandoDeOrden<PonerOrdenEnEsperaComando>(ordenes, reloj)
{
    protected override Task AplicarAsync(OrdenDeTrabajo orden, PonerOrdenEnEsperaComando c, CancellationToken cancellationToken)
    {
        orden.PonerEnEspera(c.Motivo, Ahora);
        return Task.CompletedTask;
    }
}
