using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarHallazgoValidador : ValidadorBase<RegistrarHallazgoComando>
{
    protected override void DefinirReglas(RegistrarHallazgoComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.OrdenId, nameof(c.OrdenId))
        .Requerido(c.Descripcion, nameof(c.Descripcion));
}
