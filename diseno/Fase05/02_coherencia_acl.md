# Fase 5 · Matriz de coherencia ACL ↔ mapa de contextos

![V09](../vistas/V09_interoperabilidad_y_anticorrupcion.png)

Toda fila de la tabla ACL de la Fase 2 aparece en V9 (componente ACL, interfaz y servicio), tiene su relación con patrón en V8 y el servicio interno que la consume existe en V4.

| ID externo (Fase 2) | Externo | ¿Aparece en V9? | ¿Aparece en V8 con patrón? ¿Coincide con la justificación? | ¿El servicio interno existe en V4? |
|---|---|---|---|---|
| ACL-01 | Programación de servicios a clientes | ✔ (ACL – Programación de servicios) | ✔ Capa anticorrupción; Lenguaje publicado | ✔ sd_plan, sv_disp (V4) |
| ACL-02 | Inventario y compras de repuestos | ✔ (ACL – Inventario y compras) | ✔ Capa anticorrupción; Cliente-Proveedor | ✔ sd_rep (V4) |
| ACL-03 | Telemetría de vuelo del fabricante | ✔ (ACL – Telemetría del fabricante) | ✔ Capa anticorrupción | ✔ sd_oper (V4) |
| ACL-04 | Certificaciones de personal | ✔ (ACL – Certificaciones de personal) | ✔ Capa anticorrupción | ✔ sd_hab, sd_ot (V4) |
| ACL-05 | Registro y supervisión aeronáutica | ✔ (ACL – Autoridad aeronáutica) | ✔ Lenguaje publicado | ✔ sv_evid (V4) |
| ACL-06 | Contabilidad y facturación | ✔ (ACL – Contabilidad y facturación) | ✔ Capa anticorrupción; Cliente-Proveedor | ✔ sd_ind, sd_ot (V4) |
| ACL-07 | Soporte, garantías y boletines del fabricante | ✔ (ACL – Fabricante y distribuidor) | ✔ Cliente-Proveedor; Conformista | ✔ sd_plan, sd_flota (V4) |
| ACL-08 | Cobertura de seguros | ✔ (ACL – Aseguradora) | ✔ Lenguaje publicado | ✔ sv_evid (V4) |
| ACL-09 | Auditoría comercial de clientes | ✔ (ACL – Clientes (auditoría)) | ✔ Lenguaje publicado | ✔ sv_evid (V4) |
| ACL-10 | Gestión de residuos y posconsumo | ✔ (ACL – Gestor de residuos) | ✔ Capa anticorrupción; Cliente-Proveedor | ✔ sd_flota (V4) |

**Mecanismo de comunicación.** Todo es asíncrono (archivo exportado, correo, portal) porque hoy no existen APIs ni integraciones pagas; el ACL guarda la huella del archivo o el identificador del mensaje para que los reintentos sean idempotentes (mismo archivo = mismo resultado), y un fallo no bloquea el flujo interno (se reintenta en la siguiente ventana). Lo síncrono se limita a consultas internas entre contextos (habilitación, evidencia). Ver ACL-03 (archivo manual) y ACL-01 (Excel, lunes).
**Qué traduce cada ACL** (opcional del guion): ver columna «Qué traduce» en `Fase02/02_tabla_acl.md`.
