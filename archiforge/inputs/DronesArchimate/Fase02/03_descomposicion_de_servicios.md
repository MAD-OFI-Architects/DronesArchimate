# Fase 2 · V4 — Descomposición de servicios

![V04](../vistas/V04_descomposicion_de_servicios.png)

**Capas (siete bandas de arriba hacia abajo).** N1 proceso E2E → N2 servicios de negocio de plataforma (4) → N3 servicios de subdominio (7) → N4 servicios básicos (20, agrupados por subdominio) → ACL capa anticorrupción con los 10 servicios externos → N5 servicios fundamentales (3) → N6 infraestructura de servicio (3), más los servicios fuera del alcance. Los servicios son *Business Service* (amarillo) con nombres de resultado de negocio, no verbos CRUD técnicos (por ejemplo «Registro de operación de flota» y no «API de horas»). Las relaciones que saltan bandas (N2→ACL, N5→N3) van por los carriles laterales.

**Cómo se decidió la granularidad (P1/P2 de la metodología SOA).** Se partió de cada paso del E2E y se preguntó quién es responsable, quién gestiona los datos, quién define las reglas, dónde más se usa y qué cambia junto con qué:
- *Programación de mantenimiento preventivo* (N2) agrupa detectar, programar y alistar, porque un mismo actor (el jefe) las decide juntas y cambian juntas.
- *Ejecución y liberación* (N2) agrupa ejecutar, verificar y cerrar: comparten la OT y la regla «quien ejecuta no libera».
- *Disponibilidad de la flota* (N2) responde a Comercial y Gerencia; *Evidencia de mantenimiento* (N2) responde a auditorías.
- En N3 cada subdominio posee sus datos y sus reglas: Operación, Flota y componentes, Plan, Órdenes, Repuestos del taller, Indicadores y Habilitación. Los servicios no se llaman entre sí: la coordinación vive en los eventos (Fase 4/5).
- N4 contiene operaciones atómicas visibles solo dentro de su subdominio (V04a-d): por ejemplo «Evaluación de vencimientos» o «Autorización de liberación».

**Vistas por servicio de plataforma.** V04a (programación), V04b (ejecución y liberación), V04c (disponibilidad) y V04d (evidencia) muestran, de izquierda a derecha, roles → procesos de V3 que realizan el servicio → servicio N2 ← servicios N3 con sus N4 anidados ← servicios fundamentales y externos; arriba, las capacidades de V2 que el servicio realiza.

![V04a](../vistas/V04a_servicios_de_programacion_de_mantenimiento_preventivo.png)

![V04b](../vistas/V04b_servicios_de_ejecucion_y_liberacion_de_intervenciones.png)

![V04c](../vistas/V04c_servicios_de_disponibilidad_de_la_flota.png)

![V04d](../vistas/V04d_servicios_de_evidencia_de_mantenimiento.png)

**Enlaces con otras vistas.** Cada servicio realiza una capacidad de V2 (*Realization*), cada paso o función de V3 realiza un servicio de plataforma (*Realization*) y cada servicio lleva su rol responsable (*Assignment*). Las flechas *Serving* van del proveedor al consumidor.

**Exclusiones tan importantes como las inclusiones.** Doce servicios fuera del alcance, con proveedor: misiones de vuelo, facturación, nómina, contabilidad, CRM, inventario general, compras, gestión documental de certificaciones, telemetría en la nube, trámites ante la Aerocivil, mantenimiento predictivo con analítica avanzada y SST. Ver `01_tabla_inclusion_exclusion.md`.

**Infraestructura (N6).** Identidad y permisos, auditoría y trazabilidad de cambios y notificación sirven a los cuatro servicios de plataforma (las flechas existen en el modelo y se omiten en V04 por claridad). Son servicios genéricos que se compran o integran, claramente separados del negocio.
