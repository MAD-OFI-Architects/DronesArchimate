# 03 · Cómo funciona ArchiForge por dentro

## La metáfora: una obra con inspectores

Pensá en la construcción de un edificio:

- Hay un **plano** (el modelo ArchiMate).
- Hay un **arquitecto** que decide los materiales (lenguaje, base de datos, estilo, patrones).
- Hay **obreros** que construyen por etapas: cimientos, estructura, instalaciones, acabados (el agente de IA).
- Después de cada etapa hay un **inspector** que revisa con una lista fija. Si algo no cumple, **se devuelve la obra con la razón** y el obrero lo corrige.
- Al final se **prueba que todo funcione** junto (encender luces, abrir canillas).

ArchiForge es exactamente eso, hecho programa.

```
                        ┌───────────────────────────────────────────┐
                        │              ARCHIFORGE                    │
                        │                                            │
   PLANO ──────────────►│  LECTOR        lee el modelo               │
   (ArchiMate + .md)    │     │                                      │
                        │     ▼                                      │
   DECISIONES ─────────►│  ORQUESTADOR   reparte el trabajo en       │
   (del arquitecto)     │     │          etapas y lleva la cuenta    │
                        │     ▼                                      │
                        │  AGENTE DE IA  escribe el código de cada   │──────►  PRODUCTO
                        │     │          etapa, con órdenes precisas │         (servicios, pruebas,
                        │     ▼                                      │          web, documentos)
                        │  COMPUERTAS    inspeccionan y devuelven    │
                        │                lo que no cumple            │
                        └───────────────────────────────────────────┘
```

## Los cinco actores del programa

| Actor | Qué hace | Dónde vive |
|---|---|---|
| **Lector** | Traduce el modelo ArchiMate a un resumen compacto (IR) y deriva la lista de lo que debe existir (manifiesto) | `forge/archimate.py`, `forge/manifest.py` |
| **Orquestador (Runner)** | Ejecuta las etapas en orden, guarda el avance, reintenta, hace un commit por etapa | `forge/runner.py`, `forge/stages.py` |
| **Agente de IA** | Escribe el código/documentos de una etapa siguiendo una *orden de trabajo* | motor externo (Claude Code, OpenCode u otro) |
| **Compuertas (gates)** | Revisan automáticamente lo que el agente produjo | `forge/gates.py`, `forge/conformance.py`, `forge/solid.py` |
| **Pantalla TUI** | Interfaz de terminal para decidir, construir y ver el avance | `forge/studio/` |

## Las etapas de un servicio

Para **cada servicio** que se construye, el programa recorre estas etapas **en orden**:

```
 ETAPA            QUÉ SE HACE                                                  QUIÉN
 ─────────────    ───────────────────────────────────────────────────────────  ──────────────
 S00-ir           Traducir el ArchiMate al IR (resumen compacto)               programa (determinista)
 S01-manifest     Derivar la lista de símbolos que deben existir               programa
 S02-scaffold     Crear el esqueleto: carpetas, bus, simuladores, compose,     programa
                  esqueleto del microfrontend, módulos de mensajería
 S03-adr          Redactar las decisiones de arquitectura argumentadas (ADR)   agente (arquitecto)
 S10-kernel       Núcleo compartido del servicio (solo C#)                     agente (C#)
 S11-domain       Capa de dominio: agregados, reglas, eventos, pruebas         agente
 S12-application  Capa de aplicación: comandos, consultas, validadores         agente
 S13-adapters     Capa de infraestructura y API: base de datos, bus, ACL, rutas agente
 S30-smoke        Prueba de humo: levantar el servicio en contenedores         agente + Docker
 S40-microfrontend Pantallas web del servicio (un formulario por comando)      agente (frontend)
 S50-verify       Revisión independiente (decisiones, SOLID, patrones)         agente (revisor)
 S60-report       Informe final: conformidad y trazabilidad                    programa
```

Observá la mezcla: **las etapas deterministas (S00, S01, S02, S60) las hace el programa sin IA** y siempre dan el mismo resultado;
**las etapas "creativas" las hace el agente**, pero siempre **dentro de las compuertas**.

## El ciclo de una etapa con agente

Esto es lo que más se debe entender:

