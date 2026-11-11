using BuildingBlocks.Domain;

namespace Intervenciones.Application.Reglas;

public sealed class TecnicoNoHabilitado(bool estaHabilitado) : IBusinessRule
{
    public bool IsBroken() => !estaHabilitado;

    public string Message => "TECNICO_NO_HABILITADO: el técnico no tiene habilitación vigente.";
}
