using BuildingBlocks.Application.Validacion;
using Intervenciones.Domain;

namespace Intervenciones.Application.Comandos;

public sealed class AbrirOrdenDeTrabajoValidador : ValidadorBase<AbrirOrdenDeTrabajoComando>
{
    protected override void DefinirReglas(AbrirOrdenDeTrabajoComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.ParadaId, nameof(c.ParadaId))
        .Requerido(c.DronId, nameof(c.DronId))
        .EnumValido<TipoDeOrden>(c.Tipo, nameof(c.Tipo));
}
