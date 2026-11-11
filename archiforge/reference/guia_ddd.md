# Guía DDD — Implementación de microservicios (prof. César López)

_Fuente: reference/DDD_Implementacion_MicroSvc.pptx. Texto extraído automáticamente de las diapositivas._


## Diapositiva 1

Implementación de Microservicios usando DDD

MSc. César Augusto López Gallego
Profesor Facultad Ingeniería en TIC – UPB
Coordinador Área de Programación, Computación y Desarrollo de Software
cesar.lopezg@upb.edu.co

## Diapositiva 2

Capas de los Microservicios – Clean Architecture

| Capa | Función |
| API | Punto de entrada (controladores, middleware, configuración). Recibe peticiones HTTP y las traduce a comandos/queries. |
| Application | Orquestación de las acciones que involucran a múltiples componentes para ejecutar un caso de uso. Dice: Qué datos llegan (Commands/Queries). Qué reglas de validación básica se aplican (Validators). Qué partes del dominio deben intervenir (entidades, servicios de dominio, repositorios).  Qué infraestructura se necesita (repositorios, servicios de email, etc.). Qué eventos publicar o qué comandos ejecutar. Qué respuesta devolver (DTOs, IDs, etc.). |
| Domain | Reglas de negocio puras: entidades, value objects, eventos de dominio, interfaces de repositorio, servicios de dominio. No tiene dependencias externas. |
| Infrastructure | Implementación concreta de repositorios (EF Core), acceso a base de datos, servicios de infraestructura (email, SMS, etc.). |

| Contracts | Contiene el lenguaje publicado del microservicio que otros sistemas pueden conocer. Son record con tipos primitivos únicamente (Guid, texto, fechas, enteros), sin dependencias de ningún otro proyecto y con el sufijo V1 para versionarlos.  |

No es una capa más de la arquitectura sino un proyecto aparte, pensado para que otro contexto lo referencie sin arrastrar el dominio.

## Diapositiva 3

De SOA a Microservicios: el mapa

Microservicio Sanciones

Microservicio Pagos

Microservicio Licencias

Comparendos, apelaciones y descuentos

Cobro, recibo y reversión

Licencias y saldo de puntos

Sanciones.Api

Pagos.Api

Licencias.Api

BD propia
(JSON)

BD propia
(JSON)

BD propia
(JSON)

HTTP

Sanciones.Application

Pagos.Application

Licencias.Application

Sanciones.Domain

Pagos.Domain

Licencias.Domain

Sanciones.Infrastructure

Pagos.Infrastructure

Licencias.Infrastructure

Sanciones.Contracts

Pagos.Contracts

Licencias.Contracts

BrokerEnMemoria · bus de eventos por tópicos (el papel de RabbitMQ o Azure Service Bus) · único componente compartido

BuildingBlocks
shared kernel: un proyecto por capa

Domain
Entity, AggregateRoot, Guard, Dinero

Application
CQRS, mediador, validación, puertos

Infrastructure
BD JSON, outbox/inbox, broker, HTTP

Api
enrutador, middlewares, ProblemDetails

## Diapositiva 4

PANORAMA

El mapa: cuatro sistemas, cinco capas

BuildingBlocks

Sanciones

Pagos

Licencias

Api

Servidor, enrutador, middlewares, ProblemDetails

2 módulos · 7 rutas

1 módulo · 2 rutas

1 módulo (MicroservicioLicencias) · 5 rutas (LicenciasEndpoints.cs) – 2 Solicitudes

Infrastructure

BD JSON, outbox, broker, canales, HTTP

Repositorio, catálogo, webhook Policía

Repositorio, ACL, pasarela FakePay

Repositorio(RepositorioDeLicencias), consecutivo(GeneradorNumeroLicenciaDocumental), webhook RUNT (ServiceCollectionExtensions)

Application

CQRS, mediador, pipeline, validación

4 comandos · 4 consultas

2 comandos · 1 consulta · puerto pasarela

4 comandos con sus eventos(Cancelar Descontar, Expedir, Renovar) · 2 consultas  con DTOs (ListarLicencia, Obtener Licencia) – 3 Eventos

Domain

Entity, AggregateRoot, Guard, Dinero

Sancion + Apelacion · 6 reglas

Pago + State · 6 reglas

Agregado Licencia - Entidad  DescuentoDePuntos · 4 reglas – 5 Eventos – 1 Servicio de Expedición
* Organizar carpetas de dominio

Contracts

No tiene

5 contratos V1

2 contratos V1

4 contratos V1

## Diapositiva 5

¿Qué es BuildingBlocks?

Librería compartida que todos los microservicios necesitan y que sería idéntico si cada uno lo escribiera por su cuenta: qué es una entidad, cómo se despacha un comando, cómo se guarda un documento JSON, cómo se publica un evento.

Función:
Evita duplicar lógica de infraestructura o dominio genérico.
Centraliza definiciones de eventos, excepciones base, interfaces de publicación de eventos, etc.

También es llamado Shared Kernel

Ilustración: Dependencias Mínimas

## Diapositiva 6

BuildingBlocks: el shared kernel

BuildingBlocks.Api

BuildingBlocks.Infrastructure

BuildingBlocks.Application

BuildingBlocks.Domain

ServidorApi (como Kestrel)
Enrutador y módulos
Cadena de middlewares
ProblemDetails (RFC 9457) Es el estándar actual para APIs HTTP.

BD documental JSON
Unidad de trabajo y outbox
Broker y canales
Red HTTP y notificaciones

CQRS y mediador
Pipeline de comportamientos
Validación de entrada
Eventos y puertos

Entity y AggregateRoot
Guard y reglas de negocio
DomainEvent y Memento
Specification y Dinero

Abstracciones de Hosting

Abstracciones de Hosting

Solo abstracciones de DI y logging

Sin paquetes

Cada proyecto solo depende de la capa interior →

Sin conceptos de negocio

Dependencias mínimas

Versionado

No hay Sancion, Pago ni Licencia. Única excepción: Dinero, que significa lo mismo en todo el sistema.

Licencias.Domain referencia solo BuildingBlocks.Domain: ni JSON, ni contenedor de dependencias, ni logging.

En producción se publican como paquetes NuGet versionados: ningún microservicio obliga a otro a recompilar.

## Diapositiva 7

GRÁFICA 1 · ORDEN DE DEPENDENCIAS (EN EL CÓDIGO)

Dependencias: quién referencia a quién

BUILDINGBLOCKS

MICROSERVICIO PAGOS

QUÉ PUEDE VER CADA PROYECTO

Pagos.Api
endpoints y composition root

Conoce todas las capas: es el único lugar que las conecta

referencia

BuildingBlocks.Api

para registrar los adaptadores al arrancar

Pagos.Infrastructure
repositorio, ACL, adaptador FakePay

Ve hacia adentro para implementar los puertos; nadie de adentro la ve a ella

BuildingBlocks.Infrastructure

para implementar los puertos que ella declara

Pagos.Application
comandos, manejadores, IPasarelaDePagos

Pagos.Contracts
lo que publica

Sanciones.Contracts
lo que consume

BuildingBlocks.Application

para usar Pago, ServicioDeCobro y sus puertos

Pagos.Domain
Pago, estados, ServicioDeCobro, reglas

No ve a ningún otro proyecto de Pagos, ni a Sanciones, ni a FakePay

BuildingBlocks.Domain

Cada flecha significa «este proyecto referencia a aquel» en su .csproj. No dice quién llama a quién cuando el sistema se ejecuta.

## Diapositiva 8

GRÁFICA 2 · ORDEN DE EJECUCIÓN (PAGAR UNA SANCIÓN)

Ejecución: por dónde viaja la petición

solicitud

respuesta

1

10

Api

Infrastructure
no está en el camino: se llama por puertos

IDA: hacia el dominio

REGRESO

Endpoint
POST /api/pagos: lee el JSON y arma el comando

Respuesta
201 Created con el recibo, o 402

Capa anticorrupción
GET a Sanciones; trae la obligación y su valor

A

comando

DTO

2

3

9

Application

Mediador y pipeline
registra y valida la forma del comando

Manejador
pasa de primitivos a tipos del dominio

Manejador
devuelve ResultadoDePagoDto

Repositorio y consecutivo
número REC-AAAA-NNN; el pago queda rastreado

B

6

8

Manejador
pide autorizar el cargo a la pasarela

Transacción
el pipeline confirma la unidad de trabajo

Adaptador FakePay
pesos a centavos; aprobado o rechazado

tipos del dominio

C

C

D

Domain

4

5

7

Unidad de trabajo
pago en JSON + PagoConfirmadoV1 en la bandeja de salida

ServicioDeCobro
consulta la deuda y verifica las reglas

Pago.Iniciar
nace Pendiente, con su recibo

Pago.Confirmar
pasa a Confirmado y anota el evento

D

A

B

Después de responder: el outbox publica PagoConfirmadoV1 → Sanciones aplica el pago y emite SancionPagadaV1 → Licencias descuenta los puntos.

## Diapositiva 9

MICROSERVICIO SANCIONES · CAPA DE DOMINIO

Sanciones.Domain

Api

Infrastructure

Application

Domain

Referencia solo a BuildingBlocks.Domain

Agregado y entidad interna

Value objects

Enumeraciones

Sancion

Apelacion

SancionId

ApelacionId

EstadoSancion

ResultadoApelacion

NumeroComparendo

Placa

Infraccion

ResultadoRecepcionPago

Eventos de dominio

PagoAplicado

ConductorId

SancionRegistrada

SancionPagada

Reglas de negocio

PagoDeSancionRechazado

SancionApelada

FechaDeInfraccionNoPuedeSerFutura

Estrategia de descuento

ApelacionRechazada

SancionAnulada

IPoliticaDeDescuento

SancionDebeEstarPendiente

DescuentoPorProntoPago

SinDescuento

MontoPagadoDebeSerIgualAlValorAPagar

Puertos

ApelacionDebePresentarseDentroDelPlazo

ISancionRepository

Mementos

SoloSePermiteUnaApelacion

ICatalogoDeInfracciones

SancionMemento

ApelacionMemento

SancionDebeTenerApelacionEnCurso

IGeneradorNumeroComparendo

## Diapositiva 10

