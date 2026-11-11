# Fase 4 · Agregados, comandos y eventos (V6)

![V06a - Agregados Flota y Componentes](../vistas/V06a_agregados_flota_y_componentes.png)

![V06b - Agregados Plan de Mantenimiento](../vistas/V06b_agregados_plan_de_mantenimiento.png)

![V06c - Agregados Intervenciones](../vistas/V06c_agregados_intervenciones.png)

![V06d - Agregados Operación y Horas](../vistas/V06d_agregados_operacion_y_horas.png)

![V06e - Agregados Repuestos del Taller](../vistas/V06e_agregados_repuestos_del_taller.png)

![V06f - Agregados Indicadores](../vistas/V06f_agregados_indicadores.png)

![V06g - Agregados Habilitación de Personal](../vistas/V06g_agregados_habilitacion_de_personal.png)

Un diagrama por dominio con diseño táctico (los tres core y los cuatro de soporte); los dominios genéricos (Evidencia y Notificaciones) no tienen diseño táctico porque se compran o integran. Convención: comandos en imperativo, eventos en pasado, objetos en sustantivo singular. En ArchiMate: raíz/entidades/objetos de valor = *Data Object* (con `Rol`), límite = *Grouping*, comando = *Application Process*, evento = *Application Event*, actor = *Business Role*, política = *Triggering* evento → comando. Las referencias entre agregados son solo por ID.

## Verificación de consistencia
- Todo evento tiene al menos un emisor: **59 eventos, 59 con comando emisor**.
- Todo comando tiene un agregado receptor: **54 comandos**, cada uno con *Access* hacia la raíz de su agregado.
- Eventos externos (de negocio) que disparan políticas: Vuelo completado, Boletín del fabricante recibido.

## Políticas entre agregados («cuando X ocurrió entonces comando Y»)

| Cuando ocurre (evento) | Entonces (comando) | Agregado receptor |
|---|---|---|
| Vuelo completado | Registrar jornada de vuelo | Jornada de vuelo |
| Telemetría importada | Consolidar horas y ciclos | Jornada de vuelo |
| Discrepancia detectada | Corregir jornada | Jornada de vuelo |
| Horas consolidadas | Acumular horas de dron | Dron |
| Horas consolidadas | Acumular uso del componente | Componente |
| Horas consolidadas | Calcular indicador | Medición de indicador |
| Horas de dron acumuladas | Evaluar vencimientos del dron | Plan por dron |
| Uso de componente acumulado | Evaluar vencimientos del dron | Plan por dron |
| Tarea vencida | Programar parada | Programa semanal |
| Boletín del fabricante recibido | Aplicar boletín del fabricante | Plan por modelo |
| Versión del plan publicada | Evaluar vencimientos del dron | Plan por dron |
| Parada programada | Abrir orden de trabajo | Orden de trabajo |
| Parada programada | Reservar repuesto | Existencia |
| Parada no cumplida | Reprogramar parada | Programa semanal |
| Faltante detectado | Poner orden en espera | Orden de trabajo |
| Stock mínimo alcanzado | Solicitar reposición | Solicitud de reposición |
| Orden de trabajo cerrada | Reiniciar reloj de tarea | Plan por dron |
| Orden de trabajo cerrada | Confirmar consumo | Existencia |
| Orden de trabajo cerrada | Instalar componente en dron | Dron |
| Orden de trabajo cerrada | Retirar componente del dron | Dron |
| Orden de trabajo cerrada | Calcular indicador | Medición de indicador |
| Componente instalado en dron | Registrar hora de corte | Componente |
| Componente retirado del dron | Registrar hora de corte | Componente |
| Habilitación vencida | Reprogramar parada | Programa semanal |

## Fichas de agregado

### Dron — dominio Flota y Componentes
Vista: `V06a - Agregados Flota y Componentes`

