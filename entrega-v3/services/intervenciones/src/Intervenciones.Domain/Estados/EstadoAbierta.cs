namespace Intervenciones.Domain;

public sealed class EstadoAbierta : EstadoDeLaOrden
{
    public override string Nombre => "Abierta";

    public override EstadoDeLaOrden AlRegistrarTarea() => EnEjecucion;

    public override EstadoDeLaOrden AlRegistrarConsumo() => EnEjecucion;

    public override EstadoDeLaOrden AlPonerEnEspera() => EnEspera;
}
