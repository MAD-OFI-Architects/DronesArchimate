using BuildingBlocks.Api.Endpoints;
using BuildingBlocks.Api.Middlewares;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.DependencyInjection;

namespace BuildingBlocks.Api.DependencyInjection;

public static class ApiExtensions
{
    public static IServiceCollection AgregarBloquesDeApi(this IServiceCollection services) =>
        services.AgregarModuloDeEndpoints<EventosEntrantesEndpoints>();

    public static IServiceCollection AgregarModuloDeEndpoints<TModulo>(this IServiceCollection services)
        where TModulo : class, IModuloDeEndpoints =>
        services.AddSingleton<IModuloDeEndpoints, TModulo>();

    /// <summary>Cadena de middlewares: correlación → registro → errores.</summary>
    public static IApplicationBuilder UsarBloquesDeApi(this IApplicationBuilder app) => app
        .UseMiddleware<CorrelacionMiddleware>()
        .UseMiddleware<RegistroDeSolicitudesMiddleware>()
        .UseMiddleware<ManejoDeErroresMiddleware>();

    public static IEndpointRouteBuilder MapearModulosDeEndpoints(this IEndpointRouteBuilder rutas)
    {
        foreach (var modulo in rutas.ServiceProvider.GetServices<IModuloDeEndpoints>())
            modulo.Mapear(rutas);

        return rutas;
    }
}
