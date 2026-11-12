# 02 · El modelo ArchiMate: cómo se organiza para que el programa lo entienda

## ¿Qué es ArchiMate? (en una frase)

Es un **lenguaje para dibujar organizaciones**: quién hace qué, con qué sistemas y por qué. Se usa con una herramienta de dibujo
llamada **Archi**. El resultado es un archivo (`diseno/modelo/drones-mantenimiento.archimate`) que es, en el fondo, **una base de datos
de piezas conectadas entre sí**: cada pieza es un *elemento* y cada conexión una *relación*.

Un ejemplo cotidiano: es como el plano de una casa donde cada habitación, puerta y cañería tiene un nombre, una etiqueta y está
conectada a otras. El programa lee ese plano y entiende "esta habitación es la cocina, aquí hay una puerta a la sala".

**Este modelo en números** (medidos con el programa):

| Qué | Cuántos |
|---|---|
| Elementos | 812 |
| Relaciones entre elementos | 1.350 |
| Vistas (diagramas) | 32 |
| Contextos delimitados (los "departamentos" del software) | 9 |
| Agregados (los "objetos de negocio con reglas") | 13 |
| Comandos (las acciones que se pueden pedir) | 54 |
| Eventos de dominio (los hechos que ocurren) | 59 |
| Políticas ("cuando pasa X, haz Y") | 24 |
| Relaciones entre contextos | 33 |
| Contratos de servicio | 37 |
| Términos del lenguaje del negocio | 100 |

## Las capas del modelo (de lo abstracto a lo concreto)

El modelo se construyó en **seis fases**; cada una agrega una capa y todas viven en el mismo archivo:

```
  FASE 0   Entrevista al experto ............ (texto: qué dice el negocio)
     │
  FASE 1   MOTIVACIÓN y CAPACIDADES ......... ¿Por qué? ¿Qué sabe hacer la empresa?
     │                                        (Capability, Driver, Goal…)
  FASE 2   SERVICIOS, ACL y CONTRATOS ....... ¿Qué servicios ofrece? ¿Con qué sistemas externos habla?
     │                                        (BusinessService, Contract)
  FASE 3   DOMINIOS y LENGUAJE ............... ¿Cómo se llaman las cosas? ¿Cuáles son los "departamentos"?
     │                                        (Grouping "Dominio: …", BusinessObject)
  FASE 4   AGREGADOS, COMANDOS y EVENTOS .... ¿Qué objetos tienen reglas? ¿Qué acciones? ¿Qué hechos?
     │                                        (DataObject, ApplicationProcess, ApplicationEvent)
  FASE 5   MAPA DE CONTEXTOS ................. ¿Cómo se relacionan los departamentos entre sí?
     │                                        (tabla de relaciones: asíncrona / síncrona)
  FASE 6   CANVAS y TRAZABILIDAD ............. Ficha de un contexto y el rastro de cada decisión
```

Para el programa, **las fases 2 a 5 son las importantes**: de ellas sale casi todo lo que se construye.

## Los dos insumos que lee el programa

El programa necesita **dos cosas a la vez**:

```
   ┌───────────────────────────────┐        ┌────────────────────────────────────────┐
   │  1. El archivo .archimate      │        │  2. Los documentos de fase (.md)        │
   │     (los elementos y sus       │   +    │     con tablas que NO caben bien en el  │
   │      relaciones, con etiquetas)│        │     dibujo: contratos, relaciones entre │
   │                                │        │     contextos, errores de cada servicio │
   └───────────────────────────────┘        └────────────────────────────────────────┘
        diseno/modelo/*.archimate                 diseno/Fase02/04_contratos_servicios.md
                                                  diseno/Fase05/01_mapa_de_contextos.md
```

