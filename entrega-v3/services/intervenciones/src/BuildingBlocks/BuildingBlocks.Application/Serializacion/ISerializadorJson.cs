namespace BuildingBlocks.Application.Serializacion;

public interface ISerializadorJson
{
    string Serializar<T>(T valor);

    T Deserializar<T>(string json);
}
