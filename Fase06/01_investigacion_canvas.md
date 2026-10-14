# Fase 6 · Investigación del Bounded Context Canvas en ArchiMate

**Contexto elegido: Plan de Mantenimiento** (core). Es el contexto core más rico: concentra la mayor cantidad de reglas (condición compuesta con «lo que ocurra primero», fuente del intervalo, diferimientos, restricciones de dos bahías y de misma línea, boletines) y de interoperabilidad (Comercial, fabricante, Repuestos, Habilitación, Intervenciones, Notificaciones e Indicadores) (D-12).

## Opciones y decisión

| Opción | Idea | Pros | Contras | Resultado |
|---|---|---|---|---|
| **A. Vista ArchiMate con rejilla** | Una vista con Groupings/Notes como casillas del canvas y, dentro, elementos reales del modelo | Coherente y trazable: son los mismos elementos de V1, V5, V6, V7, V8 y V9 | Hay que trabajar el diseño visual | **Elegida** |
| B. Canvas de Archi (plantilla de bloques) | Plantilla tipo post-it | Parecido al canvas original | Los bloques no son elementos ArchiMate: se pierde trazabilidad | No elegida |
| C. Híbrido | Canvas (B) como página con enlaces a vistas | Claridad | Dos fuentes que mantener | No elegida |

## Qué se hizo
Se construyó la opción A: una rejilla de 3 × 3 Groupings con los títulos del canvas (Nombre/Propósito, Clasificación estratégica, Rol del dominio, Comunicación entrante, Contexto (centro), Comunicación saliente, Lenguaje ubicuo, Decisiones de negocio, Supuestos), donde el centro contiene el componente *Plan de Mantenimiento* con los agregados (raíces) y comandos de V6b; a la izquierda están los colaboradores y eventos que recibe y a la derecha lo que emite; abajo el lenguaje ubicuo de V7 (los mismos *Business Objects*), las decisiones de negocio (requerimiento y principios de V1 más las invariantes) y los supuestos como *Requirement* con propiedad `Tipo = Supuesto`.

## Verificación en la herramienta
La vista se exporta a imagen apaisada con escala 2× (*File → Export → View As Image*). La comparación de las opciones A–C se apoya en la documentación de la herramienta.
