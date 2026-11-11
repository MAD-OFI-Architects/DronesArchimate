using Microsoft.Extensions.DependencyInjection;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Domain;
using BuildingBlocks.Infrastructure.Outbox;
using BuildingBlocks.Infrastructure.Persistencia;
using BuildingBlocks.Tests.Soporte;
using System.Text.Json;

namespace BuildingBlocks.Tests.Infraestructura;

public class BandejaDeSalidaTests
{
    private static MensajeDeSalida Mensaje() => new()
    {
        Id = Guid.NewGuid(), Topico = "t.v1", PayloadJson = "{}", OcurrioEn = Escenario.Inicio, CorrelacionId = Guid.NewGuid()
    };

    [Fact]
    public async Task Guarda_el_documento_y_el_mensaje_en_una_sola_operacion()
    {
        var almacen = new AlmacenDeDocumentosEnMemoria();
        var mensaje = Mensaje();

        await new BandejaDeSalida(almacen).GuardarAsync(
            new LoteDeEscritura([new EscrituraDeDocumento("c", "1", "{}", 0)], [mensaje], []));

        Assert.Equal(1, (await almacen.ObtenerAsync("c", "1"))!.Version);
        Assert.Equal(mensaje.Id, Assert.Single(almacen.MensajesDeSalida).Id);
    }

    [Fact]
    public async Task Si_un_documento_esta_desactualizado_no_se_guarda_nada()
    {
        var almacen = new AlmacenDeDocumentosEnMemoria();
        var bandeja = new BandejaDeSalida(almacen);
        await bandeja.GuardarAsync(new LoteDeEscritura([new EscrituraDeDocumento("c", "viejo", "{}", 0)], [], []));

        var lote = new LoteDeEscritura(
            [new EscrituraDeDocumento("c", "nuevo", "{}", 0), new EscrituraDeDocumento("c", "viejo", "{\"x\":1}", 0)],
            [Mensaje()],
            [Guid.NewGuid()]);

        await Assert.ThrowsAsync<ConflictoDeConcurrenciaException>(() => bandeja.GuardarAsync(lote));

        Assert.Null(await almacen.ObtenerAsync("c", "nuevo"));
        Assert.Equal("{}", (await almacen.ObtenerAsync("c", "viejo"))!.Json);
        Assert.Empty(almacen.MensajesDeSalida);
        Assert.False(await almacen.ExisteMensajeEntranteAsync(lote.MensajesEntrantes[0]));
    }

    [Fact]
    public async Task Un_comando_exitoso_deja_el_agregado_y_su_evento_traducido_juntos()
    {
        await using var escenario = new Escenario();
        var id = Guid.NewGuid();

        await escenario.EnviarAsync(new AbrirCuentaComando(id, "Ana"));

        var documento = await escenario.Almacen.ObtenerAsync("cuentas", id.ToString());
        var mensaje = Assert.Single(escenario.Almacen.MensajesDeSalida);
        Assert.Equal(CuentaAbiertaTraductor.NombreDelTopico, mensaje.Topico);
        using var payload = JsonDocument.Parse(mensaje.PayloadJson);
        Assert.Equal(id, payload.RootElement.GetProperty("cuentaId").GetGuid());
        Assert.Equal(mensaje.Id, payload.RootElement.GetProperty("eventoId").GetGuid());
        Assert.NotNull(documento);
        Assert.Equal(1, documento.Version);
    }

    [Fact]
    public async Task Un_comando_que_viola_una_regla_no_deja_ni_cambios_ni_eventos()
    {
        await using var escenario = new Escenario();
        var id = Guid.NewGuid();
        await escenario.EnviarAsync(new AbrirCuentaComando(id, "Ana"));
        var antes = (await escenario.Almacen.ObtenerAsync("cuentas", id.ToString()))!;

        await Assert.ThrowsAsync<BusinessRuleViolationException>(() => escenario.EnviarAsync(new DepositarComando(id, 0)));

        Assert.Equal(antes, await escenario.Almacen.ObtenerAsync("cuentas", id.ToString()));
        Assert.Single(escenario.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Un_cambio_sin_traductor_se_guarda_pero_no_se_publica()
    {
        await using var escenario = new Escenario();
        var id = Guid.NewGuid();
        await escenario.EnviarAsync(new AbrirCuentaComando(id, "Ana"));

        await escenario.EnviarAsync(new DepositarComando(id, 40));

        Assert.Equal(40, (await escenario.EnviarAsync(new ObtenerCuentaConsulta(id))).Saldo);
        Assert.Equal(2, (await escenario.Almacen.ObtenerAsync("cuentas", id.ToString()))!.Version);
        Assert.Single(escenario.Almacen.MensajesDeSalida);
    }

    [Fact]
    public async Task Dos_actualizaciones_simultaneas_del_mismo_agregado_provocan_conflicto()
    {
        await using var escenario = new Escenario();
        var id = Guid.NewGuid();
        await escenario.EnviarAsync(new AbrirCuentaComando(id, "Ana"));
        await using var a = escenario.Proveedor.CreateAsyncScope();
        await using var b = escenario.Proveedor.CreateAsyncScope();
        var repoA = a.ServiceProvider.GetRequiredService<IRepositorioDeCuentas>();
        var repoB = b.ServiceProvider.GetRequiredService<IRepositorioDeCuentas>();
        (await repoA.ObtenerAsync(id, default))!.Depositar(1, escenario.Reloj.Now);
        (await repoB.ObtenerAsync(id, default))!.Depositar(2, escenario.Reloj.Now);

        await a.ServiceProvider.GetRequiredService<IUnidadDeTrabajo>().ConfirmarAsync();

        await Assert.ThrowsAsync<ConflictoDeConcurrenciaException>(
            () => b.ServiceProvider.GetRequiredService<IUnidadDeTrabajo>().ConfirmarAsync());
    }
}
