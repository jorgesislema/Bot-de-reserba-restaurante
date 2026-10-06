# Restaurant AI Platform

Sistema omnicanal de IA para atencion al cliente, pedidos, reservas, delivery y CRM via WhatsApp, Telegram y web.

**Estado:** funcional para desarrollo y demo. Arranca, tests en verde, sin reservas dobles ni precios inventados.

## Arquitectura

```
LLM  ->  TOOLS  ->  DOMAIN (skills)  ->  DATABASE
```

El LLM **nunca** es autoridad de: disponibilidad, precios, clientes, IDs, estados ni permisos.
Toda respuesta de negocio viene del backend; si el backend rechaza, el agente informa el motivo real.

Garantias clave:

- **Sin doble reserva**: unica por `(fecha, hora, telefono)` (indice unico en BD) + mutex por slot en proceso + `pg_advisory_xact_lock` en PostgreSQL + re-verificacion de capacidad en la misma transaccion.
- **Precios reales**: `total = base + precio_adicional_del_tamano + extras`, calculado siempre por `db_manager`.
- **Clientes por telefono**: idempotente al crear; el agente no inventa `cliente_id`.
- **Confirmacion obligatoria**: un nodo determinista del grafo (`validar_confirmacion`) bloquea `crear_reserva`, `cancelar_*`, `confirmar/cancelar_pedido`, `crear_envio_delivery` y envio de mensajes hasta que el usuario confirme con los mismos argumentos. No depende solo del system prompt.
- **Canales sin simulacion**: si WhatsApp/Telegram no estan configurados, la tool devuelve `{"success": false, "error": "channel_not_configured"}`; nunca dice "Mensaje enviado" sin enviar.

## Prerrequisitos

- Python 3.11+ (probado en 3.13)
- SQLite (incluido, default) o PostgreSQL
- `OPENROUTER_API_KEY` para el agente (los tests de integracion usan el LLM real)

Opcionales: `WHATSAPP_TOKEN` + `WHATSAPP_PHONE_ID`, `TELEGRAM_BOT_TOKEN`.

## Instalacion

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env: OPENROUTER_API_KEY obligatorio para el chat
# Produccion: WHATSAPP_APP_SECRET (firma del webhook) y REQUIRE_API_KEY=true

# Datos de ejemplo (opcional)
python scripts/seed_data.py
python scripts/ingestar_menu.py

# Iniciar servidor
uvicorn api.main:app --reload --port 8000
```

Dashboard: `http://localhost:8000/` · Health: `http://localhost:8000/api/health`

## Variables de entorno principales

| Variable | Descripcion |
|---|---|
| `OPENROUTER_API_KEY` | LLM del agente (obligatoria para chat) |
| `KILO_BASE_URL`, `KILO_CHAT_MODEL` | Endpoint/modelo del LLM |
| `DATABASE_URL` | Default `sqlite:///restaurant_ai.db`; PostgreSQL usa advisory locks extra |
| `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`, `WHATSAPP_VERIFY_TOKEN` | Envio real WhatsApp + verificacion del webhook |
| `WHATSAPP_APP_SECRET` | Firma `X-Hub-Signature-256` del webhook; **obligatoria**: sin ella `POST /webhook/whatsapp` responde 403 (fail-closed) |
| `SECRET_KEY` | Firma JWT (HS256) de clientes para `/api/*` |
| `TELEGRAM_BOT_TOKEN` | Envio real Telegram |
| `REQUIRE_API_KEY` / `API_KEY` | En produccion `REQUIRE_API_KEY=true` exige header `X-API-Key` en `/api/*` (excepto health) |
| `CORS_ORIGINS` | Origenes permitidos (coma-separados) |
| `RATE_LIMIT_MESSAGES_PER_MINUTE` | Limite por cliente (default 30) |
| `RESTAURANT_TOTAL_CAPACITY`, `RESERVATION_MAX_PARTY`, `RESERVATION_DURATION_MIN`, `RESERVATION_SLOT_MINUTES`, `RESERVATION_OPEN_HOUR`, `RESERVATION_CLOSE_HOUR` | Reglas de reserva |

Nunca subir `.env` al repositorio (esta en `.gitignore`).

## Estructura

