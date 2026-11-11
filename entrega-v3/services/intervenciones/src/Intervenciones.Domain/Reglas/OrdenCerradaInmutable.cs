using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class OrdenCerradaInmutable(EstadoDeLaOrden estado) : IBusinessRule
{
    public bool IsBroken() => estado.EsTerminal;

    public string Message => "ORDEN_CERRADA_INMUTABLE: una orden de trabajo cerrada no admite cambios.";
}
