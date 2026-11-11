using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record HorasHombre
{
    public HorasHombre(decimal valor) => Valor = Guard.Positivo(valor, nameof(valor));

    public decimal Valor { get; }

    public HorasHombre Sumar(HorasHombre otras) => new(Valor + otras.Valor);
}
