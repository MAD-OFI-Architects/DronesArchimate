# Ejecución del humo de Repuestos del Taller

Desde la raíz del repositorio:

```bash
cd out/.platform/repuestos-del-taller
docker compose up --build --wait
GATEWAY_URL=http://localhost:8080 python ../../services/repuestos-del-taller/smoke/smoke.py
```

La plataforma publica el gateway en `http://localhost:8080`, el servicio real
escucha internamente en `5102`, el bus en `5100` y los simuladores en `5110`.
El gateway enruta `/api/repuestos/...` al microservicio y `/sim/...` a la
plataforma simulada. El escenario espera salud, registra stock, emite una
parada programada, confirma una OT cerrada, fuerza un faltante y comprueba su
entrega al suscriptor. Después ejercita reserva, liberación, ajuste, solicitud,
aprobación y cancelación mediante las rutas del manifiesto.

Las pruebas herméticas del servicio se ejecutan sin Docker ni red:

```bash
cd out/services/repuestos-del-taller
python -m pytest
```

El servicio guarda su estado en memoria; para repetir el humo desde cero ejecuta antes
`docker compose restart repuestos-del-taller`.

Para detener la plataforma: `docker compose down`.
