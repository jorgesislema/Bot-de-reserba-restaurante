# API - Restaurant AI Platform

## Endpoints

### Webhooks

- `GET /webhook/whatsapp` - Verificacion de webhook
- `POST /webhook/whatsapp` - Mensajes de WhatsApp
- `POST /webhook/telegram` - Mensajes de Telegram

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

- `GET /api/productos` - Lista productos
- `GET /api/productos/{id}` - Detalle de producto
- `POST /api/pedidos` - Crear pedido
- `GET /api/pedidos/{id}` - Detalle de pedido
- `POST /api/pedidos/{id}/items` - Agregar item
- `POST /api/pedidos/{id}/confirmar` - Confirmar pedido
- `POST /api/pedidos/{id}/cancelar` - Cancelar pedido
- `POST /api/reservas` - Crear reserva
- `GET /api/reservas/disponibilidad` - Verificar disponibilidad
- `GET /api/clientes/buscar` - Buscar clientes
- `GET /api/clientes/{id}` - Detalle de cliente
- `GET /api/metricas` - Metricas generales
- `GET /api/health` - Health check
- `POST /api/chat` - Chat sincrono
- `GET /api/handoffs` - Handoffs pendientes
