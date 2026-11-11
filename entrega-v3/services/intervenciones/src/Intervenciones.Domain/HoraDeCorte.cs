using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record HoraDeCorte
{
    public HoraDeCorte(decimal horas) => Horas = Guard.NoNegativo(horas, nameof(horas));

    public decimal Horas { get; }
}
