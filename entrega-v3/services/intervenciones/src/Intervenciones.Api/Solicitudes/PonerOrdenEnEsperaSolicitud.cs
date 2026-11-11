using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record PonerOrdenEnEsperaSolicitud(string Motivo) : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) => new PonerOrdenEnEsperaComando(ordenId, Motivo);
}
