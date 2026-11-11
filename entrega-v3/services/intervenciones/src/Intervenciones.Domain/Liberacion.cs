using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class Liberacion : Entity<Guid>
{
    public Liberacion(Guid id, string liberadaPor, DateTimeOffset firmadaEn, VueloDePrueba? vueloDePrueba)
        : base(Guard.NoVacio(id, nameof(id)))
    {
        LiberadaPor = Guard.Texto(liberadaPor, nameof(liberadaPor), 100);
        FirmadaEn = Guard.NoPorDefecto(firmadaEn, nameof(firmadaEn));
        VueloDePrueba = vueloDePrueba;
    }

    public string LiberadaPor { get; }

    public DateTimeOffset FirmadaEn { get; }

    public VueloDePrueba? VueloDePrueba { get; }
}
