namespace BuildingBlocks.Infrastructure.DependencyInjection;

/// <summary>Identidad y entorno del servicio; las variables las fija el orquestador en el compose.</summary>
public sealed record OpcionesDeMicroservicio
{
    public required string Nombre { get; init; }
    public int Puerto { get; init; } = 5000;
    public string? BusUrl { get; init; }
    public string? SimulatorsUrl { get; init; }
    public string? CifradoClave { get; init; }
    public string? MongoUrl { get; init; }

    public static OpcionesDeMicroservicio DesdeEntorno(string nombre, Func<string, string?>? leer = null)
    {
        leer ??= Environment.GetEnvironmentVariable;
        return new OpcionesDeMicroservicio
        {
            Nombre = nombre,
            Puerto = int.TryParse(leer("PORT"), out var puerto) ? puerto : 5000,
            BusUrl = leer("BUS_URL"),
            SimulatorsUrl = leer("SIMULATORS_URL"),
            CifradoClave = leer("CIFRADO_CLAVE"),
            MongoUrl = leer("MONGO_URL")
        };
    }
}
