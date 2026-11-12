# 05 · El producto generado: topología y comunicación

Este documento muestra **cómo quedan armadas las piezas** cuando el producto está corriendo y **cómo se hablan entre sí**.

## 1. Vista general: todas las piezas

```
                                   NAVEGADOR  (http://localhost:8080)
                                         │
                                         ▼
 ┌───────────────────────────────────────────────────────────────────────────────────────────┐
 │  GATEWAY  (nginx)  — la única puerta de entrada                                            │
 │     /                    → pantallas web (panel + microfrontends)                          │
 │     /api/intervenciones/ → servicio Intervenciones                                         │
 │     /api/repuestos/      → servicio Repuestos del Taller                                   │
 │     /bus/                → bus de eventos (estado, mensajes muertos)                       │
 │     /sim/                → simuladores                                                     │
 └──────────┬──────────────────────────┬─────────────────────────────┬──────────────┬─────────┘
            │                          │                             │              │
            ▼                          ▼                             ▼              ▼
 ┌─────────────────────┐   ┌─────────────────────┐        ┌──────────────────┐ ┌──────────────┐
 │   INTERVENCIONES    │   │ REPUESTOS DEL TALLER │        │    EVENT-BUS     │ │ SIMULADORES  │
 │   C# / .NET 8       │   │ Python / FastAPI     │        │  (puente HTTP)   │ │ (contextos   │
 │   Clean + DDD       │   │ Hexagonal            │        │  :5100           │ │  no          │
 │   puerto 5101       │   │ puerto 5102          │        └────────┬─────────┘ │  construidos)│
 └───┬────────┬────────┘   └───┬─────────┬────────┘                 │           │  :5110       │
     │        │                │         │                          ▼           └──────────────┘
     │        │ publica y      │         │ publica y        ┌──────────────────┐
     │        │ recibe eventos │         │ recibe eventos   │    RABBITMQ      │
     │        └────────────────┼─────────┼─────────────────►│  (los mensajes   │
     │                         │         └─────────────────►│   esperan aquí)  │
     ▼                         ▼                            │  :5672  UI :15672│
 ┌───────────┐          ┌─────────────┐                     └──────────────────┘
 │  MONGODB  │          │ POSTGRESQL  │
 │ (réplica  │          │             │
 │  rs0)     │          │             │
 └───────────┘          └─────────────┘
```

**Lectura rápida:** el navegador solo habla con el gateway. Cada servicio tiene **su propia base de datos** (nadie más la toca).
Los servicios **no se llaman entre sí**: publican y reciben **eventos** a través del bus y RabbitMQ.

## 2. Los dos canales de comunicación

Hay solo **dos formas** de que algo hable con algo. Entender la diferencia es entender la interoperabilidad:

```
 CANAL 1 · EVENTOS (asíncrono)                          CANAL 2 · LLAMADA DIRECTA (síncrona)
 ─────────────────────────────                          ────────────────────────────────────
 "Avisar que algo ocurrió"                              "Preguntar y esperar la respuesta"

   Servicio A ──► bus ──► Servicio B                      Servicio A ──► (capa anticorrupción) ──► Sistema externo
   (A no sabe quién escucha)                              (A espera la respuesta, con tiempo máximo)

 Ejemplo: "Orden de trabajo cerrada"                    Ejemplo: "¿El técnico Ana tiene habilitación vigente?"
 Cuándo: lo que pasó importa, pero quien                Cuándo: se necesita la respuesta AHORA para
 lo recibe no tiene que responder ya.                   poder continuar.
```

| | Eventos | Llamada directa |
|---|---|---|
| Acoplamiento | Bajo: el emisor ignora quién escucha | Mayor: el emisor depende de que el otro responda |
| Si el otro está caído | El mensaje **espera** y se entrega al volver | La operación **falla** (respuesta 503) |
| Cuándo se usa en este producto | Para todo el flujo de negocio entre contextos | Solo para consultas puntuales (habilitación, avisos) |

El **mapa de contextos** del diseño (Fase 5) ya decía cuál es cuál: casi todas las relaciones entre contextos son **asíncronas**, y solo las
consultas a Habilitación y Notificaciones son síncronas. El producto respeta eso.

## 3. Los eventos que circulan

| Tópico (nombre del evento) | Quién lo publica | Quién lo recibe |
|---|---|---|
| `plan-de-mantenimiento.parada-programada.v1` | Plan de Mantenimiento *(simulado)* | **Intervenciones** y **Repuestos** |
| `intervenciones.orden-de-trabajo-cerrada.v1` | **Intervenciones** | **Repuestos**, Flota y Componentes, Plan de Mantenimiento e Indicadores *(estos tres simulados)* |
| `repuestos-del-taller.faltante-detectado.v1` | **Repuestos** | **Intervenciones** |

