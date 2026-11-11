using BuildingBlocks.Application.Validacion;

namespace Intervenciones.Application.Comandos;

public sealed class RegistrarConsumoDeRepuestoValidador : ValidadorBase<RegistrarConsumoDeRepuestoComando>
{
    protected override void DefinirReglas(RegistrarConsumoDeRepuestoComando c, ColectorDeErrores errores) => errores
        .NoVacio(c.OrdenId, nameof(c.OrdenId))
        .NoVacio(c.ConsumoId, nameof(c.ConsumoId))
        .Requerido(c.Referencia, nameof(c.Referencia))
        .Positivo(c.Cantidad, nameof(c.Cantidad))
        .Cumple(c.HoraDeCorte is null or >= 0, nameof(c.HoraDeCorte), "El campo 'HoraDeCorte' no puede ser negativo.");
}
