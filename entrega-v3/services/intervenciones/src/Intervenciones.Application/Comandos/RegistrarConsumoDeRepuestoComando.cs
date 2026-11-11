namespace Intervenciones.Application.Comandos;

public sealed record RegistrarConsumoDeRepuestoComando(
    Guid OrdenId,
    Guid ConsumoId,
    string Referencia,
    int Cantidad,
    bool RequiereSerie,
    string? SerieRetirada,
    string? SerieInstalada,
    decimal? HoraDeCorte) : IComandoDeOrden;