| Campo | Contenido |
|---|---|
| Raíz | Dron |
| Entidades internas | Componente instalado |
| Objetos de valor | ID interno, Modelo, Horas de dron, Estado del dron |
| **Invariantes** | 1. Un dron tiene a lo sumo un componente instalado por posición del despiece de su modelo.<br>2. Las horas de dron nunca disminuyen.<br>3. El ID interno es único e inmutable.<br>4. Un dron donante nunca queda en estado verde.<br>5. Un componente figura instalado en un solo dron a la vez (se verifica contra el estado del componente por ID). |
| Comandos (precondición → evento) | Registrar dron → Dron registrado<br>Instalar componente en dron → Componente instalado en dron<br>Retirar componente del dron → Componente retirado del dron<br>Acumular horas de dron → Horas de dron acumuladas<br>Marcar dron como donante → Dron marcado como donante<br>Actualizar estado del dron → Estado del dron actualizado |
| Eventos que emite (y quién reacciona) | Dron registrado → sin política interna (consumo externo o histórico)<br>Componente instalado en dron → Registrar hora de corte<br>Componente retirado del dron → Registrar hora de corte<br>Horas de dron acumuladas → Evaluar vencimientos del dron<br>Dron marcado como donante → sin política interna (consumo externo o histórico)<br>Estado del dron actualizado → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Modelo (por ID de modelo); Componente (por ID de componente instalado). |
| ¿Por qué este límite? | La invariante «una pieza por posición» y la de instalación única exigen modificar el dron y su mapa de instalación en una sola transacción. |
| ¿Por qué no más grande? | Meter el Componente (contadores y vida) dentro del Dron lo haría crecer con cada vuelo y obligaría a modificar dos drones al mover una pieza (H-20, H-21). |
| ¿Por qué no más pequeño? | Separar «Componente instalado» del Dron rompería la invariante de una pieza por posición. |

### Componente — dominio Flota y Componentes
Vista: `V06a - Agregados Flota y Componentes`

| Campo | Contenido |
|---|---|
| Raíz | Componente |
| Entidades internas | Contador |
| Objetos de valor | Número de serie, Tipo de componente, Vida remanente, Estado del componente |
| **Invariantes** | 1. El contador pertenece al componente y viaja con él; solo crece (las correcciones se documentan).<br>2. El número de serie es único.<br>3. Un componente retirado o dispuesto no puede instalarse.<br>4. Los ciclos de una batería solo provienen de la telemetría, por ID de batería.<br>5. La vida remanente = umbral aplicable − contador y no se almacena negativa. |
| Comandos (precondición → evento) | Registrar componente → Componente registrado<br>Acumular uso del componente → Uso de componente acumulado<br>Registrar hora de corte → Hora de corte registrada<br>Retirar componente de servicio → Componente retirado de servicio<br>Disponer componente → Componente dispuesto |
| Eventos que emite (y quién reacciona) | Componente registrado → sin política interna (consumo externo o histórico)<br>Uso de componente acumulado → Evaluar vencimientos del dron<br>Hora de corte registrada → sin política interna (consumo externo o histórico)<br>Componente retirado de servicio → sin política interna (consumo externo o histórico)<br>Componente dispuesto → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Dron actual (por ID de dron); Modelo (por ID). |
| ¿Por qué este límite? | El contador y la vida remanente deben cambiar juntos y viajar con la pieza entre drones (pool de baterías, donantes). |
| ¿Por qué no más grande? | Incluir el plan o las condiciones dentro del Componente lo acoplaría a las reglas que cambian con cada boletín. |
| ¿Por qué no más pequeño? | Separar el Contador del Componente permitiría contadores huérfanos sin pieza. |

### Plan por modelo — dominio Plan de Mantenimiento
Vista: `V06b - Agregados Plan de Mantenimiento`

| Campo | Contenido |
|---|---|
| Raíz | Plan por modelo |
| Entidades internas | Tarea de plan |
| Objetos de valor | Condición de mantenimiento, Umbral, Fuente del intervalo |
| **Invariantes** | 1. Toda tarea tiene al menos una condición; con varias manda lo que ocurra primero.<br>2. Una tarea no puede tener dos condiciones activas del mismo tipo.<br>3. Todo umbral registra su fuente: manual del fabricante o criterio interno.<br>4. Un umbral interno nunca es más laxo que el del manual (cuando el manual se conoce).<br>5. Todo cambio de intervalo crea una nueva versión del plan; las versiones publicadas no se editan.<br>6. Una tarea crítica no admite diferimiento. |
| Comandos (precondición → evento) | Definir tarea de plan → Tarea de plan definida<br>Ajustar umbral de condición → Umbral ajustado<br>Publicar versión del plan → Versión del plan publicada<br>Aplicar boletín del fabricante → Boletín del fabricante aplicado |
| Eventos que emite (y quién reacciona) | Tarea de plan definida → sin política interna (consumo externo o histórico)<br>Umbral ajustado → sin política interna (consumo externo o histórico)<br>Versión del plan publicada → Evaluar vencimientos del dron<br>Boletín del fabricante aplicado → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Modelo (por ID de modelo); Tipo de componente (por ID). |
| ¿Por qué este límite? | Las condiciones de un modelo se versionan juntas: un boletín cambia varias tareas a la vez. |
| ¿Por qué no más grande? | Meter los planes de cada dron aquí haría que un ajuste individual bloquee la edición del modelo. |
| ¿Por qué no más pequeño? | Una tarea sin su condición no tiene sentido; condición y fuente deben cambiar juntas. |

