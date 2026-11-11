# Decisiones y supuestos

## Decisiones

| ID | Decisión | Alternativas descartadas | Criterio | Razón | Riesgo | Hallazgo |
|---|---|---|---|---|---|---|
| D-01 | El E2E es «gestionar la disponibilidad de la flota por mantenimiento preventivo» (de la operación registrada a la liberación con indicadores) | Cadena completa del servicio de fumigación; solo el proceso del taller | Alcance de la solicitud y urgencia de las horas a tiempo | Une las cinco funciones pedidas y deja fuera misiones y facturación | Que el profesor entienda otro E2E (pendiente de aclarar) | H-24, H-38 |
| D-02 | El correctivo se registra con la misma OT (tipo «C») pero no se planifica ni se gestiona | Excluirlo; gestionarlo completo | Cohesión y propiedad de datos; alcance | Una OT es una OT y el histórico necesita ambas (P147); la solicitud es de preventivo | El correctivo es el 40 % de las OTs y puede pedir más funciones | H-27, H-38 |
| D-03 | Se incluye la consulta de habilitación vigente del técnico; la gestión documental de certificaciones queda fuera | Incluir toda la gestión de certificaciones; excluir también la consulta | Propiedad de datos | Mantenimiento necesita saber quién puede hacer qué (P156), pero los registros son de Administración | Datos de habilitación desactualizados (vencimientos que se detectan tarde) | H-04, H-06 |
| D-04 | Compras llega solo hasta la solicitud de reposición | Gestionar compras completas; solo consultar existencias | Alcance y existencia de un proveedor interno | La solicitud pide «repuestos por cada cambio», no un ERP (P152, P156) | El jefe seguirá comprando por fuera para urgencias | H-30, H-38 |
| D-05 | La telemetría no se construye: se importa por archivo con capa anticorrupción (ACL-03) | Contratar la gestión de flota en la nube del fabricante; construir integración por API | Costo/beneficio y riesgo | No hay API paga ni presupuesto (P87, P142) | El fabricante cambia el formato del export | H-35 |
| D-06 | Los donantes se excluyen del denominador de la disponibilidad, con una única regla versionada | Incluir los 12 drones; decidir caso por caso | Una sola cifra por período | Contarlos castiga el indicador sin reflejar capacidad; en octubre se obtuvieron 86,8 % o 90 % según la regla (P95) | El gerente prefiere ver la cifra con los 12 | H-28 |
| D-07 | Dron y Componente son dos agregados | Un solo agregado Dron con componentes dentro | Invariante que exige modificar juntos | El contador viaja con el componente y mover una pieza no debe modificar la flota (H-20, H-21) | Carreras de consistencia al instalar (se compensa con política) | H-20, H-21 |
| D-08 | La Condición de mantenimiento vive en el Plan por modelo (objeto de valor) | Dentro del Componente; agregado propio | Razón para cambiar | Cambia con boletines y hallazgos, no con cada vuelo | El Componente necesita el umbral para calcular su vida (núcleo compartido) | H-15, H-17 |
| D-09 | Plan por modelo, Plan por dron y Programa semanal son tres agregados distintos; la OT es otro | Plan y OT en un solo ciclo de vida | Ciclo de vida y concurrencia | Años vs. días; restricciones de bahías visibles solo en el programa semanal | Más eventos entre agregados | H-19, H-22 |
| D-10 | «Operación y Horas» es un dominio de soporte propio, con agregados acotados (Jornada de vuelo e Importación) | Dejarlo dentro de Flota; un registro de operación sin límite | Lenguaje y responsable distintos | Lenguaje de parte, jornada y consolidación; evita tamaño ilimitado | Duplicar datos de dron | H-24, H-26 |
| D-11 | La reserva de repuestos es inmediata y el consumo es eventual (por «Orden de trabajo cerrada») | Todo en la misma transacción | Una transacción modifica un solo agregado | La OT y la existencia son agregados distintos | Stock momentáneamente desfasado | H-29 |
| D-12 | El contexto del canvas es Plan de Mantenimiento | Intervenciones; Flota y Componentes | Mayor cantidad de reglas e interoperabilidad | Concentra condiciones, diferimientos, restricciones y 7 relaciones de contexto | Intervenciones también es rico en invariantes | H-15, H-17, H-19 |
| D-13 | El canvas se hace como vista ArchiMate con rejilla (opción A) | Plantilla de canvas de Archi; híbrido | Coherencia con el modelo | Los elementos son los mismos de las otras vistas | No se probó en Archi (ver investigación) | — |
| D-14 | Flota y Plan comparten un núcleo (condición, umbral, fuente) | Que Flota consulte a Plan por API | Costo de coordinación aceptado | Mismo equipo; vida remanente depende del umbral | Acoplamiento de cambios | H-13, H-15 |
| D-15 | Con la autoridad: lenguaje publicado + traducción del ID interno (ACL-05) | Conformista puro | Poder de negociación | No podemos influir en sus formatos y el ID interno no es la matrícula | Cambio de normativa | H-02, H-03 |
| D-16 | Los dominios Evidencia y Notificaciones son genéricos: se compran o integran | Construirlos | Madurez/commodity | Cualquier sistema exporta y avisa | Dependencia de un tercero | H-05 |
| D-17 | La infraestructura (identidad, auditoría, notificación) es N6 y se compra o integra | Construirla | Madurez/commodity | Servicios transversales sin negocio | Costos de licencias por usuario (presupuesto) | H-10, H-11 |
| D-18 | Todas las integraciones iniciales son por archivo (asíncronas e idempotentes) | APIs síncronas | Costo/beneficio y riesgo | No hay APIs ni conectividad estable en campo | Datos con retraso de hasta un día | H-35 |

## Supuestos

| ID | Supuesto | Hallazgo / fuente | Estado y cómo se validaría |
|---|---|---|---|
| S-01 | La «certificación» de técnicos son cursos del fabricante/distribuidor, sin licencia estatal | H-06 | No verificado; consultar a la Aerocivil o al distribuidor |
| S-02 | Ciclo exacto de reemplazo de hélices y motores según el manual DJI vigente | H-15 | No verificado; leer la tabla del manual |
| S-03 | El RAC 100 exige registros de mantenimiento/vuelo y un plazo de retención | H-12, H-40 | No verificado; leer el reglamento |
| S-04 | No se exige licencia estatal de técnico de mantenimiento UAS | H-06 | No verificado |
| S-05 | La Res. 799/2025 alcanza a las baterías de litio de la flota | H-09 | No verificado; MinAmbiente o autoridad regional |
| S-06 | El Decreto 1843/1991 aplica a la aspersión con UAS como a la tripulada | H-07 | No verificado; concepto del ICA |
| S-07 | La tarifa realista es $40-60 mil COP/ha | H-31 | No verificado; cotizaciones del sector |
| S-08 | Congelar el firmware en campaña es seguro y suficiente | H-39 | No verificado; boletines de DJI |
| S-09 | Las integraciones iniciales son por archivo exportado (sin API del fabricante) | H-35 | Verificar términos de la plataforma DJI |
| S-10 | Pilotos y técnicos aceptan registrar desde el celular o el taller con conectividad regular | P142, P144 | No verificado; riesgo de resistencia al cambio |
| S-11 | Los donantes se identifican con una marca en el dron (estado «donante») | H-28 | Decisión de diseño por validar con el experto |
