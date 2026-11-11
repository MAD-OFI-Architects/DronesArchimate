using BuildingBlocks.Application.Serializacion;
using Intervenciones.Application.Puertos;
using Intervenciones.Domain;

namespace Intervenciones.Infrastructure.Cifrado;

/// <summary>Cifra en reposo los datos de personas del memento (técnico, quien ejecuta, quien libera) al serializar
/// y los descifra al deserializar; cualquier otro tipo pasa tal cual al serializador base.</summary>
public sealed class SerializadorDeOrdenCifrado(ISerializadorJson interno, Cifrador cifrador) : ISerializadorJson
{
    public string Serializar<T>(T valor) =>
        interno.Serializar(valor is OrdenDeTrabajoMemento memento ? (T)(object)Transformar(memento, cifrador.Cifrar) : valor);

    public T Deserializar<T>(string json)
    {
        var valor = interno.Deserializar<T>(json);
        return valor is OrdenDeTrabajoMemento memento ? (T)(object)Transformar(memento, cifrador.Descifrar) : valor;
    }

    private static OrdenDeTrabajoMemento Transformar(OrdenDeTrabajoMemento memento, Func<string, string> proteger) => memento with
    {
        Tecnico = memento.Tecnico is null ? null : proteger(memento.Tecnico),
        Tareas = memento.Tareas.Select(t => t with { EjecutadaPor = proteger(t.EjecutadaPor) }).ToList(),
        Liberacion = memento.Liberacion is null ? null : memento.Liberacion with { LiberadaPor = proteger(memento.Liberacion.LiberadaPor) }
    };
}
