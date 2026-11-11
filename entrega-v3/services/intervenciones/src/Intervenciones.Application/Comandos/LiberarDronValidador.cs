using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Comandos;

public sealed class LiberarDronValidador : ValidadorBase<LiberarDronComando>
{
    protected override void DefinirReglas(LiberarDronComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.OrdenId, nameof(c.OrdenId))
        .NoVacio(c.LiberacionId, nameof(c.LiberacionId))
        .Requerido(c.LiberadaPor, nameof(c.LiberadaPor));
}