### Plan por dron — dominio Plan de Mantenimiento
Vista: `V06b - Agregados Plan de Mantenimiento`

| Campo | Contenido |
|---|---|
| Raíz | Plan por dron |
| Entidades internas | Tarea programada |
| Objetos de valor | Ajuste por dron, Diferimiento, Vencimiento |
| **Invariantes** | 1. Una tarea crítica vencida deja al dron en rojo: no vuela.<br>2. Solo se difieren tareas menores, hasta 10 % del intervalo, con autorización del jefe.<br>3. Un ajuste por dron no puede relajar el umbral del plan por modelo.<br>4. Un dron donante solo conserva un plan mínimo.<br>5. El vencimiento se recalcula solo con contadores informados (nunca se estima). |
| Comandos (precondición → evento) | Crear plan de dron → Plan de dron creado<br>Evaluar vencimientos del dron → Umbral de condición alcanzado, Tarea vencida<br>Diferir tarea → Tarea diferida<br>Ajustar plan por dron → Plan de dron ajustado<br>Reiniciar reloj de tarea → Reloj de tarea reiniciado |
| Eventos que emite (y quién reacciona) | Plan de dron creado → sin política interna (consumo externo o histórico)<br>Umbral de condición alcanzado → sin política interna (consumo externo o histórico)<br>Tarea vencida → Programar parada<br>Tarea diferida → sin política interna (consumo externo o histórico)<br>Plan de dron ajustado → sin política interna (consumo externo o histórico)<br>Reloj de tarea reiniciado → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Dron (por ID); Plan por modelo (por ID y versión); Componente (por ID, para leer contadores). |
| ¿Por qué este límite? | Cada dron decide su vencimiento y sus diferimientos con su propia historia; una transacción por dron. |
| ¿Por qué no más grande? | Un solo agregado con todos los drones bloquearía el cálculo de vencimientos de toda la flota. |
| ¿Por qué no más pequeño? | Las tareas de un dron comparten la invariante «crítica vencida ⇒ dron rojo». |

### Programa semanal — dominio Plan de Mantenimiento
Vista: `V06b - Agregados Plan de Mantenimiento`

| Campo | Contenido |
|---|---|
| Raíz | Programa semanal |
| Entidades internas | Parada |
| Objetos de valor | Bahía, Ventana de parada |
| **Invariantes** | 1. No hay más de dos paradas concurrentes (dos bahías).<br>2. No hay dos drones de la misma línea en el taller a la vez.<br>3. Una parada agrupa todas las tareas que vencen en las próximas 25-50 h.<br>4. Una tarea crítica prevalece sobre un servicio comprometido: se cambia el dron del servicio, no la parada.<br>5. El técnico asignado está habilitado para el modelo. |
| Comandos (precondición → evento) | Programar parada → Parada programada<br>Reprogramar parada → Parada reprogramada<br>Cancelar parada → Parada cancelada<br>Registrar parada no cumplida → Parada no cumplida |
| Eventos que emite (y quién reacciona) | Parada programada → Abrir orden de trabajo, Reservar repuesto<br>Parada reprogramada → sin política interna (consumo externo o histórico)<br>Parada cancelada → sin política interna (consumo externo o histórico)<br>Parada no cumplida → Reprogramar parada |
| Referencias externas (por ID) | Dron (por ID); Técnico habilitado (por ID); Tareas programadas (por ID). |
| ¿Por qué este límite? | Las restricciones de capacidad (dos bahías, misma línea) solo se pueden proteger viendo todas las paradas de la semana a la vez. |
| ¿Por qué no más grande? | Programar todo el año en un agregado generaría conflictos de concurrencia entre semanas sin relación. |
| ¿Por qué no más pequeño? | Una Parada aislada no puede garantizar el tope de bahías. |

