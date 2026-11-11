namespace Intervenciones.Domain;

public sealed class EstadoEjecutada : EstadoDeLaOrden
{
    public override string Nombre => "Ejecutada";

    public override EstadoDeLaOrden AlRegistrarVueloDePrueba() => this;

    public override EstadoDeLaOrden AlLiberar() => Liberada;
}
