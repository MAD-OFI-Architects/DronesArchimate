namespace BuildingBlocks.Domain;

/// <summary>Validaciones reutilizables: los setters lanzan DomainException y los getters InvalidOperationException.</summary>
public static class Guard
{
    public static T NoNulo<T>(T? valor, string campo) where T : class =>
        valor ?? throw new DomainException($"El campo '{campo}' es obligatorio.");

    public static string Texto(string? valor, string campo, int longitudMaxima = 250)
    {
        if (string.IsNullOrWhiteSpace(valor))
            throw new DomainException($"El campo '{campo}' es obligatorio.");

        var limpio = valor.Trim();
        if (limpio.Length > longitudMaxima)
            throw new DomainException($"El campo '{campo}' no puede superar {longitudMaxima} caracteres.");

        return limpio;
    }

    public static Guid NoVacio(Guid valor, string campo) =>
        valor == Guid.Empty ? throw new DomainException($"El campo '{campo}' no puede estar vacío.") : valor;

    public static T NoPorDefecto<T>(T valor, string campo) where T : struct =>
        EqualityComparer<T>.Default.Equals(valor, default)
            ? throw new DomainException($"El campo '{campo}' es obligatorio.")
            : valor;

    public static int EnRango(int valor, int minimo, int maximo, string campo) =>
        valor < minimo || valor > maximo
            ? throw new DomainException($"El campo '{campo}' debe estar entre {minimo} y {maximo}.")
            : valor;

    public static decimal EnRango(decimal valor, decimal minimo, decimal maximo, string campo) =>
        valor < minimo || valor > maximo
            ? throw new DomainException($"El campo '{campo}' debe estar entre {minimo} y {maximo}.")
            : valor;

    public static int Positivo(int valor, string campo) =>
        valor <= 0 ? throw new DomainException($"El campo '{campo}' debe ser mayor que cero.") : valor;

    public static decimal Positivo(decimal valor, string campo) =>
        valor <= 0 ? throw new DomainException($"El campo '{campo}' debe ser mayor que cero.") : valor;

    public static decimal NoNegativo(decimal valor, string campo) =>
        valor < 0 ? throw new DomainException($"El campo '{campo}' no puede ser negativo.") : valor;

    public static TEnum Definido<TEnum>(TEnum valor, string campo) where TEnum : struct, Enum =>
        Enum.IsDefined(valor)
            ? valor
            : throw new DomainException($"El valor '{valor}' no es válido para '{campo}'.");

    public static T Inicializado<T>(T? valor, string campo) where T : class =>
        valor ?? throw new InvalidOperationException($"La propiedad '{campo}' no ha sido inicializada.");

    public static T Asignado<T>(T valor, string campo) where T : struct =>
        EqualityComparer<T>.Default.Equals(valor, default)
            ? throw new InvalidOperationException($"La propiedad '{campo}' no ha sido asignada.")
            : valor;
}
