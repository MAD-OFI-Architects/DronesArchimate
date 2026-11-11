using BuildingBlocks.Application.Integracion;
using BuildingBlocks.Application.Persistencia;
using BuildingBlocks.Application.Serializacion;
using BuildingBlocks.Application.Tiempo;
using BuildingBlocks.Infrastructure.Mensajeria;
using BuildingBlocks.Infrastructure.Outbox;
using BuildingBlocks.Infrastructure.Persistencia;
using BuildingBlocks.Infrastructure.Serializacion;
using BuildingBlocks.Infrastructure.Tiempo;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using MongoDB.Driver;

namespace BuildingBlocks.Infrastructure.DependencyInjection;

public static class ServiceCollectionExtensions
{
    /// <summary>Registra la plataforma genérica: serializador, reloj, almacén (MongoDB, o memoria sin MONGO_URL),
    /// unidad de trabajo, outbox, bus HTTP y consumo idempotente.</summary>
    public static IServiceCollection AgregarBloquesDeInfraestructura(
        this IServiceCollection services, OpcionesDeMicroservicio opciones)
    {
        services.TryAddSingleton<ISerializadorJson, SerializadorJson>();
        services.TryAddSingleton<IClock, RelojDelSistema>();

        if (string.IsNullOrWhiteSpace(opciones.MongoUrl))
        {
            services.AddSingleton<AlmacenDeDocumentosEnMemoria>();
            services.AddSingleton<IAlmacenDeDocumentos>(sp => sp.GetRequiredService<AlmacenDeDocumentosEnMemoria>());
            services.AddSingleton<IAlmacenDeMensajeria>(sp => sp.GetRequiredService<AlmacenDeDocumentosEnMemoria>());
        }
        else
        {
            services.AddSingleton<IMongoClient>(_ => new MongoClient(opciones.MongoUrl));
            services.AddSingleton(sp => sp.GetRequiredService<IMongoClient>().GetDatabase(opciones.Nombre));
            services.AddSingleton<AlmacenDeDocumentosMongo>();
            services.AddSingleton<IAlmacenDeDocumentos>(sp => sp.GetRequiredService<AlmacenDeDocumentosMongo>());
            services.AddSingleton<IAlmacenDeMensajeria>(sp => sp.GetRequiredService<AlmacenDeDocumentosMongo>());
        }

        services.AddScoped<BandejaDeSalida>();
        services.AddScoped<UnidadDeTrabajoDocumental>();
        services.AddScoped<IUnidadDeTrabajo>(sp => sp.GetRequiredService<UnidadDeTrabajoDocumental>());

        if (string.IsNullOrWhiteSpace(opciones.BusUrl))
            services.AddSingleton<IBusDeEventos, BusDeEventosEnMemoria>();
        else
            services.AddHttpClient<IBusDeEventos, BusDeEventosHttp>(http =>
                http.BaseAddress = new Uri(opciones.BusUrl.TrimEnd('/') + "/"));

        services.TryAddSingleton(new OpcionesDeDespacho());
        services.AddScoped<DespachadorDeBandejaDeSalida>();
        services.AddHostedService<ServicioDeDespachoDeBandeja>();
        services.AddSingleton<ProcesadorDeMensajeEntrante>();
        return services;
    }

    /// <summary>Suscribe un consumidor idempotente a un tópico del bus.</summary>
    public static IServiceCollection AgregarConsumidor<TMensaje, TManejador>(this IServiceCollection services, string topico)
        where TManejador : class, IManejadorDeEventoDeIntegracion<TMensaje>
    {
        services.AddScoped<IManejadorDeEventoDeIntegracion<TMensaje>, TManejador>();
        services.AddSingleton(ConsumidorRegistrado.Para<TMensaje>(topico));
        return services;
    }
}