**Cómo se lee un nombre de tópico:** `<contexto>.<evento>.v<versión>`. La **versión** (`v1`) permite que el contrato evolucione sin romper
a nadie: se *agregan* campos opcionales y, si hiciera falta un cambio incompatible, nacería un `v2` en paralelo.

**El sobre** (igual para todos los eventos):

```json
{
  "eventId":       "uuid — el mismo del evento de dominio; sirve para no procesarlo dos veces",
  "topic":         "intervenciones.orden-de-trabajo-cerrada.v1",
  "occurredOn":    "2026-11-20T15:30:00Z",
  "correlationId": "uuid — sigue una operación a través de varios servicios",
  "payload":       { "…": "los datos del hecho" }
}
```

## 4. Tres historias completas

### Historia A · "Se programó una parada" (un evento, dos reacciones)

```
 Plan de Mant.      BUS / RABBITMQ         INTERVENCIONES               REPUESTOS
  (simulado)                                (C#)                         (Python)
      │                   │                    │                            │
      │ Parada programada │                    │                            │
      │──────────────────►│                    │                            │
      │   (202 Aceptado)  │  copia para cada   │                            │
      │                   │  suscriptor        │                            │
      │                   │───────────────────►│ ABRE la orden de trabajo   │
      │                   │                    │ (estado Abierta)           │
      │                   │──────────────────────────────────────────────►  │ RESERVA los repuestos
      │                   │                    │                            │ de cada tarea
      │                   │                    │                            │
      │                   │                    │      ¿Alcanza el stock?    │
      │                   │                    │                            ├── SÍ: reserva hecha
      │                   │                    │                            └── NO: publica
      │                   │◄──────────────────────────────────────────────── "Faltante detectado"
      │                   │───────────────────►│ PONE la orden EN ESPERA    │
```

Esto se ve en los datos de demostración: la orden de **ADV-02** quedó *En espera* porque faltaba un repuesto.

### Historia B · "Se cerró una orden" (el stock se descuenta solo)

```
 Técnico          INTERVENCIONES              BUS / RABBITMQ               REPUESTOS
    │                   │                          │                           │
    │ Cerrar orden      │                          │                           │
    │──────────────────►│ guarda la orden CERRADA  │                           │
    │                   │ y el mensaje a enviar    │                           │
    │                   │ EN LA MISMA TRANSACCIÓN  │                           │
    │   204 OK          │                          │                           │
    │◄──────────────────│                          │                           │
    │                   │ (después, un despachador)│                           │
    │                   │ "Orden cerrada"          │                           │
    │                   │─────────────────────────►│ entrega al suscriptor     │
    │                   │                          │──────────────────────────►│ CONFIRMA el consumo:
    │                   │                          │                           │ stock físico −cantidad
    │                   │                          │                           │ ¿bajo el mínimo?
    │                   │                          │                           │  → crea solicitud de
    │                   │                          │                           │    reposición
```

El técnico recibe su respuesta **sin esperar** a que Repuestos termine: eso es lo que da robustez.

### Historia C · "Repuestos está caído" (la mensajería funciona)

```
  1. Cierran una orden  →  Intervenciones publica el evento  →  RabbitMQ lo GUARDA
  2. Repuestos no responde  →  el bus REINTENTA con espera (hasta 5 veces)
  3a. Repuestos vuelve antes de agotar los intentos  →  el mensaje se entrega y el stock se descuenta
  3b. Se agotan los intentos  →  el mensaje pasa a la COLA DE MENSAJES MUERTOS (se guarda, no se pierde)
  4.  Cuando Repuestos está bien  →  POST /bus/dlq/reprocesar  →  los mensajes vuelven a su cola y se entregan
```

Esto **se probó con RabbitMQ real** (ver doc 08): suscriptor caído, reinicio del bus a mitad de entrega, agotamiento de intentos y reproceso.

## 5. Cómo funciona el bus con RabbitMQ

