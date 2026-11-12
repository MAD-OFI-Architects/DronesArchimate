using System.Text.Json;
using BuildingBlocks.Api.Errores;
using BuildingBlocks.Api.Middlewares;
using BuildingBlocks.Application.Correlacion;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Validacion;
using BuildingBlocks.Domain;
using BuildingBlocks.Tests.Soporte;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging.Abstractions;

namespace BuildingBlocks.Tests.Api;

public class ProblemDetailsTests
{
    [Fact]
    public void Cada_excepcion_se_traduce_a_su_estado_HTTP()
    {
        Assert.Equal(400, TraductorDeExcepcionesAProblema.Traducir(new ValidacionException([new("a", "mal")])).Status);
        Assert.Equal(400, TraductorDeExcepcionesAProblema.Traducir(new DomainException("dato")).Status);
        Assert.Equal(404, TraductorDeExcepcionesAProblema.Traducir(new RecursoNoEncontradoException("la orden", 1)).Status);
        Assert.Equal(409, TraductorDeExcepcionesAProblema.Traducir(new ConflictoDeConcurrenciaException("choque")).Status);
        var caida = TraductorDeExcepcionesAProblema.Traducir(new DependenciaNoDisponibleException("Habilitación", "no responde"));
        Assert.Equal(503, caida.Status);
        Assert.Equal("Habilitación", caida.Extensions["dependencia"]);
        Assert.Equal(422, TraductorDeExcepcionesAProblema.Traducir(new BusinessRuleViolationException(new DepositoDebeSerPositivo(0))).Status);
        Assert.Equal(500, TraductorDeExcepcionesAProblema.Traducir(new InvalidOperationException("secreto")).Status);
    }

    [Fact]
    public void La_regla_incumplida_viaja_en_el_campo_regla_y_no_se_confunde_con_400()
    {
        var problema = TraductorDeExcepcionesAProblema.Traducir(new BusinessRuleViolationException(new DepositoDebeSerPositivo(0)));

        Assert.Equal(nameof(DepositoDebeSerPositivo), problema.Extensions["regla"]);
        Assert.Equal("El depósito debe ser positivo.", problema.Detail);
    }

    [Fact]
    public void Un_error_inesperado_no_filtra_su_mensaje() =>
        Assert.DoesNotContain("secreto", TraductorDeExcepcionesAProblema.Traducir(new InvalidOperationException("secreto")).Detail);

    private static (DefaultHttpContext Contexto, MemoryStream Cuerpo) CrearContexto()
    {
        var servicios = new ServiceCollection().AddScoped<IContextoDeCorrelacion, ContextoDeCorrelacion>().BuildServiceProvider();
        var cuerpo = new MemoryStream();
        var contexto = new DefaultHttpContext { RequestServices = servicios.CreateScope().ServiceProvider };
        contexto.Response.Body = cuerpo;
        contexto.Request.Path = "/api/cuentas";
        return (contexto, cuerpo);
    }

    private static async Task<JsonElement> EjecutarAsync(Exception excepcion, DefaultHttpContext contexto, MemoryStream cuerpo)
    {
        var middleware = new ManejoDeErroresMiddleware(_ => throw excepcion, NullLogger<ManejoDeErroresMiddleware>.Instance);
        await middleware.InvokeAsync(contexto);
        cuerpo.Position = 0;
        return JsonDocument.Parse(cuerpo).RootElement.Clone();
    }

    [Fact]
    public async Task El_middleware_responde_application_problem_json_con_regla_y_correlacion()
    {
        var (contexto, cuerpo) = CrearContexto();
        var correlacion = Guid.NewGuid();
        contexto.RequestServices.GetRequiredService<IContextoDeCorrelacion>().Id = correlacion;

        var json = await EjecutarAsync(new BusinessRuleViolationException(new DepositoDebeSerPositivo(0)), contexto, cuerpo);

        Assert.Equal(422, contexto.Response.StatusCode);
        Assert.Equal("application/problem+json", contexto.Response.ContentType);
        Assert.Equal(422, json.GetProperty("status").GetInt32());
        Assert.Equal("Regla de negocio incumplida", json.GetProperty("title").GetString());
        Assert.Equal(nameof(DepositoDebeSerPositivo), json.GetProperty("regla").GetString());
        Assert.Equal("/api/cuentas", json.GetProperty("instance").GetString());
        Assert.Equal(correlacion, json.GetProperty("correlationId").GetGuid());
    }

    [Fact]
    public async Task El_middleware_incluye_los_errores_por_campo_en_las_validaciones()
    {
        var (contexto, cuerpo) = CrearContexto();

        var json = await EjecutarAsync(
            new ValidacionException([new ErrorDeValidacion("titular", "obligatorio")]), contexto, cuerpo);

        Assert.Equal(400, contexto.Response.StatusCode);
        var error = json.GetProperty("errores")[0];
        Assert.Equal("titular", error.GetProperty("campo").GetString());
        Assert.Equal("obligatorio", error.GetProperty("mensaje").GetString());
    }

    [Fact]
    public async Task La_correlacion_se_toma_del_encabezado_o_se_genera()
    {
        var (contexto, _) = CrearContexto();
        var recibido = Guid.NewGuid();
        contexto.Request.Headers["X-Correlation-Id"] = recibido.ToString();
        var middleware = new CorrelacionMiddleware(_ => Task.CompletedTask, NullLogger<CorrelacionMiddleware>.Instance);

        await middleware.InvokeAsync(contexto);

        Assert.Equal(recibido, contexto.RequestServices.GetRequiredService<IContextoDeCorrelacion>().Id);
        Assert.Equal(recibido.ToString(), contexto.Response.Headers["X-Correlation-Id"].ToString());

        var (otro, _) = CrearContexto();
        await middleware.InvokeAsync(otro);
        Assert.True(Guid.TryParse(otro.Response.Headers["X-Correlation-Id"], out var generado) && generado != Guid.Empty);
    }
}
