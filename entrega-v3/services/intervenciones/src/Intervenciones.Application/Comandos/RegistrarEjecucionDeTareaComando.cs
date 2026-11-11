namespace Intervenciones.Application.Comandos;

public sealed record RegistrarEjecucionDeTareaComando(
    Guid OrdenId, Guid TareaId, string Descripcion, string Resultado, string EjecutadaPor, decimal Horas) : IComandoDeOrden;
