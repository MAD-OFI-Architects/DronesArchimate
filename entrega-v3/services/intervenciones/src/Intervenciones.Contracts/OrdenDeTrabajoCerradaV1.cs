namespace Intervenciones.Contracts;

public sealed record OrdenDeTrabajoCerradaV1(
    Guid OrdenId,
    Guid ParadaId,
    string DronId,
    DateTimeOffset CerradaEn,
    decimal HorasHombre,
    IReadOnlyList<ConsumoCerradoV1> Consumos);

public sealed record ConsumoCerradoV1(string Referencia, int Cantidad, string? NumeroSerie);
