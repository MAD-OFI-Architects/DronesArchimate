using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record CerrarOrdenDeTrabajoSolicitud : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) => new CerrarOrdenDeTrabajoComando(ordenId);
}
