# Fase 1 · V3 — Cadena de valor y proceso E2E

![V03](../vistas/V03_cadena_de_valor_y_proceso_e2e.png)

![V03b](../vistas/V03b_excepciones_del_proceso_e2e.png)

**Flujo de valor (estrategia).** Cinco etapas de la empresa para prestar el servicio: contratar el servicio → programar el servicio → preparar la flota y la misión → aplicar el producto → informar y facturar (P12, P97). Las capacidades de V2 que sirven a cada etapa se conectan con *Serving*; las coloreadas son las impactadas por la aplicación (todas llegan a «Preparar la flota y la misión», donde vive la gestión de flota y aeronavegabilidad).

**Proceso E2E elegido.** *Gestionar la disponibilidad de la flota por mantenimiento preventivo*: empieza cuando se **registra la operación** (horas y ciclos) y termina cuando el dron queda **liberado y los indicadores actualizados**. Se descompone en 7 pasos (contenedor con composición) encadenados con *Triggering* a eventos de negocio.

| Paso | Disparador | Qué hace | Quién | Alcance |
|---|---|---|---|---|
| Registrar operación de vuelo | Vuelo completado | Unifica app del fabricante, parte de vuelo y WhatsApp en horas y ciclos | Piloto remoto (registro); jefe (consolidación) | Dentro |
| Detectar intervención por vencer | Umbral de condición alcanzado; boletín del fabricante; hallazgo reportado | Cruza contadores contra el plan | Jefe de Operaciones y Mantenimiento | Dentro |
| Programar intervención | Lista de intervenciones armada | Fija fecha, técnico y repuestos sin chocar con servicios | Jefe; Coordinación de servicios | Dentro |
| Alistar repuestos y bahía | Intervención programada | Abre la OT, reserva repuestos, prepara bahía | Almacenista | Dentro |
| Ejecutar intervención | Dron ingresado a taller | Diagnóstico, cambio, calibración y pruebas | Técnico de mantenimiento | Dentro |
| Verificar y liberar dron | Intervención ejecutada | Autoverificación, vuelo de prueba y firma | Técnico; jefe (mayores) | Dentro |
| Cerrar y registrar intervención | Dron liberado | Cierra OT, descuenta repuestos, actualiza bitácora, costo y contadores | Técnico | Dentro |

**Roles y actores.** Piloto remoto, Jefe de Operaciones y Mantenimiento, Técnico de mantenimiento, Almacenista, Coordinación de servicios y Gerencia (P22), con los actores que los desempeñan (Pompilio, Nubia, Sandra, los técnicos, el equipo de pilotos y Don Hernando). **Objetos de negocio** accedidos: parte de vuelo, registro de operación, plan por dron, programa semanal, reserva de repuesto, orden de trabajo, liberación y bitácora (son los mismos objetos del lenguaje ubicuo, V7).

**Bifurcaciones y excepciones (V3b).** Insumo del Event Storming de la Fase 3:

| Excepción / bifurcación | Se origina en | Cómo se resuelve | Vuelve a | Fuente |
|---|---|---|---|---|
| Faltante de repuesto detectado | Alistar repuestos | Resolver faltante: canibalizar donantes, prestar entre gemelos, comprar urgente o reprogramar; OT en espera (amarillo) | Alistar repuestos y bahía | P65, P106 |
| Condición crítica vencida en servicio | Operación (fuera) | Retirar el dron: aterriza, se envía sustituto; decide el jefe | Programar intervención | P50, P106 |
| Vuelo de prueba fallido | Verificar y liberar | Repetir la intervención; no se libera | Ejecutar intervención | P24, P34 |
| Intervención no cumplida | Programar intervención | Reprogramar el lunes siguiente con el motivo | Programar intervención | P76 |

**Alcance de la aplicación.** Amarillo = pasos que la aplicación automatiza o apoya; gris = procesos de otras áreas que se ven pero no se construyen: *Operar vuelo y aspersión*, *Programar servicios a clientes*, *Comprar o importar repuestos* y *Reportar a la autoridad y renovar registros* (P148, P155). El paso 2 destaca el cuello de botella real del negocio: el registro entra tarde (2-4 días) y el cierre se digita tarde (H-24).

## Decisión D-01: por qué este E2E y no otro

- *Alternativa A:* la cadena completa de prestación del servicio (de la orden de servicio al informe firmado). Se descartó como E2E de la aplicación porque la mayor parte (misiones, facturación) está fuera del alcance (P155) y diluiría el diseño; se conserva como flujo de valor.
- *Alternativa B:* solo el taller (de la parada a la liberación). Se descartó porque deja fuera lo que más duele —el registro de horas a tiempo (P149)— y los disparadores.
- *Elegida:* de la operación registrada a la liberación con indicadores, que es el hilo que une las cinco funciones de la solicitud. Está pendiente confirmar con el profesor qué entiende por E2E.

*Trazabilidad:* P12, P22, P28-P39, P50, P65, P76, P106 y H-22, H-23, H-24, H-34, H-38.
