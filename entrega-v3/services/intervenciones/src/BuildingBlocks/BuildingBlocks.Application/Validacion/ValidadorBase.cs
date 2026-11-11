namespace BuildingBlocks.Application.Validacion;

public abstract class ValidadorBase<T> : IValidador<T>
{
    public IReadOnlyList<ErrorDeValidacion> Validar(T instancia)
    {
        var colector = new ColectorDeErrores();
        DefinirReglas(instancia, colector);
        return colector.Errores;
    }

    protected abstract void DefinirReglas(T instancia, ColectorDeErrores errores);
}
