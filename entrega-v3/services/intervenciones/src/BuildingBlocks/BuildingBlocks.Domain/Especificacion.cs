namespace BuildingBlocks.Domain;

/// <summary>Condición de negocio reutilizable, combinable con Y, O y No.</summary>
public abstract class Especificacion<T>
{
    public abstract bool EsSatisfechaPor(T candidato);

    public Especificacion<T> Y(Especificacion<T> otra) => new EspecificacionY<T>(this, otra);

    public Especificacion<T> O(Especificacion<T> otra) => new EspecificacionO<T>(this, otra);

    public Especificacion<T> No() => new EspecificacionNo<T>(this);
}

internal sealed class EspecificacionY<T>(Especificacion<T> izquierda, Especificacion<T> derecha) : Especificacion<T>
{
    public override bool EsSatisfechaPor(T candidato) =>
        izquierda.EsSatisfechaPor(candidato) && derecha.EsSatisfechaPor(candidato);
}

internal sealed class EspecificacionO<T>(Especificacion<T> izquierda, Especificacion<T> derecha) : Especificacion<T>
{
    public override bool EsSatisfechaPor(T candidato) =>
        izquierda.EsSatisfechaPor(candidato) || derecha.EsSatisfechaPor(candidato);
}

internal sealed class EspecificacionNo<T>(Especificacion<T> interna) : Especificacion<T>
{
    public override bool EsSatisfechaPor(T candidato) => !interna.EsSatisfechaPor(candidato);
}
