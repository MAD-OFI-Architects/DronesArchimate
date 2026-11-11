using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Comandos;

public sealed class CerrarOrdenDeTrabajoValidador : ValidadorBase<CerrarOrdenDeTrabajoComando>
{
    protected override void DefinirReglas(CerrarOrdenDeTrabajoComando c, ColectorDeErrores errores) =>
        errores.NoVacio(c.OrdenId, nameof(c.OrdenId));
}
