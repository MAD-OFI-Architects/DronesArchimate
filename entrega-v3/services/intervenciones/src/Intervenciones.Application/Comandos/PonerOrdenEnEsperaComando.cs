namespace Intervenciones.Application.Comandos;

public sealed record PonerOrdenEnEsperaComando(Guid OrdenId, string Motivo) : IComandoDeOrden;
