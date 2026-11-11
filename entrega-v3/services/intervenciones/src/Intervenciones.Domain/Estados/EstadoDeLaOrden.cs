using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

/// <summary>Patrón State: cada estado decide a qué estado pasa la orden o rechaza la acción.</summary>
public abstract class EstadoDeLaOrden : IEquatable<EstadoDeLaOrden>
{
    public static readonly EstadoDeLaOrden Abierta = new EstadoAbierta();
    public static readonly EstadoDeLaOrden EnEspera = new EstadoEnEspera();
    public static readonly EstadoDeLaOrden EnEjecucion = new EstadoEnEjecucion();
    public static readonly EstadoDeLaOrden Ejecutada = new EstadoEjecutada();
    public static readonly EstadoDeLaOrden Liberada = new EstadoLiberada();
    public static readonly EstadoDeLaOrden Cerrada = new EstadoCerrada();

    private static readonly EstadoDeLaOrden[] Todos = [Abierta, EnEspera, EnEjecucion, Ejecutada, Liberada, Cerrada];

    public abstract string Nombre { get; }

    public virtual bool EsTerminal => false;

    public static EstadoDeLaOrden Desde(string nombre) =>
        Todos.FirstOrDefault(e => e.Nombre == nombre)
        ?? throw new DomainException($"El estado de la orden '{nombre}' no es válido.");

    public virtual EstadoDeLaOrden AlAsignarTecnico() => this;

    public virtual EstadoDeLaOrden AlRegistrarTarea() => Rechazar("registrar una tarea");

    public virtual EstadoDeLaOrden AlRegistrarConsumo() => Rechazar("registrar un consumo de repuesto");

    public virtual EstadoDeLaOrden AlRegistrarHallazgo() => this;

    public virtual EstadoDeLaOrden AlRegistrarVueloDePrueba() => Rechazar("registrar un vuelo de prueba");

    public virtual EstadoDeLaOrden AlLiberar() => Rechazar("liberar el dron");

    public virtual EstadoDeLaOrden AlCerrar() => Rechazar("cerrar la orden");

    public virtual EstadoDeLaOrden AlPonerEnEspera() => Rechazar("poner la orden en espera");

    protected EstadoDeLaOrden Rechazar(string accion) =>
        throw new DomainException($"No se puede {accion} con la orden en estado '{Nombre}'.");

    public bool Equals(EstadoDeLaOrden? otro) => otro is not null && Nombre == otro.Nombre;

    public override bool Equals(object? obj) => Equals(obj as EstadoDeLaOrden);

    public override int GetHashCode() => Nombre.GetHashCode();

    public override string ToString() => Nombre;
}
