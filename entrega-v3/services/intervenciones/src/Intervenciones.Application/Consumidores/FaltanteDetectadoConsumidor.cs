using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Integracion;
using Intervenciones.Application.Comandos;
using Intervenciones.Contracts;
using Intervenciones.Domain;

namespace Intervenciones.Application.Consumidores;

/// <summary>Faltante detectado → Poner orden en espera. Idempotente: si la orden ya espera, no hace nada.</summary>
public sealed class FaltanteDetectadoConsumidor(IMediador mediador, IOrdenDeTrabajoRepository ordenes)
    : IManejadorDeEventoDeIntegracion<FaltanteDetectadoV1>
{
    public async Task ManejarAsync(FaltanteDetectadoV1 mensaje, ContextoDeMensaje contexto, CancellationToken cancellationToken)
    {
        var orden = await ordenes.ObtenerPorParadaAsync(mensaje.ParadaId, cancellationToken)
            ?? throw new RecursoNoEncontradoException("la orden de trabajo de la parada", mensaje.ParadaId);

        if (orden.Estado == EstadoDeLaOrden.EnEspera)
            return;

        await mediador.EnviarAsync(
            new PonerOrdenEnEsperaComando(orden.Id, $"Faltante de {mensaje.Referencia}: {mensaje.CantidadFaltante}"),
            cancellationToken);
    }
}
