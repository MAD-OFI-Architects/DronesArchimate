# Fase 3 · Dominios (clústeres) y clasificación (V5)

![V05](../vistas/V05_dominios.png)

Se extrajeron **9 dominios** del Event Storming: 3 core, 4 de soporte y 2 genéricos. No todo es core: la prueba rápida (diferenciación vs. complejidad) deja arriba a la derecha solo Flota y Componentes, Plan de Mantenimiento e Intervenciones.

```
complejidad ↑
 alta  |  Flota y Comp. ●   Plan ●   Intervenciones ●      (core)
 media |  Operación y Horas ○   Repuestos ○                  (soporte)
 baja  |  Indicadores ○  Habilitación ○   Evidencia □  Notificaciones □
        ------------------------------------------------→ diferenciación del negocio
```

## Preguntas de tensión (con nuestra postura y hallazgos)
- **¿La gestión de indicadores diferencia al negocio o es reporte genérico?** Soporte. Las fórmulas son estándar (P91); lo propio es la regla de conteo única (H-28), que se modela, pero el tablero en sí podría ser BI.
- **¿La gestión de inventario/repuestos es core?** No: es soporte acotado al stock del taller (reserva, consumo, solicitud); el inventario general y las compras quedan fuera y se integran (D-04, ACL-02).
- **¿El registro de horas/ciclos es un dominio propio?** Sí, como soporte: «Operación y Horas» consolida tres canales con discrepancias e idempotencia; no es core porque la diferenciación está en qué se hace con los contadores (Flota y Plan), pero tampoco se puede dejar dentro de otro dominio porque su lenguaje (jornada, parte, consolidación, horas de motor) y su responsable (piloto y jefe) son distintos (H-24, H-26).

## Fichas de dominio

