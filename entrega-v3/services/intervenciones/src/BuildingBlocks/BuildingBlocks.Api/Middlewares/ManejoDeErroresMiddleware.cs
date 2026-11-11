using System.Text.Json;
using BuildingBlocks.Api.Errores;
using BuildingBlocks.Application.Correlacion;
using BuildingBlocks.Infrastructure.Serializacion;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Api.Middlewares;

/// <summary>Captura las excepciones y responde application/problem+json con la correlación de la petición.</summary>
public sealed class ManejoDeErroresMiddleware(RequestDelegate siguiente, ILogger<ManejoDeErroresMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext contexto)
    {
        try
        {
            await siguiente(contexto);
        }
        catch (OperationCanceledException) when (contexto.RequestAborted.IsCancellationRequested)
        {
            throw;
        }
        catch (Exception ex) when (!contexto.Response.HasStarted)
        {
            var problema = TraductorDeExcepcionesAProblema.Traducir(ex);
            if (problema.Status >= 500)
                logger.LogError(ex, "Error no controlado en {Ruta}", contexto.Request.Path);

            problema.Instance = contexto.Request.Path;
            problema.Extensions["correlationId"] = contexto.RequestServices.GetService<IContextoDeCorrelacion>()?.Id;

            contexto.Response.Clear();
            contexto.Response.StatusCode = problema.Status!.Value;
            contexto.Response.ContentType = TraductorDeExcepcionesAProblema.TipoDeContenido;
            await JsonSerializer.SerializeAsync(contexto.Response.Body, problema, SerializadorJson.Opciones, contexto.RequestAborted);
        }
    }
}
