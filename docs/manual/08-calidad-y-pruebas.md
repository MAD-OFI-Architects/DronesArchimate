# 08 · Calidad y pruebas: qué se comprobó, qué falló y qué falta

> **Principio de este documento:** decir con la misma claridad **lo que funciona** y **lo que no está resuelto**. Un proyecto que muestra sus límites es más creíble que uno que
> afirma ser perfecto.

## 1. Las pruebas automáticas, en números

Todas se ejecutan sin intervención y pasaron en la última corrida:

| Qué se prueba | Herramienta | Pruebas | Qué cubre |
|---|---|---:|---|
| **El programa (ArchiForge)** | pytest | **202** | Lector del modelo, manifiesto, compuertas, TUI, decisiones, detección de cambios, bus, plataforma |
| **Intervenciones** — núcleo compartido | xUnit | **69** | Reglas de negocio, mediador, pipeline, outbox/inbox, cifrado, errores |
| **Intervenciones** — servicio | xUnit | **125** | Dominio, comandos, consumidores y **rutas HTTP completas** |
| **Repuestos del Taller** | pytest | **66** | Dominio, aplicación, adaptadores (incluida una base SQL), rutas y composición |
| **Pantallas** — Intervenciones | Vitest | **41** | Cada formulario, validaciones, ayudas, mensajes de error |
| **Pantallas** — Repuestos | Vitest | **15** | Ídem |
| **Datos de demostración** | unittest | **6** | El script de carga es idempotente y se reanuda tras una interrupción |
| **Total** | | **≈ 524** | |

**Pruebas "herméticas":** no dependen de Docker, de internet ni del agente de IA; por eso se pueden correr en cualquier momento y dar el mismo resultado.

## 2. Pruebas con el sistema real (lo que no se puede simular)

Las pruebas automáticas no bastan para la mensajería y la concurrencia. Se hicieron pruebas **con los contenedores reales**, en un entorno aislado:

### 2.1 Mensajería con RabbitMQ real — 4 escenarios

| Escenario | Qué se hizo | Resultado |
|---|---|---|
| **1. Entrega normal** | Publicar «Parada programada» | Llegó a **ambos** servicios en **~1 s** |
| **2. Suscriptor caído** | Apagar Repuestos, publicar, volver a encenderlo | Se reintentó y se **entregó al volver** (~1 s tras el arranque) |
| **3. Bus reiniciado a mitad de entrega** | Apagar Repuestos, publicar, **reiniciar el bus**, encender Repuestos | El mensaje **sobrevivió** y se entregó (~6 s) |
| **4. Mensaje muerto + reproceso** | Dejar Repuestos apagado hasta agotar los 5 intentos | El mensaje quedó en la **cola de mensajes muertos** (~39 s); con `POST /bus/dlq/reprocesar` se **entregó** y la cola quedó vacía |

### 2.2 Concurrencia — un error real encontrado y corregido

**Prueba:** 20 peticiones **simultáneas** para abrir la orden de **la misma parada**, repetido 5 veces.

| | Antes de la corrección | Después |
|---|---|---|
| Órdenes creadas por una parada | **entre 6 y 20** (duplicadas) | **1** |
| Respuestas | 201 y también **errores 500** | 201 y **409** (conflicto) |
| Efecto adicional | Una vez duplicada, esa parada **quedaba rota** (la búsqueda fallaba) | Sin efectos secundarios |

**Causa:** la operación comprobaba "¿existe?" y después insertaba; dos peticiones simultáneas pasaban la comprobación a la vez.
**Corrección:** el identificador de la orden **se deriva de la parada**; así la segunda inserción choca en la base de datos en lugar de duplicar. Un conflicto transitorio de MongoDB también se traduce ahora a 409.

> **Lección para la exposición:** *"Las pruebas unitarias no habrían encontrado este error. Se encontró probando con el sistema real y con peticiones simultáneas."*

## 3. La revisión de código profunda

Se revisó el código de los dos servicios contra el diseño: reglas de negocio, patrones, principios SOLID, responsabilidades de cada clase y herencias.

**Veredicto:** la estructura y las reglas centrales **respetan el diseño**; había desviaciones en los bordes. Estado de cada hallazgo:

| # | Hallazgo | Gravedad | Estado |
|---|---|---|---|
| 1 | **Outbox de Repuestos en memoria**: se perdía al reiniciar y descartaba eventos tras 3 fallos | Alta | ✅ Ahora es **durable** en PostgreSQL y lo agotado queda como *fallido*, no se borra. ⚠ Sigue sin ser transaccional (ver §4) |
| 2 | **Idempotencia de consumidores en memoria** (y duplicada en dos clases) | Alta | ✅ Una sola bandeja de entrada **durable**; el evento se marca al terminar y cada elemento es idempotente |
| 3 | Regla de vuelo de prueba lanzaba una excepción genérica (400) en lugar de una **regla con nombre** | Media | ✅ `PRUEBA_DE_VUELO_PENDIENTE` → **422** con `regla` y `codigo` |
| 4 | **Errores distintos** en cada servicio (409 y `{"error": …}` en uno, 422 y `regla` en el otro) | Media | ✅ **Problem Details** en ambos (cambió el contrato público de Repuestos) |
| 5 | Búsqueda por parada recorría toda la colección y fallaba si había duplicados | Media | ✅ Lectura directa por identificador derivado; tolera duplicados antiguos |
| 6 | **Concurrencia en «Abrir»** | Alta | ✅ Ver §2.2 |
| 7 | **Contrato de cierre sin hora de corte ni serie retirada**, aunque el diseño pide informar instalaciones **y retiros** con hora de corte | Media | ✅ Corregido en el servicio **y en el generador** (la causa era un contrato de plataforma que quedaba sin contexto) |
| 8 | **Habilitación caída → error 500** | Media | ✅ Ahora **503** con la dependencia indicada |
| 9 | **Cifrado de Python "abierto"**: sin clave usaba una clave pública fija | Alta (seguridad) | ✅ Ahora **no arranca** sin `CIFRADO_CLAVE` |
| 10 | Mensajes agotados en la bandeja de C# se quedaban sin publicar **en silencio** | Media | ◐ Ahora se registran como **error**; falta una vía de reproceso |
| 11 | Las pantallas de Intervenciones traducían errores por código de contrato, pero el servicio mandaba el **nombre de la clase** (nunca coincidían) | Media | ✅ El servicio manda también `codigo`; las pantallas lo usan |
| 12 | «Aprobación sin aprobador» | — | ❌ **Retirado: fue un error de la revisión.** El diseño solo pide "nivel de aprobación por monto", y eso **ya está implementado** |

