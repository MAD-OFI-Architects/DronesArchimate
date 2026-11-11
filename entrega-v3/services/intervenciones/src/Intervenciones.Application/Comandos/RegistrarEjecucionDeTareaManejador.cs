using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarEjecucionDeTareaManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : ManejadorDeComandoDeOrden<RegistrarEjecucionDeTareaComando>(ordenes, reloj)
{
    protected override Task AplicarAsync(OrdenDeTrabajo orden, RegistrarEjecucionDeTareaComando c, CancellationToken cancellationToken)
    {
        orden.RegistrarEjecucionDeTarea(c.TareaId, c.Descripcion, c.Resultado, c.EjecutadaPor, new HorasHombre(c.Horas), Ahora);
        return Task.CompletedTask;
    }
}
