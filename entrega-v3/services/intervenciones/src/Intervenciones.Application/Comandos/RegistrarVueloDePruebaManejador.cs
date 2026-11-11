using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarVueloDePruebaManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : ManejadorDeComandoDeOrden<RegistrarVueloDePruebaComando>(ordenes, reloj)
{
    protected override Task AplicarAsync(OrdenDeTrabajo orden, RegistrarVueloDePruebaComando c, CancellationToken cancellationToken)
    {
        orden.RegistrarVueloDePrueba(new VueloDePrueba(c.RealizadoEn, c.DuracionEnMinutos, c.Aprobado, c.Observaciones), Ahora);
        return Task.CompletedTask;
    }
}