MICROSERVICIO SANCIONES · CAPA DE APLICACIÓN

Sanciones.Application

Api

Infrastructure

Application

Domain

Referencia a Sanciones.Domain, Sanciones.Contracts, Pagos.Contracts y BuildingBlocks.Application

Comandos

Consultas

Manejadores

RegistrarSancionComando

ObtenerSancionConsulta

Uno por cada comando y consulta: 8

ApelarSancionComando

ObtenerObligacionConsulta

Validadores

ResolverApelacionComando

ListarSancionesDelConductorConsulta

RegistrarSancionValidador

RecibirPagoComando

ListarInfraccionesConsulta

ApelarSancionValidador

Modelos de lectura

Consumidor

ResolverApelacionValidador

RecibirPagoValidador

SancionDto

ApelacionDto

InfraccionDto

PagoConfirmadoConsumidor

SancionRegistradaDto

SancionMapeador

Observadores

Traductores

Registro

NotificarSancionRegistradaManejador

SancionRegistradaTraductor

AgregarAplicacionSanciones

NotificarSancionPagadaManejador

SancionPagadaTraductor

SancionAnuladaTraductor

NotificarSancionAnuladaManejador

PagoDeSancionRechazadoTraductor

## Diapositiva 11

MICROSERVICIO SANCIONES · CAPAS EXTERNAS

Sanciones: infraestructura, API y contratos

Sanciones.Infrastructure  ·  adaptadores de salida

Persistencia

Catálogo

Canales de salida

Consumidor registrado

RepositorioDeSanciones

CatalogoDeInfraccionesEnMemoria

Bus de eventos

PagoConfirmadoV1

GeneradorNumeroComparendoDocumental

Bitácora de auditoría

Buzón de archivos

Webhook Policía

Sanciones.Api  ·  presentación y composition root

Sanciones.Contracts  ·  lenguaje publicado

Rutas

Composition root y módulos

Consulta síncrona, eventos y tópicos

POST /api/sanciones

GET /api/sanciones/{id}

MicroservicioSanciones

SancionesEndpoints

ObligacionDeSancionV1

SancionRegistradaV1

GET …/{id}/obligacion

POST …/{id}/apelacion

InfraccionesEndpoints

SancionPagadaV1

SancionAnuladaV1

POST …/apelacion/resolucion

PagoDeSancionRechazadoV1

SancionesTopicos

Solicitudes HTTP

GET …/conductores/{id}/sanciones

GET /api/infracciones

RegistrarSancionSolicitud

ApelarSancionSolicitud

ResolverApelacionSolicitud

## Diapositiva 12

MICROSERVICIO PAGOS · CAPA DE DOMINIO

Pagos.Domain

Api

Infrastructure

Application

Domain

Referencia solo a BuildingBlocks.Domain

Agregado

Estados · patrón State

Value objects

Pago

EstadoDePago

EstadoPendiente

PagoId

NumeroRecibo

EstadoConfirmado

EstadoRechazado

CorreoElectronico

ReferenciaObligacion

Enumeraciones

EstadoReversado

TipoObligacion

EstadoPago

Eventos de dominio

MetodoPago

OperacionDePago

PagoIniciado

PagoConfirmado

Reglas de negocio

PagoDebePermitirLaOperacion

PagoRechazado

PagoReversado

Servicio de dominio y su modelo

MontoDelPagoDebeSerPositivo

ServicioDeCobro

ObligacionPorPagar

Puertos

ObligacionDebeExistir

IPagoRepository

ObligacionDebeAdmitirPago

Memento

IConsultaDeObligaciones

MontoDebeCoincidirConLaObligacion

PagoMemento

IGeneradorNumeroRecibo

NoDebeExistirOtroPagoActivo

## Diapositiva 13

MICROSERVICIO PAGOS · CAPA DE APLICACIÓN

Pagos.Application

Api

Infrastructure

Application

Domain

Referencia a Pagos.Domain, Pagos.Contracts, Sanciones.Contracts y BuildingBlocks.Application

Puerto de la pasarela

Comandos

Consulta

IPasarelaDePagos

PagarObligacionComando

ObtenerPagoConsulta

SolicitudDeAutorizacion

ReversarPagoComando

Manejadores

ResultadoDeAutorizacion

Uno por cada comando y consulta: 3

Validadores

PagarObligacionValidador

Modelos de lectura

Consumidor

ResultadoDePagoDto

PagoDto

ReversarPagoValidador

PagoDeSancionRechazadoConsumidor

Traductores

Observadores

PagoConfirmadoTraductor

NotificarPagoConfirmadoManejador

PagoReversadoTraductor

NotificarPagoRechazadoManejador

NotificarPagoReversadoManejador

## Diapositiva 14

MICROSERVICIO PAGOS · CAPAS EXTERNAS

Pagos: infraestructura, API y contratos

Pagos.Infrastructure  ·  adaptadores de salida

Capa anticorrupción

Pasarela de pagos

Persistencia

Canales de salida

Consumidor registrado

ConsultaDeObligacionesDeSanciones

PasarelaFakePayAdapter

RepositorioDePagos

Bus de eventos

PagoDeSancionRechazadoV1

FakePayClient

GeneradorNumeroReciboDocumental

Bitácora de auditoría

FakePayChargeRequest

Buzón de archivos

FakePayChargeResponse

Pagos.Api  ·  presentación y composition root

Pagos.Contracts  ·  lenguaje publicado

Composition root y solicitud HTTP

Rutas

Eventos y tópicos

MicroservicioPagos

PagarObligacionSolicitud

POST /api/pagos

GET /api/pagos/{id}

PagoConfirmadoV1

PagoReversadoV1

PagosTopicos

## Diapositiva 15

MICROSERVICIO LICENCIAS · CAPA DE DOMINIO

Licencias.Domain

Api

Infrastructure

Application

Domain

Referencia solo a BuildingBlocks.Domain

Agregado y entidad interna

Value objects

Enumeraciones

Licencia

DescuentoDePuntos

LicenciaId

DescuentoId

ConductorId

CategoriaLicencia

CategoriaLicenciaExtensions

NumeroLicencia

Vigencia

SaldoDePuntos

EstadoLicencia

Especificaciones

Eventos de dominio

Reglas de negocio

LicenciaActiva

LicenciaDeCategoria

LicenciaExpedida

PuntosDescontados

LicenciaCanceladaNoAdmiteCambios

Expedición · servicio de dominio

LicenciaSuspendida

LicenciaRenovada

SoloSeRenuevaUnaLicenciaVigente

LicenciaCancelada

ConductorNoDebeTenerOtraLicenciaActivaDeLaCategoria

ServicioDeExpedicion

SolicitudDeExpedicion

NumeroDeLicenciaDebeSerUnico

IReglaDeExpedicion

Estrategia de vigencia

ReglaUnaLicenciaActivaPorCategoria

Puertos

ReglaNumeroDeLicenciaUnico

IPoliticaDeVigencia

VigenciaPorCategoria

ILicenciaRepository

IGeneradorNumeroLicencia

Mementos

LicenciaMemento

DescuentoDePuntosMemento

## Diapositiva 16

MICROSERVICIO LICENCIAS · CAPA DE APLICACIÓN

Licencias.Application

Api

Infrastructure

Application

Domain

Referencia a Licencias.Domain, Licencias.Contracts, Sanciones.Contracts y BuildingBlocks.Application

Comandos

Consultas

Manejadores

ExpedirLicenciaComando

ObtenerLicenciaConsulta

ExpedirLicenciaManejador

DescontarPuntosComando

ListarLicenciasDelConductorConsulta

DescontarPuntosManejador

RenovarLicenciaComando

RenovarLicenciaManejador

Validadores

CancelarLicenciaComando

CancelarLicenciaManejador

ObtenerLicenciaManejador

ExpedirLicenciaValidador

Modelos de lectura

ListarLicenciasDelConductorManejador

DescontarPuntosValidador

RenovarLicenciaValidador

LicenciaDto

DescuentoDto

Consumidor

CancelarLicenciaValidador

LicenciaExpedidaDto

LicenciaMapeador

SancionPagadaConsumidor

Traductores

Observadores

Registro

LicenciaExpedidaTraductor

NotificarLicenciaExpedidaManejador

AgregarAplicacionLicencias

PuntosDescontadosTraductor

NotificarPuntosDescontadosManejador

LicenciaSuspendidaTraductor

NotificarLicenciaSuspendidaManejador

LicenciaCanceladaTraductor

## Diapositiva 17

MICROSERVICIO LICENCIAS · CAPAS EXTERNAS

Licencias: infraestructura, API y contratos

Licencias.Infrastructure  ·  adaptadores de salida

Persistencia

Canales de salida

Consumidor registrado

Registro

RepositorioDeLicencias

Bus de eventos

SancionPagadaV1

AgregarInfraestructuraLicencias

GeneradorNumeroLicenciaDocumental

Bitácora de auditoría

Buzón de archivos

Webhook RUNT

Licencias.Api  ·  presentación y composition root

Licencias.Contracts  ·  lenguaje publicado

Composition root y módulo

Solicitudes HTTP

Eventos y tópicos

MicroservicioLicencias

LicenciasEndpoints

ExpedirLicenciaSolicitud

LicenciaExpedidaV1

PuntosDescontadosV1

CancelarLicenciaSolicitud

LicenciaSuspendidaV1

LicenciaCanceladaV1

Rutas

LicenciasTopicos

POST /api/licencias

GET /api/licencias/{id}

POST …/{id}/renovacion

POST …/{id}/cancelacion

GET …/conductores/{id}/licencias

## Diapositiva 18

Ejemplo: Implementación

## Diapositiva 19

MAPA GENERAL · 1

Mapa general: cada capa con su bloque

BuildingBlocks · genérico

Licencias · concreto

BuildingBlocks.Api
IModuloDeEndpoints, EnrutadorHttp, ContextoHttp, Resultados, middlewares, ServidorApi

Licencias.Api
LicenciasEndpoints, solicitudes HTTP, composition root

depende de

BuildingBlocks.Infrastructure
RepositorioDocumentalBase, UnidadDeTrabajoDocumental, GeneradorDeConsecutivos, canales, consumo

