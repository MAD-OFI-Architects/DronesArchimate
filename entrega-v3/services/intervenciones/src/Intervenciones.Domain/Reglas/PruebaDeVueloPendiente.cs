using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class PruebaDeVueloPendiente(bool esTrabajoMayor, VueloDePrueba? vuelo) : IBusinessRule
{
    public bool IsBroken() => esTrabajoMayor && vuelo is not { Aprobado: true };

    public string Message => "PRUEBA_DE_VUELO_PENDIENTE: en trabajos mayores la liberación exige un vuelo de prueba aprobado.";
}
