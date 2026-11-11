# Supuestos de diseño — Repuestos del Taller

- Los campos de los eventos entre contextos son supuestos (ver `contrato-bus.md`): el modelo ArchiMate no los define.
- La bandeja de salida es en memoria y guarda cada evento cifrado con `CifradorAes` (los avisos pueden llevar datos de contacto); el destinatario del aviso de reposición es «compras» por defecto.
- Solo `Faltante detectado` tiene contrato publicado (`FaltanteDetectadoV1`): los manejadores escriben en la bandeja únicamente eventos con traductor; el resto de eventos de dominio se descarta tras guardar el agregado.
- Los consumidores deduplican por `eventId` en memoria; el modelo no define un almacén de mensajes procesados.
- Esquema PostgreSQL: dos tablas (`existencia`, `solicitud_de_reposicion`) que guardan el memento del agregado como JSON; se crean al iniciar (`CREATE TABLE IF NOT EXISTS`), sin migraciones, por tamaño del contexto. Se prueba con sqlite3 porque no hay servidor PostgreSQL en el entorno de revisión.
- `CifradorAes` exige `cryptography` (ya declarada en `pyproject.toml`); se eliminó el fallback XOR+HMAC. Si `CIFRADO_CLAVE` falta usa una clave local derivada: aceptable solo en desarrollo.
- El `DATABASE_URL` del compose viene en formato de SQLAlchemy (`postgresql+psycopg://…`); el servicio lo normaliza a `postgresql://` antes de `psycopg.connect`, porque el driver no entiende el sufijo de dialecto.
- El humo usa referencias y solicitudes con sufijo aleatorio por corrida: repetirlo sobre la misma base no altera las cifras de stock que verifica.