Licencias.Infrastructure
RepositorioDeLicencias, GeneradorNumeroLicenciaDocumental, configuración de canales y consumidores

BuildingBlocks.Application
CQRS, IMediador, pipeline, ValidadorBase, observadores, traductores, IClock

Licencias.Application
Comandos, consultas, manejadores, validadores, notificadores, traductores, consumidor

BuildingBlocks.Domain
Guard, Entity, AggregateRoot, DomainEvent, IBusinessRule, Especificacion, IOriginador

Licencias.Domain
Licencia, DescuentoDePuntos, value objects, eventos, reglas, especificaciones

solo el bloque de su misma capa

## Diapositiva 20

BUILDING BLOCKS · DOMAIN

Domain: El modelo

Guard

Entity · AggregateRoot

DomainEvent

IBusinessRule

Valida en getters y setters. Centraliza los if para no repetirlos (DRY).

Igualdad por tipo e Id. La raíz guarda los eventos con Raise, que es protected.

abstract record inmutable con EventoId y OcurrioEn. El Id viaja hasta el mensaje de integración.

Cada regla es una clase con nombre del lenguaje ubicuo. BusinessRules.Check lanza si está rota.

Encapsulamiento

Aggregate

Domain Event

SRP + abierto/cerrado

IOriginador

Especificacion

Dinero

Excepciones

El agregado produce una instantánea de tipos primitivos y se reconstruye desde ella, validando.

EsSatisfechaPor(candidato) y combinadores Y, O, No para armar reglas nuevas.

Compartido por todos: decimal, moneda ISO 4217, inmutable. Impide operar monedas distintas.

DomainException: dato inválido.
BusinessRuleViolationException: regla con nombre propio.

Memento

Specification + Composite

Value Object

HTTP 400 · HTTP 422

## Diapositiva 21

BUILDING BLOCKS · DOMAIN

Guard Clase estática de validaciones que usan los getters y setters del dominio para rechazar datos inválidos sin repetir el mismo if

Setter → DomainException
El dato que llega es inválido para el negocio. La API responde 400.
NoNulo · Texto · EnRango · Positivo · Definido

Getter → InvalidOperationException
Leer algo que nunca se asignó es un error de programación.
Inicializado · Asignado

```csharp
private NumeroLicencia? _numero;   // campo de respaldo privado
 
public NumeroLicencia Numero
{
    get => Guard.Inicializado(_numero, nameof(Numero));
    private set => _numero = Guard.NoNulo(value, "número de licencia");
}
```

Licencia.cs: toda propiedad del dominio sigue este molde

## Diapositiva 22

CAPA DE DOMINIO · 2.1

Guard

BuildingBlock · genérico

Guard.cs

Licencias · concreto

Licencia.cs

```csharp
public static class Guard
{
    // setters → DomainException
    public static T NoNulo<T>(T? valor, string campo)
        where T : class => valor ?? throw new DomainException(
            $"El campo '{campo}' es obligatorio.");
    public static string Texto(string? valor, string campo,
                               int longitudMaxima = 250) { ... }
    public static Guid NoVacio(Guid valor, string campo) => ...
    public static int EnRango(int valor, int minimo,
                              int maximo, string campo) => ...
    public static TEnum Definido<TEnum>(TEnum valor, ...) => ...
 
    // getters → InvalidOperationException
    public static T Inicializado<T>(T? valor, string campo) ...
    public static T Asignado<T>(T valor, string campo) ...
}
```

```csharp
public NumeroLicencia Numero
{
    get => Guard.Inicializado(_numero, nameof(Numero));
    private set => _numero =
        Guard.NoNulo(value, "número de licencia");
}
 
public ConductorId ConductorId
{
    get => Guard.Asignado(_conductorId, nameof(ConductorId));
    private set => _conductorId =
        Guard.NoPorDefecto(value, "conductor");
}
 
public void Cancelar(string motivo, DateTimeOffset ahora)
{
    ...
    MotivoEstado = Guard.Texto(motivo,
        "motivo de la cancelación", 300);
}
```

Qué gana Licencias: mensajes de error uniformes y ninguna propiedad repite el mismo if. Como los setters privados validan, RestaurarDesde vuelve a validar lo leído de la base de datos: un JSON corrupto no entra al modelo.

## Diapositiva 23

CAPA DE DOMINIO · 2.2

DomainException: Excepción que indica que un dato no es válido para el negocio; la API la convierte en HTTP 400

BuildingBlock · genérico

DomainException.cs

Licencias · concreto

Vigencia.cs · NumeroLicencia.cs · DescuentoDePuntos.cs

```csharp
// Dato inválido para el dominio
public class DomainException(string message)
    : Exception(message);
```

```csharp
// Vigencia.cs: regla entre dos campos
if (vencimiento <= expedicion)
    throw new DomainException(
        "La fecha de vencimiento debe ser posterior a la de expedición.");
 
// NumeroLicencia.cs: formato LIC-AAAA-NNN
if (!Formato().IsMatch(normalizado))
    throw new DomainException(
        $"'{value}' no es un número de licencia válido (LIC-AAAA-NNN).");
 
// DescuentoDePuntos.cs
if (aplicados > solicitados)
    throw new DomainException(
        "No se pueden aplicar más puntos de los solicitados.");
```

Qué gana Licencias: además de recibirla indirectamente desde Guard, la lanza para invariantes de varios campos o de formato propio; el middleware de errores de la API la convierte en HTTP 400 sin que el dominio sepa nada de HTTP.

## Diapositiva 24

CAPA DE DOMINIO · 2.3

Entity<TId>:Clase base de los objetos que se distinguen por su Id y no por sus datos; rechaza Ids vacíos.

BuildingBlock · genérico

Entity.cs

Licencias · concreto

DescuentoDePuntos.cs

```csharp
public abstract class Entity<TId> where TId : notnull
{
    protected Entity(TId id) => Id = id;
 
    public TId Id
    {
        get => _tieneId ? _id
            : throw new InvalidOperationException(...);
        protected set
        {
            if (value is null || EqualityComparer<TId>
                    .Default.Equals(value, default!))
                throw new DomainException(...);
            ...
        }
    }
 
    protected static void CheckRule(IBusinessRule rule) =>
        BusinessRules.Check(rule);
 
    public override bool Equals(object? obj) => ...
}
```

```csharp
// Entidad interna del agregado
public sealed class DescuentoDePuntos
    : Entity<DescuentoId>
{
    private DescuentoDePuntos(DescuentoId id)
        : base(id) { }
    ...
}
 
// Licencia también es una entidad,
// pero a través de AggregateRoot.
 
// LicenciaId, DescuentoId y ConductorId son
// readonly record struct: Entity rechaza su
// valor default y cada struct rechaza
// Guid.Empty con Guard.NoVacio.
```

Qué gana Licencias: igualdad por identidad, protección contra Ids vacíos y el atajo CheckRule(...) sin escribir nada.

## Diapositiva 25

CAPA DE DOMINIO · 2.4

AggregateRoot: Entidad principal de un agregado; es la única puerta para cambiarlo y va guardando los eventos de lo que le ocurre.

BuildingBlock · genérico

AggregateRoot.cs · IAggregateRoot.cs

Licencias · concreto

Licencia.cs

```csharp
public abstract class AggregateRoot<TId>
    : Entity<TId>, IAggregateRoot where TId : notnull
{
    private readonly List<IDomainEvent> _domainEvents = [];
 
    public IReadOnlyCollection<IDomainEvent> DomainEvents =>
        _domainEvents.AsReadOnly();
 
    protected void Raise(IDomainEvent domainEvent) =>
        _domainEvents.Add(...);
 
    public void ClearDomainEvents() => _domainEvents.Clear();
}
 
// UnidadDeTrabajoDocumental los recoge por IAggregateRoot
var eventos = _rastreados.Values
    .SelectMany(e => e.Agregado.DomainEvents).ToList();
```

```csharp
public sealed class Licencia : AggregateRoot<LicenciaId>,
    IOriginador<Licencia, LicenciaMemento>
{
    public static Licencia Expedir(...)
    {
        var licencia = new Licencia(id) { ... };
        licencia.Raise(new LicenciaExpedida(ahora, id,
            conductorId, numero.Valor, categoria,
            licencia.Vigencia.Vencimiento));
        return licencia;
    }
}
 
// Expedir             → LicenciaExpedida
// DescontarPuntos     → PuntosDescontados
// Renovar             → LicenciaRenovada
// Cancelar            → LicenciaCancelada
// Suspender (privado) → LicenciaSuspendida
```

Qué gana Licencias: el agregado solo declara lo que ocurrió; publicar, guardar en la bandeja de salida y notificar es trabajo del BuildingBlock. Licencias nunca llama a DomainEvents ni a ClearDomainEvents().

## Diapositiva 26

CAPA DE DOMINIO · 2.5

DomainEvent: Registro inmutable de algo que ya pasó en el dominio, con su propio Id y fecha.

BuildingBlock · genérico

IDomainEvent.cs · DomainEvent.cs

Licencias · concreto

Licencias/Eventos/LicenciaExpedida.cs

```csharp
public interface IDomainEvent
{
    Guid EventoId { get; }
    DateTimeOffset OcurrioEn { get; }
}
 
public abstract record DomainEvent(
    DateTimeOffset OcurrioEn) : IDomainEvent
{
    public Guid EventoId { get; init; } = Guid.NewGuid();
}
```

```csharp
public sealed record LicenciaExpedida(
    DateTimeOffset OcurrioEn,
    LicenciaId LicenciaId,
    ConductorId ConductorId,
    string NumeroLicencia,
    CategoriaLicencia Categoria,
    DateOnly Vencimiento) : DomainEvent(OcurrioEn);
 
// Cinco eventos, todos sealed record:
//   LicenciaExpedida
//   PuntosDescontados
//   LicenciaRenovada
//   LicenciaSuspendida
//   LicenciaCancelada
```

Qué gana Licencias: cada evento recibe automáticamente un EventoId único. Ese mismo Id se conserva al traducirlo a evento de integración y permite detectar duplicados en los consumidores.

## Diapositiva 27

CAPA DE DOMINIO · 2.6

IBusinessRule: Contrato para escribir cada regla de negocio como una clase con nombre propio; si se incumple, la API responde 422 indicando cuál fue.

