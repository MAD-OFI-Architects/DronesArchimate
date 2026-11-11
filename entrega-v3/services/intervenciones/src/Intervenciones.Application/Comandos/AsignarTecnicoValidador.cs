using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Comandos;

public sealed class AsignarTecnicoValidador : ValidadorBase<AsignarTecnicoComando>
{
    protected override void DefinirReglas(AsignarTecnicoComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.OrdenId, nameof(c.OrdenId))
        .Requerido(c.Tecnico, nameof(c.Tecnico));
}
