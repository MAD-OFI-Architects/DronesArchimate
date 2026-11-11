namespace Intervenciones.Application.Comandos;

public sealed record RegistrarHallazgoComando(Guid OrdenId, string Descripcion) : IComandoDeOrden;