### Flota y Componentes — Core
| Campo | Contenido |
|---|---|
| Propósito | Saber qué drones hay, qué componentes lleva cada uno y cuánta vida les queda, con el contador pegado al componente. |
| Eventos y comandos principales | Registrar dron → Dron registrado; Instalar componente en dron → Componente instalado en dron; Retirar componente del dron → Componente retirado del dron; Registrar componente → Componente registrado; Acumular uso del componente → Uso de componente acumulado; Registrar hora de corte → Hora de corte registrada |
| Actores | Almacenista, Jefe de Operaciones y Mantenimiento, Técnico |
| Clasificación | Core |
| Argumento 1 · diferenciación | El «reloj del componente» y su arrastre entre drones es lo que hoy no se logra (H-20, H-21) y origina fallas como la del ADV-02. |
| Argumento 2 · complejidad/volatilidad | Alta: dos marcas, despiece por modelo, pool de baterías, donantes; cambia al comprar equipos nuevos. |
| Argumento 3 · comprar vs. construir | No existe un producto que modele este despiece con arrastre de vida entre drones; se construye. |
| Estrategia de inversión | Diseño táctico completo (agregados Dron y Componente, V6a). |
| Dependencias con otros dominios | Recibe horas de Operación y Horas; informa contadores a Plan; recibe cambios de Intervenciones. |
### Plan de Mantenimiento — Core
| Campo | Contenido |
|---|---|
| Propósito | Decidir cuándo toca intervenir cada dron y componente y programar paradas sin chocar con los servicios. |
| Eventos y comandos principales | Definir tarea de plan → Tarea de plan definida; Ajustar umbral de condición → Umbral ajustado; Publicar versión del plan → Versión del plan publicada; Crear plan de dron → Plan de dron creado; Evaluar vencimientos del dron → Umbral de condición alcanzado, Tarea vencida; Diferir tarea → Tarea diferida; Programar parada → Parada programada; Reprogramar parada → Parada reprogramada; Cancelar parada → Parada cancelada |
| Actores | Jefe de Operaciones y Mantenimiento |
| Clasificación | Core |
| Argumento 1 · diferenciación | Convierte datos en la decisión de cuándo intervenir: «lo que ocurra primero», fuentes de intervalos, diferimientos y paradas con restricciones físicas (H-15, H-17, H-19). |
| Argumento 2 · complejidad/volatilidad | Alta: reglas cambian con boletines y hallazgos; restricciones de bahías, líneas y técnicos. |
| Argumento 3 · comprar vs. construir | Un ERP de mantenimiento genérico no cubre estas reglas ni el ajuste por dron; se construye. |
| Estrategia de inversión | Diseño táctico completo (agregados Plan por modelo, Plan por dron y Programa semanal, V6b). |
| Dependencias con otros dominios | Consume contadores de Flota; pide reservas a Repuestos; programa paradas que abren OTs; consulta Habilitación. |
### Intervenciones — Core
| Campo | Contenido |
|---|---|
| Propósito | Ejecutar, liberar y cerrar el trabajo de mantenimiento dejando evidencia verificable. |
| Eventos y comandos principales | Abrir orden de trabajo → Orden de trabajo abierta; Asignar técnico → Técnico asignado; Registrar ejecución de tarea → Ejecución de tarea registrada |
| Actores | Jefe de Operaciones y Mantenimiento, Técnico |
| Clasificación | Core |
| Argumento 1 · diferenciación | Aplica «quien ejecuta no libera» y la hora de corte; es la prueba de aeronavegabilidad ante autoridad, aseguradora e ingenios (H-22, H-23). |
| Argumento 2 · complejidad/volatilidad | Alta: estados, invariantes de liberación y cierre; correctivos y preventivos comparten OT. |
| Argumento 3 · comprar vs. construir | Un software de OT genérico no impone la liberación ni arrastra vida; se construye. |
| Estrategia de inversión | Diseño táctico completo (agregado Orden de trabajo, V6c). |
| Dependencias con otros dominios | Recibe paradas de Plan; confirma consumos a Repuestos; informa cierres a Flota, Plan e Indicadores. |
### Operación y Horas — Soporte
| Campo | Contenido |
|---|---|
| Propósito | Registrar las operaciones de vuelo y consolidar horas y ciclos en una entrada única. |
| Eventos y comandos principales | Registrar jornada de vuelo → Jornada de vuelo registrada; Registrar vuelo → Vuelo registrado; Confirmar jornada → Jornada confirmada; Importar telemetría → Telemetría importada; Rechazar importación duplicada → Importación rechazada por duplicado |
| Actores | Jefe de Operaciones y Mantenimiento, Piloto |
| Clasificación | Soporte |
| Argumento 1 · diferenciación | Es necesario y urgente (P149) pero no diferencia: cualquier flota necesita horas al día. |
| Argumento 2 · complejidad/volatilidad | Media: tres canales, discrepancias e idempotencia de la telemetría. |
| Argumento 3 · comprar vs. construir | No se compra: depende del modelo de telemetría de cada fabricante (ACL-03); se construye lo mínimo con ACL. |
| Estrategia de inversión | Diseño razonable: dos agregados pequeños (V6d) y capa anticorrupción. |
| Dependencias con otros dominios | Emite horas consolidadas a Flota e Indicadores; importa telemetría por ACL-03. |
### Repuestos del Taller — Soporte
| Campo | Contenido |
|---|---|
| Propósito | Reservar y consumir repuestos por OT y pedir reposición al tocar el mínimo. |
| Eventos y comandos principales | Registrar entrada de repuesto → Repuesto recibido; Reservar repuesto → Repuesto reservado, Faltante detectado; Liberar reserva → Reserva liberada; Solicitar reposición → Reposición solicitada; Aprobar solicitud → Solicitud aprobada; Cancelar solicitud → Solicitud cancelada |
| Actores | Almacenista, Jefe de Operaciones y Mantenimiento |
| Clasificación | Soporte |
| Argumento 1 · diferenciación | Apoya al core (evita el caso ADV-02) pero un taller cualquiera también reserva repuestos. |
| Argumento 2 · complejidad/volatilidad | Media: reservas, mínimos y niveles de aprobación. |
| Argumento 3 · comprar vs. construir | Existen sistemas de inventario, pero el inventario general quedó fuera; se construye solo reserva, consumo y solicitud. |
| Estrategia de inversión | Diseño razonable (V6e). |
| Dependencias con otros dominios | Atiende reservas de Plan y consumos de Intervenciones; avisa a Notificaciones. |
### Indicadores — Soporte
| Campo | Contenido |
|---|---|
| Propósito | Calcular disponibilidad, cumplimiento del plan, MTBF y costo por hora con una sola regla de conteo. |
| Eventos y comandos principales | Definir indicador → Indicador definido; Cambiar regla de conteo → Regla de conteo cambiada; Fijar meta → Meta fijada; Calcular indicador → Indicador calculado, Meta incumplida detectada |
| Actores | Gerencia, Jefe de Operaciones y Mantenimiento |
| Clasificación | Soporte |
| Argumento 1 · diferenciación | Las fórmulas son estándar; solo la regla de conteo única (donantes) es propia (H-28). No diferencia al negocio. |
| Argumento 2 · complejidad/volatilidad | Baja a media: cálculos sobre eventos; la regla es lo delicado. |
| Argumento 3 · comprar vs. construir | Una herramienta de BI podría sustituir los tableros, pero la regla y las metas se modelan aquí. |
| Estrategia de inversión | Diseño razonable, agregados livianos (V6f). |
| Dependencias con otros dominios | Escucha eventos de Operación, Plan e Intervenciones. |
### Habilitación de Personal — Soporte
| Campo | Contenido |
|---|---|
| Propósito | Saber qué técnico está habilitado para qué modelo y tarea (espejo de lo que administra Talento humano). |
| Eventos y comandos principales | Registrar habilitación sincronizada → Habilitación registrada; Revocar habilitación vencida → Habilitación vencida |
| Actores | Marta (Administración, dueña de las carpetas y hojas de vida) y Jefe de Operaciones y Mantenimiento (consulta la vigencia) |
| Clasificación | Soporte |
| Argumento 1 · diferenciación | Específico del taller (curso por modelo) pero sin ventaja competitiva. |
| Argumento 2 · complejidad/volatilidad | Baja: pocas reglas, datos de solo lectura. |
| Argumento 3 · comprar vs. construir | Los registros viven en Administración (ACL-04); aquí solo se consulta la vigencia. |
| Estrategia de inversión | Diseño mínimo (V6g). |
| Dependencias con otros dominios | Consume ACL-04; sirve a Plan e Intervenciones. |
### Evidencia y Reportes — Genérico
| Campo | Contenido |
|---|---|
| Propósito | Entregar el histórico por dron a ingenios, aseguradora y autoridad en un día. |
| Eventos y comandos principales | Sin diseño táctico propio (comprar/integrar) |
| Actores | Jefe de Operaciones y Mantenimiento (arma el paquete) y Gerencia (lo entrega) |
| Clasificación | Genérico |
| Argumento 1 · diferenciación | Cualquier operador debe poder exportar su historial; no es lo que diferencia al negocio. |
| Argumento 2 · complejidad/volatilidad | Baja: lee lo que producen Flota e Intervenciones. |
| Argumento 3 · comprar vs. construir | Comprar o integrar una herramienta de reportes/exportación sobre los datos del core. |
| Estrategia de inversión | Solo se justifica la compra/integración; sin diseño táctico propio. |
| Dependencias con otros dominios | Lee de Flota, Operación e Intervenciones; entrega por ACL-05, ACL-08 y ACL-09. |
### Notificaciones — Genérico
| Campo | Contenido |
|---|---|
| Propósito | Avisar por correo o WhatsApp vencimientos, paradas y habilitaciones por vencer. |
| Eventos y comandos principales | Sin diseño táctico propio (comprar/integrar) |
| Actores | Jefe de Operaciones y Mantenimiento (define qué avisar y a quién) |
| Clasificación | Genérico |
| Argumento 1 · diferenciación | Funcionalidad común a cualquier sistema. |
| Argumento 2 · complejidad/volatilidad | Baja. |
| Argumento 3 · comprar vs. construir | Comprar/integrar un servicio de mensajería; no se construye. |
| Estrategia de inversión | Solo integración; sin diseño táctico propio. |
| Dependencias con otros dominios | Atiende pedidos de Plan, Repuestos y Habilitación. |
