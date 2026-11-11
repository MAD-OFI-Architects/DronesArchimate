namespace Intervenciones.Application.Comandos;

public sealed record CerrarOrdenDeTrabajoComando(Guid OrdenId) : IComandoDeOrden;
