namespace Intervenciones.Application.Comandos;

public sealed record AsignarTecnicoComando(Guid OrdenId, string Tecnico) : IComandoDeOrden;
