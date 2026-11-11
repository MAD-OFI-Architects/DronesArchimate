using BuildingBlocks.Application.Cqrs;

namespace Intervenciones.Application.Consultas;

public sealed record ObtenerOrdenDeTrabajoPorParadaConsulta(Guid ParadaId) : IConsulta<OrdenDeTrabajoDto>;
