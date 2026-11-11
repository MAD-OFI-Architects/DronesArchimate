using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class ConsumoConSerieInstalada : Especificacion<ConsumoDeRepuesto>
{
    public override bool EsSatisfechaPor(ConsumoDeRepuesto candidato) => candidato.SerieInstalada is not null;
}
