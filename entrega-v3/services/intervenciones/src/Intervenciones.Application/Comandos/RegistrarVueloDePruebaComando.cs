namespace Intervenciones.Application.Comandos;

public sealed record RegistrarVueloDePruebaComando(
    Guid OrdenId, DateTimeOffset RealizadoEn, int DuracionEnMinutos, bool Aprobado, string Observaciones) : IComandoDeOrden;
