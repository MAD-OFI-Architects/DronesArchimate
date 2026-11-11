using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record RegistrarEjecucionDeTareaSolicitud(
    Guid TareaId, string Descripcion, string Resultado, string EjecutadaPor, decimal Horas) : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) =>
        new RegistrarEjecucionDeTareaComando(ordenId, TareaId, Descripcion, Resultado, EjecutadaPor, Horas);
}
