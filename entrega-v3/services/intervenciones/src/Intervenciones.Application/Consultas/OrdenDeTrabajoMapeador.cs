using Intervenciones.Domain;

namespace Intervenciones.Application.Consultas;

/// <summary>Frontera de lectura: el agregado nunca sale de la aplicación, solo su DTO.</summary>
public static class OrdenDeTrabajoMapeador
{
    public static OrdenDeTrabajoDto ADto(OrdenDeTrabajo orden) => new(
        orden.Id,
        orden.ParadaId,
        orden.DronId,
        orden.Tipo.ToString(),
        orden.EsTrabajoMayor,
        orden.Estado.Nombre,
        orden.AbiertaEn,
        orden.Tecnico,
        orden.MotivoDeEspera,
        orden.CerradaEn,
        orden.HorasHombreTotales?.Valor ?? 0m,
        orden.Tareas.Select(t => new TareaEjecutadaDto(t.Id, t.Descripcion, t.Resultado, t.EjecutadaPor, t.Horas.Valor, t.EjecutadaEn)).ToList(),
        orden.Consumos.Select(c => new ConsumoDeRepuestoDto(
            c.Id, c.Referencia, c.Cantidad, c.RequiereSerie, c.SerieRetirada, c.SerieInstalada, c.HoraDeCorte?.Horas)).ToList(),
        orden.Hallazgos.Select(h => new HallazgoDto(h.Descripcion, h.RegistradoEn)).ToList(),
        orden.VueloDePrueba is null
            ? null
            : new VueloDePruebaDto(
                orden.VueloDePrueba.RealizadoEn, orden.VueloDePrueba.DuracionEnMinutos,
                orden.VueloDePrueba.Aprobado, orden.VueloDePrueba.Observaciones),
        orden.Liberacion is null
            ? null
            : new LiberacionDto(orden.Liberacion.Id, orden.Liberacion.LiberadaPor, orden.Liberacion.FirmadaEn));
}
