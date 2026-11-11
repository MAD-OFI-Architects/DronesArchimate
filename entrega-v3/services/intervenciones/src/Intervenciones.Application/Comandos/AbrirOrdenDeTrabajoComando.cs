using BuildingBlocks.Application.Cqrs;

namespace Intervenciones.Application.Comandos;

/// <summary>Responde con el id de la orden (la existente si la parada ya tenía una).</summary>
public sealed record AbrirOrdenDeTrabajoComando(
    Guid ParadaId,
    bool ParadaProgramada,
    string DronId,
    string Tipo,
    bool EsTrabajoMayor) : IComando<Guid>;
