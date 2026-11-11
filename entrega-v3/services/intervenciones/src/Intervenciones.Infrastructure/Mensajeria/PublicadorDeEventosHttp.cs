using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Infrastructure.Mensajeria;

namespace Intervenciones.Infrastructure.Mensajeria;

/// <summary>Publica los eventos de integración en el bus con POST {BUS_URL}/publish.</summary>
public sealed class PublicadorDeEventosHttp(HttpClient http) : IBusDeEventos
{
    private readonly BusDeEventosHttp _bus = new(http);

    public Task PublicarAsync(SobreDeEvento sobre, CancellationToken cancellationToken = default) =>
        _bus.PublicarAsync(sobre, cancellationToken);
}
