using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class ConsumoDeRepuesto : Entity<Guid>
{
    public ConsumoDeRepuesto(
        Guid id, string referencia, int cantidad, bool requiereSerie,
        string? serieRetirada, string? serieInstalada, HoraDeCorte? horaDeCorte)
        : base(Guard.NoVacio(id, nameof(id)))
    {
        Referencia = Guard.Texto(referencia, nameof(referencia), 100);
        Cantidad = Guard.Positivo(cantidad, nameof(cantidad));
        RequiereSerie = requiereSerie;
        SerieRetirada = Limpiar(serieRetirada);
        SerieInstalada = Limpiar(serieInstalada);
        HoraDeCorte = horaDeCorte;
    }

    public string Referencia { get; }

    public int Cantidad { get; }

    public bool RequiereSerie { get; }

    public string? SerieRetirada { get; }

    public string? SerieInstalada { get; }

    public HoraDeCorte? HoraDeCorte { get; }

    private static string? Limpiar(string? serie) =>
        string.IsNullOrWhiteSpace(serie) ? null : Guard.Texto(serie, nameof(serie), 100);
}
