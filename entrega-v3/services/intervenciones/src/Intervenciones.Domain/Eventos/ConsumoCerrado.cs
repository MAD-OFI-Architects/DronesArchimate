namespace Intervenciones.Domain;

public sealed record ConsumoCerrado(string Referencia, int Cantidad, string? NumeroDeSerie, string? SerieRetirada, decimal? HoraDeCorte);
