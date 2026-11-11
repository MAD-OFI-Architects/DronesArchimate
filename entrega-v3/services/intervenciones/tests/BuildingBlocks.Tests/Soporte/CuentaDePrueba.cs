using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Serializacion;
using BuildingBlocks.Application.Tiempo;
using BuildingBlocks.Application.Validacion;
using BuildingBlocks.Domain;
using BuildingBlocks.Infrastructure.Persistencia;

namespace BuildingBlocks.Tests.Soporte;

public sealed record CuentaAbierta(DateTimeOffset OcurrioEn, Guid CuentaId, string Titular) : DomainEvent(OcurrioEn);

public sealed record DepositoRealizado(DateTimeOffset OcurrioEn, Guid CuentaId, int Monto) : DomainEvent(OcurrioEn);

public sealed record CuentaMemento(Guid Id, string Titular, int Saldo);

public sealed class DepositoDebeSerPositivo(int monto) : IBusinessRule
{
    public bool IsBroken() => monto <= 0;

    public string Message => "El depósito debe ser positivo.";
}

public sealed class Cuenta : AggregateRoot<Guid>, IOriginador<Cuenta, CuentaMemento>
{
    private string? _titular;

    private Cuenta(Guid id) : base(id)
    {
    }

    public string Titular
    {
        get => Guard.Inicializado(_titular, nameof(Titular));
        private set => _titular = Guard.Texto(value, "titular", 50);
    }

    public int Saldo { get; private set; }

    public static Cuenta Abrir(Guid id, string titular, DateTimeOffset ahora)
    {
        var cuenta = new Cuenta(id) { Titular = titular };
        cuenta.Raise(new CuentaAbierta(ahora, id, cuenta.Titular));
        return cuenta;
    }

    public void Depositar(int monto, DateTimeOffset ahora)
    {
        CheckRule(new DepositoDebeSerPositivo(monto));
        Saldo += monto;
        Raise(new DepositoRealizado(ahora, Id, monto));
    }

    public CuentaMemento CrearMemento() => new(Id, Titular, Saldo);

    public static Cuenta RestaurarDesde(CuentaMemento memento) =>
        new(memento.Id) { Titular = memento.Titular, Saldo = Guard.EnRango(memento.Saldo, 0, int.MaxValue, "saldo") };
}

public interface IRepositorioDeCuentas
{
    Task<Cuenta?> ObtenerAsync(Guid id, CancellationToken cancellationToken);

    Task AgregarAsync(Cuenta cuenta, CancellationToken cancellationToken);
}

public sealed class RepositorioDeCuentas(
    IAlmacenDeDocumentos almacen, UnidadDeTrabajoDocumental unidadDeTrabajo, ISerializadorJson serializador)
    : RepositorioDocumentalBase<Cuenta, Guid, CuentaMemento>(almacen, unidadDeTrabajo, serializador), IRepositorioDeCuentas
{
    protected override string Coleccion => "cuentas";

    protected override string ClaveDe(Guid id) => id.ToString();

    public Task<Cuenta?> ObtenerAsync(Guid id, CancellationToken cancellationToken) => ObtenerPorIdAsync(id, cancellationToken);
}

public sealed record CuentaAbiertaV1(Guid EventoId, Guid CuentaId, string Titular);

public sealed class CuentaAbiertaTraductor : TraductorDeEventoDeDominio<CuentaAbierta>
{
    public const string NombreDelTopico = "pruebas.cuenta-abierta.v1";

    protected override string Topico => NombreDelTopico;

    protected override object CrearContrato(CuentaAbierta evento) => new CuentaAbiertaV1(evento.EventoId, evento.CuentaId, evento.Titular);
}

public sealed record AbrirCuentaComando(Guid Id, string Titular) : IComando<Guid>;

public sealed class AbrirCuentaValidador : ValidadorBase<AbrirCuentaComando>
{
    protected override void DefinirReglas(AbrirCuentaComando instancia, ColectorDeErrores errores) =>
        errores.NoVacio(instancia.Id, nameof(instancia.Id)).Requerido(instancia.Titular, nameof(instancia.Titular));
}

public sealed class AbrirCuentaManejador(IRepositorioDeCuentas cuentas, IClock reloj) : IManejadorDeComando<AbrirCuentaComando, Guid>
{
    public async Task<Guid> ManejarAsync(AbrirCuentaComando comando, CancellationToken cancellationToken)
    {
        await cuentas.AgregarAsync(Cuenta.Abrir(comando.Id, comando.Titular, reloj.Now), cancellationToken);
        return comando.Id;
    }
}

public sealed record DepositarComando(Guid Id, int Monto) : IComando<Unidad>;

public sealed class DepositarManejador(IRepositorioDeCuentas cuentas, IClock reloj) : IManejadorDeComando<DepositarComando, Unidad>
{
    public async Task<Unidad> ManejarAsync(DepositarComando comando, CancellationToken cancellationToken)
    {
        var cuenta = await cuentas.ObtenerAsync(comando.Id, cancellationToken)
            ?? throw new RecursoNoEncontradoException("la cuenta", comando.Id);
        cuenta.Depositar(comando.Monto, reloj.Now);
        return Unidad.Valor;
    }
}

public sealed record ObtenerCuentaConsulta(Guid Id) : IConsulta<CuentaMemento>;

public sealed class ObtenerCuentaManejador(IRepositorioDeCuentas cuentas) : IManejadorDeConsulta<ObtenerCuentaConsulta, CuentaMemento>
{
    public async Task<CuentaMemento> ManejarAsync(ObtenerCuentaConsulta consulta, CancellationToken cancellationToken) =>
        (await cuentas.ObtenerAsync(consulta.Id, cancellationToken))?.CrearMemento()
        ?? throw new RecursoNoEncontradoException("la cuenta", consulta.Id);
}

public sealed record CuentaExternaV1(Guid CuentaId, string Titular);

public sealed class CuentaExternaConsumidor(IMediador mediador) : IManejadorDeEventoDeIntegracion<CuentaExternaV1>
{
    public const string NombreDelTopico = "externo.cuenta-creada.v1";

    public async Task ManejarAsync(CuentaExternaV1 mensaje, ContextoDeMensaje contexto, CancellationToken cancellationToken) =>
        await mediador.EnviarAsync(new AbrirCuentaComando(mensaje.CuentaId, mensaje.Titular), cancellationToken);
}
