using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Serialization;
using BuildingBlocks.Application.Serializacion;

namespace BuildingBlocks.Infrastructure.Serializacion;

/// <summary>JSON en camelCase, con enums como texto y tildes legibles.</summary>
public sealed class SerializadorJson : ISerializadorJson
{
    public static readonly JsonSerializerOptions Opciones = new(JsonSerializerDefaults.Web)
    {
        Converters = { new JsonStringEnumConverter() },
        Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
    };

    public string Serializar<T>(T valor) => JsonSerializer.Serialize(valor, Opciones);

    public T Deserializar<T>(string json) =>
        JsonSerializer.Deserialize<T>(json, Opciones)
        ?? throw new JsonException($"El documento no contiene un {typeof(T).Name} válido.");
}
