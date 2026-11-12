# Manual de ArchiForge y del producto que genera

Este manual explica, sin dar nada por sabido, **qué es el proyecto, cómo funciona, cómo se usa y por qué se decidió cada cosa**.
Está escrito para que una persona sin formación técnica pueda seguirlo, y tiene el detalle técnico al final de cada documento
para quien quiera profundizar.

## La idea en una imagen

```
   LO QUE SE HIZO A MANO                 LO QUE HACE EL PROGRAMA                 LO QUE SE OBTIENE
   (el "plano")                          (ArchiForge)                            (el "edificio")

 ┌─────────────────────┐            ┌───────────────────────────┐          ┌──────────────────────────┐
 │  Modelo ArchiMate   │            │ 1. Lee el modelo          │          │ Servicios que funcionan  │
 │  + documentos de    │  ───────►  │ 2. El arquitecto decide   │  ─────►  │ (código, pruebas, bases  │
 │  diseño (Fase 0-6)  │            │    las tecnologías        │          │  de datos, mensajería)   │
 │                     │            │ 3. Un agente de IA escribe│          │ + pantallas web          │
 │  "QUÉ necesita el   │            │    el código por etapas   │          │ + documentación          │
 │   negocio"          │            │ 4. Compuertas verifican   │          │                          │
 └─────────────────────┘            └───────────────────────────┘          └──────────────────────────┘
```

**Dicho simple:** se dibuja el negocio una vez (el plano). El programa lo lee, la persona que arquitecta elige cómo construirlo
(lenguaje, base de datos, estilo...) y el programa construye y comprueba el resultado.

## Cómo leerlo según quién seas

| Si querés... | Leé | Tiempo |
|---|---|---|
| Entender de qué trata, sin tecnicismos | [01 · Qué es](01-que-es.md) | 10 min |
| Saber cómo se prepara el modelo para que el programa lo entienda | [02 · El modelo ArchiMate](02-el-modelo-archimate.md) | 20 min |
| Ver cómo trabaja el programa por dentro | [03 · Cómo funciona](03-como-funciona-el-programa.md) | 20 min |
| Usarlo (instalar, decidir, construir, probar) | [04 · Guía de uso](04-guia-de-uso.md) | 15 min |
| Ver cómo quedan los servicios y cómo se hablan | [05 · El producto generado](05-el-producto-generado.md) | 25 min |
| Defender **por qué** se eligió cada tecnología | [06 · Justificación de tecnologías](06-justificacion-de-tecnologias.md) | 25 min |
| Defender **por qué** se usó cada patrón | [07 · Justificación de patrones](07-justificacion-de-patrones.md) | 25 min |
| Ver, servicio por servicio, qué se decidió y la justificación | [11 · Decisiones por servicio](11-decisiones-por-servicio.md) | 15 min |
| Saber qué se probó, qué falló y qué falta | [08 · Calidad y pruebas](08-calidad-y-pruebas.md) | 15 min |
| Prepararte para las preguntas | [09 · Preguntas frecuentes](09-preguntas-frecuentes.md) | 15 min |
| Buscar el significado de una palabra | [10 · Glosario](10-glosario.md) | — |

## Las cinco ideas que hay que llevarse

1. **Un solo modelo manda.** El negocio se describe una vez en ArchiMate; todo lo demás se deriva de ahí y se puede rastrear hasta él.
2. **La persona decide, la herramienta ejecuta.** El programa no elige lenguaje, base de datos, patrones, gateway ni canal de eventos:
   los elige quien arquitecta, en una pantalla, y la herramienta se detiene si falta una decisión.
3. **Cada servicio es distinto a propósito.** Intervenciones usa C# + MongoDB + Clean/DDD; Repuestos usa Python + PostgreSQL + Hexagonal.
   El producto demuestra que el mismo modelo puede construirse con tecnologías diferentes.
4. **Los servicios no se llaman entre sí: se avisan.** Cuando algo ocurre en un servicio, se publica un evento en RabbitMQ y los demás
   reaccionan. Así uno puede caerse sin arrastrar al otro.
5. **Nada se da por bueno sin comprobarlo.** El código pasa por compuertas automáticas (conformidad con el modelo, principios SOLID,
   pruebas, humo en contenedores) y por pruebas reales de fallos.

## Dónde está cada cosa en el repositorio

```
DronesArchimate/
├── diseno/                  ← EL PLANO: modelo ArchiMate + análisis de las 6 fases (entrevista, capacidades, dominios...)
├── archiforge/              ← EL PROGRAMA: lee el modelo y construye el producto (también tiene la pantalla TUI)
│   ├── forge/               ·   el código del programa
│   ├── prompts/             ·   las instrucciones que recibe el agente de IA en cada etapa
│   ├── catalog/             ·   el catálogo de 50 patrones de diseño (explicados, sin recomendar)
│   ├── decisiones/          ·   las decisiones del arquitecto (un archivo por servicio + la plataforma)
│   └── tests/               ·   las pruebas del programa
├── entrega-v3/              ← EL PRODUCTO: servicios, bus, gateway, pantallas web y datos de demostración
├── docs/
│   ├── manual/              ← ESTE MANUAL
│   ├── decisiones.md        ·   decisiones de diseño del negocio (D-01…D-18) y supuestos (S-01…S-11)
│   └── guia-ejecucion-v3.md ·   guía paso a paso de la ejecución
└── odd/tasks/               ← bitácoras de trabajo de cada bloque de cambios
```

> **Nota sobre cifras.** Los números de este manual (cantidad de elementos del modelo, de pruebas, de símbolos generados) se
> obtuvieron ejecutando el propio programa sobre este repositorio. Si el modelo cambia, las cifras cambian.
