using BuildingBlocks.Application.Correlacion;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Api.Middlewares;

/// <summary>Toma o genera el X-Correlation-Id de la petición y lo devuelve en la respuesta.</summary>
public sealed class CorrelacionMiddleware(RequestDelegate siguiente, ILogger<CorrelacionMiddleware> logger)
{
    public const string Encabezado = "X-Correlation-Id";

    public async Task InvokeAsync(HttpContext contexto)
    {
        var id = Guid.TryParse(contexto.Request.Headers[Encabezado].FirstOrDefault(), out var recibido) && recibido != Guid.Empty
            ? recibido
            : Guid.NewGuid();

        contexto.RequestServices.GetRequiredService<IContextoDeCorrelacion>().Id = id;
        contexto.Response.Headers[Encabezado] = id.ToString();

        using (logger.BeginScope(new Dictionary<string, object> { ["CorrelationId"] = id }))
            await siguiente(contexto);
    }
}
