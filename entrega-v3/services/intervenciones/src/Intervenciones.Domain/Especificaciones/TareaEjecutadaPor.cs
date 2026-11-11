using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class TareaEjecutadaPor(string persona) : Especificacion<TareaEjecutada>
{
    public override bool EsSatisfechaPor(TareaEjecutada candidato) =>
        string.Equals(candidato.EjecutadaPor, persona, StringComparison.OrdinalIgnoreCase);
}
