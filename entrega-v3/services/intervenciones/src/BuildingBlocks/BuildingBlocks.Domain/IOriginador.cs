namespace BuildingBlocks.Domain;

/// <summary>Memento: el agregado entrega una instantánea de su estado y se reconstruye (validando) desde ella.</summary>
public interface IOriginador<TSelf, TMemento> where TSelf : IOriginador<TSelf, TMemento>
{
    TMemento CrearMemento();

    static abstract TSelf RestaurarDesde(TMemento memento);
}