BuildingBlock · genérico

IBusinessRule.cs · BusinessRules.cs

Licencias · concreto

Reglas/ · Licencia.cs · ServicioDeExpedicion.cs

```csharp
public interface IBusinessRule
{
    bool IsBroken();
    string Message { get; }
}
 
public static class BusinessRules
{
    public static void Check(IBusinessRule rule)
    {
        if (rule.IsBroken())
            throw new BusinessRuleViolationException(rule);
    }
}
 
public sealed class BusinessRuleViolationException(
    IBusinessRule brokenRule)
    : DomainException(brokenRule.Message)
{
    public IBusinessRule BrokenRule { get; } = brokenRule;
}
```

```csharp
public sealed class LicenciaCanceladaNoAdmiteCambios(
    EstadoLicencia estado) : IBusinessRule
{
    public bool IsBroken() =>
        estado == EstadoLicencia.Cancelada;
    public string Message =>
        "La licencia está cancelada y no admite cambios.";
}
 
// 1. Dentro del agregado (Licencia.cs)
CheckRule(new LicenciaCanceladaNoAdmiteCambios(Estado));
CheckRule(new SoloSeRenuevaUnaLicenciaVigente(Estado));
 
// 2. En el servicio de dominio (ServicioDeExpedicion.cs)
foreach (var regla in _reglas)
    BusinessRules.Check(await regla.EvaluarAsync(
        solicitud, cancellationToken));
```

Qué gana Licencias: cuatro reglas propias. La excepción conserva qué regla se rompió: la API responde HTTP 422 e incluye el nombre de la clase en el campo regla del ProblemDetails.

## Diapositiva 28

CAPA DE DOMINIO · 2.7

Especificacion<T>: predicados, condición de negocio reutilizable que responde sí o no sobre un objeto y se puede combinar con Y, O y No.

BuildingBlock · genérico

Especificaciones/Especificacion.cs

Licencias · concreto

LicenciaActiva.cs · regla · DescontarPuntosManejador.cs

```csharp
public abstract class Especificacion<T>
{
    public abstract bool EsSatisfechaPor(T candidato);
 
    public Especificacion<T> Y(Especificacion<T> otra)
        => new EspecificacionY<T>(this, otra);
    public Especificacion<T> O(Especificacion<T> otra)
        => new EspecificacionO<T>(this, otra);
    public Especificacion<T> No()
        => new EspecificacionNo<T>(this);
}
```

```csharp
public sealed class LicenciaActiva : Especificacion<Licencia>
{
    public override bool EsSatisfechaPor(Licencia candidato) =>
        candidato.Estado != EstadoLicencia.Cancelada;
}
 
// Se combinan con Y en una regla de negocio
private readonly Especificacion<Licencia> _activaDeLaCategoria =
    new LicenciaActiva().Y(new LicenciaDeCategoria(categoria));
 
public bool IsBroken() =>
    licenciasDelConductor.Any(_activaDeLaCategoria.EsSatisfechaPor);
 
// Y se reutilizan en DescontarPuntosManejador
var activas = delConductor.Where(Activa.EsSatisfechaPor).ToList();
```

Qué gana Licencias: el concepto «licencia activa» se define una sola vez y se usa en dos lugares distintos. Los nodos Y/O/No son internal en el BuildingBlock: Licencias los usa sin conocerlos.

## Diapositiva 29

CAPA DE DOMINIO · 2.8

IOriginador: Contrato por el que un agregado entrega una instantánea de su estado y se reconstruye desde ella, para guardarse en JSON sin exponer sus setters.

BuildingBlock · genérico

IOriginador.cs

Licencias · concreto

Licencia.cs · LicenciaMemento.cs

```csharp
public interface IOriginador<TSelf, TMemento>
    where TSelf : IOriginador<TSelf, TMemento>
{
    TMemento CrearMemento();
    static abstract TSelf RestaurarDesde(
        TMemento memento);
}
 
// El repositorio genérico lo exige y lo
// invoca sin reflexión:
var agregado = TAgregado.RestaurarDesde(memento);
```

```csharp
public LicenciaMemento CrearMemento() => new(
    Id.Valor, Numero.Valor, ConductorId.Valor, Categoria,
    Vigencia.Expedicion, Vigencia.Vencimiento, Saldo.Valor,
    Estado, MotivoEstado,
    _descuentos.Select(d => d.CrearMemento()).ToList());
 
public static Licencia RestaurarDesde(LicenciaMemento memento)
{
    var licencia = new Licencia(new LicenciaId(memento.Id))
    {
        // pasa por los setters con Guard
        Numero = NumeroLicencia.De(memento.Numero),
        ConductorId = new ConductorId(memento.ConductorId),
        ...
    };
    licencia._descuentos.AddRange(memento.Descuentos
        .Select(DescuentoDePuntos.RestaurarDesde));
    return licencia;
}
```

El patrón Memento captura el estado interno de un objeto en una instantánea externa para poder restaurarlo después, sin exponer sus detalles internos ni romper su encapsulamiento.
Qué gana Licencias: no necesita setters públicos ni atributos de serialización en el dominio: la infraestructura serializa el memento, no el agregado.

## Diapositiva 30

CAPA DE DOMINIO · 2.9

Dinero: la pieza que no se usa

BuildingBlock · genérico

Dinero.cs

Licencias · concreto

sin uso

Value object compartido

Nada que implementar

Es el único concepto de negocio del shared kernel
Lo usan Sanciones y Pagos, que sí manejan montos
Con él viene Guard.NoNegativo, que Licencias tampoco usa

Uso en Licencias: ninguno
Licencias maneja puntos y fechas, no montos
Su aritmética propia vive en SaldoDePuntos y Vigencia

Qué gana Licencias: no está obligado a usarlo. El shared kernel es una caja de herramientas, no una imposición.

## Diapositiva 31

Estructura de la Capa Application (Orquestadora)

| Qué hace la subcapa: | Lo que NO debe tener |
| Commands Representan una intención de cambiar el estado del sistema (escritura). Son objetos inmutables que contienen los datos necesarios para ejecutar una acción (ej: CrearMultaCommand con ConductorId, Monto, etc.). | Lógica de negocio (no validar reglas como “si el monto > 500, rechazar”). Acceso a base de datos. Dependencias de infraestructura (DbContext, IConfiguration). Métodos con comportamiento. |
| Queries Representan una petición de lectura de datos sin modificar el estado. Ej: GetConductorQuery { Id }.  | Lógica de negocio. Modificaciones de estado. |
| Contracts (o DTOs (Data Transfer Objects)) Función: Contratos para devolver datos al cliente. Son planos, sin comportamiento. Solo propiedades públicas. | Métodos que calculen algo (ej. CalcularDescuento()). Referencias a entidades de dominio (ej. Multa). Validaciones (esas van en Validators o en el dominio). |
| Validators validan la forma y la integridad básica de los datos de entrada (Commands o Queries) antes de que lleguen al Handler. Son reglas de validación básica que no implican al dominio: NotEmpty, GreaterThan, Lengths. Las reglas de negocio reales están dentro de las entidades y value objects del dominio. Un validator no debe reemplazar ni adelantarse a la validación del dominio | *Nota: Los Validators en Application son el primer filtro de seguridad. Validan que los datos de entrada tengan la forma correcta (requeridos, longitud, rangos, formato básico).   Debate en la aplicación de DDD, cada arquitecto debe resolver |

## Diapositiva 32

Estructura de la Capa Application (Orquestadora)

| Qué hace la subcapa: | Lo que NO debe tener |
| Handlers Clases que implementan la interfaz IRequestHandler<TRequest, TResponse> de MediatR. Orquestan la ejecución de un comando o query: llaman a repositorios, servicios de dominio, publican eventos, etc. | Reglas de negocio (ej. “la multa no puede exceder 1000” – eso va dentro del constructor de Multa). Llamadas directas a DbContext (debe usar repositorio). Lógica de infraestructura (enviar email, loguear a archivo). |
| Mappings  Función: Transformar objetos de dominio a DTOs y viceversa.  | Lógica de negocio, validaciones. |
| Consumers Función: Escuchan eventos provenientes de un bus de mensajes (RabbitMQ, etc.). Al recibir un evento (ej: MultaCreadaEvent), suelen ejecutar un comando o llamar a un servicio. | Lógica de negocio del dominio (ej. calcular puntos de licencia). Acceso directo a repositorios (debe usar comandos). Valores fijos quemados (usar configuración). |

## Diapositiva 33

CAPA DE APLICACIÓN · 3.1

CQRS: Separación de las solicitudes en dos tipos: comandos, que cambian el estado, y consultas, que solo leen.

BuildingBlock · genérico

Cqrs/

Licencias · concreto

Comandos/ · Consultas/ (cada caso de uso es un record)

```csharp
public interface ISolicitud<TRespuesta>;
 
// cambia estado → abre transacción
public interface IComando<TRespuesta>
    : ISolicitud<TRespuesta>;
 
// solo lee → nunca abre transacción
public interface IConsulta<TRespuesta>
    : ISolicitud<TRespuesta>;
 
// el "void" de las respuestas
public readonly record struct Unidad
{
    public static readonly Unidad Valor = new();
}
```

ExpedirLicenciaComando

IComando → LicenciaExpedidaDto

DescontarPuntosComando

IComando → int (licencias afectadas)

RenovarLicenciaComando

IComando → DateOnly

CancelarLicenciaComando

IComando → Unidad

ObtenerLicenciaConsulta

IConsulta → LicenciaDto

ListarLicenciasDelConductorConsulta

IConsulta → IReadOnlyList<LicenciaDto>

Qué gana Licencias: con solo marcar IComando o IConsulta, el pipeline decide si confirma la transacción.

## Diapositiva 34

CAPA DE APLICACIÓN · 3.2

Manejadores de comando y consulta: Clases que atienden cada una un solo caso de uso: reciben la solicitud, delegan en el dominio y devuelven la respuesta.

BuildingBlock · genérico

Cqrs/IManejadorDeSolicitud.cs

Licencias · concreto

CancelarLicenciaManejador.cs

