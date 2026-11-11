namespace Intervenciones.Domain;

public sealed class EstadoCerrada : EstadoDeLaOrden
{
    public override string Nombre => "Cerrada";

    public override bool EsTerminal => true;
}