> Fue importante **retractar el hallazgo 12**: una revisión honesta también reconoce cuando se equivocó.

### Cómo se verificó cada corrección

- Se escribió **primero la prueba** que reproduce el problema y se comprobó que **fallaba**; luego se corrigió.
- En la corrección de concurrencia se hizo además una **prueba de mutación**: se revirtió a propósito el arreglo y se confirmó que la prueba lo detecta.
- Los cambios de contrato se verificaron contra **el servicio real** en contenedores.

## 4. Límites conocidos (la lista honesta)

Para cada uno se indica qué haría falta. Es mejor que lo digas tú antes de que lo pregunten.

| Límite | Qué significa | Qué haría falta |
|---|---|---|
| **Outbox de Repuestos no transaccional** | Si el proceso muere justo entre guardar el dato y guardar el mensaje, ese evento puede perderse | Una conexión por operación y una unidad de trabajo; el generador ya trae un esqueleto, falta **regenerar** el servicio |
| **El bus no valida el contenido** de los eventos | Un emisor podría mandar un `payload` con campos incorrectos | Validar contra los contratos (esquemas) |
| **Orden de entrega** | Se conserva mientras no hay fallos; un reintento va al final de la cola | Un esquema de particiones o numeración por agregado |
| **Mensajes agotados en C#** | Quedan sin publicar tras 10 intentos y solo se registran | Reproceso manual o cola de mensajes muertos propia |
| **Sin autenticación entre servicios ni en el gateway** | Cualquiera con acceso a la red puede llamar a la API | Identidad y permisos en el borde (ya existe el contexto "Identidad y permisos" en el modelo, sin construir) |
| **Roles solo en la pantalla** | El filtro por rol ocurre en el cliente | Autorización en el servidor |
| **Clave de cifrado de desarrollo** | Está escrita en el compose | Gestor de secretos y rotación de claves |
| **Cifrado determinista (C#)** | Dos textos iguales dan el mismo cifrado | Aceptable para este uso (el documento no cambia si el dato no cambia); documentarlo |
| **Caché por instancia** | Con varias réplicas, cada una tendría la suya | Caché compartida o invalidación por evento |
| **Dos servicios reales de nueve** | Los demás contextos se simulan | Construirlos con el mismo procedimiento (es el propósito de la herramienta) |
| **Concurrencia fina en Repuestos** | La reserva no bloquea la fila: dos reservas simultáneas sobre la misma referencia podrían superar el stock (no está probado) | Bloqueo de fila o actualización condicional, y una prueba con peticiones simultáneas |
| **Tabla fija de servicios N3 → contexto** | El generador conoce los nombres de este modelo | Hacerla configurable para aceptar cualquier ArchiMate |
| **Opciones de plataforma "propio", "sin frontend", "sin simuladores", "sin compose"** | Están probadas solo con pruebas herméticas, no levantadas en vivo | Una corrida de humo por cada combinación |
| **Kubernetes y Angular** | No son opciones | Escribir su generador y verificarlo |

## 5. Cómo se verificó el propio programa

- **Pruebas herméticas** de cada pieza (lector, manifiesto, compuertas, decisiones, TUI con un "piloto" automático que simula teclas).
- **Ejecución de punta a punta con un agente simulado** (`forge.dryrun.toml`): recorre todo el pipeline sin gastar un agente real.
- **Pruebas de mutación** en los cambios críticos: se rompe a propósito la corrección y se comprueba que alguna prueba falla.
- **Regeneración idéntica:** con las decisiones del proyecto, el generador reproduce **byte a byte** los archivos de plataforma entregados (gateway, bus, simuladores, SQL de inicio).
- **Cada bloque de cambios** deja una bitácora en `odd/tasks/` con lo pedido, lo hecho, lo verificado y lo pendiente.

## 6. Qué demuestra todo esto

```
   El diseño (ArchiMate)  ──►  el código  ──►  las pruebas  ──►  el sistema corriendo
         │                        │               │                     │
         └──── trazabilidad ──────┴── conformidad ┴── compuertas ───────┘
                                                                 + pruebas con fallos reales
```

- El código **nace del modelo** y se puede rastrear hasta él.
- Se **comprueba** automáticamente (conformidad, arquitectura, SOLID, patrones, pruebas).
- Se **probó con fallos reales** (servicio caído, reinicio, concurrencia) y lo que falló **se corrigió y se documentó**.
- Los **límites** están a la vista.

---
Anterior: [07 · Justificación de patrones](07-justificacion-de-patrones.md) · Siguiente: [09 · Preguntas frecuentes](09-preguntas-frecuentes.md)
