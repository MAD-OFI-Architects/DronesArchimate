using BuildingBlocks.Application.Tiempo;
using BuildingBlocks.Domain;
using Intervenciones.Application.Puertos;
using Intervenciones.Application.Reglas;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class AsignarTecnicoManejador(
    IOrdenDeTrabajoRepository ordenes, IClock reloj, IConsultaDeHabilitacion habilitacion)
    : ManejadorDeComandoDeOrden<AsignarTecnicoComando>(ordenes, reloj)
{
    protected override async Task AplicarAsync(OrdenDeTrabajo orden, AsignarTecnicoComando comando, CancellationToken cancellationToken)
    {
        BusinessRules.Check(new TecnicoNoHabilitado(await habilitacion.EstaHabilitadoAsync(comando.Tecnico, cancellationToken)));
        orden.AsignarTecnico(comando.Tecnico, Ahora);
    }
}
