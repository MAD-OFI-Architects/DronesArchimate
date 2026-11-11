using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class ConsumoRequiereSerie : Especificacion<ConsumoDeRepuesto>
{
    public override bool EsSatisfechaPor(ConsumoDeRepuesto candidato) => candidato.RequiereSerie;
}
