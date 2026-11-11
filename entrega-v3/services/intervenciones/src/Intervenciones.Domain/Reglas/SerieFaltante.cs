using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class SerieFaltante(ConsumoDeRepuesto consumo) : IBusinessRule
{
    private static readonly Especificacion<ConsumoDeRepuesto> SinSerie =
        new ConsumoRequiereSerie().Y(new ConsumoConSerieInstalada().No());

    public bool IsBroken() => SinSerie.EsSatisfechaPor(consumo);

    public string Message => $"SERIE_FALTANTE: el repuesto '{consumo.Referencia}' exige el número de serie instalado.";
}
