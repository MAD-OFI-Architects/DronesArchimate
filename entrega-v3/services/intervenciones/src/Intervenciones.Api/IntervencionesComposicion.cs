using BuildingBlocks.Api.DependencyInjection;
using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.DependencyInjection;
using BuildingBlocks.Application.EventosDeDominio;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Infrastructure.DependencyInjection;
using Intervenciones.Application.Comandos;
using Intervenciones.Application.Consultas;
using Intervenciones.Application.Consumidores;
using Intervenciones.Application.Puertos;
using Intervenciones.Contracts;
using Intervenciones.Domain;
using Intervenciones.Infrastructure.Cifrado;
using Intervenciones.Infrastructure.Habilitacion;
using Intervenciones.Infrastructure.Mensajeria;
using Intervenciones.Infrastructure.Persistencia;
using Microsoft.Extensions.DependencyInjection;

namespace Intervenciones.Api;

/// <summary>Raíz de composición: el único lugar que conoce todas las capas y las une.</summary>
public static class IntervencionesComposicion
{
    public static readonly TimeSpan TimeoutDeHabilitacion = TimeSpan.FromSeconds(5);

    public static IServiceCollection AgregarIntervenciones(this IServiceCollection services, OpcionesDeMicroservicio opciones)
    {
        services
            .AgregarBloquesDeAplicacion(typeof(AbrirOrdenDeTrabajoComando).Assembly)
            .AgregarBloquesDeInfraestructura(opciones)
            .AgregarBloquesDeApi()
            .AgregarModuloDeEndpoints<IntervencionesEndpoints>();

        services.AddSingleton<Cifrador>(_ => new CifradorAes(opciones.CifradoClave));
        services.AddScoped<IOrdenDeTrabajoRepository, RepositorioOrdenDeTrabajo>();
        AgregarCacheDeLectura(services);
        AgregarPublicadorDeEventos(services, opciones);
        AgregarHabilitacion(services, opciones);

        services.AgregarConsumidor<ParadaProgramadaV1, ParadaProgramadaConsumidor>(IntervencionesTopicos.ParadaProgramada);
        services.AgregarConsumidor<FaltanteDetectadoV1, FaltanteDetectadoConsumidor>(IntervencionesTopicos.FaltanteDetectado);
        return services;
    }

    /// <summary>La consulta lee a través del decorador con caché; los comandos siguen sobre el repositorio directo.</summary>
    private static void AgregarCacheDeLectura(IServiceCollection services)
    {
        services.AddSingleton(sp => new CacheDeOrdenes(sp.GetRequiredService<BuildingBlocks.Application.Tiempo.IClock>()));
        services.AddScoped<IManejadorDeEventoDeDominio, InvalidadorDeCacheDeOrdenes>();
        services.AddScoped<IManejadorDeSolicitud<ObtenerOrdenDeTrabajoConsulta, OrdenDeTrabajoDto>>(sp =>
            new ObtenerOrdenDeTrabajoManejador(new RepositorioCacheadoOrdenDeTrabajo(
                sp.GetRequiredService<IOrdenDeTrabajoRepository>(), sp.GetRequiredService<CacheDeOrdenes>())));
    }

    private static void AgregarPublicadorDeEventos(IServiceCollection services, OpcionesDeMicroservicio opciones)
    {
        if (!string.IsNullOrWhiteSpace(opciones.BusUrl))
            services.AddHttpClient<IBusDeEventos, PublicadorDeEventosHttp>(http =>
                http.BaseAddress = new Uri(opciones.BusUrl.TrimEnd('/') + "/"));
    }

    private static void AgregarHabilitacion(IServiceCollection services, OpcionesDeMicroservicio opciones)
    {
        if (string.IsNullOrWhiteSpace(opciones.SimulatorsUrl))
            throw new InvalidOperationException("Falta SIMULATORS_URL: Habilitación de Personal se consulta por HTTP.");

        services.AddHttpClient<IConsultaDeHabilitacion, ConsultaDeHabilitacionAdapter>(http =>
        {
            http.BaseAddress = new Uri(opciones.SimulatorsUrl.TrimEnd('/') + "/");
            http.Timeout = TimeoutDeHabilitacion;
        });
    }
}
