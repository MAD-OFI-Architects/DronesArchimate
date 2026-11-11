using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record AsignarTecnicoSolicitud(string Tecnico) : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) => new AsignarTecnicoComando(ordenId, Tecnico);
}
