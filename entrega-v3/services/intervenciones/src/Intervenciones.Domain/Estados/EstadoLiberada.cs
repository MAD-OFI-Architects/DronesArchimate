namespace Intervenciones.Domain;

public sealed class EstadoLiberada : EstadoDeLaOrden
{
    public override string Nombre => "Liberada";

    public override EstadoDeLaOrden AlCerrar() => Cerrada;
}