### Orden de trabajo — dominio Intervenciones
Vista: `V06c - Agregados Intervenciones`

| Campo | Contenido |
|---|---|
| Raíz | Orden de trabajo |
| Entidades internas | Tarea ejecutada, Consumo (de repuesto), Liberación |
| Objetos de valor | Tipo de orden, Estado de la orden, Hallazgo, Horas-hombre, Hora de corte, Vuelo de prueba |
| **Invariantes** | 1. En trabajos mayores quien libera es distinto de quien ejecutó.<br>2. La liberación de un trabajo mayor exige un vuelo de prueba satisfactorio.<br>3. No se cierra una OT sin repuestos con serie retirada e instalada y sin hora de corte de cada componente cambiado.<br>4. Una OT cerrada es inmutable; las correcciones se agregan como hallazgo o nota.<br>5. Solo se consume un repuesto reservado o autorizado para esa OT.<br>6. Una OT correctiva se registra con el mismo agregado, marcada «C». |
| Comandos (precondición → evento) | Abrir orden de trabajo → Orden de trabajo abierta<br>Asignar técnico → Técnico asignado<br>Registrar ejecución de tarea → Ejecución de tarea registrada<br>Registrar consumo de repuesto → Consumo de repuesto registrado<br>Registrar hallazgo → Hallazgo registrado<br>Registrar vuelo de prueba → Vuelo de prueba registrado<br>Liberar dron → Dron liberado<br>Cerrar orden de trabajo → Orden de trabajo cerrada<br>Poner orden en espera → Orden de trabajo puesta en espera |
| Eventos que emite (y quién reacciona) | Orden de trabajo abierta → sin política interna (consumo externo o histórico)<br>Técnico asignado → sin política interna (consumo externo o histórico)<br>Ejecución de tarea registrada → sin política interna (consumo externo o histórico)<br>Consumo de repuesto registrado → sin política interna (consumo externo o histórico)<br>Hallazgo registrado → sin política interna (consumo externo o histórico)<br>Vuelo de prueba registrado → sin política interna (consumo externo o histórico)<br>Dron liberado → sin política interna (consumo externo o histórico)<br>Orden de trabajo cerrada → Reiniciar reloj de tarea, Confirmar consumo, Instalar componente en dron, Retirar componente del dron, Calcular indicador<br>Orden de trabajo puesta en espera → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Dron (por ID); Parada (por ID); Técnico habilitado (por ID); Componentes y repuestos (por ID y serie). |
| ¿Por qué este límite? | La liberación, el vuelo de prueba y el cierre comparten el mismo ciclo de vida y la misma regla «quien ejecuta no libera». |
| ¿Por qué no más grande? | Incluir el Plan de dron dentro de la OT mezclaría un ciclo de vida largo con uno corto. |
| ¿Por qué no más pequeño? | Separar la Liberación de la OT permitiría liberar sin que se verifique la ejecución. |

### Jornada de vuelo — dominio Operación y Horas
Vista: `V06d - Agregados Operación y Horas`

| Campo | Contenido |
|---|---|
| Raíz | Jornada de vuelo |
| Entidades internas | Vuelo |
| Objetos de valor | Horas de vuelo, Carga de caldo, Origen del dato, Estado de confirmación |
| **Invariantes** | 1. Un vuelo se cuenta una sola vez aunque llegue por más de un canal.<br>2. Horas de vuelo y horas de motor son campos distintos.<br>3. Para horas de mantenimiento manda la plataforma; el parte en papel solo cuenta si no hubo sincronía.<br>4. Una diferencia mayor de 20 h obliga a revisión antes de volver a volar.<br>5. Una jornada confirmada solo se corrige con motivo registrado. |
| Comandos (precondición → evento) | Registrar jornada de vuelo → Jornada de vuelo registrada<br>Registrar vuelo → Vuelo registrado<br>Confirmar jornada → Jornada confirmada<br>Corregir jornada → Jornada corregida<br>Consolidar horas y ciclos → Horas consolidadas, Discrepancia detectada |
| Eventos que emite (y quién reacciona) | Jornada de vuelo registrada → sin política interna (consumo externo o histórico)<br>Vuelo registrado → sin política interna (consumo externo o histórico)<br>Jornada confirmada → sin política interna (consumo externo o histórico)<br>Jornada corregida → sin política interna (consumo externo o histórico)<br>Horas consolidadas → Acumular horas de dron, Acumular uso del componente, Calcular indicador<br>Discrepancia detectada → Corregir jornada |
| Referencias externas (por ID) | Dron (por ID); Piloto (por ID); Batería (por ID de componente). |
| ¿Por qué este límite? | Una jornada es el límite natural para no duplicar vuelos y confirmar datos. |
| ¿Por qué no más grande? | Un agregado «registro de operación» que crezca sin límite con todos los vuelos de un dron causaría contención y tamaño ilimitado. |
| ¿Por qué no más pequeño? | Un Vuelo aislado no puede evitar el doble conteo entre canales. |

