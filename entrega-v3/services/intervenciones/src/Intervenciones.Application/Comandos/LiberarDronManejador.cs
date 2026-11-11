using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class LiberarDronManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : ManejadorDeComandoDeOrden<LiberarDronComando>(ordenes, reloj)
{
    protected override Task AplicarAsync(OrdenDeTrabajo orden, LiberarDronComando c, CancellationToken cancellationToken)
    {
        orden.LiberarDron(c.LiberacionId, c.LiberadaPor, Ahora);
        return Task.CompletedTask;
    }
}
