namespace BuildingBlocks.Application.Validacion;

public sealed record ErrorDeValidacion(string Campo, string Mensaje);

public interface IValidador<in T>
{
    IReadOnlyList<ErrorDeValidacion> Validar(T instancia);
}
