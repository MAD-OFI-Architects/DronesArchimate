using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

/// <summary>Cuerpo HTTP de un comando sobre una orden existente; el id de la orden viaja en la ruta.</summary>
public interface ISolicitudDeOrden
{
    IComandoDeOrden AComando(Guid ordenId);
}
