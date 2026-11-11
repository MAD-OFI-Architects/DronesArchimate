namespace BuildingBlocks.Application.Validacion;

/// <summary>Acumula todos los errores de forma de una solicitud para responderlos juntos.</summary>
public sealed class ColectorDeErrores
{
    private readonly List<ErrorDeValidacion> _errores = [];

    public IReadOnlyList<ErrorDeValidacion> Errores => _errores;

    public ColectorDeErrores Requerido(string? valor, string campo) =>
        Cumple(!string.IsNullOrWhiteSpace(valor), campo, $"El campo '{campo}' es obligatorio.");

    public ColectorDeErrores NoVacio(Guid valor, string campo) =>
        Cumple(valor != Guid.Empty, campo, $"El campo '{campo}' no puede estar vacío.");

    public ColectorDeErrores Positivo(decimal valor, string campo) =>
        Cumple(valor > 0, campo, $"El campo '{campo}' debe ser mayor que cero.");

    public ColectorDeErrores EnRango(decimal valor, decimal minimo, decimal maximo, string campo) =>
        Cumple(valor >= minimo && valor <= maximo, campo, $"El campo '{campo}' debe estar entre {minimo} y {maximo}.");

    public ColectorDeErrores EnumValido<TEnum>(string? valor, string campo) where TEnum : struct, Enum =>
        Cumple(
            Enum.TryParse<TEnum>(valor, ignoreCase: true, out var resultado) && Enum.IsDefined(resultado),
            campo,
            $"El campo '{campo}' no tiene un valor válido.");

    public ColectorDeErrores Cumple(bool condicion, string campo, string mensaje)
    {
        if (!condicion)
            _errores.Add(new ErrorDeValidacion(campo, mensaje));

        return this;
    }
}
