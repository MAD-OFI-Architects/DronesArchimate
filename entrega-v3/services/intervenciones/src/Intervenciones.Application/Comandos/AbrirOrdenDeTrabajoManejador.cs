using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class AbrirOrdenDeTrabajoManejador(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : IManejadorDeComando<AbrirOrdenDeTrabajoComando, Guid>
{
    public async Task<Guid> ManejarAsync(AbrirOrdenDeTrabajoComando comando, CancellationToken cancellationToken)
    {
        var existente = await ordenes.ObtenerPorParadaAsync(comando.ParadaId, cancellationToken);
        if (existente is not null)
            return existente.Id;

        var orden = OrdenDeTrabajo.Abrir(
            Guid.NewGuid(), comando.ParadaId, comando.ParadaProgramada, comando.DronId,
            Enum.Parse<TipoDeOrden>(comando.Tipo, ignoreCase: true), comando.EsTrabajoMayor, reloj.Now);

        await ordenes.GuardarAsync(orden, cancellationToken);
        return orden.Id;
    }
}