```csharp
public interface IManejadorDeSolicitud
    <in TSolicitud, TRespuesta>
    where TSolicitud : ISolicitud<TRespuesta>
{
    Task<TRespuesta> ManejarAsync(TSolicitud solicitud,
        CancellationToken cancellationToken);
}
 
public interface IManejadorDeComando
    <in TComando, TRespuesta>
    : IManejadorDeSolicitud<TComando, TRespuesta> ...
 
public interface IManejadorDeConsulta
    <in TConsulta, TRespuesta>
    : IManejadorDeSolicitud<TConsulta, TRespuesta> ...
```

```csharp
public sealed class CancelarLicenciaManejador(
    ILicenciaRepository licencias, IClock reloj)
    : IManejadorDeComando<CancelarLicenciaComando, Unidad>
{
    public async Task<Unidad> ManejarAsync(
        CancelarLicenciaComando comando, CancellationToken ct)
    {
        var licencia = await licencias.ObtenerAsync(
                new LicenciaId(comando.LicenciaId), ct)
            ?? throw new RecursoNoEncontradoException(
                "la licencia", comando.LicenciaId);
 
        licencia.Cancelar(comando.Motivo, reloj.Now);
        await licencias.ActualizarAsync(licencia, ct);
        return Unidad.Valor;   // no hay "guardar"
    }
}
```

Qué gana Licencias: seis manejadores (cuatro de comando y dos de consulta) y ninguno se registra a mano: los descubre AgregarBloquesDeAplicacion por reflexión.

## Diapositiva 35

CAPA DE APLICACIÓN · 3.3

IMediador: Intermediario que recibe cualquier solicitud y la entrega a su manejador, de modo que quien envía no conoce a quien atiende.

BuildingBlock · genérico

Cqrs/IMediador.cs · Mediador.cs

Licencias · concreto

LicenciasEndpoints.cs · SancionPagadaConsumidor.cs

```csharp
public interface IMediador
{
    Task<TRespuesta> EnviarAsync<TRespuesta>(
        ISolicitud<TRespuesta> solicitud,
        CancellationToken ct = default);
}
```

```csharp
// API: LicenciasEndpoints.cs
var expedida = await contexto.Mediador.EnviarAsync(
    new ExpedirLicenciaComando(
        solicitud.ConductorId, solicitud.Categoria),
    cancellationToken);
 
// Mensajería: SancionPagadaConsumidor.cs
await mediador.EnviarAsync(
    new DescontarPuntosComando(mensaje.ConductorId,
        mensaje.SancionId, mensaje.PuntosADescontar),
    cancellationToken);
```

Qué gana Licencias: la API y el consumidor dependen de una única abstracción, y el mismo comando pasa por el mismo pipeline venga de HTTP o del bus.

## Diapositiva 36

CAPA DE APLICACIÓN · 3.4

Pipeline de comportamientos: Cadena de pasos que envuelve a todos los casos de uso: registra, valida y confirma la transacción automáticamente.

BuildingBlock · genérico

ServiceCollectionExtensions.cs

Licencias · concreto

ninguna línea de código

// Chain of Responsibility: tres eslabones,
// registrados en este orden
services.AddScoped(
    typeof(IComportamientoDePipeline<,>),
    typeof(RegistroComportamiento<,>));    // 1. externo
 
services.AddScoped(
    typeof(IComportamientoDePipeline<,>),
    typeof(ValidacionComportamiento<,>));  // 2.
 
services.AddScoped(
    typeof(IComportamientoDePipeline<,>),
    typeof(TransaccionComportamiento<,>)); // 3. interno

Registro

Log «Comando ExpedirLicenciaComando completado en N ms» o «rechazado: <motivo>»

Validación

Ejecuta ExpedirLicenciaValidador, CancelarLicenciaValidador, etc.

Transacción

Guarda la licencia + bandeja de salida; las consultas pasan sin transacción

Código propio

Ninguno: los recibe gratis por registrar el ensamblado

Qué gana Licencias: ExpedirLicenciaManejador termina con AgregarAsync y no llama a ningún «guardar»: no puede olvidarse de confirmar.

## Diapositiva 37

CAPA DE APLICACIÓN · 3.5

ValidadorBase y ColectorDeErrores:  Base para validar la forma de una solicitud antes de tocar el dominio, acumulando todos los errores en una sola respuesta.

BuildingBlock · genérico

ValidadorBase.cs · ColectorDeErrores.cs

Licencias · concreto

validadores de Expedir y DescontarPuntos

```csharp
public abstract class ValidadorBase<T> : IValidador<T>
{
    public IReadOnlyList<ErrorDeValidacion> Validar(
        T instancia)
    {
        var colector = new ColectorDeErrores();
        DefinirReglas(instancia, colector); // paso variable
        return colector.Errores;
    }
    protected abstract void DefinirReglas(
        T instancia, ColectorDeErrores errores);
}
 
// ColectorDeErrores acumula todos los errores:
//   Requerido · NoVacio · Positivo · EnRango
//   EnumValido<TEnum> · Cumple
```

```csharp
// ExpedirLicenciaValidador.cs
protected override void DefinirReglas(
    ExpedirLicenciaComando instancia,
    ColectorDeErrores errores) =>
    errores
        .NoVacio(instancia.ConductorId,
            nameof(instancia.ConductorId))
        .EnumValido<CategoriaLicencia>(instancia.Categoria,
            nameof(instancia.Categoria));
 
// DescontarPuntosValidador.cs: constante del dominio
errores
    .NoVacio(instancia.ConductorId, ...)
    .NoVacio(instancia.SancionId, ...)
    .EnRango(instancia.Puntos, 1, SaldoDePuntos.Maximo,
        nameof(instancia.Puntos));
```

Qué gana Licencias: un validador por comando. Guard (dominio) lanza al primer error; el colector (aplicación) acumula todos y responde 400 con errores por campo. El límite de 300 caracteres del motivo está en ambos: el Guard es la última barrera.

## Diapositiva 38

CAPA DE APLICACIÓN · 3.6

Excepciones de aplicación: Tres excepciones para fallos que no son reglas de negocio: recurso inexistente (404), solicitud mal formada (400) y conflicto de concurrencia (409).

BuildingBlock · genérico

Excepciones/

Licencias · concreto

RenovarLicenciaManejador.cs

```csharp
// → 404
public sealed class RecursoNoEncontradoException(
    string recurso, object clave)
    : Exception($"No existe {recurso} '{clave}'.");
 
// → 400
public sealed class ValidacionException(
    IReadOnlyList<ErrorDeValidacion> errores)
    : Exception(...);
 
// → 409
public sealed class ConflictoDeConcurrenciaException(
    string mensaje) : Exception(mensaje);
```

```csharp
var licencia = await licencias.ObtenerAsync(
        new LicenciaId(comando.LicenciaId),
        cancellationToken)
    ?? throw new RecursoNoEncontradoException(
        "la licencia", comando.LicenciaId);
 
// ValidacionException: Licencias nunca la lanza;
// la lanza el pipeline con los errores de
// sus validadores.
 
// ConflictoDeConcurrenciaException: tampoco;
// la lanza la base documental si dos peticiones
// modifican la misma licencia a la vez.
```

Qué gana Licencias: solo escribe un throw, repetido en tres manejadores. Las otras dos excepciones le llegan solas desde el pipeline y desde la base documental.

## Diapositiva 39

CAPA DE APLICACIÓN · 3.7

Observadores de eventos de dominio: Clases que reaccionan a un evento dentro del mismo microservicio, después de guardar, para efectos secundarios como avisar al conductor.

BuildingBlock · genérico

ManejadorDeEventoDeDominio.cs

Licencias · concreto

NotificarLicenciaSuspendidaManejador.cs

```csharp
public abstract class
    ManejadorDeEventoDeDominio<TEvento>
    : IManejadorDeEventoDeDominio
    where TEvento : IDomainEvent
{
    public Type TipoDeEvento => typeof(TEvento);
 
    public Task ManejarAsync(IDomainEvent evento,
        CancellationToken ct) =>
        evento is TEvento tipado
            ? AlOcurrirAsync(tipado, ct)
            : Task.CompletedTask;
 
    protected abstract Task AlOcurrirAsync(
        TEvento evento, CancellationToken ct);
}
```

```csharp
public sealed class NotificarLicenciaSuspendidaManejador(
    IServicioDeNotificaciones notificaciones)
    : ManejadorDeEventoDeDominio<LicenciaSuspendida>
{
    protected override Task AlOcurrirAsync(
        LicenciaSuspendida evento, CancellationToken ct) =>
        notificaciones.NotificarAsync(new Notificacion(
            $"conductor:{evento.ConductorId}",
            "LICENCIA SUSPENDIDA",
            $"Su licencia fue suspendida: {evento.Motivo}. ...",
            CanalDeNotificacion.Email
            | CanalDeNotificacion.Sms
            | CanalDeNotificacion.Push), ct);
}
```

Qué gana Licencias: tres observadores que avisan al conductor. Cada uno recibe el evento ya tipado, sin if ni cast, y un correo fallido no deshace una licencia ya guardada: el despachador corre después de confirmar.

## Diapositiva 40

CAPA DE APLICACIÓN · 3.8

Notificaciones a las personas: Modelo del mensaje para una persona y puerto para enviarlo por correo, SMS o push sin saber cómo se entrega.

BuildingBlock · genérico

Notificaciones/

Licencias · concreto

los tres observadores de EventosDeDominio/

```csharp
[Flags]
public enum CanalDeNotificacion
{ Ninguno = 0, Email = 1, Sms = 2, Push = 4 }
 
public sealed record Notificacion
{
    public Notificacion(string destinatario,
        string asunto, string mensaje,
        CanalDeNotificacion canales)
    {
        ArgumentException
            .ThrowIfNullOrWhiteSpace(destinatario);
        ...
        if (canales == CanalDeNotificacion.Ninguno)
            throw new ArgumentException(...);
    }
}
 
// Puerto de salida: IServicioDeNotificaciones
```

NotificarLicenciaExpedidaManejador

LicenciaExpedida → Email

NotificarPuntosDescontadosManejador

PuntosDescontados → SMS + Push

NotificarLicenciaSuspendidaManejador

LicenciaSuspendida → Email + SMS + Push

Adaptador propio

Ninguno: ServicioDeNotificaciones y la fábrica de canales viven en el BuildingBlock de infraestructura