```
              ┌──────────────────────────────────────────────────────────────┐
              │                                                              │
              ▼                                                              │
   ┌────────────────────┐                                                    │
   │ 1. El programa     │   ← incluye: qué construir, decisiones del        │
   │    escribe la      │     arquitecto, símbolos esperados y, si es un     │
   │    ORDEN DE TRABAJO│     reintento, el motivo del rechazo anterior      │
   └─────────┬──────────┘                                                    │
             ▼                                                               │
   ┌────────────────────┐                                                    │
   │ 2. El AGENTE       │                                                    │
   │    escribe código  │                                                    │
   └─────────┬──────────┘                                                    │
             ▼                                                               │
   ┌────────────────────┐        NO (hasta 3 intentos por defecto)           │
   │ 3. COMPUERTAS      │ ─────────────────────────────────────────────────► ┘
   │    ¿todo cumple?   │        se devuelve el motivo exacto
   └─────────┬──────────┘
             │ SÍ
             ▼
   ┌────────────────────┐
   │ 4. Se guarda un    │   un commit por etapa en el repositorio del producto,
   │    COMMIT y se     │   y el estado queda anotado para poder reanudar
   │    pasa a la sig.  │
   └────────────────────┘
```

Detalles importantes:

- **La orden de trabajo es un archivo** (`.forge/<servicio>/work/<etapa>.md`) que se puede abrir y leer: ahí está exactamente lo que se le pidió al agente.
- **El agente nunca lee el XML del modelo**; recibe el IR y el manifiesto.
- **Si una etapa falla tras todos los intentos**, las etapas que dependen de ella se **omiten** y se informa por qué.
- **El avance se guarda** (`.forge/<servicio>/state.json`): si se corta la luz o se acaba la cuota del agente, se **reanuda** donde quedó.
- **Cada servicio tiene su propio estado, logs y puerto**, y se pueden construir **en paralelo** (cada uno en su proceso).

## Las compuertas: la lista de verificación

Cada compuerta revisa algo distinto. Es lo que da **confianza** al resultado:

| Compuerta | Qué comprueba | Si falla |
|---|---|---|
| **Conformidad** | Que **cada símbolo del manifiesto exista** en el código, declarado en la **capa correcta** (≥ 90 %, configurable) | Lista lo que falta |
| **Arquitectura** | Que las capas respeten la dirección de dependencias (el dominio no depende de la infraestructura): revisa imports y proyectos | Muestra el archivo que rompe la regla |
| **SOLID** | Señales objetivas de los cinco principios: clases que crecen sin límite (SRP), cadenas de `if` por tipo (OCP), métodos heredados que lanzan «no soportado» (LSP), puertos con demasiados métodos (ISP), instanciación directa de colaboradores concretos (DIP). Son heurísticas: detectan los olores graves, el revisor independiente aporta el criterio humano | Indica clase y principio |
| **Patrones** | Que cada patrón elegido tenga su **estructura real** en el código (no solo el nombre) | Lista el patrón y lo que falta |
| **Estilo de servicio** | Que un microservicio **no guarde estado local** y **no tenga direcciones fijas** hacia otros servicios, el bus, los simuladores o las bases de datos: todo llega por variables de entorno (`BUS_URL`, `<CONTEXTO>_API_URL`, `DATABASE_URL`…), para que se pueda crear, destruir y escalar sin perder nada | Señala el archivo y la dirección fija |
| **Cableado** | Que todo adaptador definido se **use de verdad** en la composición (que no queden piezas sueltas) | Lista adaptadores sin usar |
| **Pruebas** | `dotnet test`, `pytest` o `mvn test` según el lenguaje | Muestra las que fallan |
| **ADR** | Que el documento de decisiones tenga todas las secciones y cite **todos** los patrones elegidos con clases reales | Indica la sección |
| **Humo** | Que el servicio **arranque en contenedores** y responda | Muestra el log |
| **Microfrontend** | Que cada formulario exista, tenga **ayudas** en cada campo, use el sistema de diseño y no deje "esqueletos pendientes" | Indica el formulario |
| **Interconexión** | Que los servicios que llaman a otros lean la URL del proveedor de su variable de entorno, y que el proveedor exponga la ruta | Indica el archivo |
| **Políticas del equipo** | Reglas opcionales del proyecto (ver más abajo) | Indica la política |

> **Frase clave para la exposición:** *"El agente escribe, pero no es él quien decide si está bien: decide un conjunto de compuertas que no se cansan ni se olvidan."*

## Dónde está cada decisión: tres niveles

Para no confundir quién decide qué, hay **tres niveles**:

