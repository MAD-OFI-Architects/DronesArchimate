using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarEjecucionDeTareaValidador : ValidadorBase<RegistrarEjecucionDeTareaComando>
{
    protected override void DefinirReglas(RegistrarEjecucionDeTareaComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.OrdenId, nameof(c.OrdenId))
        .NoVacio(c.TareaId, nameof(c.TareaId))
        .Requerido(c.Descripcion, nameof(c.Descripcion))
        .Requerido(c.Resultado, nameof(c.Resultado))
        .Requerido(c.EjecutadaPor, nameof(c.EjecutadaPor))
        .Positivo(c.Horas, nameof(c.Horas));
}