Qué gana Licencias: sus observadores construyen una Notificacion y combinan canales con |. No escribe ningún adaptador de notificación.

## Diapositiva 41

CAPA DE APLICACIÓN · 3.9

Traductores: Clases que convierten un evento de dominio en un contrato público V1 para que salga hacia otros sistemas.

BuildingBlock · genérico

Integracion/TraductorDeEventoDeDominio.cs

Licencias · concreto

Integracion/Traductores/LicenciaExpedidaTraductor.cs

```csharp
public abstract class
    TraductorDeEventoDeDominio<TEvento>
    : ITraductorDeEventoDeDominio
    where TEvento : IDomainEvent
{
    public Type TipoDeEvento => typeof(TEvento);
    protected abstract string Topico { get; }
 
    public EventoDeIntegracion Traducir(
        IDomainEvent evento) =>
        evento is TEvento tipado
            ? new EventoDeIntegracion(tipado.EventoId,
                Topico, CrearContrato(tipado),
                tipado.OcurrioEn)
            : throw new ArgumentException(...);
 
    protected abstract object CrearContrato(
        TEvento evento);
}
```

```csharp
public sealed class LicenciaExpedidaTraductor
    : TraductorDeEventoDeDominio<LicenciaExpedida>
{
    // "licencias.licencia-expedida.v1"
    protected override string Topico =>
        LicenciasTopicos.LicenciaExpedida;
 
    protected override object CrearContrato(
        LicenciaExpedida evento) => new LicenciaExpedidaV1(
        evento.EventoId, evento.OcurrioEn,
        evento.LicenciaId.Valor,      // tipo rico → primitivo
        evento.ConductorId.Valor,
        evento.NumeroLicencia,
        evento.Categoria.ToString(),  // enum → texto
        evento.Vencimiento);
}
```

Qué gana Licencias: decidir qué se publica es agregar o no un traductor: hay cuatro, y LicenciaRenovada no sale del microservicio porque no tiene el suyo. El Id y la fecha del evento se conservan solos.

## Diapositiva 42

CAPA DE APLICACIÓN · 3.10

Consumidor: Clase que recibe un evento publicado por otro microservicio y lo convierte en un comando propio.

BuildingBlock · genérico

Integracion/IManejadorDeEventoDeIntegracion.cs

Licencias · concreto

Integracion/Consumidores/SancionPagadaConsumidor.cs

```csharp
public interface
    IManejadorDeEventoDeIntegracion<in TMensaje>
{
    Task ManejarAsync(TMensaje mensaje,
        ContextoDeMensaje contexto,
        CancellationToken cancellationToken);
}
```

```csharp
public sealed class SancionPagadaConsumidor(IMediador mediador)
    : IManejadorDeEventoDeIntegracion<SancionPagadaV1>
{
    public async Task ManejarAsync(SancionPagadaV1 mensaje,
        ContextoDeMensaje contexto, CancellationToken ct)
    {
        if (mensaje.PuntosADescontar <= 0)
            return;
 
        await mediador.EnviarAsync(
            new DescontarPuntosComando(mensaje.ConductorId,
                mensaje.SancionId, mensaje.PuntosADescontar),
            ct);
    }
}
```

Qué gana Licencias: consume un contrato de otro contexto (Sanciones) y lo traduce a una intención propia. No maneja deserialización, duplicados, correlación ni transacción: todo eso lo hace ProcesadorDeMensajeEntrante.

## Diapositiva 43

CAPA DE APLICACIÓN · 3.11

IClock: Interfaz que entrega la hora actual, para que el dominio la reciba como dato y se pueda simular en las pruebas.

BuildingBlock · genérico

Tiempo/IClock.cs

Licencias · concreto

ExpedirLicenciaManejador.cs · CancelarLicenciaManejador.cs

```csharp
public interface IClock
{
    DateTimeOffset Now { get; }
}
```

```csharp
// ExpedirLicenciaManejador.cs
var ahora = reloj.Now;
var numero = await generadorDeNumeros.SiguienteAsync(
    ahora.Year, cancellationToken);
...
 
// CancelarLicenciaManejador.cs
public sealed class CancelarLicenciaManejador(ILicenciaRepository 
licencias, IClock reloj)
: IManejadorDeComando<CancelarLicenciaComando, Unidad>

//
licencia.Cancelar(comando.Motivo, reloj.Now);
 
// Los manejadores piden la hora y se la pasan
// al dominio como parámetro "ahora".
// El dominio nunca llama a DateTime.Now.
```

Qué gana Licencias: con el RelojSimulado del BuildingBlock se puede adelantar el tiempo para probar vencimientos sin esperar años.

## Diapositiva 44

CAPA DE APLICACIÓN · 3.12

Unidad de trabajo y correlación: Dos abstracciones de plataforma: una confirma todos los cambios juntos y la otra lleva el identificador que sigue una operación entre servicios.

BuildingBlock · genérico

Persistencia/IUnidadDeTrabajo.cs · Correlacion/

Licencias · concreto

ninguna referencia directa

Dos abstracciones de plataforma

Cero líneas propias

IUnidadDeTrabajo e IContextoDeCorrelacion
Las consumen piezas del propio BuildingBlock:
TransaccionComportamiento y UnidadDeTrabajoDocumental
CorrelacionMiddleware y ProcesadorDeMensajeEntrante

Licencias no las referencia en su código
Se beneficia de ellas sin conocerlas
Sus eventos salen con el CorrelacionId de la petición que los originó

Qué gana Licencias: transacción y trazabilidad de punta a punta sin escribir ni importar nada.

## Diapositiva 45

CAPA DE APLICACIÓN · 3.13

Registro por convención: Mecanismo que recorre el proyecto y registra solo los manejadores, validadores, observadores y traductores en el contenedor de dependencias.

DependencyInjection/ServiceCollectionExtensions.cs

BuildingBlock · genérico

Licencias · concreto

Licencias.Application/DependencyInjection/

```csharp
public static IServiceCollection
    AgregarBloquesDeAplicacion(
    this IServiceCollection services, Assembly ensamblado)
{
    services.AddScoped<IMediador, Mediador>();
    services.AddScoped<IContextoDeCorrelacion,
        ContextoDeCorrelacion>();
    services.AddScoped<IDespachadorDeEventosDeDominio,
        DespachadorDeEventosDeDominio>();
    // ... pipeline
    foreach (var tipo in tiposConcretos)
    {
        RegistrarInterfacesGenericas(services, tipo,
            typeof(IManejadorDeSolicitud<,>));
        RegistrarInterfacesGenericas(services, tipo,
            typeof(IValidador<>));
        // + observadores y traductores
    }
}
```

```csharp
public static IServiceCollection
    AgregarAplicacionLicencias(
    this IServiceCollection services)
{
    // 1 línea = 17 clases
    services.AgregarBloquesDeAplicacion(
       //ensamblado .dll de licencias entra como parámetro
        typeof(ServiceCollectionExtensions).Assembly); 
//El building block recorre las clases del ensamblado
//Y extrae los tipos concretos que implementan: 
IManejadorSolictud, Ivalidador, IManejadordeEventos.., 
ITraductordeEventos
    
// Lo único que registra a mano
    services.AddSingleton<IPoliticaDeVigencia,
        VigenciaPorCategoria>();
    services.AddScoped<ServicioDeExpedicion>();
    services.AddScoped<IReglaDeExpedicion,
        ReglaUnaLicenciaActivaPorCategoria>();
    services.AddScoped<IReglaDeExpedicion,
        ReglaNumeroDeLicenciaUnico>();
    return services;
}
```

Qué gana Licencias: una sola línea registra los 6 manejadores, 4 validadores, 3 observadores y 4 traductores. Un caso de uso nuevo no exige tocar este archivo.

## Diapositiva 46

CAPA DE INFRAESTRUCTURA · 4.1

Capa de Infraestructura para un microservicio

BuildingBlock · genérico

DependencyInjection/

Licencias · concreto

Licencias.Infrastructure/DependencyInjection/

```csharp
public static IServiceCollection AgregarInfraestructuraLicencias(
    this IServiceCollection services,
    EntornoDeSimulacion entorno, OpcionesDeMicroservicio opciones)
{
    // plataforma genérica
    services.AgregarBloquesDeInfraestructura(entorno, opciones);
 
    // Lo único propio: adaptadores de los puertos del dominio
    services.AddScoped<ILicenciaRepository,
        RepositorioDeLicencias>();
    services.AddScoped<IGeneradorNumeroLicencia,
        GeneradorNumeroLicenciaDocumental>();
 
    services.AgregarCanalesDeSalida(...);
    services.AgregarConsumidor<SancionPagadaV1,
        SancionPagadaConsumidor>(SancionesTopicos.SancionPagada);
    return services;
}
```

Registra la plataforma común

Reloj, serializador, broker y red
Base de datos propia y unidad de trabajo
Generador de consecutivos
Procesador de la bandeja de salida
Servicio de suscripciones
Cliente HTTP con reintentos
Notificaciones

Qué gana Licencias: con el nombre "licencias" obtiene su propia base de datos en bd/licencias, separada de la de Sanciones y Pagos: base de datos por servicio.

## Diapositiva 47

CAPA DE INFRAESTRUCTURA · 4.2

Repositorio documental genérico: Clase base que guarda y recupera cualquier agregado como documento JSON; el repositorio concreto solo indica la colección y la clave.

BuildingBlock · genérico

Persistencia/RepositorioDocumentalBase.cs

Licencias · concreto

Persistencia/RepositorioDeLicencias.cs

```csharp
public abstract class RepositorioDocumentalBase
    <TAgregado, TId, TMemento>(...)
    where TAgregado : AggregateRoot<TId>,
                      IOriginador<TAgregado, TMemento>
{
    protected abstract string Coleccion { get; } // variable
    protected abstract string ClaveDe(TId id);   // variable
 
    public Task AgregarAsync(...) / ActualizarAsync(...)
    protected Task<TAgregado?> ObtenerPorIdAsync(TId id, ...)
    protected Task<IReadOnlyList<TAgregado>> BuscarAsync(
        Func<TMemento, bool> filtro, ...)
 
    private TAgregado Materializar(Documento documento, ...)
    {
        memento ??= serializador
            .Deserializar<TMemento>(documento.Json);
        return TAgregado.RestaurarDesde(memento);
    }
}
```

