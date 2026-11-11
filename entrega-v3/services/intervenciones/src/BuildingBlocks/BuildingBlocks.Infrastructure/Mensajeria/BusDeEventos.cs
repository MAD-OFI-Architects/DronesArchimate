using System.Text;
using System.Text.Json;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Infrastructure.Serializacion;

namespace BuildingBlocks.Infrastructure.Mensajeria;

/// <summary>Publica el sobre con POST {BUS_URL}/publish. El cuerpo viaja con Content-Length (no fragmentado)
/// porque el bus lee exactamente esa cantidad de bytes.</summary>
public sealed class BusDeEventosHttp(HttpClient http) : IBusDeEventos
{
    public async Task PublicarAsync(SobreDeEvento sobre, CancellationToken cancellationToken = default)
    {
        try
        {
            using var cuerpo = new StringContent(
                JsonSerializer.Serialize(sobre, SerializadorJson.Opciones), Encoding.UTF8, "application/json");
            using var respuesta = await http.PostAsync("publish", cuerpo, cancellationToken);
            if (!respuesta.IsSuccessStatusCode)
                throw new FalloDePublicacionException(
                    $"El bus rechazó '{sobre.Topic}' con estado {(int)respuesta.StatusCode}.");
        }
        catch (HttpRequestException ex)
        {
            throw new FalloDePublicacionException($"No se pudo contactar al bus para '{sobre.Topic}'.", ex);
        }
    }
}

/// <summary>Bus en memoria para pruebas: conserva lo publicado.</summary>
public sealed class BusDeEventosEnMemoria : IBusDeEventos
{
    private readonly List<SobreDeEvento> _publicados = [];

    public IReadOnlyList<SobreDeEvento> Publicados
    {
        get
        {
            lock (_publicados)
                return _publicados.ToList();
        }
    }

    public Task PublicarAsync(SobreDeEvento sobre, CancellationToken cancellationToken = default)
    {
        lock (_publicados)
            _publicados.Add(sobre);
        return Task.CompletedTask;
    }
}