```
                          RABBITMQ
   ┌──────────────────────────────────────────────────────────────────────────────┐
   │   INTERCAMBIO "eventos" (tipo tópico)                                         │
   │            │                                                                  │
   │            │  según el tópico, copia el mensaje a la cola de cada suscriptor   │
   │            ▼                                                                  │
   │   ┌───────────────────────────────────────────────────────────────────┐      │
   │   │  COLA  parada-programada::intervenciones      ──► (consumidor 1)   │      │
   │   │  COLA  parada-programada::repuestos-del-taller ──► (consumidor 2)   │      │
   │   │  COLA  orden-cerrada::repuestos-del-taller    ──► (consumidor 3)   │      │
   │   │  …una cola por cada (tópico, suscriptor)…                          │      │
   │   └───────────────────────────────────────────────────────────────────┘      │
   │                                                                               │
   │   Si la entrega falla:                                                        │
   │      cola  ──► cola ".retry" (espera 5 s)  ──► vuelve a la cola principal      │
   │      tras 5 fallos ──► cola ".dlq" (mensajes muertos: se guardan y se revisan)│
   └──────────────────────────────────────────────────────────────────────────────┘
```

*(Los nombres de las colas están abreviados en el dibujo; los reales son, por ejemplo, `plan-de-mantenimiento.parada-programada.v1::intervenciones`.)*

- **Una cola por suscriptor:** si uno es lento o está caído, no frena a los demás.
- **Mensajes persistentes y colas durables:** sobreviven a un reinicio del bus **y** del propio RabbitMQ.
- **Un consumidor por cola:** se conserva el **orden** de entrega mientras no hay fallos.
- **El bus sigue hablando HTTP con los servicios** (`POST /publish` para publicar y `POST /events/{tópico}` para entregar): así los servicios
  no cambian si mañana se reemplaza el broker.

## 6. Garantías: ¿qué pasa si algo se cae a mitad de camino?

Estas tres ideas aparecen una y otra vez; vale la pena dominarlas:

| Idea | Qué significa | Dónde se aplica |
|---|---|---|
| **Entrega al menos una vez** | Un mensaje puede llegar **más de una vez**, pero nunca se pierde en silencio | El bus reintenta hasta que el suscriptor responde 2xx |
| **Consumidor idempotente** | Recibir **el mismo mensaje dos veces no repite sus efectos** (se descuenta el stock una sola vez) | Cada servicio guarda el `eventId` de lo ya procesado (**bandeja de entrada** / *inbox*) |
| **Bandeja de salida (outbox)** | El evento a enviar **se guarda junto con el cambio de negocio** y un despachador lo envía después; así nunca hay "cambié el dato pero no avisé" | Ambos servicios |

**Honestidad técnica sobre el outbox:**

