namespace Intervenciones.Contracts;

/// <summary>Evento publicado por Repuestos del Taller que este contexto consume.</summary>
public sealed record FaltanteDetectadoV1(Guid ParadaId, string Referencia, int CantidadFaltante);
