using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class LiberaElMismoQueEjecuto(bool esTrabajoMayor, string liberadaPor, IEnumerable<TareaEjecutada> tareas) : IBusinessRule
{
    public bool IsBroken() => esTrabajoMayor && tareas.Any(new TareaEjecutadaPor(liberadaPor).EsSatisfechaPor);

    public string Message => "LIBERA_EL_MISMO_QUE_EJECUTO: en trabajos mayores la liberación la firma quien no ejecutó.";
}
