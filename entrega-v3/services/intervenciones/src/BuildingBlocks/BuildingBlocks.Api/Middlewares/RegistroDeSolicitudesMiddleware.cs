using System.Diagnostics;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Api.Middlewares;

public sealed class RegistroDeSolicitudesMiddleware(RequestDelegate siguiente, ILogger<RegistroDeSolicitudesMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext contexto)
    {
        var reloj = Stopwatch.StartNew();
        await siguiente(contexto);
        logger.LogInformation("{Metodo} {Ruta} → {Estado} en {Milisegundos} ms",
            contexto.Request.Method, contexto.Request.Path, contexto.Response.StatusCode, reloj.ElapsedMilliseconds);
    }
}
