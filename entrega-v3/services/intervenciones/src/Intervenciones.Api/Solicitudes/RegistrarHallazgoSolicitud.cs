using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record RegistrarHallazgoSolicitud(string Descripcion) : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) => new RegistrarHallazgoComando(ordenId, Descripcion);
}