```
api/            FastAPI (main.py) + agente LangGraph (agent.py)
  agent.py        grafo: agent -> validar(confirmacion) -> tools
database/       modelos SQLAlchemy + db_manager (dominio)
skills/         dominio: menu, orders, reservations, delivery, customers,
                channels, analytics
tools/          tools LangGraph (clasificadas READ / WRITE / SIDE_EFFECT)
templates/      Frontend Jinja2 (dashboard, CRM)
scripts/        seed_data.py, ingestar_menu.py
tests/          141 tests (137 rapidos + 4 de integracion LLM)
docs/           ARQUITECTURA, API, DESPLIEGUE, GUIA_USUARIO
```

## Tests

```bash
# Rapida (sin LLM, sin red)
pytest tests/ -m "not llm" --no-cov -q

# Integracion LLM real (test_integracion.py: ~4-8 min, requiere OPENROUTER_API_KEY)
pytest tests/ -m llm --no-cov -q

# Suite completa
pytest --no-cov -q
```

Cobertura actual por area: base de datos, reservas (incl. concurrencia), precios,
clientes, seguridad (API key, rate limit, idempotencia, injection), autenticacion
JWT e IDOR (tokens invalidos, recursos ajenos), webhook WhatsApp (firma
`X-Hub-Signature-256`, fail-closed), autorizacion de tools, envio WhatsApp
(errores no se reportan como exito), gate de confirmacion, tools, skills, API e
integracion.

## Seguridad

- **Dos capas de autenticacion en `/api/*`**: servicio (`X-API-Key`, siempre en
  `/api/clientes/buscar`, `/api/auth/token`, `/api/metricas`, `/api/handoffs`;
  en todo `/api/*` con `REQUIRE_API_KEY=true`) y cliente (`Authorization: Bearer
  <JWT>`, HS256 firmado con `SECRET_KEY`, expira en 1 h).
- **Anti-IDOR**: pedidos, clientes y reservas solo son visibles/editables por su
  dueno (404 si no existe, 403 si es de otro cliente). La identidad nunca viene
  del LLM ni de headers declarativos.
- **Webhook WhatsApp firmado**: `POST /webhook/whatsapp` valida
  `X-Hub-Signature-256` (HMAC-SHA256 del body crudo con `WHATSAPP_APP_SECRET`)
  antes de procesar; sin secreto o con firma invalida responde 403.
- **Tools con identidad de contexto**: el canal verificado propaga el telefono
  via `ContextVar`; con identidad, las tools solo acceden a recursos propios
  (dashboard webchat y Telegram quedan en contexto interno confiable).
- **Telegram**: verificacion de firma pendiente (fuera de alcance de esta fase).

## Endpoints principales

- `POST /api/chat` — chat con el agente (webchat)
- `POST /api/auth/token` — emite JWT de cliente (requiere `X-API-Key`)
- `GET /api/productos`, `GET /api/reservas/disponibilidad`, `GET /api/health` — publicos
- `GET /api/metricas`, `GET /api/clientes/buscar` — con `X-API-Key`
- `POST /api/pedidos`, `POST /api/reservas`, `GET /api/pedidos/{id}` — con JWT, recursos propios
- `POST /webhook/whatsapp` — firma `X-Hub-Signature-256` + rate limit + idempotencia
- `POST /webhook/telegram` — rate limit + idempotencia (sin verificacion de firma)

Ver [docs/API.md](docs/API.md).

## Limitaciones conocidas

- **Memoria del agente**: `MemorySaver` (in-memory, por proceso) — en produccion usar checkpointer PostgreSQL/Redis.
- **Rate limit e idempotencia**: en memoria (por proceso) — en produccion usar Redis.
- **RAG / Qdrant**: documentado en `.env.example` pero no implementado; el menu se consulta via tools a la BD.
- **Docker**: no hay Dockerfile/docker-compose en el repo.
- **Sin credenciales LLM** el servidor arranca igual; el chat responde un mensaje de error seguro (queda en logs).
- **`WHATSAPP_APP_SECRET` pendiente en `.env`**: hasta agregarlo, `POST /webhook/whatsapp` responde 403 (fail-closed, por diseno).
- **Defecto pre-existente (no corregido, fuera de alcance)**: `order_tool.consultar_pedido_cliente` llama una accion inexistente en `OrderSkill` (`KeyError`) — el comportamiento es el mismo que antes de esta fase.

## Documentacion

- [Arquitectura](docs/ARQUITECTURA.md)
- [API](docs/API.md)
- [Despliegue](docs/DESPLIEGUE.md)
- [Guia de Usuario](docs/GUIA_USUARIO.md)

## Licencia

MIT License
