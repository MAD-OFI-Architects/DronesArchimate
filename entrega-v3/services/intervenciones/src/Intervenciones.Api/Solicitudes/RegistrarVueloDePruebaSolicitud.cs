using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record RegistrarVueloDePruebaSolicitud(
    DateTimeOffset RealizadoEn, int DuracionEnMinutos, bool Aprobado, string Observaciones) : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) =>
        new RegistrarVueloDePruebaComando(ordenId, RealizadoEn, DuracionEnMinutos, Aprobado, Observaciones);
}
