using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class CerrarOrdenDeTrabajoManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : ManejadorDeComandoDeOrden<CerrarOrdenDeTrabajoComando>(ordenes, reloj)
{
    protected override Task AplicarAsync(OrdenDeTrabajo orden, CerrarOrdenDeTrabajoComando c, CancellationToken cancellationToken)
    {
        orden.Cerrar(Ahora);
        return Task.CompletedTask;
    }
}
