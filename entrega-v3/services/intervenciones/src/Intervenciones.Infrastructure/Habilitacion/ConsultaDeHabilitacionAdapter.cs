using System.Net.Http.Json;
using System.Text.Json.Serialization;
using BuildingBlocks.Application.Excepciones;
using Intervenciones.Application.Puertos;

namespace Intervenciones.Infrastructure.Habilitacion;

public sealed class HabilitacionNoDisponibleException(string mensaje, Exception? interna = null)
    : DependenciaNoDisponibleException("Habilitación de Personal", mensaje, interna);

/// <summary>Capa anticorrupción hacia Habilitación de Personal: llama a su API y traduce la respuesta externa
/// a un sí/no; el dominio nunca ve el formato del otro contexto.</summary>
public sealed class ConsultaDeHabilitacionAdapter(HttpClient http) : IConsultaDeHabilitacion
{
    public const string Ruta = "api/habilitacion-de-personal/consulta-de-habilitacion";

    public async Task<bool> EstaHabilitadoAsync(string tecnico, CancellationToken cancellationToken = default)
    {
        try
        {
            using var respuesta = await http.PostAsJsonAsync(Ruta, new ConsultaExterna(tecnico), cancellationToken);
            respuesta.EnsureSuccessStatusCode();
            var cuerpo = await respuesta.Content.ReadFromJsonAsync<RespuestaExterna>(cancellationToken);
            return cuerpo?.Habilitado ?? throw new HabilitacionNoDisponibleException("Respuesta inválida de Habilitación de Personal.");
        }
        catch (Exception ex) when (!cancellationToken.IsCancellationRequested
                                   && ex is HttpRequestException or TaskCanceledException or System.Text.Json.JsonException)
        {
            throw new HabilitacionNoDisponibleException("No se pudo consultar Habilitación de Personal.", ex);
        }
    }

    private sealed record ConsultaExterna(string Tecnico);

    private sealed record RespuestaExterna([property: JsonPropertyName("habilitado")] bool? Habilitado);
}
