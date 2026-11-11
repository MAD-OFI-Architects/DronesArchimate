using System.Text.Json;
using BuildingBlocks.Api.Endpoints;
using BuildingBlocks.Application.Cqrs;
using BuildingBlocks.Application.Validacion;
using BuildingBlocks.Application.Excepciones;
using BuildingBlocks.Infrastructure.Serializacion;
using Intervenciones.Api.Solicitudes;
using Intervenciones.Application.Consultas;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;

namespace Intervenciones.Api;

/// <summary>Rutas HTTP del contexto: crear y consultar la orden de trabajo y un POST por cada comando.
/// Los errores salen como application/problem+json por el middleware del kernel.</summary>
public sealed class IntervencionesEndpoints : IModuloDeEndpoints
{
    private const string Base = "/api/orden-de-trabajo";

    public void Mapear(IEndpointRouteBuilder rutas)
    {
        rutas.MapGet("/health", () => Results.Ok(new { estado = "ok" }));
        rutas.MapPost(Base, AbrirAsync);
        rutas.MapGet(Base + "/{id:guid}", ObtenerAsync);
        rutas.MapGet(Base + "/por-parada/{paradaId:guid}", ObtenerPorParadaAsync);

        MapearComando<AsignarTecnicoSolicitud>(rutas, "asignar-tecnico");
        MapearComando<RegistrarEjecucionDeTareaSolicitud>(rutas, "registrar-ejecucion-de-tarea");
        MapearComando<RegistrarConsumoDeRepuestoSolicitud>(rutas, "registrar-consumo-de-repuesto");
        MapearComando<RegistrarHallazgoSolicitud>(rutas, "registrar-hallazgo");
        MapearComando<RegistrarVueloDePruebaSolicitud>(rutas, "registrar-vuelo-de-prueba");
        MapearComando<LiberarDronSolicitud>(rutas, "liberar-dron");
        MapearComando<PonerOrdenEnEsperaSolicitud>(rutas, "poner-orden-en-espera");
        rutas.MapPost(Base + "/{id:guid}/cerrar-orden-de-trabajo", CerrarAsync);
    }

    private static void MapearComando<TSolicitud>(IEndpointRouteBuilder rutas, string segmento)
        where TSolicitud : class, ISolicitudDeOrden =>
        rutas.MapPost($"{Base}/{{id:guid}}/{segmento}", async (Guid id, HttpRequest peticion, IMediador mediador, CancellationToken ct) =>
        {
            var solicitud = await LeerCuerpoAsync<TSolicitud>(peticion, ct);
            await mediador.EnviarAsync(solicitud.AComando(id), ct);
            return Results.NoContent();
        });

    private static async Task<IResult> AbrirAsync(HttpRequest peticion, IMediador mediador, CancellationToken ct)
    {
        var solicitud = await LeerCuerpoAsync<AbrirOrdenDeTrabajoSolicitud>(peticion, ct);
        var id = await mediador.EnviarAsync(solicitud.AComando(), ct);
        return Results.Created($"{Base}/{id}", new { id });
    }

    private static async Task<IResult> CerrarAsync(Guid id, IMediador mediador, CancellationToken ct)
    {
        await mediador.EnviarAsync(new CerrarOrdenDeTrabajoSolicitud().AComando(id), ct);
        return Results.NoContent();
    }

    private static async Task<IResult> ObtenerAsync(Guid id, IMediador mediador, CancellationToken ct) =>
        Results.Ok(await mediador.EnviarAsync(new ObtenerOrdenDeTrabajoConsulta(id), ct));

    private static async Task<IResult> ObtenerPorParadaAsync(Guid paradaId, IMediador mediador, CancellationToken ct) =>
        Results.Ok(await mediador.EnviarAsync(new ObtenerOrdenDeTrabajoPorParadaConsulta(paradaId), ct));

    private static async Task<T> LeerCuerpoAsync<T>(HttpRequest peticion, CancellationToken ct) where T : class
    {
        try
        {
            return await JsonSerializer.DeserializeAsync<T>(peticion.Body, SerializadorJson.Opciones, ct)
                ?? throw CuerpoInvalido("El cuerpo es obligatorio.");
        }
        catch (JsonException)
        {
            throw CuerpoInvalido("El cuerpo no es un JSON válido para esta operación.");
        }
    }

    private static ValidacionException CuerpoInvalido(string mensaje) => new([new ErrorDeValidacion("cuerpo", mensaje)]);
}
