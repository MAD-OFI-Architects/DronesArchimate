using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed record Hallazgo
{
    public Hallazgo(string descripcion, DateTimeOffset registradoEn)
    {
        Descripcion = Guard.Texto(descripcion, nameof(descripcion), 500);
        RegistradoEn = Guard.NoPorDefecto(registradoEn, nameof(registradoEn));
    }

    public string Descripcion { get; }

    public DateTimeOffset RegistradoEn { get; }
}
