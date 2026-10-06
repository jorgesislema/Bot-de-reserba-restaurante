# API - Restaurant AI Platform

## Autenticacion y autorizacion

Dos capas de seguridad sobre `/api/*`:

1. **Servicio (integraciones/CRM)**: header `X-API-Key` con el valor de
   `API_KEY`. En produccion se exige con `REQUIRE_API_KEY=true` para todo
   `/api/*` (excepto `/api/health`).
2. **Cliente (recursos propios)**: header `Authorization: Bearer <JWT>`.
   El token es un JWT HS256 firmado con `SECRET_KEY` (expira en 1 hora) y
   solo se emite en `POST /api/auth/token` presentando la `X-API-Key` del
   servicio. Identifica al dueño del recurso: los endpoints de cliente,
   pedido y reserva solo operan sobre los datos del `sub` del token.

Errores: `401` sin token / token invalido o expirado / API key invalida;
`403` cuando el recurso pertenece a otro cliente; `404` cuando el pedido
no existe. La identidad nunca se toma de headers declarativos ni de
argumentos del LLM.

Nota: `GET /api/clientes/buscar` y las metricas/handoffs son datos del
negocio (staff): requieren `X-API-Key`.

## Endpoints

### Webhooks

- `GET /webhook/whatsapp` - Verificacion de webhook (`WHATSAPP_VERIFY_TOKEN`)
- `POST /webhook/whatsapp` - Mensajes de WhatsApp. Autenticado con
  `X-Hub-Signature-256` (HMAC-SHA256 del body crudo con
  `WHATSAPP_APP_SECRET`). **Fail-closed**: sin secreto configurado o con
  firma invalida responde `403` y no procesa nada.
- `POST /webhook/telegram` - Mensajes de Telegram (fuera de alcance de
  esta fase: sin verificacion de firma)

### CRM Web

- `/` - Dashboard
- `/inbox` - Inbox omnicanal
- `/clientes` - Customer 360
- `/pedidos` - Gestion de pedidos
- `/reservas` - Gestion de reservas
- `/menu` - Catalogo de productos
- `/promociones` - Promociones
- `/delivery` - Estado de deliveries
- `/analytics` - Metricas
- `/ai-intelligence` - Analisis de IA
- `/ai-governance` - Control de IA
- `/configuracion` - Settings

### API REST

Publicos (solo datos del menu/disponibilidad, sin PII):

- `GET /api/productos` - Lista productos
- `GET /api/productos/{id}` - Detalle de producto
- `GET /api/reservas/disponibilidad` - Verificar disponibilidad
- `GET /api/health` - Health check

Requieren JWT de cliente (recursos propios):

- `POST /api/auth/token` - Emite JWT (requiere `X-API-Key` de servicio)
- `POST /api/pedidos` - Crear pedido (siempre del cliente autenticado)
- `GET /api/pedidos/{id}` - Detalle de pedido
- `POST /api/pedidos/{id}/items` - Agregar item
- `POST /api/pedidos/{id}/confirmar` - Confirmar pedido
- `POST /api/pedidos/{id}/cancelar` - Cancelar pedido
- `POST /api/reservas` - Crear reserva (`cliente_id` y telefono deben
  coincidir con el token)
- `GET /api/clientes/{id}` - Detalle de cliente (solo el propio)

Requieren `X-API-Key` (staff/servicio):

- `GET /api/clientes/buscar` - Buscar clientes
- `GET /api/metricas` - Metricas generales
- `GET /api/handoffs` - Handoffs pendientes

Con rate limit propio:

- `POST /api/chat` - Chat sincrono
