# Skills - Restaurant AI Platform v1.0

## Skills Disponibles

| Skill | Archivo | Función |
|-------|---------|---------|
| Menu | `menu_skill.py` | Consulta menú, precios, ingredientes, disponibilidad |
| Order | `order_skill.py` | Crear, modificar, cancelar pedidos (State Machine) |
| Reservation | `reservation_skill.py` | Crear, modificar, cancelar reservas |
| Delivery | `delivery_skill.py` | Costos, tiempos, zonas de envío |
| Customer | `customer_skill.py` | CRM, historial, preferencias, Customer 360 |
| Promotion | `promotion_skill.py` | Descuentos, combos, upselling inteligente |
| Channel | `channel_skill.py` | WhatsApp, Telegram, WebChat (omnicanal) |
| Analytics | `analytics_skill.py` | Métricas, reportes, AI Intelligence |
| Monitoring | `monitoring_skill.py` | Failover, alertas, health checks |
| Knowledge | `knowledge_skill.py` | RAG sobre menú, FAQ, políticas |

---

## Menu Skill (v1.0)

### Capacidades
- `buscar_producto` - Búsqueda semántica en el menú
- `obtener_producto` - Detalle completo de un producto
- `obtener_categorias` - Listar categorías disponibles
- `verificar_disponibilidad` - Stock en tiempo real
- `obtener_opciones` - Tamaños, extras, personalizaciones
- `calcular_precio` - Precio con extras y variantes
- `recomendar` - Sugerencias basadas en preferencias

### Estructura de Datos

```
PRODUCT
├── id
├── nombre
├── descripción
├── categoría
├── precio_base
├── ingredientes[]
├── alérgenos[]
├── disponible
├── personalizable
└── imagen

PRODUCT_OPTIONS
├── Tamaño: Personal/Mediana/Familiar
├── Extras: Queso/Pepperoni/Champiñones
└── Modificaciones: Sin gluten/ Sin lactosa
```

---

## Order Skill (v1.0)

### State Machine

```
DRAFT → CONFIRMED → PAID → PREPARING → READY → DELIVERING → COMPLETED
```

### Capacidades
- `crear_pedido` - Crear con validación de stock
- `agregar_item` - Añadir productos al carrito
- `modificar_item` - Cambiar cantidad o opciones
- `eliminar_item` - Quitar producto del pedido
- `calcular_total` - Subtotal, delivery, impuestos, total
- `confirmar_pedido` - Cambiar a CONFIRMED
- `cancelar_pedido` - Con validación de motivo
- `obtener_estado` - Estado actual del pedido
- `actualizar_estado` - Avanzar en la state machine

### Reglas
- Máximo 1 upselling suggestion por pedido
- Validar stock antes de confirmar
- Calcular precio en backend, nunca en LLM
- Log de cambios de estado

---

## Reservation Skill (v1.0)

### Capacidades
- `verificar_disponibilidad` - Mesas libres por fecha/hora/personas
- `crear_reserva` - Con todos los datos
- `modificar_reserva` - Cambiar fecha, hora, personas
- `cancelar_reserva` - Con política de cancelación
- `obtener_reservas` - Lista de reservas activas
- `recordatorio` - Envío automático 24h antes

### Estructura

```
RESERVATION
├── id
├── cliente_id
├── fecha
├── hora
├── personas
├── nombre_contacto
├── teléfono
├── preferencias (terraza, interior, privado)
├── observaciones
├── estado (pendiente, confirmada, cancelada, completada)
└── google_calendar_event_id
```

---

## Delivery Skill (v1.0)

### Capacidades
- `calcular_costo` - Tarifa por zona/dirección
- `estimar_tiempo` - Tiempo de preparación + envío
- `verificar_zona` - Si cubre la dirección
- `crear_envío` - Crear orden de delivery
- `rastrear_pedido` - Tracking en tiempo real

### Zonas de Delivery

```
ZONA 1 (0-3km):  $2.00  (20-30 min)
ZONA 2 (3-6km):  $3.50  (30-45 min)
ZONA 3 (6-10km): $5.00  (45-60 min)
Fuera de zona:    No disponible
```

---

## Customer Skill (v1.0)

### Customer 360

```
CUSTOMER
├── id
├── nombre
├── teléfono
├── email
├── canal_preferido (whatsapp/telegram/web)
├── fecha_registro
├── total_pedidos
├── valor_acumulado
├── último_pedido
├── preferencias[]
├── frecuencia
└── segmento (frecuente/inactivo/nuevo/alto_valor)
```

### Capacidades
- `obtener_cliente` - Customer 360 completo
- `buscar_cliente` - Por teléfono, nombre, email
- `crear_cliente` - Nuevo registro
- `actualizar_cliente` - Modificar datos
- `obtener_historial` - Pedidos y reservas anteriores
- `obtener_preferencias` - Gustos y alérgenos
- `calcular_segmento` - Frecuente/Inactivo/Nuevo/Alto Valor
- `obtener_frecuencia` - Pedidos por mes

---

## Promotion Skill (v1.0)

### Capacidades
- `obtener_promociones` - Activas por canal
- `aplicar_descuento` - Validar y aplicar
- `verificar_elegibilidad` - Cliente califica
- `sugerir_upsell` - Máx 1 suggestion por pedido
- `sugerir_cross_sell` - Productos complementarios
- `crear_combo` - Agrupar productos con descuento

### Reglas de Upselling
- Máximo 1 sugerencia por pedido
- Basado en historial del cliente
- No molestar si el cliente dice "no"
- Preferencias > Historial > Genérico

---

## Channel Skill (v1.0)

### Omnicanal

```
CLIENTE
    │
    ┌─────────┴─────────┐
    │                   │
 WhatsApp           Telegram
    │                   │
    └─────────┬─────────┘
              ▼
        CHANNEL LAYER
              ▼
       NORMALIZACIÓN
              ▼
       AI ORCHESTRATOR
```

### Normalización

```json
{
  "channel": "whatsapp",
  "user_id": "12345",
  "message": "quiero una pizza familiar",
  "timestamp": "2024-01-15T19:30:00Z"
}
```

Para la IA ambos canales son: `CUSTOMER_MESSAGE`

---

## Analytics Skill (v1.0)

### Métricas

```
CONVERSACIONES PROCESADAS:    4,281
RESUELTAS AUTOMÁTICAMENTE:    3,604
HUMAN HANDOFF:                  677
AI RESOLUTION RATE:            84.2%

PEDIDOS GENERADOS:              428
RESERVAS GENERADAS:             193
PROMEDIOS POR PEDIDO:          $28.50
```

### AI Intelligence
- ¿Qué pregunta la gente? (menú, pedidos, reservas...)
- Horas pico de actividad
- Tasa de resolución por tipo de consulta
- Knowledge gaps (preguntas sin respuesta)

---

## Monitoring Skill (v1.0)

### Capacidades
- `health_check` - Estado de todos los componentes
- `registrar_fallo` - Log de errores
- `enviar_alerta` - Email/Slack cuando hay problemas
- `failover_modelo` - Cambiar LLM si falla
- `metricas` - Uso de API, tiempos, errores
- `reporte_mensual` - Telemetría consolidada
