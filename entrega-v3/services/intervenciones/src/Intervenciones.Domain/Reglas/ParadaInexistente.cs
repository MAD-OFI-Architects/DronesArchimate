using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class ParadaInexistente(bool paradaExiste) : IBusinessRule
{
    public bool IsBroken() => !paradaExiste;

    public string Message => "PARADA_INEXISTENTE: la parada programada de la orden no existe.";
}
