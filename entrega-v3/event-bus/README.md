# Bus de eventos por tópicos (sobre RabbitMQ)

Los servicios publican con `POST /publish` y reciben con `POST /events/{topic}`; entre ambos, RabbitMQ guarda los mensajes.
Contrato: `../docs/contrato-bus.md`.

- Por cada (tópico, suscriptor) hay una cola durable `<tópico>::<contexto>`, una cola de espera `.retry` y una cola de
  mensajes muertos `.dlq`. Tras `BUS_MAX_INTENTOS` (5) entregas fallidas el mensaje queda en la `.dlq`.
- `GET /dlq` cuenta los mensajes muertos por cola; `POST /dlq/reprocesar` los devuelve a su cola principal.
- `GET /events` muestra las últimas publicaciones; `GET /topics`, el catálogo.
- Consola de RabbitMQ: `http://localhost:${RABBITMQ_UI_PORT:-15672}` (usuario y clave `guest`).
- Sin `RABBITMQ_URL` el bus trabaja en memoria (solo pruebas): no conserva nada al reiniciarse.
