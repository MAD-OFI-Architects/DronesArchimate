using System.Reflection;
using BuildingBlocks.Application.Correlacion;
using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.EventosDeDominio;
using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Validacion;
using Microsoft.Extensions.DependencyInjection;

namespace BuildingBlocks.Application.DependencyInjection;

public static class ServiceCollectionExtensions
{
    /// <summary>Registra mediador, pipeline (Registro → Validación → Transacción) y descubre por convención los
    /// manejadores, validadores, observadores, traductores y consumidores del ensamblado.</summary>
    public static IServiceCollection AgregarBloquesDeAplicacion(this IServiceCollection services, Assembly ensamblado)
    {
        services.AddScoped<IMediador, Mediador>();
        services.AddScoped<IContextoDeCorrelacion, ContextoDeCorrelacion>();
        services.AddScoped<IDespachadorDeEventosDeDominio, DespachadorDeEventosDeDominio>();

        services.AddScoped(typeof(IComportamientoDePipeline<,>), typeof(RegistroComportamiento<,>));
        services.AddScoped(typeof(IComportamientoDePipeline<,>), typeof(ValidacionComportamiento<,>));
        services.AddScoped(typeof(IComportamientoDePipeline<,>), typeof(TransaccionComportamiento<,>));

        var tiposConcretos = ensamblado.GetTypes().Where(t => t is { IsClass: true, IsAbstract: false, IsGenericTypeDefinition: false });
        foreach (var tipo in tiposConcretos)
        {
            RegistrarInterfacesGenericas(services, tipo, typeof(IManejadorDeSolicitud<,>));
            RegistrarInterfacesGenericas(services, tipo, typeof(IValidador<>));
            RegistrarInterfacesGenericas(services, tipo, typeof(IManejadorDeEventoDeIntegracion<>));
            RegistrarInterfaz<IManejadorDeEventoDeDominio>(services, tipo);
            RegistrarInterfaz<ITraductorDeEventoDeDominio>(services, tipo);
        }

        return services;
    }

    private static void RegistrarInterfacesGenericas(IServiceCollection services, Type tipo, Type definicion)
    {
        foreach (var contrato in tipo.GetInterfaces().Where(i => i.IsGenericType && i.GetGenericTypeDefinition() == definicion))
            services.AddScoped(contrato, tipo);
    }

    private static void RegistrarInterfaz<TContrato>(IServiceCollection services, Type tipo)
    {
        if (typeof(TContrato).IsAssignableFrom(tipo))
            services.AddScoped(typeof(TContrato), tipo);
    }
}
