using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Consultas;

public sealed class ObtenerOrdenDeTrabajoValidador : ValidadorBase<ObtenerOrdenDeTrabajoConsulta>
{
    protected override void DefinirReglas(ObtenerOrdenDeTrabajoConsulta c, ColectorDeErrores errores) =>
        errores.NoVacio(c.OrdenId, nameof(c.OrdenId));
}
