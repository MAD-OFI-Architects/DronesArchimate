namespace Intervenciones.Domain;

public sealed class EstadoEnEjecucion : EstadoDeLaOrden
{
    public override string Nombre => "EnEjecucion";

    public override EstadoDeLaOrden AlRegistrarTarea() => this;

    public override EstadoDeLaOrden AlRegistrarConsumo() => this;

    public override EstadoDeLaOrden AlRegistrarVueloDePrueba() => Ejecutada;

    public override EstadoDeLaOrden AlLiberar() => Liberada;

    public override EstadoDeLaOrden AlPonerEnEspera() => EnEspera;
}
