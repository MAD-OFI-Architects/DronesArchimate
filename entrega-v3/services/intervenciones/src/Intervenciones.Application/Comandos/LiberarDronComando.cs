namespace Intervenciones.Application.Comandos;

public sealed record LiberarDronComando(Guid OrdenId, Guid LiberacionId, string LiberadaPor) : IComandoDeOrden;
