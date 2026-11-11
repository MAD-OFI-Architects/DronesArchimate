using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.DependencyInjection;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Validacion;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace BuildingBlocks.Tests.Aplicacion;

public sealed class Bitacora
{
    public List<string> Pasos { get; } = [];
}

public sealed record PingComando(string Texto, bool Falla = false) : IComando<string>;

public sealed record PingConsulta(string Texto) : IConsulta<string>;

public sealed class PingValidador(Bitacora bitacora) : ValidadorBase<PingComando>
{
    protected override void DefinirReglas(PingComando instancia, ColectorDeErrores errores)
    {
        bitacora.Pasos.Add("validar");
        errores.Requerido(instancia.Texto, nameof(instancia.Texto));
    }
}

public sealed class PingManejador(Bitacora bitacora) : IManejadorDeComando<PingComando, string>
{
    public Task<string> ManejarAsync(PingComando solicitud, CancellationToken cancellationToken)
    {
        bitacora.Pasos.Add("manejar");
        return solicitud.Falla ? throw new InvalidOperationException("boom") : Task.FromResult($"pong {solicitud.Texto}");
    }
}

public sealed class PingConsultaManejador(Bitacora bitacora) : IManejadorDeConsulta<PingConsulta, string>
{
    public Task<string> ManejarAsync(PingConsulta solicitud, CancellationToken cancellationToken)
    {
        bitacora.Pasos.Add("consultar");
        return Task.FromResult($"pong {solicitud.Texto}");
    }
}

public sealed class UnidadDeTrabajoEspia(Bitacora bitacora) : IUnidadDeTrabajo
{
    public Task ConfirmarAsync(CancellationToken cancellationToken = default)
    {
        bitacora.Pasos.Add("confirmar");
        return Task.CompletedTask;
    }
}

public sealed class LoggerEspia<T>(Bitacora bitacora) : ILogger<T>
{
    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

    public bool IsEnabled(LogLevel logLevel) => true;

    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
    {
        if (typeof(T).Name.StartsWith("RegistroComportamiento", StringComparison.Ordinal))
            bitacora.Pasos.Add("registro: " + formatter(state, exception));
    }
}

public class PipelineTests
{
    private static (ServiceProvider Proveedor, Bitacora Bitacora) Crear()
    {
        var servicios = new ServiceCollection();
        servicios.AddSingleton<Bitacora>();
        servicios.AddScoped<IUnidadDeTrabajo, UnidadDeTrabajoEspia>();
        servicios.AddSingleton(typeof(ILogger<>), typeof(LoggerEspia<>));
        servicios.AgregarBloquesDeAplicacion(typeof(PipelineTests).Assembly);
        var proveedor = servicios.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true });
        return (proveedor, proveedor.GetRequiredService<Bitacora>());
    }

    [Fact]
    public void Los_eslabones_se_registran_en_el_orden_Registro_Validacion_Transaccion()
    {
        var servicios = new ServiceCollection().AgregarBloquesDeAplicacion(typeof(PipelineTests).Assembly);

        var orden = servicios
            .Where(d => d.ServiceType == typeof(IComportamientoDePipeline<,>))
            .Select(d => d.ImplementationType)
            .ToArray();

        Assert.Equal(
            [typeof(RegistroComportamiento<,>), typeof(ValidacionComportamiento<,>), typeof(TransaccionComportamiento<,>)],
            orden);
    }

    [Fact]
    public async Task Un_comando_pasa_por_registro_validacion_manejador_y_confirma_la_transaccion()
    {
        var (proveedor, bitacora) = Crear();
        await using var alcance = proveedor.CreateAsyncScope();

        var respuesta = await alcance.ServiceProvider.GetRequiredService<IMediador>().EnviarAsync(new PingComando("a"));

        Assert.Equal("pong a", respuesta);
        Assert.Equal(["validar", "manejar", "confirmar"], bitacora.Pasos.Take(3));
        Assert.StartsWith("registro: Solicitud PingComando completada", bitacora.Pasos[3]);
        Assert.Equal(4, bitacora.Pasos.Count);
    }

    [Fact]
    public async Task Una_consulta_nunca_abre_transaccion()
    {
        var (proveedor, bitacora) = Crear();
        await using var alcance = proveedor.CreateAsyncScope();

        await alcance.ServiceProvider.GetRequiredService<IMediador>().EnviarAsync(new PingConsulta("a"));

        Assert.DoesNotContain("confirmar", bitacora.Pasos);
        Assert.Contains("consultar", bitacora.Pasos);
    }

    [Fact]
    public async Task Un_comando_invalido_no_llega_al_manejador_ni_confirma_y_se_registra_como_rechazado()
    {
        var (proveedor, bitacora) = Crear();
        await using var alcance = proveedor.CreateAsyncScope();

        var ex = await Assert.ThrowsAsync<ValidacionException>(
            () => alcance.ServiceProvider.GetRequiredService<IMediador>().EnviarAsync(new PingComando(" ")));

        Assert.Equal("Texto", Assert.Single(ex.Errores).Campo);
        Assert.DoesNotContain("manejar", bitacora.Pasos);
        Assert.DoesNotContain("confirmar", bitacora.Pasos);
        Assert.StartsWith("registro: Solicitud PingComando rechazada", bitacora.Pasos[^1]);
    }

    [Fact]
    public async Task Si_el_manejador_falla_no_se_confirma_la_transaccion()
    {
        var (proveedor, bitacora) = Crear();
        await using var alcance = proveedor.CreateAsyncScope();

        await Assert.ThrowsAsync<InvalidOperationException>(
            () => alcance.ServiceProvider.GetRequiredService<IMediador>().EnviarAsync(new PingComando("a", Falla: true)));

        Assert.DoesNotContain("confirmar", bitacora.Pasos);
    }
}