```csharp
public sealed class RepositorioDeLicencias(...)
    : RepositorioDocumentalBase<Licencia, LicenciaId,
        LicenciaMemento>(baseDeDatos, unidadDeTrabajo,
        serializador), ILicenciaRepository
{
    protected override string Coleccion => "licencias";
    protected override string ClaveDe(LicenciaId id) =>
        id.Valor.ToString();
 
    public Task<Licencia?> ObtenerAsync(LicenciaId id,
        CancellationToken ct) => ObtenerPorIdAsync(id, ct);
 
    public Task<IReadOnlyList<Licencia>>
        ListarPorConductorAsync(ConductorId conductorId,
            CancellationToken ct) =>
        BuscarAsync(m => m.ConductorId == conductorId.Valor, ct);
 
    public async Task<bool> ExisteNumeroAsync(
        NumeroLicencia numero, CancellationToken ct) =>
        (await BuscarAsync(m => m.Numero == numero.Valor, ct))
            .Count > 0;
}
```

Qué gana Licencias: serialización, identity map, rastreo de cambios y restauración validada. El genérico exige IOriginador en compilación: sin CrearMemento y RestaurarDesde en Licencia, este repositorio no compilaría.

## Diapositiva 48

CAPA DE INFRAESTRUCTURA · 4.3

Unit of Work con Outbox: Componente que guarda en una sola transacción los agregados modificados y los eventos por publicar, para que nunca quede uno sin el otro.

BuildingBlock · genérico

Persistencia/UnidadDeTrabajoDocumental.cs

Licencias · concreto

uso indirecto

```csharp
public async Task ConfirmarAsync(
    CancellationToken cancellationToken = default)
{
    var eventos = _rastreados.Values
        .SelectMany(e => e.Agregado.DomainEvents)
        .ToList();
 
    // agregados nuevos o modificados → lote
    // eventos → traductores → bandeja_salida
    // mensajes consumidos → bandeja_entrada
 
    baseDeDatos.Confirmar(lote);
 
    // ClearDomainEvents() y despacho a observadores
}
```

Referencia en el código

Ninguna: la recibe RepositorioDeLicencias por el constructor y la invoca TransaccionComportamiento

Al cancelar una licencia

UPDATE licencias/<id>: el LicenciaMemento con estado Cancelada

En la misma transacción

INSERT bandeja_salida/<eventoId>: el LicenciaCanceladaV1 que produce LicenciaCanceladaTraductor

Qué gana Licencias: nunca queda una licencia cancelada sin su evento, ni un evento publicado sin su cambio.

## Diapositiva 49

CAPA DE INFRAESTRUCTURA · 4.4

Generador de consecutivos: Servicio que entrega el siguiente número de una secuencia de forma segura entre hilos; de ahí salen LIC-2026-001, 002…

BuildingBlock · genérico

Persistencia/GeneradorDeConsecutivos.cs

Licencias · concreto

Persistencia/GeneradorNumeroLicenciaDocumental.cs

```csharp
// Secuencias de negocio
// con concurrencia optimista y reintentos
public long Siguiente(string clave)
```

```csharp
// Adaptador del puerto de dominio IGeneradorNumeroLicencia
public sealed class GeneradorNumeroLicenciaDocumental(
    GeneradorDeConsecutivos consecutivos)
    : IGeneradorNumeroLicencia
{
    public Task<NumeroLicencia> SiguienteAsync(int anio,
        CancellationToken cancellationToken) =>
        Task.FromResult(NumeroLicencia.Generar(anio,
            consecutivos.Siguiente($"licencias-{anio}")));
}
```

Qué gana Licencias: un consecutivo por año (licencias-2026 → LIC-2026-001, LIC-2026-002…) seguro entre hilos, sin escribir lógica de concurrencia.

## Diapositiva 50

CAPA DE INFRAESTRUCTURA · 4.5

Canales de salida: Conjunto configurable de destinos por los que se publica cada evento: bus, auditoría, buzón de archivos y webhooks

BuildingBlock · genérico

Mensajeria/Canales/ConstructorDeCanales.cs

Licencias · concreto

Licencias.Infrastructure/DependencyInjection/

```csharp
public ConstructorDeCanales ConBusDeEventos() => ...
public ConstructorDeCanales ConBitacoraDeAuditoria() => ...
public ConstructorDeCanales ConBuzonDeArchivos(
    string patronTopico = "*") => ...
public ConstructorDeCanales ConWebhook(string host,
    string ruta, string patronTopico) => ...
 
private ConstructorDeCanales Agregar(
    ICanalDeMensajeria canal, string patronTopico)
{
    ICanalDeMensajeria decorado = new CanalConReintentos(
        canal, IntentosPorCanal, ...);
    decorado = new CanalConRegistro(decorado, _logger);
    if (patronTopico != "*")
        decorado = new CanalFiltradoPorTopico(
            decorado, patronTopico);
    ...
}
```

```csharp
services.AgregarCanalesDeSalida(canales => canales
    .ConBusDeEventos()        // otros microservicios
    .ConBitacoraDeAuditoria() // auditoria/eventos.jsonl
    .ConBuzonDeArchivos()     // buzon-archivos/licencias/
    .ConWebhook("runt", "/webhooks/licencias",
        LicenciasTopicos.Todos)); // RUNT: "licencias.*"
 
// Árbol resultante:
// CanalCompuesto "salida-licencias"
//   Registro → Reintentos → Bus
//   Registro → Reintentos → Bitácora
//   Registro → Reintentos → Buzón de archivos
//   FiltroPorTópico "licencias.*" → Registro
//       → Reintentos → Webhook RUNT
```

Qué gana Licencias: una declaración de cinco líneas produce cuatro canales con reintentos, registro y filtro (Builder + Composite + Decorator).

## Diapositiva 51

CAPA DE INFRAESTRUCTURA · 4.6

Consumo de mensajes idempotente: Proceso que recibe los mensajes del bus y descarta los repetidos, de modo que procesar uno dos veces da el mismo resultado.

BuildingBlock · genérico

Mensajeria/Consumo/ProcesadorDeMensajeEntrante.cs

Licencias · concreto

Licencias.Infrastructure/DependencyInjection/

// Una línea
services.AgregarConsumidor<SancionPagadaV1,
    SancionPagadaConsumidor>(SancionesTopicos.SancionPagada);
 
// Idempotencia en dos niveles
 
// Genérico (infraestructura):
//   ProcesadorDeMensajeEntrante + bandeja de entrada
//   evitan el mismo mensaje entregado dos veces.
 
// Concreto (dominio):
//   Licencia.DescontarPuntos con YaDescontoPorSancion
//   evita la misma sanción descontada dos veces,
//   aunque llegue en mensajes distintos.

Pasos fijos por cada mensaje

1. Abrir un alcance de dependencias
2. Propagar la correlación
3. Descartar si ya se procesó (bandeja de entrada)
4. Deserializar el contrato
5. Llamar al manejador
6. Confirmar

Qué gana Licencias: una línea lo suscribe al tópico de Sanciones; el consumidor idempotente lo pone el BuildingBlock y el dominio agrega su propia defensa.

## Diapositiva 52

CAPA DE INFRAESTRUCTURA · 4.7

Outbox, JSON y notificaciones: Piezas de infraestructura que publican los eventos pendientes, serializan a JSON y entregan las notificaciones, sin código del microservicio.

BuildingBlock · genérico

piezas que llegan con AgregarBloquesDeInfraestructura

Licencias · concreto

relación con Licencias

ProcesadorDeBandejaDeSalida

Cada 100 ms publica los pendientes por el CanalCompuesto

Publica

LicenciaExpedidaV1, PuntosDescontadosV1, etc. por sus 4 canales

SerializadorJson

JSON con enums como texto y tildes legibles

Guarda

LicenciaMemento con "Categoria": "B1" y "Estado": "Vigente"

ServicioDeNotificaciones

Implementa el puerto y envía por los canales marcados

Entrega

Las notificaciones de los 3 observadores de Licencias

EntornoDeSimulacion · OpcionesDeMicroservicio

Plataforma compartida e identidad del servicio

Identifica

Licencias es "licencias": host HTTP, origen de mensajes y nombre de la BD

Qué gana Licencias: no escribe ningún código para estas piezas.

## Diapositiva 53

CAPA DE PRESENTACIÓN (API) · 5.1

Módulo de endpoints y enrutador: Forma de declarar las rutas HTTP de un microservicio en una clase y de dirigir cada petición a su función.

BuildingBlock · genérico

IModuloDeEndpoints.cs · EnrutadorHttp.cs

Licencias · concreto

Endpoints/LicenciasEndpoints.cs

```csharp
public interface IModuloDeEndpoints
{
    void Mapear(EnrutadorHttp enrutador);
}
 
public sealed class EnrutadorHttp
{
    public EnrutadorHttp MapearGet(
        string plantilla,
        ManejadorDeRuta manejador) => ...
    public EnrutadorHttp MapearPost(
        string plantilla,
        ManejadorDeRuta manejador) => ...
    // 404 si no hay ruta,
    // 405 si existe con otro método
}
```

```csharp
public sealed class LicenciasEndpoints : IModuloDeEndpoints
{
    public void Mapear(EnrutadorHttp enrutador) => enrutador
        .MapearPost("/api/licencias", ExpedirAsync)
        .MapearGet("/api/licencias/{id}", ObtenerAsync)
        .MapearPost("/api/licencias/{id}/renovacion",
            RenovarAsync)
        .MapearPost("/api/licencias/{id}/cancelacion",
            CancelarAsync)
        .MapearGet("/api/conductores/{conductorId}/licencias",
            ListarDelConductorAsync);
}
```

Qué gana Licencias: declara sus cinco rutas en una sola clase, al estilo Minimal APIs; el enrutador genérico responde 404 y 405 por su cuenta.

## Diapositiva 54

CAPA DE PRESENTACIÓN (API) · 5.2

ContextoHttp: lo que usa un endpoint: Objeto que le da al endpoint el cuerpo JSON, los parámetros de la ruta y el mediador; responde 400 si vienen mal.

