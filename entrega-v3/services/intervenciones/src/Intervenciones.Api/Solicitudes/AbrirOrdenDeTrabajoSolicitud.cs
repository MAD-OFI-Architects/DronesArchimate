using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record AbrirOrdenDeTrabajoSolicitud(
    Guid ParadaId,
    bool ParadaProgramada,
    string DronId,
    string Tipo,
    bool EsTrabajoMayor)
{
    public AbrirOrdenDeTrabajoComando AComando() => new(ParadaId, ParadaProgramada, DronId, Tipo, EsTrabajoMayor);
}
