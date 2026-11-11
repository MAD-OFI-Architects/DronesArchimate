namespace Intervenciones.Application.Puertos;

/// <summary>Capa anticorrupción hacia Habilitación de Personal: solo expone lo que este contexto necesita saber.</summary>
public interface IConsultaDeHabilitacion
{
    Task<bool> EstaHabilitadoAsync(string tecnico, CancellationToken cancellationToken = default);
}