BuildingBlock · genérico

ContextoHttp.cs

Licencias · concreto

Endpoints/LicenciasEndpoints.cs

```csharp
public IMediador Mediador =>
    Servicios.GetRequiredService<IMediador>();
 
// GUID válido o ValidacionException (400)
public Guid ParametroGuid(string nombre) => ...
 
// cuerpo ausente o JSON mal formado
// → ValidacionException (400)
public T LeerCuerpo<T>() => ...
```

```csharp
private static async Task<RespuestaHttp> CancelarAsync(
    ContextoHttp contexto, CancellationToken ct)
{
    // cuerpo JSON
    var solicitud = contexto
        .LeerCuerpo<CancelarLicenciaSolicitud>();
 
    await contexto.Mediador.EnviarAsync(
        new CancelarLicenciaComando(
            contexto.ParametroGuid("id"), // {id} de la ruta
            solicitud.Motivo), ct);
 
    return Resultados.SinContenido();
}
```

Qué gana Licencias: un id que no es GUID o un JSON roto responden 400 sin que el endpoint escriba un try/catch. Los cuerpos (ExpedirLicenciaSolicitud, CancelarLicenciaSolicitud) son contratos HTTP propios, distintos de los comandos.

## Diapositiva 55

Estructura de la Capa API

| Qué hace la subcapa: | Lo que NO debe tener |
| Controllers Reciben peticiones HTTP, extraen datos, invocan comandos/queries a través de IMediator, y devuelven respuestas HTTP (201, 200, 400, etc.).  | Lógica de negocio (ej. verificar si el conductor existe). Acceso directo a repositorios. Validaciones que ya están en validators. Capturar excepciones de dominio para transformar en 400 (eso puede ir en middleware). |
| Middleware Componentes que se ejecutan en el pipeline de ASP.NET Core para manejar aspectos transversales: logging de peticiones, manejo global de excepciones (ErrorHandlingMiddleware), autenticación, compresión, etc. | Reglas de negocio. Llamadas a repositorios. Dependencias específicas de un microservicio (debe ser genérico). |

## Diapositiva 56

CAPA DE PRESENTACIÓN (API) · 5.3

Resultados: Métodos fábrica que construyen las respuestas HTTP estándar: 200, 201, 202, 204 y errores.

BuildingBlock · genérico

Resultados.cs

Licencias · concreto

Endpoints/LicenciasEndpoints.cs

```csharp
public static RespuestaHttp Ok(object cuerpo) =>
    Json(200, cuerpo);
 
public static RespuestaHttp Creado(string ubicacion,
    object cuerpo) => /* 201 + Location */;
 
public static RespuestaHttp Aceptado(object cuerpo) =>
    Json(202, cuerpo);
 
public static RespuestaHttp SinContenido() =>
    new(204, null);
 
public static RespuestaHttp Problema(int estado,
    string titulo, ...) => /* RFC 9457 */;
```

POST /api/licencias

Creado(...) · 201 + Location

GET /api/licencias/{id}

Ok(licenciaDto) · 200

POST …/{id}/renovacion

Ok(new { nuevoVencimiento }) · 200

POST …/{id}/cancelacion

SinContenido() · 204

GET /api/conductores/{conductorId}/licencias

Ok(lista) · 200

Qué gana Licencias: sus cinco endpoints responden con los mismos métodos fábrica, sin armar códigos ni encabezados a mano.

## Diapositiva 57

CAPA DE PRESENTACIÓN (API) · 5.4

Middlewares HTTP: Cadena por la que pasa toda petición antes del endpoint: asigna la correlación, registra la solicitud y captura errores.

BuildingBlock · genérico

Middlewares/ (registrados por AgregarApiSimulada)

Licencias · concreto

ninguna línea de código

1. CorrelacionMiddleware

Toma o genera el X-Correlation-Id

Chain of Responsibility ya armada

Licencias no escribe ninguna línea
Cada petición a /api/licencias... atraviesa los tres, en ese orden
Sus endpoints no registran, no correlacionan y no capturan excepciones

2. RegistroDeSolicitudesMiddleware

Registra método, ruta, código y duración

3. ManejoDeErroresMiddleware

Traduce excepciones a ProblemDetails

Qué gana Licencias: correlación, registro y manejo de errores llegan resueltos con AgregarApiSimulada.

## Diapositiva 58

CAPA DE PRESENTACIÓN (API) · 5.5

Errores de excepción a HTTP: Middleware que traduce cada excepción, venga de la capa que venga, al código HTTP y al formato de error estándar.

BuildingBlock · genérico

Middlewares/ManejoDeErroresMiddleware.cs

Licencias · concreto

situaciones reales, desde cualquier capa

```csharp
catch (ValidacionException ex)
  { return Resultados.Problema(400,
      "Solicitud inválida", ...); }
catch (RecursoNoEncontradoException ex)
  { return Resultados.Problema(404,
      "Recurso no encontrado", ...); }
catch (BusinessRuleViolationException ex)
  { return Resultados.Problema(422,
      "Regla de negocio incumplida", ex.Message,
      regla: ex.BrokenRule.GetType().Name); }
catch (DomainException ex)
  { return Resultados.Problema(400,
      "Dato inválido para el dominio", ...); }
catch (ConflictoDeConcurrenciaException ex)
  { return Resultados.Problema(409,
      "Conflicto de concurrencia", ...); }
```

Categoria = "Z9" al expedir

Aplicación · ExpedirLicenciaValidador → 400

El id de la ruta no es GUID

API · ContextoHttp.ParametroGuid → 400

Licencia inexistente al renovar

Aplicación · RenovarLicenciaManejador → 404

Renovar una licencia suspendida

Dominio · SoloSeRenuevaUnaLicenciaVigente → 422

Segunda licencia B1 activa

Dominio · ServicioDeExpedicion → 422

Un setter recibe un dato prohibido

Dominio · Guard.* → 400

Dos cancelaciones a la vez

Infraestructura · BaseDeDatosDocumental → 409

Qué gana Licencias: el orden de los catch importa: BusinessRuleViolationException hereda de DomainException y se captura antes; así una regla incumplida produce 422 y no 400.

## Diapositiva 59

CAPA DE PRESENTACIÓN (API) · 5.6

Composition root: Único lugar del microservicio que conoce todas las capas y las conecta al arrancar.

BuildingBlock · genérico

AgregarApiSimulada · ServidorApi.cs

Licencias · concreto

MicroservicioLicencias.cs

```csharp
// El único lugar donde se conocen todas las capas
constructor.Services
    .AgregarAplicacionLicencias()
        // → AgregarBloquesDeAplicacion
    .AgregarInfraestructuraLicencias(entorno,
        new OpcionesDeMicroservicio { Nombre = Nombre })
        // → AgregarBloquesDeInfraestructura
    .AgregarApiSimulada()
        // BuildingBlocks.Api
    .AgregarModuloDeEndpoints<LicenciasEndpoints>();
        // módulo propio
```

La capa de presentación común

AgregarApiSimulada() registra el servidor y los middlewares
ServidorApi hace el papel de Kestrel: un alcance de DI por petición
AgregarModuloDeEndpoints<T>() conecta el módulo del microservicio

Qué gana Licencias: cada capa tiene su método de extensión y cada uno empieza llamando al del BuildingBlock de su capa. El patrón se repite idéntico en Sanciones y Pagos.

## Diapositiva 60

PIEZAS SIN USO · 7

Piezas que Licencias no usa

BuildingBlock · genérico

Licencias · por qué no la necesita

Dinero y Guard.NoNegativo

Licencias no maneja montos (sí Sanciones y Pagos)

Especificacion.O(...) y .No()

Solo necesita combinar con Y

ColectorDeErrores.Positivo y Cumple

Sus validaciones se cubren con NoVacio, EnRango, Requerido y EnumValido

IClienteHttp y ClienteHttpConReintentos

No llama por HTTP a otros servicios: solo reacciona a eventos. Queda registrado, pero sin uso

ContextoHttp.ConsultaFecha y Resultados.Aceptado

Ningún endpoint de Licencias filtra por fecha ni responde 202

No es un defecto: el BuildingBlock sirve a los tres microservicios, y cada uno toma solo lo que necesita.

## Diapositiva 61

Glosario de Instrucciones

| Task<T> | Representa una operación asíncrona que devuelve un valor de tipo T. En las interfaces de repositorio y servicios se usa para indicar que el método no bloqueará el hilo mientras espera, por ejemplo, acceso a base de datos o llamadas HTTP.  |
| DbContext | Clase de Entity Framework Core que actúa como puente entre el código y la base de datos. Gestiona conexiones, seguimiento de cambios y operaciones CRUD. Cada microservicio tiene su propio DbContext apuntando a su propia base de datos (autocontenida).  |
| ModelBuilder | Se usa dentro del método OnModelCreating del DbContext para configurar el mapeo de las entidades a las tablas: claves primarias, índices, longitudes de campos, relaciones, etc. Permite definir cómo se persisten los value objects (owned types).  |
| Token request | Generalmente se refiere al CancellationToken que se pasa a los métodos asíncronos. Permite cancelar la operación si el cliente cancela la solicitud (por ejemplo, cierra el navegador). Se usa en los handlers de MediatR y en los repositorios. |

## Diapositiva 62

Glosario de Instrucciones

| await | Palabra clave que detiene la ejecución del método hasta que la tarea asíncrona termine, pero libera el hilo para que pueda atender otras solicitudes. Es fundamental para escalabilidad.  |
| RuleFor | Método de FluentValidation que define una regla de validación para una propiedad de un comando o DTO. Por ejemplo: RuleFor(x => x.Monto).GreaterThan(0) valida que el monto sea mayor a cero.  |
| IMapper | Interfaz de AutoMapper (o de un mapeador manual) que transforma un objeto de un tipo a otro.  |
| CreateMap | Método de AutoMapper para definir cómo se convierte una clase origen en una clase destino. Por ejemplo: CreateMap<Conductor, ConductorDto>(). Con mapeo manual no se usa.  |
| Mapping Profile | Clase que hereda de Profile en AutoMapper y agrupa todas las definiciones de CreateMap. Centraliza las reglas de transformación. En tu proyecto, al usar mapeo manual, no existe esta clase. |
