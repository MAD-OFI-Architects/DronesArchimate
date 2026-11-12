namespace Intervenciones.Contracts;

public sealed record OrdenDeTrabajoCerradaV1(
    Guid OrdenId,
    Guid ParadaId,
    string DronId,
    DateTimeOffset CerradaEn,
    decimal HorasHombre,
    IReadOnlyList<ConsumoCerradoV1> Consumos);

/// <summary>Instalación y retiro con su hora de corte (Intervenciones → Flota y Componentes): si el consumo cambió una pieza,
/// <c>NumeroSerie</c> es la instalada, <c>SerieRetirada</c> la que salió y <c>HoraDeCorte</c> el momento del cambio.</summary>
public sealed record ConsumoCerradoV1(string Referencia, int Cantidad, string? NumeroSerie, string? SerieRetirada, decimal? HoraDeCorte);
