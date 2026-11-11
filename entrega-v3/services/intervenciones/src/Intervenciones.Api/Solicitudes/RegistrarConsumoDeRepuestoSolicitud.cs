using Intervenciones.Application.Comandos;

namespace Intervenciones.Api.Solicitudes;

public sealed record RegistrarConsumoDeRepuestoSolicitud(
    Guid ConsumoId,
    string Referencia,
    int Cantidad,
    bool RequiereSerie,
    string? SerieRetirada,
    string? SerieInstalada,
    decimal? HoraDeCorte) : ISolicitudDeOrden
{
    public IComandoDeOrden AComando(Guid ordenId) => new RegistrarConsumoDeRepuestoComando(
        ordenId, ConsumoId, Referencia, Cantidad, RequiereSerie, SerieRetirada, SerieInstalada, HoraDeCorte);
}