### Importación de telemetría — dominio Operación y Horas
Vista: `V06d - Agregados Operación y Horas`

| Campo | Contenido |
|---|---|
| Raíz | Importación de telemetría |
| Entidades internas | Lectura de telemetría |
| Objetos de valor | Huella del archivo, Fuente del archivo |
| **Invariantes** | 1. La misma huella de archivo no se importa dos veces (idempotencia).<br>2. Toda lectura de batería lleva el ID de la batería.<br>3. Las horas de motor se conservan aparte de las horas de vuelo.<br>4. La importación es todo o nada. |
| Comandos (precondición → evento) | Importar telemetría → Telemetría importada<br>Rechazar importación duplicada → Importación rechazada por duplicado |
| Eventos que emite (y quién reacciona) | Telemetría importada → Consolidar horas y ciclos<br>Importación rechazada por duplicado → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Dron y Batería (por ID). |
| ¿Por qué este límite? | Un archivo es la unidad de idempotencia y de consistencia: entra completo o no entra. |
| ¿Por qué no más grande? | Mezclar las lecturas con la Jornada de vuelo ataría la telemetría a un modelo ajeno (ACL-03). |
| ¿Por qué no más pequeño? | Una lectura aislada no puede garantizar que su archivo no se repita. |

### Existencia — dominio Repuestos del Taller
Vista: `V06e - Agregados Repuestos del Taller`

| Campo | Contenido |
|---|---|
| Raíz | Existencia |
| Entidades internas | Reserva de repuesto |
| Objetos de valor | Stock mínimo, Cantidad, Plazo de entrega |
| **Invariantes** | 1. Lo reservado nunca supera la existencia.<br>2. La existencia usable = física − reservado y no es negativa.<br>3. Toda salida se hace contra una OT.<br>4. Al llegar al stock mínimo se solicita reposición.<br>5. Un conteo físico ajusta con motivo registrado. |
| Comandos (precondición → evento) | Registrar entrada de repuesto → Repuesto recibido<br>Reservar repuesto → Repuesto reservado, Faltante detectado<br>Liberar reserva → Reserva liberada<br>Confirmar consumo → Consumo confirmado, Stock mínimo alcanzado<br>Ajustar existencia por conteo → Existencia ajustada |
| Eventos que emite (y quién reacciona) | Repuesto recibido → sin política interna (consumo externo o histórico)<br>Repuesto reservado → sin política interna (consumo externo o histórico)<br>Faltante detectado → Poner orden en espera<br>Reserva liberada → sin política interna (consumo externo o histórico)<br>Consumo confirmado → sin política interna (consumo externo o histórico)<br>Stock mínimo alcanzado → Solicitar reposición<br>Existencia ajustada → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Repuesto (por ID de referencia); OT (por ID). |
| ¿Por qué este límite? | Reserva y existencia deben cambiar en la misma transacción para que no se prometa lo que no hay. |
| ¿Por qué no más grande? | Meter la solicitud de reposición dentro de la existencia mezclaría stock con aprobaciones. |
| ¿Por qué no más pequeño? | Una Reserva sin su Existencia no puede validar «reservado ≤ existencia». |

### Solicitud de reposición — dominio Repuestos del Taller
Vista: `V06e - Agregados Repuestos del Taller`

