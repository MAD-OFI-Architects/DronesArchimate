using BuildingBlocks.Application.Cqrs;

namespace Intervenciones.Application.Consultas;

public sealed record ObtenerOrdenDeTrabajoConsulta(Guid OrdenId) : IConsulta<OrdenDeTrabajoDto>;
