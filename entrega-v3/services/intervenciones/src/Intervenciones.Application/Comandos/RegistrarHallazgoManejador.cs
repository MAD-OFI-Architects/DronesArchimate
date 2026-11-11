using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarHallazgoManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : ManejadorDeComandoDeOrden<RegistrarHallazgoComando>(ordenes, reloj)
{
    protected override Task AplicarAsync(OrdenDeTrabajo orden, RegistrarHallazgoComando c, CancellationToken cancellationToken)
    {
        orden.RegistrarHallazgo(c.Descripcion, Ahora);
        return Task.CompletedTask;
    }
}
