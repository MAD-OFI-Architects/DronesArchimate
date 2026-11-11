using System.Text.Json;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Validacion;
using BuildingBlocks.Infrastructure.Mensajeria;
using BuildingBlocks.Infrastructure.Serializacion;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;

namespace BuildingBlocks.Api.Endpoints;

/// <summary>POST /events/{topic}: el bus entrega el sobre; responde 2xx si procesó o si ya lo había procesado.</summary>
public sealed class EventosEntrantesEndpoints : IModuloDeEndpoints
{
    public void Mapear(IEndpointRouteBuilder rutas) => rutas.MapPost("/events/{topic}", RecibirAsync);

    private static async Task<IResult> RecibirAsync(
        string topic, HttpRequest peticion, ProcesadorDeMensajeEntrante procesador, CancellationToken cancellationToken)
    {
        var sobre = await LeerSobreAsync(peticion, cancellationToken);
        Validar(sobre, topic);

        return await procesador.ProcesarAsync(sobre, cancellationToken) switch
        {
            ResultadoDeProcesamiento.Procesado => Results.Ok(new { estado = "procesado" }),
            ResultadoDeProcesamiento.Duplicado => Results.Ok(new { estado = "duplicado" }),
            _ => throw new RecursoNoEncontradoException("el tópico", topic)
        };
    }

    private static async Task<SobreDeEvento> LeerSobreAsync(HttpRequest peticion, CancellationToken cancellationToken)
    {
        try
        {
            return await JsonSerializer.DeserializeAsync<SobreDeEvento>(peticion.Body, SerializadorJson.Opciones, cancellationToken)
                ?? throw SobreInvalido("El cuerpo es obligatorio.");
        }
        catch (JsonException)
        {
            throw SobreInvalido("El cuerpo no es un sobre de evento válido.");
        }
    }

    private static void Validar(SobreDeEvento sobre, string topico)
    {
        var errores = new ColectorDeErrores()
            .NoVacio(sobre.EventId, "eventId")
            .Cumple(sobre.Topic == topico, "topic", "El tópico del sobre no coincide con la ruta.")
            .Cumple(sobre.Payload.ValueKind != JsonValueKind.Undefined, "payload", "El campo 'payload' es obligatorio.")
            .Errores;

        if (errores.Count > 0)
            throw new ValidacionException(errores);
    }

    private static ValidacionException SobreInvalido(string mensaje) =>
        new([new ErrorDeValidacion("cuerpo", mensaje)]);
}
