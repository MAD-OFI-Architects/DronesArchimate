using Microsoft.AspNetCore.Routing;

namespace BuildingBlocks.Api.Endpoints;

/// <summary>Un microservicio declara sus rutas HTTP en una clase que implementa este contrato.</summary>
public interface IModuloDeEndpoints
{
    void Mapear(IEndpointRouteBuilder rutas);
}
