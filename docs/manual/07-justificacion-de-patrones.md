# 07 · Los patrones de diseño: cuáles se usan, dónde están y por qué no otros

## 1. ¿Qué es un patrón? (sin tecnicismos)

Un **patrón de diseño** es una **receta probada** para resolver un problema que se repite al programar. Como en la cocina: no es un plato terminado,
es una técnica ("cómo se hace una salsa") que se adapta a cada plato.

Ejemplo cotidiano: un **semáforo** es un patrón para resolver "¿cómo evitar que dos autos choquen en un cruce?". Funciona en cualquier ciudad.

**Un patrón no es bueno ni malo en sí mismo.** Resuelve un problema a cambio de un costo (más clases, más complejidad). Por eso
**un patrón se elige cuando el problema existe, no "porque sí"**. Usar demasiados es tan malo como no usar ninguno.

## 2. Cómo se eligen los patrones en ArchiForge

```
   CATÁLOGO DE 50 PATRONES                 EL ARQUITECTO                       EL PROGRAMA
 ┌──────────────────────────┐        ┌──────────────────────┐        ┌────────────────────────────┐
 │ Cada ficha explica:       │        │ Marca los que usa y   │        │ Pide al agente que los      │
 │  · qué es                 │  ───►  │ escribe POR QUÉ       │  ───►  │ implemente, y las compuertas│
 │  · cuándo sirve           │        │ (nada viene marcado)  │        │ comprueban que su ESTRUCTURA│
 │  · cuándo NO sirve        │        └──────────────────────┘        │ exista de verdad en el      │
 │  · costo                  │                                         │ código                      │
 └──────────────────────────┘                                          └────────────────────────────┘
        no recomienda nada                  decide una persona               "un patrón de adorno" se rechaza
```

El catálogo (`archiforge/catalog/*.toml`) tiene **50 patrones** en 9 categorías y **no recomienda ni valora**: solo describe.

| Categoría | Cantidad | Ejemplos |
|---|---|---|
| Aplicación | 4 | CQRS, Pipeline, DTO, Service Layer |
| Dominio | 5 | Specification, Repository, Domain Events, Domain Service, Null Object |
| Integración | 6 | Outbox, Eventos, ACL, Saga, Idempotent Consumer, Dead Letter Queue |
| Infraestructura | 2 | Caché, Cifrado |
| Persistencia | 5 | Unit of Work, Data Mapper, Identity Map, Event Sourcing, Materialized View |
| Resiliencia | 5 | Circuit Breaker, Retry, Timeout, Bulkhead, Rate Limiter |
| Comportamiento (GoF) | 11 | Memento, State, Chain of Responsibility, Command, Mediator, Observer, Strategy, Template Method… |
| Creacionales (GoF) | 5 | Factory Method, Abstract Factory, Builder, Prototype, Singleton |
| Estructurales (GoF) | 7 | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |

## 3. Los patrones elegidos en este proyecto

