namespace Intervenciones.Domain;

public sealed class EstadoEnEspera : EstadoDeLaOrden
{
    public override string Nombre => "EnEspera";

    public override EstadoDeLaOrden AlRegistrarTarea() => EnEjecucion;

    public override EstadoDeLaOrden AlRegistrarConsumo() => EnEjecucion;
}
