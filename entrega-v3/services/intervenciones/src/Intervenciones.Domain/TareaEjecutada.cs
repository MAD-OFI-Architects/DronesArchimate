using BuildingBlocks.Domain;

namespace Intervenciones.Domain;

public sealed class TareaEjecutada : Entity<Guid>
{
    public TareaEjecutada(Guid id, string descripcion, string resultado, string ejecutadaPor, HorasHombre horas, DateTimeOffset ejecutadaEn)
        : base(Guard.NoVacio(id, nameof(id)))
    {
        Descripcion = Guard.Texto(descripcion, nameof(descripcion));
        Resultado = Guard.Texto(resultado, nameof(resultado), 500);
        EjecutadaPor = Guard.Texto(ejecutadaPor, nameof(ejecutadaPor), 100);
        Horas = Guard.NoNulo(horas, nameof(horas));
        EjecutadaEn = Guard.NoPorDefecto(ejecutadaEn, nameof(ejecutadaEn));
    }

    public string Descripcion { get; }

    public string Resultado { get; }

    public string EjecutadaPor { get; }

    public HorasHombre Horas { get; }

    public DateTimeOffset EjecutadaEn { get; }
}
