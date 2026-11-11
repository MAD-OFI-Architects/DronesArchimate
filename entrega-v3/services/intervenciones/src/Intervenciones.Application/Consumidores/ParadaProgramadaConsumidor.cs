using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Integracion;
using Intervenciones.Application.Comandos;
using Intervenciones.Contracts;
using Intervenciones.Domain;

namespace Intervenciones.Application.Consumidores;

/// <summary>Parada programada → Abrir orden de trabajo. Idempotente: una parada abre una sola orden.</summary>
public sealed class ParadaProgramadaConsumidor(IMediador mediador) : IManejadorDeEventoDeIntegracion<ParadaProgramadaV1>
{
    public async Task ManejarAsync(ParadaProgramadaV1 mensaje, ContextoDeMensaje contexto, CancellationToken cancellationToken) =>
        await mediador.EnviarAsync(
            new AbrirOrdenDeTrabajoComando(
                mensaje.ParadaId, ParadaProgramada: true, mensaje.DronId, nameof(TipoDeOrden.Preventiva), EsTrabajoMayor: false),
            cancellationToken);
}
