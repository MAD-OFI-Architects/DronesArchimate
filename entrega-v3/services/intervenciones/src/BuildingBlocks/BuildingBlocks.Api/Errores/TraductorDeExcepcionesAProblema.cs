using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Domain;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace BuildingBlocks.Api.Errores;

/// <summary>Traduce cada excepción, venga de la capa que venga, a ProblemDetails (RFC 9457).
/// El orden importa: BusinessRuleViolationException hereda de DomainException y se evalúa antes.</summary>
public static class TraductorDeExcepcionesAProblema
{
    public const string TipoDeContenido = "application/problem+json";

    public static ProblemDetails Traducir(Exception excepcion) => excepcion switch
    {
        ValidacionException ex => Problema(StatusCodes.Status400BadRequest, "Solicitud inválida", ex.Message,
            ("errores", ex.Errores.Select(e => new { campo = e.Campo, mensaje = e.Mensaje }).ToList())),
        RecursoNoEncontradoException ex => Problema(StatusCodes.Status404NotFound, "Recurso no encontrado", ex.Message),
        BusinessRuleViolationException ex => Problema(StatusCodes.Status422UnprocessableEntity, "Regla de negocio incumplida",
            ex.Message, ("regla", ex.BrokenRule.GetType().Name), ("codigo", CodigoDelContrato(ex.Message))),
        DomainException ex => Problema(StatusCodes.Status400BadRequest, "Dato inválido para el dominio", ex.Message),
        DependenciaNoDisponibleException ex => Problema(StatusCodes.Status503ServiceUnavailable, "Dependencia no disponible",
            ex.Message, ("dependencia", ex.Dependencia)),
        ConflictoDeConcurrenciaException ex => Problema(StatusCodes.Status409Conflict, "Conflicto de concurrencia", ex.Message),
        _ => Problema(StatusCodes.Status500InternalServerError, "Error interno", "Ocurrió un error inesperado.")
    };

    /// <summary>Las reglas anteponen el código del contrato al mensaje ("CODIGO: detalle"); sin código devuelve vacío.</summary>
    private static string CodigoDelContrato(string mensaje)
    {
        var corte = mensaje.IndexOf(':');
        var candidato = corte > 0 ? mensaje[..corte] : string.Empty;
        return candidato.Length > 0 && candidato.All(c => c is >= 'A' and <= 'Z' or '_') ? candidato : string.Empty;
    }

    private static ProblemDetails Problema(int estado, string titulo, string detalle, params (string Clave, object Valor)[] extensiones)
    {
        var problema = new ProblemDetails { Type = "about:blank", Status = estado, Title = titulo, Detail = detalle };
        foreach (var (clave, valor) in extensiones)
            problema.Extensions[clave] = valor;

        return problema;
    }
}
