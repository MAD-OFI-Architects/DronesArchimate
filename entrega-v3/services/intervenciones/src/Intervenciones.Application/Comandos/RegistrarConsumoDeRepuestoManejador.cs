using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarConsumoDeRepuestoManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : ManejadorDeComandoDeOrden<RegistrarConsumoDeRepuestoComando>(ordenes, reloj)
{
    protected override Task AplicarAsync(OrdenDeTrabajo orden, RegistrarConsumoDeRepuestoComando c, CancellationToken cancellationToken)
    {
        orden.RegistrarConsumoDeRepuesto(
            c.ConsumoId, c.Referencia, c.Cantidad, c.RequiereSerie, c.SerieRetirada, c.SerieInstalada,
            c.HoraDeCorte is { } horas ? new HoraDeCorte(horas) : null, Ahora);
        return Task.CompletedTask;
    }
}
