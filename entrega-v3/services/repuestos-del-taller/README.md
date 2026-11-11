# Repuestos del Taller

Microservicio Python hexagonal para existencias y solicitudes de reposición.

## Ejecución

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
uvicorn repuestos_del_taller.adapters.inbound.http.composicion:app --port 5102
```

Variables: `PORT` (5102), `BUS_URL`, `SIMULATORS_URL`, `CIFRADO_CLAVE` (base64),
`DATABASE_URL` (PostgreSQL). Las pruebas no requieren red ni base de datos.

Rutas: `GET /health`, `POST /api/existencia`, los comandos de existencia bajo
`/api/existencia/{referencia}/`, y los comandos de reposición bajo
`/api/solicitud-de-reposicion/`.

La persistencia se encapsula en repositorios, con decoradores de caché TTL de 60
segundos. `BandejaDeSalida` publica eventos con reintentos y
`ProcesadorDeMensajeEntrante` deduplica por `eventId`.
