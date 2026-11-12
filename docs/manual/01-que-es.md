# 01 · Qué es este proyecto (explicado para todos)

## El problema del negocio

**AgroDrones del Valle S.A.S.** (Palmira, Valle del Cauca) presta servicios de fumigación de cultivos con una flota de **12 drones**.
Un dron que falla en plena campaña es un cliente sin servicio. Por eso la empresa necesita un software que le ayude a:

- saber cuántas **horas y ciclos** lleva cada dron y cada pieza (baterías, motores, bomba, hélices);
- **planificar** el mantenimiento preventivo antes de que algo se rompa;
- controlar los **repuestos** que se necesitan y los que se gastan;
- dejar **evidencia** para la autoridad aeronáutica;
- medir si la flota está **disponible** (indicadores).

El jefe de Operaciones y Mantenimiento fue entrevistado en cinco sesiones (17 bloques, 168 preguntas). De esas entrevistas salió el
diseño completo que está en la carpeta `diseno/`.

## Qué se construyó

Se construyeron **dos cosas**, y es importante no confundirlas:

```
        ┌────────────────────────────────────────────────────────────────────────┐
        │  COSA 1: ArchiForge  (el "constructor")                                 │
        │  Un programa que lee el diseño del negocio y construye software.        │
        └───────────────────────────────────┬────────────────────────────────────┘
                                            │ produce
                                            ▼
        ┌────────────────────────────────────────────────────────────────────────┐
        │  COSA 2: el producto  (lo que se construye con el constructor)          │
        │  Dos servicios que funcionan + pantallas web + mensajería + datos.      │
        └────────────────────────────────────────────────────────────────────────┘
```

Una forma fácil de entenderlo: **ArchiForge es una fábrica y el producto es el mueble que sale de ella.**
Si mañana cambia el negocio (otro tipo de piezas, otro proceso), no se rehace la fábrica: se cambia el diseño y la fábrica produce de nuevo.

## Por qué es distinto a "programar a mano"

| Programar a mano | Con ArchiForge |
|---|---|
| El diseño vive en documentos y el código en otro lado; con el tiempo se separan | El código **sale del modelo**: cada clase se puede rastrear hasta el elemento del diseño que la originó |
| Las decisiones técnicas quedan en la cabeza de alguien | Las decisiones quedan **escritas y justificadas** en archivos, y la herramienta las respeta |
| Cambiar de tecnología es empezar de cero | Cambiar de lenguaje o base de datos es cambiar una decisión y volver a construir |
| Nadie comprueba que el código siga el diseño | **Compuertas automáticas** comprueban conformidad, principios de diseño y pruebas |

## El recorrido completo, en seis pasos

```
 PASO 1            PASO 2              PASO 3               PASO 4              PASO 5            PASO 6
 Entender el       Diseñar el          Preparar el          Decidir cómo        Construir         Ensamblar y
 negocio           negocio             modelo para          construirlo         cada servicio     probar
                   (ArchiMate)         el programa          (el arquitecto)     (el agente)
┌──────────┐     ┌──────────────┐    ┌──────────────┐     ┌──────────────┐    ┌────────────┐    ┌────────────┐
│Entrevistas│    │Capacidades,  │    │Etiquetas y   │     │Lenguaje, BD, │    │Código,     │    │Servicios + │
│al experto │ ─► │dominios,     │ ─► │tablas que el │ ─►  │estilo,       │ ─► │pruebas,    │ ─► │bus + web + │
│(Fase 0)   │    │agregados...  │    │programa lee  │     │patrones...   │    │documentos  │    │humo en     │
│           │    │(Fases 1-6)   │    │(ver doc 02)  │     │(en la TUI)   │    │por etapas  │    │contenedores│
└──────────┘     └──────────────┘    └──────────────┘     └──────────────┘    └────────────┘    └────────────┘
   hecho a mano    hecho a mano        hecho a mano         lo decide una       lo hace el        lo hace el
                                                            persona             programa          programa
```

Los pasos 1 a 3 los hizo el equipo (con la herramienta Archi). Desde el paso 4 interviene el programa, pero **con una persona decidiendo**.

## Qué hace el producto (lo que se puede ver funcionando)

El producto cubre un proceso concreto: **la gestión de la disponibilidad de la flota por mantenimiento preventivo**.
En la práctica, para los dos servicios construidos:

**Servicio "Intervenciones"** (las órdenes de trabajo del taller)
- Se **abre una orden** cuando Plan de Mantenimiento programa una parada de un dron.
- Se le **asigna un técnico** (se consulta si tiene la habilitación vigente).
- Se **registran las tareas ejecutadas**, los repuestos consumidos y los hallazgos.
- En trabajos mayores se exige un **vuelo de prueba** (entre 5 y 10 minutos) y que **quien libera el dron no sea quien hizo el trabajo**.
- Se **libera** el dron y se **cierra** la orden; al cerrarla se avisa a los demás que se consumieron repuestos.

**Servicio "Repuestos del Taller"** (el almacén)
- Lleva la **existencia** de cada repuesto y **reserva** unidades para cada orden.
- Cuando una orden se cierra, **confirma el consumo** y descuenta el stock.
- Si el stock baja del mínimo, crea una **solicitud de reposición** (que se aprueba o cancela; el nivel de aprobación depende del monto).
- Si falta un repuesto al reservar, **avisa** para que la orden quede en espera.

**Cómo se hablan** (el corazón de la interoperabilidad): cuando Plan de Mantenimiento programa una parada, **ambos servicios se enteran
a la vez**; Intervenciones abre la orden y Repuestos reserva los repuestos. Si faltan repuestos, Repuestos avisa y la orden pasa a
"En espera". Al cerrar la orden, Repuestos descuenta el stock. **Ninguno llama directamente al otro**: se avisan por eventos.

**Pantallas web.** Un panel con una pantalla para cada servicio, filtrada por rol (Jefe de Operaciones, Técnico, Almacenista).
Cada formulario explica qué se escribe y qué rango es válido.

**Lo que no se construyó** (y se simula): los otros 7 contextos del negocio (Plan de Mantenimiento, Flota y Componentes, Operación y
Horas, Indicadores, Habilitación de Personal, Evidencia y Reportes, Notificaciones). Existen en el modelo y **se pueden construir
con el mismo procedimiento**; mientras tanto, unos *simuladores* responden en su lugar para que el producto corra completo.

## Qué NO es

- **No es magia ni "IA que hace todo".** La inteligencia artificial escribe el código, pero dentro de un marco estricto: recibe órdenes
  de trabajo precisas, y si lo que escribe no pasa las compuertas, se rechaza y se le devuelve el motivo.
- **No elige por vos.** No recomienda lenguajes ni patrones; muestra información y espera la decisión de una persona.
- **No reemplaza al arquitecto.** Lo libera del trabajo repetitivo para que se dedique a decidir.

---
Siguiente: [02 · El modelo ArchiMate](02-el-modelo-archimate.md) — cómo se prepara el "plano" para que el programa lo entienda.
