using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record LiberarDronSolicitud(Guid LiberacionId, string LiberadaPor) : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) => new LiberarDronComando(ordenId, LiberacionId, LiberadaPor);
}
