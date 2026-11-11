using BuildingBlocks.Application.Validacion;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarVueloDePruebaValidador : ValidadorBase<RegistrarVueloDePruebaComando>
{
    protected override void DefinirReglas(RegistrarVueloDePruebaComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.OrdenId, nameof(c.OrdenId))
        .Cumple(c.RealizadoEn != default, nameof(c.RealizadoEn), "El campo 'RealizadoEn' es obligatorio.")
        .EnRango(c.DuracionEnMinutos, VueloDePrueba.DuracionMinimaEnMinutos, VueloDePrueba.DuracionMaximaEnMinutos, nameof(c.DuracionEnMinutos))
        .Requerido(c.Observaciones, nameof(c.Observaciones));
}