> **Por qué dos.** El dibujo es ideal para estructura (qué contiene qué), pero las tablas largas (por ejemplo "este contrato puede fallar con
> SERIE_FALTANTE o ORDEN_CERRADA_INMUTABLE") son más claras en texto. El programa une ambas fuentes.

## Las "etiquetas" que el programa busca (la parte más importante)

El programa no "adivina" el significado de un dibujo: busca **etiquetas concretas** (propiedades y frases de la documentación).
Esta es la tabla completa de lo que lee y cómo debe estar escrito:

| Qué quiere reconocer | Tipo de elemento ArchiMate | Cómo debe estar marcado | Ejemplo real del modelo |
|---|---|---|---|
| **Un contexto** (un "departamento" del software) | Componente de aplicación | La documentación contiene `contexto delimitado «Nombre»` y la propiedad `Clasificación` (Core, Soporte, Genérico) | `Intervenciones` — *«Componente del contexto delimitado «Intervenciones» (Core)…»* |
| **A qué contexto pertenece un agregado** | Agrupación (Grouping) | Nombre `Dominio: <Contexto>`, con relaciones de *agregación* hacia los agregados que contiene | `Dominio: Intervenciones` agrupa Orden de trabajo, Hallazgo, Vuelo de prueba… |
| **Un agregado y sus piezas** | Objeto de datos | Propiedades `Agregado` (a cuál pertenece) y `Rol` = `Raíz`, `Entidad` o `VO` (objeto de valor) | `Orden de trabajo` → Rol: Raíz, Agregado: Orden de trabajo |
| **Cómo se contienen las piezas** | Relación de composición | Entre las piezas del mismo agregado | La orden contiene tareas ejecutadas y consumos |
| **Un comando** (una acción pedida) | Proceso de aplicación | Propiedad `Agregado` | `Abrir orden de trabajo` → Agregado: Orden de trabajo |
| **Quién puede pedir un comando** | Rol de negocio + relación de asociación | Asociar el rol al comando | Jefe de Operaciones ↔ Liberar dron |
| **Un evento de dominio** (un hecho ocurrido) | Evento de aplicación | Propiedad `Agregado` | `Orden de trabajo abierta` |
| **Qué evento causa qué comando** (política) | Relación de disparo (Triggering) | De un evento a un comando | `Parada programada` → `Abrir orden de trabajo` |
| **Un evento que viene de afuera** | Evento de negocio | Como origen de una relación de disparo hacia un comando | Eventos externos (2 en este modelo) |
| **Un servicio del contexto** | Servicio de aplicación | La documentación contiene `contexto «Nombre»` | — |
| **Una interfaz del contexto** | Interfaz de aplicación | Ídem | — |
| **El lenguaje del negocio** | Objeto de negocio | Propiedad `Contexto` (+ `Ejemplo` y `No usar`) | Orden de trabajo — *No usar: ticket, solicitud* |
| **Los roles de usuario** | Rol de negocio | Nombre y descripción | Piloto remoto, Jefe de Operaciones y Mantenimiento, Técnico… |
| **Un contrato de servicio** | Contrato | Propiedades `Servicio`, `Versión`, `Nivel` (N2/N3/N4), `RNF` | Contrato de ejecución y liberación de intervenciones v1.0.0 |

### Lo que viene de las tablas de texto

| Documento | Tabla | Qué aporta al programa |
|---|---|---|
| `Fase05/01_mapa_de_contextos.md` | "Contexto A (upstream) · Contexto B (downstream) · … · Mecanismo · Sinc./Asinc." | Quién se comunica con quién, con qué evento o API, y si es **asíncrono** (evento) o **síncrono** (llamada) |
| `Fase05/01_mapa_de_contextos.md` | "Contexto · … · Agregados que contiene" | Respaldo para saber a qué contexto pertenece cada agregado |
| `Fase02/04_contratos_servicios.md` | Una tabla por servicio | Las reglas de negocio con nombre (**errores** como `SERIE_FALTANTE`), precondiciones, requisitos no funcionales |

## Cómo se convierte en algo que el programa entiende: el "IR"

El archivo `.archimate` pesa **1,3 MB** de XML. Ni una persona ni un agente de IA deberían leerlo crudo. Por eso el primer paso del
programa es **traducirlo a un resumen compacto** llamado **IR** (*Intermediate Representation*, "representación intermedia"):

```
  .archimate (1,3 MB, XML)                           IR (JSON, compacto)
 ┌──────────────────────────┐                   ┌──────────────────────────────────┐
 │ 812 elementos            │                   │ contexts      : 9                │
 │ 1.350 relaciones         │   ─── lee ───►    │ aggregates    : 13               │
 │ XML difícil de leer      │   + tablas .md    │ commands      : 54               │
 └──────────────────────────┘                   │ events        : 59               │
                                                │ policies      : 24               │
                                                │ context_relations : 33           │
                                                │ contracts     : 37               │
                                                │ ubiquitous_language : 100        │
                                                └──────────────────────────────────┘
```

Cada elemento del IR conserva **el identificador original de ArchiMate**. Eso permite la **trazabilidad**: para cualquier clase del código se
puede decir "esta clase existe porque el elemento X del modelo lo pidió" (ver `entrega-v3/docs/<servicio>/trazabilidad.md`).

## Del IR al "manifiesto": la lista de compras del código

Con el IR y las decisiones del arquitecto, el programa arma el **manifiesto**: una lista de **todo lo que debe existir en el código**.

Ejemplo con el servicio Intervenciones (110 símbolos esperados) y Repuestos (100 símbolos):

```
 Del modelo                          Se espera en el código
 ──────────                          ──────────────────────
 Agregado "Orden de trabajo"    ──►  OrdenDeTrabajo (raíz), IOrdenDeTrabajoRepository, OrdenDeTrabajoMemento…
 Comando "Abrir orden…"         ──►  AbrirOrdenDeTrabajoComando, …Manejador, …Validador, …Solicitud (API), una prueba
 Evento "Orden … abierta"       ──►  OrdenDeTrabajoAbierta (evento de dominio)
 Error "SERIE_FALTANTE"         ──►  clase de regla SerieFaltante (el nombre sale del código de error)
 Evento que cruza contextos     ──►  contrato V1, traductor, consumidor, tópico del bus
 Comando con rol de usuario     ──►  un formulario web (…Form)
```

Más adelante, la compuerta de **conformidad** comprueba que cada línea de esa lista exista de verdad en el código, en la capa correcta.

## Reglas prácticas para que un modelo "se pueda ejecutar"

Si alguien quiere usar **otro** ArchiMate con este programa, el modelo debe cumplir esto:

1. **Cada contexto es un Componente de aplicación** cuya documentación diga `contexto delimitado «Nombre»`.
2. **Cada agregado tiene una raíz** (`Rol = Raíz`) y pertenece a **un** contexto (por Grouping `Dominio: …` o por la tabla de la Fase 5).
3. **Cada comando** (proceso de aplicación) **dice a qué agregado pertenece** y **emite al menos un evento** (relación de disparo).
4. **Cada evento** pertenece a un agregado y **tiene un comando que lo emite**.
5. **Las políticas** (evento → comando) que cruzan contextos son las que se vuelven **eventos de integración** entre servicios.
6. **La tabla de relaciones entre contextos** (Fase 5) indica si cada relación es asíncrona (evento) o síncrona (API).
7. **Los contratos** listan sus errores con nombres en MAYÚSCULAS_CON_GUION_BAJO: cada uno se vuelve una **regla de negocio** nombrada.

El programa **valida esto antes de construir** y **se detiene** con un mensaje claro si algo falla (por ejemplo: "Comando X no emite ningún
evento", "Agregado Y sin contexto").

## Limitaciones conocidas (para ser honestos en la exposición)

- Hay una **tabla fija dentro del programa** (`N3_TO_CONTEXT`) que une los servicios de nivel 3 de este modelo con sus contextos. Para un
  ArchiMate con otros nombres de servicio hay que agregar esa correspondencia. Es el pendiente principal para lograr un programa
  100 % independiente del modelo.
- Los **campos de los eventos** (por ejemplo, qué datos trae "Parada programada") **no están en el modelo**: ArchiMate nombra el evento pero no
  define su contenido. Esos campos son **supuestos de diseño** y están declarados en un solo lugar (`forge/eventcontracts.py`).
- Los contratos de **nivel N2** (de plataforma) cruzan contextos y quedan sin contexto en el modelo; el programa los asigna al contexto cuyas
  operaciones coinciden con los comandos (ver doc 03).

---
Anterior: [01 · Qué es](01-que-es.md) · Siguiente: [03 · Cómo funciona el programa](03-como-funciona-el-programa.md)
