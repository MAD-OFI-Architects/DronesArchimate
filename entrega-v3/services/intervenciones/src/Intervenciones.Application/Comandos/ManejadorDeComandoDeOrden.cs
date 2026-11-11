using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Tiempo;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public interface IComandoDeOrden : IComando<Unidad>
{
    Guid OrdenId { get; }
}

/// <summary>Caso de uso común: carga la orden, ejecuta un método del agregado y la guarda.
/// Los eventos salen a la bandeja cuando el pipeline confirma la unidad de trabajo.</summary>
public abstract class ManejadorDeComandoDeOrden<TComando>(IOrdenDeTrabajoRepository ordenes, IClock reloj)
    : IManejadorDeComando<TComando, Unidad> where TComando : IComandoDeOrden
{
    protected DateTimeOffset Ahora => reloj.Now;

    public async Task<Unidad> ManejarAsync(TComando comando, CancellationToken cancellationToken)
    {
        var orden = await ordenes.ObtenerAsync(comando.OrdenId, cancellationToken)
            ?? throw new RecursoNoEncontradoException("la orden de trabajo", comando.OrdenId);

        await AplicarAsync(orden, comando, cancellationToken);
        await ordenes.GuardarAsync(orden, cancellationToken);
        return Unidad.Valor;
    }

    protected abstract Task AplicarAsync(OrdenDeTrabajo orden, TComando comando, CancellationToken cancellationToken);
}
