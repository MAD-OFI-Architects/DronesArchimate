# Ejecución del dominio Intervenciones

## Levantar solo este dominio (plataforma de humo)

Requisitos: Docker con Compose v2 y Python 3.

```bash
cd .platform/intervenciones
docker compose up --build --wait        # mongo (replica set rs0), bus, simuladores, servicio y gateway
```

La plataforma se regenera: no se edita. El único servicio real es Intervenciones; los demás contextos son simuladores.

## URLs (gateway `http://localhost:8080`, o `GATEWAY_PORT`)

| URL | Destino |
|---|---|
| `/api/intervenciones/orden-de-trabajo…` | Servicio Intervenciones (`:5101`, rutas `/api/orden-de-trabajo…`) |
| `/api/intervenciones/orden-de-trabajo/por-parada/{paradaId}` | Consulta de la orden abierta para una parada |
| `/sim/simulate/<contexto>/<evento>` | Un simulador publica un evento en el bus (`POST`, cuerpo opcional) |
| `/sim/received` | Eventos que recibieron los suscriptores simulados |
| `/sim/health` | Salud de los simuladores |

## Escenario del humo

```bash
python3 services/intervenciones/smoke/smoke.py       # GATEWAY_URL=http://localhost:8080 por defecto
```

Solo usa la biblioteca estándar; cada espera reintenta hasta 60 s. Sale con 0 solo si todo ocurre:

1. Espera al simulador y al servicio.
2. `Parada programada` (simulada) abre una orden `Abierta` para el dron.
3. `Faltante detectado` (simulado) la deja `EnEspera` con el repuesto en el motivo.
4. Comandos de usuario: asignar técnico, registrar ejecución de tarea (→ `EnEjecucion`), consumo, hallazgo, vuelo de prueba (→ `Ejecutada`), liberar dron (→ `Liberada`) y cerrar (→ `Cerrada`).
5. Abrir orden de trabajo y poner en espera directamente por la API.
6. `Orden de trabajo cerrada` llega a `/sim/received` con parada, dron, 3,5 horas-hombre y consumos.

Se apaga con `docker compose down -v`.

## Pruebas del servicio (herméticas)

```bash
cd services/intervenciones
dotnet test tests/BuildingBlocks.Tests
dotnet test tests/Intervenciones.Tests
```

## Solución de problemas

- `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`: el usuario no pertenece al grupo `docker`. Añádelo (`sudo usermod -aG docker $USER`) y abre una sesión nueva, o ejecuta los comandos con un usuario con acceso al socket.
