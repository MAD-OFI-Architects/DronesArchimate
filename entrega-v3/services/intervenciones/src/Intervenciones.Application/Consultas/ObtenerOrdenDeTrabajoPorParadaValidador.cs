using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Consultas;

public sealed class ObtenerOrdenDeTrabajoPorParadaValidador : ValidadorBase<ObtenerOrdenDeTrabajoPorParadaConsulta>
{
    protected override void DefinirReglas(ObtenerOrdenDeTrabajoPorParadaConsulta c, ColectorDeErrores errores) =>
        errores.NoVacio(c.ParadaId, nameof(c.ParadaId));
}
