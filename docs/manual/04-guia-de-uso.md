# 04 · Guía de uso: de cero a un producto funcionando

Hay **dos formas de usar el proyecto**, según lo que quieras hacer:

```
   A) SOLO PROBAR EL PRODUCTO YA HECHO                  B) CONSTRUIR (o reconstruir) CON ARCHIFORGE
   ─────────────────────────────────────                ───────────────────────────────────────────
   Necesitás: Docker                                    Necesitás: Python, Docker, un agente de IA
   Tiempo:    ~5 minutos                                Tiempo:    de minutos a horas (según el agente)
   Carpeta:   entrega-v3/                               Carpeta:   archiforge/
```

---

# A · Probar el producto ya construido

## 1. Requisitos

Solo **Docker con Compose**. En Arch Linux:

```bash
sudo pacman -S docker docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER     # cerrá sesión y volvé a entrar para que tome efecto
```

## 2. Levantar todo

```bash
cd entrega-v3
docker compose up -d --build --wait
```

Esto construye y arranca **8 contenedores** (la primera vez tarda unos minutos):

| Contenedor | Qué es |
|---|---|
| `gateway` | La puerta de entrada web (sirve las pantallas y enruta las peticiones) |
| `intervenciones` | Servicio de órdenes de trabajo (C#) |
| `repuestos-del-taller` | Servicio del almacén (Python) |
| `event-bus` | El "cartero" que recibe eventos y los entrega |
| `rabbitmq` | El buzón donde esperan los mensajes |
| `simulators` | Los contextos no construidos, simulados |
| `mongo` | Base de datos de Intervenciones |
| `postgres` | Base de datos de Repuestos |

## 3. Cargar datos de demostración

```bash
python3 seed/seed.py
```

Carga **8 repuestos**, **6 órdenes de trabajo en 6 estados distintos** (Abierta, En espera, En ejecución, Ejecutada, Liberada, Cerrada)
y **3 solicitudes de reposición**. Es **idempotente**: se puede repetir sin duplicar nada. Al terminar imprime los identificadores para
pegar en las consultas.

## 4. Dónde mirar

| Dirección | Qué hay |
|---|---|
| `http://localhost:8080/` | Las pantallas (elegí un rol arriba a la derecha) |
| `http://localhost:15672/` | Consola de RabbitMQ (usuario y clave `guest`): se ven las colas y los mensajes |
| `http://localhost:8080/bus/health` | Estado del bus: debe decir `"broker": "rabbitmq"` |
| `http://localhost:8080/bus/dlq` | Cantidad de mensajes que no se pudieron entregar (idealmente 0 en cada cola) |
| `http://localhost:8080/bus/events` | Últimos eventos publicados |

## 5. Una demostración guiada de 3 minutos

1. En las pantallas, elegí el rol **Almacenista** y consultá la existencia de `BOM-12`: hay **3 unidades** (el stock inicial era 4).
2. Cambiá al rol **Jefe de Operaciones** y buscá la orden de **ADV-06** (estado *Cerrada*): esa orden consumió una bomba.
3. **Esa es la interoperabilidad funcionando:** al cerrarse la orden en Intervenciones, publicó el evento «Orden de trabajo cerrada»;
   Repuestos lo recibió por el bus y **descontó la bomba** (de 4 a 3). Ningún servicio llamó al otro.
4. Mirá la orden de **ADV-02**: está *En espera* porque faltaba un repuesto; Repuestos lo detectó y avisó por evento.

## 6. Apagar y volver a levantar

```bash
docker compose stop         # apaga sin borrar los datos
docker compose up -d        # vuelve a levantar
docker compose down -v      # BORRA todo (contenedores y datos)
```

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| "port is already allocated" | El puerto 8080 o 15672 está ocupado | `GATEWAY_PORT=8090 RABBITMQ_UI_PORT=25672 docker compose up -d` |
| El seed dice "no se pudo conectar" | Los servicios aún no están listos | Esperar un minuto y repetir |
| `bus/health` dice `iniciando` | RabbitMQ todavía arranca | Esperar unos segundos |
| Los cambios de código no se ven | La imagen no se reconstruyó | `docker compose up -d --build <servicio>` |

---

# B · Construir con ArchiForge

## 1. Instalación (Arch Linux)

```bash
sudo pacman -S python git docker docker-compose nodejs npm dotnet-sdk   # herramientas
cd archiforge
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt        # jinja2, textual, pytest
.venv/bin/python -m forge doctor                 # revisa qué herramientas faltan
```

`forge doctor` marca con ✅ o ❌ cada herramienta necesaria (git, python, node, npm, docker, docker compose, dotnet y el agente).
Para construir hace falta **un agente de IA** instalado y con sesión iniciada: **Claude Code** o **OpenCode** (o uno propio por línea de comandos).

> **Tip:** si algo falta, `doctor` lo dice. No hace falta instalar `dotnet` si ningún servicio se construye en C#.

## 2. Abrir la pantalla (TUI)

```bash
.venv/bin/python -m forge studio
```

### Pantalla de inicio

| Tecla | Acción |
|---|---|
| `n` | Nuevo proyecto (te pide el archivo `.archimate` y la carpeta de documentos; **analiza el modelo y dice si sirve**) |
| `i` | Importar un `forge.toml` existente |
| `k` | Elegir **motor, modelo y claves de API** del agente |
| `Enter` | Abrir el proyecto |
| `q` | Salir |

### Panel del proyecto

Muestra los **contextos del modelo** y su estado (decidido, construido, "se simula"), las políticas del equipo y la plataforma.

| Tecla | Acción |
|---|---|
| `Enter` | **Decidir** un servicio (se abre el formulario de decisiones) |
| `p` | **Decidir la plataforma** (canal de eventos, gateway, frontend, despliegue, simuladores, imágenes) |
| `b` | **Construir** los servicios decididos |
| `a` | **Ensamblar** (unir los servicios en una plataforma y probarla) |
| `g` | Agente y claves |
| `r` | Recargar |

## 3. Tomar las decisiones

### Decisiones de un servicio (Enter)

| Decisión | Opciones hoy |
|---|---|
| Lenguaje | C# (.NET) · Python (FastAPI) · Java (Spring Boot) |
| Arquitectura interna | Clean + DDD · Hexagonal |
| Estilo de servicio | Microservicio · SOA · Monolito modular |
| Base de datos | MongoDB · PostgreSQL |
| Puerto | (se propone uno libre) |
| Patrones | Lista de 50 patrones con ficha (qué es, cuándo sirve, cuándo no, costo). **Ninguno viene marcado** |
| Detalles de un patrón | p. ej. cifrado → algoritmo (`aes-256-gcm` o `chacha20-poly1305`) |
| Justificaciones | Un texto propio de al menos 30 caracteres por decisión |

La columna derecha es **solo referencia**: describe, no recomienda.

### Decisiones de la plataforma (p)

| Decisión | Opciones | Qué cambia |
|---|---|---|
| Canal de eventos | `rabbitmq` · `memoria` | Con RabbitMQ los mensajes se guardan y se reintentan; en memoria no |
| Gateway | `nginx` · `propio` | Con `propio` no se genera gateway: se documentan las rutas |
| Frontend | `microfrontends` · `ninguno` | Con `ninguno` no hay pantallas, solo APIs |
| Despliegue | `docker-compose` · `propio` | Con `propio` no se genera compose |
| Simuladores | `generar` · `ninguno` | Con `ninguno` el equipo configura las URL de los proveedores |
| Imágenes | versiones de mongo, postgres, rabbitmq, nginx, python, node | Vacío = la versión que trae la herramienta |

Todo se guarda en **archivos de texto legibles** (`decisiones/<servicio>.toml` y `decisiones/plataforma.toml`) que viajan con el repositorio.

## 4. Construir y ensamblar

- **`b`** → elegís qué servicios construir y las vueltas de reintento; ves el avance etapa por etapa (log en vivo, cancelable).
- **`a`** → une todo y corre la prueba de humo del conjunto.

Si **falta una decisión**, la herramienta se detiene con un mensaje como este:

```
Falta decidir el gateway de la plataforma. Decide uno con `python -m forge platform --gateway <opción>`:
  · nginx: un contenedor nginx sirve los microfrontends y enruta /api/<servicio>, /sim y /bus hacia los servicios
  · propio: sin gateway generado: cada servicio publica su puerto y se documentan las rutas que el frontend espera
```

## 5. Lo mismo por línea de comandos

```bash
cd archiforge
.venv/bin/python -m forge domains                       # contextos del modelo y su estado
.venv/bin/python -m forge patterns                      # catálogo de patrones (ficha: patterns <id>)
.venv/bin/python -m forge decide "Plan de Mantenimiento" \
      --lang python --arch hexagonal --style microservicio --db postgresql \
      --patterns memento,cache,cifrado --detail cifrado.algoritmo=aes-256-gcm \
      --why lenguaje="…" --why arquitectura="…"
.venv/bin/python -m forge platform --messaging rabbitmq --gateway nginx --frontend microfrontends \
      --deployment docker-compose --simulators generar
.venv/bin/python -m forge check "Plan de Mantenimiento"  # valida las decisiones
.venv/bin/python -m forge build "Plan de Mantenimiento"  # construye (usa el agente)
.venv/bin/python -m forge assemble                       # une y prueba todo
.venv/bin/python -m forge status                         # avance por etapa
```

## 6. ¿Y si cambia el modelo?

Volvé a ejecutar `build`: el programa compara la huella y **reconstruye solo lo afectado** (ver doc 03). No hace falta `--force`.

## 7. Construir un servicio nuevo

**Caso 1 · ya existe en el modelo** (hay 7 contextos hoy simulados): `Enter` sobre el contexto → decidir → `b` → `a`.
Al ensamblar, ese contexto **deja de simularse** y los demás se reapuntan solos.

**Caso 2 · no existe en el modelo:** agregarlo en Archi (contexto, agregados, comandos, eventos y contrato con las etiquetas del doc 02) y
seguir como el caso 1. *Límite conocido:* hay una tabla interna que une los servicios de nivel 3 con sus contextos y hay que ampliarla.

## 8. Errores frecuentes al construir

| Mensaje | Qué significa | Solución |
|---|---|---|
| "Falta decidir …" | Una decisión no está tomada | Tomarla en la TUI (`p` o `Enter`) |
| Compuerta "decisiones justificadas" | Hay justificaciones vacías o con el texto de ejemplo | Escribir un argumento propio en cada una |
| "conformidad … Faltan: …" | El código no tiene algo que el modelo pide | Se reintenta solo; si persiste, mirar el log de la etapa |
| "agente: …" | El agente no respondió o se acabó la cuota | Esperar o cambiar de motor/modelo (`g`) y reanudar |
| Etapa "OMITIDA: dependen de etapas fallidas" | Una etapa previa falló | Arreglar la primera que falló |

---
Anterior: [03 · Cómo funciona](03-como-funciona-el-programa.md) · Siguiente: [05 · El producto generado](05-el-producto-generado.md)
