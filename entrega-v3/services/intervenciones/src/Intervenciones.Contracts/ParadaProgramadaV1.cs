namespace Intervenciones.Contracts;

/// <summary>Evento publicado por Plan de Mantenimiento que este contexto consume.</summary>
public sealed record ParadaProgramadaV1(
    Guid ParadaId,
    string DronId,
    DateTimeOffset FechaProgramada,
    IReadOnlyList<TareaProgramadaV1> Tareas);

public sealed record TareaProgramadaV1(string TareaId, string Descripcion, IReadOnlyList<RepuestoProgramadoV1> Repuestos);

public sealed record RepuestoProgramadoV1(string Referencia, int Cantidad);
