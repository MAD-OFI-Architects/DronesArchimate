using BuildingBlocks.Application.Validacion;

namespace BuildingBlocks.Application.Excepciones;

/// <summary>Solicitud mal formada (HTTP 400) con los errores por campo.</summary>
public sealed class ValidacionException(IReadOnlyList<ErrorDeValidacion> errores)
    : Exception(string.Join(" ", errores.Select(e => e.Mensaje)))
{
    public IReadOnlyList<ErrorDeValidacion> Errores { get; } = errores;
}