| Patrón | Intervenciones (C#) | Repuestos (Python) |
|---|:-:|:-:|
| CQRS con mediador | ✅ | — |
| Pipeline (cadena de comportamientos) | ✅ | — |
| Memento | ✅ | ✅ |
| State | ✅ | ✅ |
| Specification | ✅ | — |
| Outbox transaccional | ✅ | ✅ |
| Eventos de integración + consumidores idempotentes | ✅ | ✅ |
| ACL (capa anticorrupción) | ✅ | ✅ |
| Caché (decorador del repositorio) | ✅ | ✅ |
| Cifrado de datos personales | ✅ | ✅ |

La política del equipo exige además **memento, caché y cifrado en cada servicio** (por eso están en ambos).

---

## 4. Cada patrón elegido: qué es, dónde está y por qué

### 4.1 CQRS con mediador (Intervenciones)

**En palabras simples:** separar **las órdenes** ("abrí esta orden", que cambian cosas) de **las preguntas** ("mostrame esta orden", que solo leen).
Como en un restaurante: quien toma el pedido y quien consulta el menú no necesitan ser lo mismo.

**Dónde está en el código:** cada acción es un **comando** con su propio **manejador** y **validador** (`AbrirOrdenDeTrabajoComando` → `…Manejador` → `…Validador`);
las lecturas son **consultas** (`ObtenerOrdenDeTrabajoConsulta`). Un **mediador** recibe el pedido y lo entrega a quien corresponde: los controladores no conocen a los manejadores.

**Por qué aquí:** la orden tiene **9 comandos** con reglas distintas y lecturas con forma distinta a la del agregado (un DTO plano para la pantalla). Separarlos mantiene cada clase pequeña y fácil de probar.

**Costo:** muchas clases (una por comando, validador, solicitud…). Por eso **no se usó en Repuestos**, que es más pequeño.

### 4.2 Pipeline / Cadena de comportamientos (Intervenciones)

**En palabras simples:** una **cadena de montaje**: cada pedido pasa por estaciones en orden. Aquí: **Registro → Validación → Transacción**.

**Dónde:** `RegistroComportamiento`, `ValidacionComportamiento`, `TransaccionComportamiento` envuelven a **todos** los manejadores.

**Por qué:** así validar, registrar y confirmar la transacción **se hace igual en todos los casos de uso**, sin repetir código en cada manejador.

**Costo:** medio; cuesta rastrear el flujo si no se conoce la cadena.

### 4.3 Memento (ambos)

**En palabras simples:** una **fotografía** del estado de un objeto, que se puede guardar y luego usar para reconstruirlo. Como guardar la partida en un videojuego.

**Dónde:** `OrdenDeTrabajoMemento` (C#) y `ExistenciaMemento` / `SolicitudDeReposicionMemento` (Python). El agregado sabe crearse y restaurarse desde su fotografía.

**Por qué:** el **dominio no debe conocer la base de datos**. La fotografía (solo datos simples) es lo que se persiste: un **documento** en MongoDB, un **JSON** en PostgreSQL.
Es lo que permite cambiar la base sin tocar las reglas.

**Costo:** bajo-medio: una clase de datos por agregado.

### 4.4 State (ambos)

**En palabras simples:** un objeto que **se comporta distinto según su etapa**, y solo permite ciertos pasos. Como un semáforo: de rojo se pasa a verde, no a "intermitente".

**Dónde:** la orden pasa por **Abierta → En espera → En ejecución → Ejecutada → Liberada → Cerrada**, cada una como una clase (`Estados/*.cs`) que dice qué transiciones acepta.
En Repuestos, la existencia (disponible → reservado → consumido → bajo mínimo → reponiendo) y la solicitud (abierta → aprobada/cancelada).

**Por qué:** el negocio **exige** que no se pueda liberar una orden que no está ejecutada ni modificar una cerrada. Con State, **esas reglas viven en un solo lugar** y no en `if` dispersos.

**Costo:** medio (una clase por estado).

### 4.5 Specification (Intervenciones)

**En palabras simples:** reglas de negocio **pequeñas y combinables** (como piezas de Lego): "requiere serie" **Y** "no tiene serie instalada".

**Dónde:** `Especificacion<T>` con `ConsumoRequiereSerie`, `ConsumoConSerieInstalada`, `TareaEjecutadaPor`; la regla `SerieFaltante` las combina.

**Por qué:** hay varias reglas del taller que se **combinan y reutilizan** (quién ejecutó, qué repuesto exige serie). Cada condición se prueba sola.

**Costo:** medio. **No se usó en Repuestos** porque allí las reglas son pocas y cada una se usa una sola vez.

### 4.6 Outbox transaccional (ambos)

**En palabras simples:** **primero anotar el aviso en una libreta junto con el cambio, y después un mensajero lo reparte.** Así nunca ocurre "guardé el dato pero me olvidé de avisar".

**Dónde:** `BandejaDeSalida` + un **despachador** que publica con reintentos (en C#, el dato y el mensaje se guardan en **la misma transacción**; en Python, el mensaje se guarda de forma durable en PostgreSQL, pero en operación separada — ver doc 05).

**Por qué:** porque ambos servicios **publican eventos que no pueden perderse** (por ejemplo, el cierre de una orden descuenta stock en otro servicio).

**Costo:** medio: una tabla/colección extra y un proceso que despacha.

### 4.7 Eventos de integración + consumidor idempotente (ambos)

**En palabras simples:** los servicios se **avisan hechos** con mensajes versionados (`…v1`), y quien los recibe **sabe ignorar un aviso repetido**.

**Dónde:** contratos `…V1`, **traductores** (de evento interno a contrato público), **consumidores** y la **bandeja de entrada** que recuerda los `eventId` ya procesados.

**Por qué:** el modelo define las relaciones entre contextos como **asíncronas**. Y como la entrega es "al menos una vez", el mismo mensaje puede llegar dos veces: sin idempotencia, se descontaría el stock dos veces.

**Costo:** medio.

### 4.8 ACL — Capa anticorrupción (ambos)

**En palabras simples:** un **intérprete** entre dos idiomas. Impide que el vocabulario de un sistema externo "contamine" el propio.

**Dónde:** `IConsultaDeHabilitacion` (puerto) + `ConsultaDeHabilitacionAdapter` (C#): consulta a Habilitación de Personal y traduce su respuesta a un simple **sí/no**. En Repuestos, `IEnviarAviso` + `EnviarAvisoAdapter`.

**Por qué:** el dominio **nunca debe ver el formato del otro sistema**; si ese sistema cambia, solo cambia el adaptador. Además el adaptador pone **tiempo máximo** (5 s) y convierte el fallo en un error claro (503).

**Costo:** bajo-medio: un puerto y un adaptador por API externa.

### 4.9 Caché como decorador de repositorio (ambos)

**En palabras simples:** una **memoria de corto plazo** delante de la base de datos: lo consultado hace poco se responde sin volver a buscarlo, y se **borra cuando el dato cambia**.

**Dónde:** `RepositorioCacheadoOrdenDeTrabajo` (C#) y `RepositorioCacheadoExistencia` / `…Solicitud…` (Python, con vencimiento de 60 s). Son **decoradores**: tienen la misma interfaz que el repositorio real y lo envuelven.

**Por qué:** las pantallas consultan la orden y las existencias con frecuencia y los datos cambian poco entre consultas; la caché se **invalida al escribir**.

**Costo:** bajo en código, pero **exige una política de invalidación**. *Límite honesto:* con varias réplicas del servicio, cada una tendría su propia caché.

### 4.10 Cifrado de datos personales (ambos)

**En palabras simples:** **guardar los datos personales "en código"**, de modo que quien lea la base de datos no entienda nada sin la clave.

**Dónde:** el puerto `Cifrador` con `CifradorAes` (AES-256-GCM). En Intervenciones se aplica en la serialización de la orden (`SerializadorDeOrdenCifrado`); en Repuestos, a los eventos pendientes de la bandeja de salida.

**Por qué:** los contratos exigen proteger datos de personas (**Ley 1581 de 2012**).

**Costo:** bajo; la clave viaja por variable de entorno (ver límites en el doc 06).

---

## 5. Patrones que aparecen sin haberlos "marcado"

Algunos patrones **aparecen como consecuencia natural** de los elegidos, o están en la base común del servicio. Conviene conocerlos para no sorprenderse:

| Patrón | Dónde aparece | Por qué está |
|---|---|---|
| **Repository** | `IOrdenDeTrabajoRepository`, `IExistenciaRepository` | Es lo que oculta la base de datos al dominio; es parte de la arquitectura (Clean/Hexagonal) |
| **Domain Events** | Eventos como `OrdenDeTrabajoCerrada` levantados por el agregado | Base de los eventos de integración y de las políticas internas |
| **Decorator** | Caché y cifrado | Así se implementan esos dos patrones |
| **Mediator** | El mediador de CQRS | Es la pieza central de CQRS |
| **Template Method** | Una clase base `ManejadorDeComandoDeOrden<T>` que define el esqueleto de "cargar la orden → ejecutar → guardar" y cada comando rellena su paso | Evita repetir ese esqueleto en los 9 manejadores |
| **Unit of Work + Identity Map** | La unidad de trabajo de C# rastrea los agregados cargados, evita cargarlos dos veces y los confirma junto con sus mensajes | Hace posible el outbox transaccional |
| **Observer** | `StockMinimoAlcanzadoObservador` (Python): al llegar al mínimo, solicita reposición y avisa | Reacción interna a un evento del mismo servicio |

---

## 6. Los patrones que NO se usaron (y por qué)

No usar un patrón también es una decisión. Esta es la lista de los más consultados, con el motivo **para este proyecto**:

### Integración y persistencia

| Patrón | Qué haría | Por qué no aquí |
|---|---|---|
| **Saga** | Coordinar una operación larga entre varios servicios con pasos y compensaciones | Cada operación vive dentro de **un** servicio y una transacción local alcanza; la coordinación entre servicios es por eventos simples. Costo alto |
| **Event Sourcing** | Guardar solo la secuencia de eventos y reconstruir el estado reproduciéndolos | Daría auditoría total, pero añade versionado de eventos y proyecciones; un historial simple alcanza. Costo alto |
| **Materialized View** | Vistas de lectura precalculadas | Las consultas actuales son simples y rápidas |
| **Data Mapper** | Una capa de mapeo entre objetos y tablas | El memento ya cumple esa función |

### Resiliencia

| Patrón | Qué haría | Estado en el proyecto |
|---|---|---|
| **Timeout** | Tiempo máximo de espera por llamada | **Sí existe** como práctica: el ACL y el bus lo aplican, aunque no se marcó como patrón independiente |
| **Retry** | Reintentar con espera creciente | **Sí existe** en el despachador de la bandeja y en el bus |
| **Dead Letter Queue** | Apartar mensajes que no se pueden procesar | **Sí existe** en el bus con RabbitMQ (cola `.dlq` + reproceso), no en los servicios |
| **Circuit Breaker** | Dejar de llamar a un servicio que está fallando | **No se usó**: las llamadas síncronas son solo dos y con tiempo máximo. Si se multiplicaran, sería lo siguiente a agregar |
| **Bulkhead** | Aislar recursos por dependencia | Una sola dependencia síncrona por servicio: sin ganancia |
| **Rate Limiter** | Limitar peticiones por unidad de tiempo | Tráfico bajo y de usuarios internos |

### Comportamiento (GoF)

| Patrón | Por qué no |
|---|---|
| **Strategy** | No hay una familia de algoritmos intercambiables (una sola variante de cada comportamiento) |
| **Observer** (como patrón elegido) | Solo aparece donde hace falta (Repuestos); no hay múltiples interesados dentro de un servicio |
| **Command** (GoF) | Los comandos de CQRS ya cumplen ese papel |
| **Visitor / Interpreter / Iterator** | No hay jerarquías cerradas que recorrer, gramáticas que interpretar ni colecciones propias |

### Creacionales y estructurales (GoF)

| Grupo | Por qué no |
|---|---|
| **Factory Method / Abstract Factory / Builder / Prototype** | Los objetos se crean con pocos datos obligatorios; los métodos estáticos del dominio (como `OrdenDeTrabajo.Abrir`) son suficientes |
| **Singleton** | La inyección de dependencias con vida de un solo objeto da lo mismo **sin** el acceso global que dificulta las pruebas |
| **Adapter / Facade / Proxy** | El ACL es un caso de *Adapter* y está elegido; los demás no resuelven un problema presente |
| **Composite / Bridge / Flyweight** | No hay jerarquías parte-todo, dos dimensiones de variación ni millones de objetos repetidos |

> **Cómo defenderlo en una frase:** *"No usamos un patrón si el problema que resuelve no existe en este negocio. Cada uno que usamos tiene una clase concreta en el código y una compuerta que lo comprueba."*

---

## 7. ¿Cómo sabemos que el patrón está de verdad y no es solo un nombre?

Es un riesgo conocido: crear una clase llamada `Cache` que nadie usa **cumple "en papel"** pero no hace nada. Por eso hay varios controles, que se
complementan:

1. **Lista de símbolos esperados (conformidad).** Al elegir un patrón, el manifiesto agrega a la lista de "lo que debe existir" sus clases concretas.
   Por ejemplo: Memento → un `…Memento` por agregado; Caché → un `RepositorioCacheado…` por agregado; Cifrado → el puerto `Cifrador` y su implementación; Outbox → la
   bandeja de salida y el procesador de mensajes entrantes. La compuerta de conformidad comprueba que cada una esté **declarada en la capa correcta**.
2. **Compuerta de cableado.** Toda clase concreta de la capa de salida (base de datos, caché, cifrado, bus, ACL) **debe usarse desde otro archivo de producción**;
   una clase que solo aparece en su propio archivo o en pruebas se rechaza como "patrón de adorno".
3. **Documento de decisiones (ADR).** Su tabla debe tener **una fila por patrón elegido** con **clases reales** que existan en el servicio.
4. **Comprobación estructural propia** (solo para los patrones que tienen una forma reconocible). El catálogo declara, para 34 de los 50 patrones, una comprobación automática:
   por ejemplo, *Decorator* y *Proxy* (una clase que envuelve a otra de su misma interfaz), *Template Method* (una clase base con pasos redefinibles), *Observer*
   (una lista de suscriptores), *Singleton* (instancia única) o *Builder* (constructor fluido). Si el arquitecto eligiera alguno de esos, también se verificaría.
5. **Pruebas.** Cada comando tiene su prueba; las compuertas ejecutan la suite de cada servicio.

> **Honestidad:** los 10 patrones elegidos aquí se verifican por los controles 1, 2, 3 y 5; la comprobación estructural propia (4) existe para otros patrones del catálogo.
> Las compuertas son **heurísticas**: detectan señales y ausencias, no prueban que el diseño sea el ideal. Por eso hay además una revisión independiente (etapa S50) y una
> revisión de código humana.

---

## 8. Los principios SOLID

Los patrones son **herramientas**; SOLID son **principios** que dicen si el diseño es sano. Cómo se aplican aquí:

| Principio | En palabras simples | Dónde se ve |
|---|---|---|
| **S** — Responsabilidad única | Una clase, una razón para cambiar | Un manejador por comando; una regla por clase; separación dominio / aplicación / infraestructura |
| **O** — Abierto/cerrado | Se extiende **agregando**, no editando | Agregar un estado o una regla = una clase nueva; el pipeline admite más comportamientos |
| **L** — Sustitución de Liskov | Un sustituto debe poder reemplazar al original sin sorpresas | Los repositorios decorados (caché) y los de memoria o reales son intercambiables |
| **I** — Segregación de interfaces | Interfaces pequeñas, a la medida del cliente | Puertos de una o dos operaciones (`IConsultaDeHabilitacion`, `IEnviarAviso`, `Cifrador`) |
| **D** — Inversión de dependencias | Lo importante no depende de lo concreto | El dominio define los puertos y la infraestructura los implementa; las compuertas lo comprueban |

**Una revisión de código real** (ver doc 08) encontró desviaciones que se corrigieron, y otras que se reportaron: por ejemplo, `OrdenDeTrabajo` (197 líneas, con la lógica del
memento incluida) y la clase de endpoints de Repuestos (12 manejadores en el constructor) están **cerca del límite** de responsabilidades; no son "clases dios", pero
conviene partirlas si siguen creciendo.

---
Anterior: [06 · Justificación de tecnologías](06-justificacion-de-tecnologias.md) · Siguiente: [08 · Calidad y pruebas](08-calidad-y-pruebas.md)