| Servicio | Outbox | Qué garantiza |
|---|---|---|
| Intervenciones (C# + Mongo) | **Transaccional**: el agregado y el mensaje se guardan en una sola transacción de MongoDB | Si se guarda la orden, el mensaje **existe**; si no, ninguno de los dos |
| Repuestos (Python + PostgreSQL) | **Durable**, guardado en PostgreSQL con reintentos | El mensaje sobrevive a reinicios, pero **no se guarda en la misma transacción** que el dato: si el proceso muere justo entre ambos pasos, ese evento podría perderse |

El generador **ya incluye** un esqueleto transaccional para Python; el producto actual se corrigió a mano con una versión durable y queda como mejora
regenerarlo (ver doc 08).

## 7. Dentro de cada servicio

### Intervenciones — Clean Architecture + DDD (C#)

```
   ┌────────────────────────────────────────────────────────────────────┐
   │  API            rutas HTTP, validación de la forma, errores         │  habla con el mundo
   ├────────────────────────────────────────────────────────────────────┤
   │  APPLICATION    un manejador por comando/consulta, validadores,     │  orquesta, no decide
   │                 consumidores de eventos, traductores                │  reglas
   ├────────────────────────────────────────────────────────────────────┤
   │  DOMAIN         OrdenDeTrabajo (raíz), reglas, estados,             │  EL CORAZÓN: las reglas
   │                 especificaciones, eventos de dominio                │  del negocio. No depende
   ├────────────────────────────────────────────────────────────────────┤  de nada de afuera
   │  INFRASTRUCTURE MongoDB, cifrado, caché, bus, ACL de habilitación   │  detalles técnicos
   └────────────────────────────────────────────────────────────────────┘
       Regla de dependencia: las flechas apuntan SIEMPRE hacia adentro (hacia el dominio).
```

### Repuestos del Taller — Hexagonal (Python)

```
                         ┌─────────────────────────────────┐
   HTTP  ──►  [puerto]──►│                                 │──►[puerto]──► PostgreSQL
   (FastAPI)  entrada    │      DOMINIO + APLICACIÓN       │   salida      (repositorios)
                         │  Existencia, Solicitud, reglas, │
   Eventos ─►[puerto]──► │  manejadores, estados           │──►[puerto]──► Bus / RabbitMQ
   del bus   entrada     │                                 │   salida
                         └─────────────────────────────────┘──►[puerto]──► Cifrado, Avisos
         adaptadores de ENTRADA            núcleo              adaptadores de SALIDA
```

Idea común a ambas: **el núcleo (reglas del negocio) no conoce la tecnología**. Se puede cambiar la base de datos o el bus sin tocar las reglas.

## 8. Los datos

| | Intervenciones | Repuestos |
|---|---|---|
| Base | MongoDB (conjunto de réplicas `rs0`, necesario para transacciones) | PostgreSQL |
| Cómo se guarda | Cada orden es **un documento** (un "snapshot" del agregado, patrón *Memento*) con su versión | Cada agregado como un registro con su snapshot en JSON |
| Concurrencia | Versión optimista: dos escrituras simultáneas del mismo documento → una recibe **409** | Cada solicitud y existencia tiene clave única |
| Datos personales | **Cifrados en reposo** (AES-256-GCM) | **Cifrados** los eventos pendientes de la bandeja de salida |

## 9. Cómo responde la API cuando algo sale mal

Ambos servicios responden **errores con el mismo formato** (estándar *Problem Details*, RFC 9457), así un cliente los lee igual venga del servicio que venga:

| Código | Cuándo | Ejemplo |
|---|---|---|
| **400** | La petición está mal formada | Falta un campo, un número fuera de rango |
| **404** | No existe lo pedido | Orden inexistente |
| **409** | Conflicto de concurrencia | Dos personas abren a la vez la orden de la misma parada |
| **422** | Se rompió una **regla de negocio** con nombre | `LIBERA_EL_MISMO_QUE_EJECUTO`, `PRUEBA_DE_VUELO_PENDIENTE`, `EXISTENCIA_INSUFICIENTE` |
| **503** | Un sistema del que depende no responde | Habilitación de Personal caída |

El cuerpo de un error de regla incluye `regla` (el nombre de la clase) y `codigo` (el código del contrato), y las pantallas **lo traducen a un
mensaje en lenguaje claro**.

## 10. Las pantallas web (microfrontends)

```
   ┌────────────────────────────── SHELL (panel) ─────────────────────────────┐
   │  Elegir rol ▼   Jefe de Operaciones y Mantenimiento                       │
   │ ┌──────────────────────────────────────────────────────────────────────┐ │
   │ │  Lee  /mfe-manifest.json  y carga solo lo que el rol puede usar       │ │
   │ │                                                                        │ │
   │ │   ┌──────────────────────────┐    ┌──────────────────────────┐       │ │
   │ │   │ <mfe-intervenciones>      │    │ <mfe-repuestos-del-taller>│      │ │
   │ │   │ 7 formularios + 1 consulta│    │ 5 formularios + 2 consultas│     │ │
   │ │   │ (Web Component)           │    │ (Web Component)           │       │ │
   │ │   └──────────────────────────┘    └──────────────────────────┘       │ │
   │ └──────────────────────────────────────────────────────────────────────┘ │
   └──────────────────────────────────────────────────────────────────────────┘
```

- **Un microfrontend por servicio**, cada uno empaquetado como un **Web Component** (un elemento HTML propio).
- El **shell** decide qué cargar según el **rol** y se comunica con ellos solo por eventos del navegador (nunca se importan entre sí).
- **Cada formulario** (uno por comando del modelo que algún rol de usuario puede pedir) explica para qué sirve y qué se escribe en cada campo, y valida antes de enviar.
- Todos comparten un **sistema de diseño** (colores, espaciados), de modo que se ven como una sola aplicación.

## 11. Configuración y secretos

Los servicios **no llevan direcciones fijas**: todo llega por **variables de entorno** que fija el `docker-compose.yml`.

| Variable | Para qué |
|---|---|
| `PORT` | Puerto del servicio |
| `BUS_URL` | Dónde publicar eventos |
| `<PROVEEDOR>_API_URL` | Dónde llamar a otro contexto (real o simulado) |
| `MONGO_URL` / `DATABASE_URL` | Su base de datos |
| `CIFRADO_CLAVE` | Clave para cifrar datos personales (si falta, **el servicio no arranca**) |
| `RABBITMQ_URL` | (solo el bus) conexión al broker |

> La clave de cifrado que trae el compose es **de desarrollo**. En un despliegue real debe reemplazarse por una clave propia y guardarse en un gestor de secretos.

---
Anterior: [04 · Guía de uso](04-guia-de-uso.md) · Siguiente: [06 · Justificación de tecnologías](06-justificacion-de-tecnologias.md)
