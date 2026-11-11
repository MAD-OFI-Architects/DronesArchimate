using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record VueloDePrueba
{
    public const int DuracionMinimaEnMinutos = 5;
    public const int DuracionMaximaEnMinutos = 10;

    public VueloDePrueba(DateTimeOffset realizadoEn, int duracionEnMinutos, bool aprobado, string observaciones)
    {
        RealizadoEn = Guard.NoPorDefecto(realizadoEn, nameof(realizadoEn));
        DuracionEnMinutos = Guard.EnRango(duracionEnMinutos, DuracionMinimaEnMinutos, DuracionMaximaEnMinutos, nameof(duracionEnMinutos));
        Aprobado = aprobado;
        Observaciones = Guard.Texto(observaciones, nameof(observaciones), 500);
    }

    public DateTimeOffset RealizadoEn { get; }

    public int DuracionEnMinutos { get; }

    public bool Aprobado { get; }

    public string Observaciones { get; }
}