```
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │ NIVEL 1 · LO QUE DICE EL NEGOCIO                          → viene del ARCHIMATE          │
 │   Qué agregados, comandos, eventos, reglas y relaciones existen.                          │
 ├─────────────────────────────────────────────────────────────────────────────────────────┤
 │ NIVEL 2 · LO QUE DECIDE EL ARQUITECTO                     → archivos en decisiones/      │
 │   Por servicio:  lenguaje · arquitectura interna · estilo · base de datos · patrones      │
 │                  · algoritmo de cifrado · justificación de cada una                       │
 │   De la plataforma: canal de eventos · gateway · frontend · despliegue · simuladores      │
 │                     · versiones de las imágenes de contenedor                             │
 ├─────────────────────────────────────────────────────────────────────────────────────────┤
 │ NIVEL 3 · LO QUE FIJA LA HERRAMIENTA                      → código de ArchiForge         │
 │   El formato de las órdenes de trabajo, las compuertas, el contrato del bus, la          │
 │   forma de los esqueletos. Es lo único que el arquitecto no elige en cada proyecto.      │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Regla de oro del programa:** *no recomienda ni preselecciona nada.* Si el modelo necesita una decisión y no está tomada, **se detiene y lista las opciones**.

## Detección de cambios: "¿tengo que volver a correr todo?"

El programa guarda una **huella** del modelo y de las decisiones de cada servicio. Al construir, la compara:

```
   ¿Cambió el MODELO o una DECISIÓN del servicio?     ──►  se reabren TODAS sus etapas y se reconstruye
   ¿Cambiaron solo las JUSTIFICACIONES (texto)?       ──►  se rehace solo el documento de decisiones y su revisión
   ¿Cambió OTRO servicio?                              ──►  este no se toca
   ¿No cambió nada?                                    ──►  "ya completada", no gasta cuota del agente
```

La pantalla y `forge domains` avisan "⚠ el modelo o las decisiones cambiaron: reconstruir" **sin necesidad de construir**.

## El ensamblado: unir los servicios

Cuando varios servicios están construidos, `forge assemble` **los une en una sola plataforma**:

1. Genera el contrato del bus y el catálogo de tópicos con **todos los servicios reales**.
2. Decide quién es **real** y quién es **simulado**: los contextos no construidos se simulan.
3. Genera el `docker-compose.yml`, el gateway, las pantallas web (un panel + un remote por servicio) y el `init` de bases de datos, **según las decisiones de la plataforma**.
4. Corre las compuertas del conjunto, incluida una **prueba de humo de todo el producto**.

## Real contra simulado

Un servicio **real** es uno que se construyó. Uno **simulado** es un "doble" que responde en su lugar:

```
  Plan de Mantenimiento  (no construido)           Intervenciones (real)
  ┌────────────────────┐                           ┌──────────────────┐
  │   SIMULADOR        │ ── "parada programada" ─► │  abre la orden   │
  │ (emite el evento   │      (por el bus)         │                  │
  │  que emitiría el   │                           └──────────────────┘
  │  servicio real)    │
  └────────────────────┘
```

Si mañana se construye Plan de Mantenimiento, **los demás no cambian**: leen la URL de su proveedor de una variable de entorno
(`<PROVEEDOR>_API_URL`) y los suscriptores del bus se reapuntan solos.

## Las reglas opcionales del equipo (`[policy]`)

El equipo puede declarar reglas para **el conjunto** de servicios (en `forge.toml`). Si no declara nada, **no se exige nada**. En este
proyecto se declararon:

| Política | Significado |
|---|---|
| `min_domains = 2` | Al menos dos servicios construidos |
| `distinct_languages = true` | Cada servicio con un lenguaje distinto |
| `mixed_architectures = true` | Arquitecturas internas distintas entre servicios |
| `required_patterns = [memento, cache, cifrado]` | Esos patrones en cada servicio |
| `require_justifications = true` | Cada decisión con una justificación real (no un texto de ejemplo) |
| `simulate_remaining = true` | Los contextos no construidos deben quedar simulados |

## Cómo se protege la información personal del usuario

- Las **claves de API** (tokens) de los proveedores de IA se guardan **fuera del proyecto** (`~/.config/archiforge/credentials.json`, permisos 600)
  y viajan al agente **solo por variable de entorno**; nunca se imprimen ni se suben a git.
- Las **preferencias personales** (qué motor y modelo usar) también quedan fuera del repositorio: cada persona usa su propia suscripción
  sin que sus cambios viajen con un `git push`.

---
Anterior: [02 · El modelo ArchiMate](02-el-modelo-archimate.md) · Siguiente: [04 · Guía de uso](04-guia-de-uso.md)
