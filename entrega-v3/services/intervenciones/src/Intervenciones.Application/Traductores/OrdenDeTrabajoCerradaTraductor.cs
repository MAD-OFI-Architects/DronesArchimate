using BuildingBlocks.Application.Integracion;
using Intervenciones.Contracts;
using Intervenciones.Domain;

namespace Intervenciones.Application.Traductores;

public sealed class OrdenDeTrabajoCerradaTraductor : TraductorDeEventoDeDominio<OrdenDeTrabajoCerrada>
{
    protected override string Topico => IntervencionesTopicos.OrdenDeTrabajoCerrada;

    protected override object CrearContrato(OrdenDeTrabajoCerrada evento) => new OrdenDeTrabajoCerradaV1(
        evento.OrdenId,
        evento.ParadaId,
        evento.DronId,
        evento.OcurrioEn,
        evento.HorasHombre,
        evento.Consumos.Select(c => new ConsumoCerradoV1(c.Referencia, c.Cantidad, c.NumeroDeSerie, c.SerieRetirada, c.HoraDeCorte)).ToList());
}
