using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Validacion;
using BuildingBlocks.Tests.Soporte;
using Microsoft.Extensions.DependencyInjection;

namespace BuildingBlocks.Tests.Aplicacion;

public sealed record SinManejadorComando : IComando<int>;

public class MediadorTests
{
    [Fact]
    public async Task Entrega_la_solicitud_a_su_manejador_y_devuelve_la_respuesta()
    {
        await using var escenario = new Escenario();
        var id = Guid.NewGuid();

        Assert.Equal(id, await escenario.EnviarAsync(new AbrirCuentaComando(id, "Ana")));
        Assert.Equal("Ana", (await escenario.EnviarAsync(new ObtenerCuentaConsulta(id))).Titular);
    }

    [Fact]
    public async Task Sin_manejador_registrado_falla_con_un_mensaje_claro()
    {
        await using var escenario = new Escenario();

        var ex = await Assert.ThrowsAsync<InvalidOperationException>(() => escenario.EnviarAsync(new SinManejadorComando()));

        Assert.Contains(nameof(SinManejadorComando), ex.Message);
    }

    [Fact]
    public async Task Rechaza_solicitudes_nulas()
    {
        await using var escenario = new Escenario();
        await using var alcance = escenario.Proveedor.CreateAsyncScope();

        await Assert.ThrowsAsync<ArgumentNullException>(
            () => alcance.ServiceProvider.GetRequiredService<IMediador>().EnviarAsync<int>(null!));
    }

    [Fact]
    public void El_colector_acumula_todos_los_errores()
    {
        var errores = new ColectorDeErrores()
            .Requerido(null, "a")
            .NoVacio(Guid.Empty, "b")
            .Positivo(0, "c")
            .EnRango(9, 1, 5, "d")
            .EnumValido<DayOfWeek>("Nunca", "e")
            .EnumValido<DayOfWeek>("monday", "f")
            .Errores;

        Assert.Equal(["a", "b", "c", "d", "e"], errores.Select(e => e.Campo));
    }
}