| Campo | Contenido |
|---|---|
| Raíz | Solicitud de reposición |
| Entidades internas | — |
| Objetos de valor | Cantidad solicitada, Nivel de aprobación |
| **Invariantes** | 1. El nivel de aprobación depende del monto: jefe hasta $5 M; gerencia por encima.<br>2. No hay dos solicitudes abiertas para la misma referencia.<br>3. El proceso del sistema termina en la solicitud; la compra es externa. |
| Comandos (precondición → evento) | Solicitar reposición → Reposición solicitada<br>Aprobar solicitud → Solicitud aprobada<br>Cancelar solicitud → Solicitud cancelada |
| Eventos que emite (y quién reacciona) | Reposición solicitada → sin política interna (consumo externo o histórico)<br>Solicitud aprobada → sin política interna (consumo externo o histórico)<br>Solicitud cancelada → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Repuesto (por ID); Existencia (por ID). |
| ¿Por qué este límite? | Tiene su propio ciclo de vida (pedir, aprobar, cancelar) y termina donde empieza compras. |
| ¿Por qué no más grande? | Unirla a Existencia bloquearía el stock mientras se espera una aprobación. |
| ¿Por qué no más pequeño? | No tiene partes que se justifiquen por sí solas. |

### Definición de indicador — dominio Indicadores
Vista: `V06f - Agregados Indicadores`

| Campo | Contenido |
|---|---|
| Raíz | Definición de indicador |
| Entidades internas | — |
| Objetos de valor | Fórmula, Regla de conteo, Meta (indicador) |
| **Invariantes** | 1. Hay una sola regla de conteo vigente por indicador.<br>2. Cambiar la regla crea una versión y no altera las mediciones pasadas.<br>3. Toda meta tiene valor y fecha. |
| Comandos (precondición → evento) | Definir indicador → Indicador definido<br>Cambiar regla de conteo → Regla de conteo cambiada<br>Fijar meta → Meta fijada |
| Eventos que emite (y quién reacciona) | Indicador definido → sin política interna (consumo externo o histórico)<br>Regla de conteo cambiada → sin política interna (consumo externo o histórico)<br>Meta fijada → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Ninguna. |
| ¿Por qué este límite? | Fórmula, regla y meta se versionan juntas. |
| ¿Por qué no más grande? | Incluir las mediciones haría crecer la definición sin límite. |
| ¿Por qué no más pequeño? | La regla de conteo sin su fórmula no se puede validar. |

### Medición de indicador — dominio Indicadores
Vista: `V06f - Agregados Indicadores`

| Campo | Contenido |
|---|---|
| Raíz | Medición de indicador |
| Entidades internas | — |
| Objetos de valor | Valor, Período, Versión de la regla |
| **Invariantes** | 1. Una medición es inmutable (solo se agregan nuevas).<br>2. Toda medición registra la versión de regla usada.<br>3. Hay una medición por indicador y período. |
| Comandos (precondición → evento) | Calcular indicador → Indicador calculado, Meta incumplida detectada |
| Eventos que emite (y quién reacciona) | Indicador calculado → sin política interna (consumo externo o histórico)<br>Meta incumplida detectada → sin política interna (consumo externo o histórico) |
| Referencias externas (por ID) | Definición de indicador (por ID y versión). |
| ¿Por qué este límite? | Cada medición es un hecho histórico independiente. |
| ¿Por qué no más grande? | Unirla a la definición la haría crecer sin límite. |
| ¿Por qué no más pequeño? | No tiene partes separables. |

### Técnico habilitado — dominio Habilitación de Personal
Vista: `V06g - Agregados Habilitación de Personal`

| Campo | Contenido |
|---|---|
| Raíz | Técnico habilitado |
| Entidades internas | Habilitación de modelo |
| Objetos de valor | Vigencia |
| **Invariantes** | 1. Sin habilitación vigente del modelo no se asigna calibración mayor ni garantía.<br>2. El XAG solo lo atienden técnicos habilitados para ese modelo (hoy Jhon Fredy y el jefe).<br>3. Una habilitación vencida se considera inexistente.<br>4. Los datos de origen son de solo lectura (vienen de ACL-04). |
| Comandos (precondición → evento) | Registrar habilitación sincronizada → Habilitación registrada<br>Revocar habilitación vencida → Habilitación vencida |
| Eventos que emite (y quién reacciona) | Habilitación registrada → sin política interna (consumo externo o histórico)<br>Habilitación vencida → Reprogramar parada |
| Referencias externas (por ID) | Técnico (por ID de persona en Administración); Modelo (por ID). |
| ¿Por qué este límite? | Las habilitaciones de un técnico se evalúan juntas al asignarle trabajo. |
| ¿Por qué no más grande? | Incluir los datos de personal de Administración violaría el límite de ACL-04. |
| ¿Por qué no más pequeño? | Una Habilitación sin su técnico no tiene sentido. |

