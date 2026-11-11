using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Comandos;

public sealed class PonerOrdenEnEsperaValidador : ValidadorBase<PonerOrdenEnEsperaComando>
{
    protected override void DefinirReglas(PonerOrdenEnEsperaComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.OrdenId, nameof(c.OrdenId))
        .Requerido(c.Motivo, nameof(c.Motivo));
}
