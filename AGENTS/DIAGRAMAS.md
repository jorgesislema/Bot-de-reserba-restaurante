# Diagramas - Restaurant AI Platform v1.0

## 1. Arquitectura General

```
                    INTERNET
                       │
                    [Nginx]
                       │
                FastAPI (puerto 8000)
                /      │       \
           CRM Web   API REST   Channel Gateway
          (Next.js)  /api/*     /webhook/*
              │         │            │
        shadcn/ui    LangGraph    WhatsApp
        Tailwind     Agent IA    Telegram
              │         │         WebChat
              │         │            │
           PostgreSQL  OpenRouter  Normalización
              │         │            │
           Redis    Tool Router  AI Orchestrator
              │         │
           Vector DB  Business Logic
```

---

## 2. Channel Gateway (Omnicanal)

```
                    CLIENTE
                       │
          ┌────────────┴────────────┐
          │            │            │
       WhatsApp     Telegram     WebChat
          │            │            │
          └────────────┼────────────┘
                       ▼
              CHANNEL GATEWAY
                       │
                       ▼
                 NORMALIZACIÓN
                       │
                       ▼
              ┌────────────────┐
              │ CUSTOMER_MESSAGE│
              │ {              │
              │   channel: ... │
              │   user_id: ... │
              │   message: ... │
              │   timestamp:.. │
              │ }              │
              └────────────────┘
                       │
                       ▼
              AI ORCHESTRATOR
```

---

## 3. AI Orchestrator

```
              AI ORCHESTRATOR
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
  INTENT ENGINE       RAG         TOOL ROUTER
       │               │               │
       │               │        ┌──────┼──────┐
       │               │        ▼      ▼      ▼
       │               │      Menu  Orders  Booking
       │               │
       └───────────────┼───────────────┘
                       │
                  BUSINESS LOGIC
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           POSTGRES   REDIS   VECTOR
              │
              ▼
              CRM
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
    Orders Reservations Customers
              │
              ▼
          ANALYTICS
```

---

## 4. Order State Machine

```
    ┌─────────┐
    │  DRAFT  │
    └────┬────┘
         │ confirmar
         ▼
    ┌────────────┐
    │ CONFIRMED  │
    └────┬───────┘
         │ pagar
         ▼
    ┌─────────┐
    │   PAID  │
    └────┬────┘
         │ preparar
         ▼
    ┌────────────┐
    │ PREPARING  │
    └────┬───────┘
         │ listo
         ▼
    ┌─────────┐
    │   READY │
    └────┬────┘
         │ enviar
         ▼
    ┌────────────┐
    │ DELIVERING │
    └────┬───────┘
         │ entregar
         ▼
    ┌───────────┐
    │ COMPLETED │
    └───────────┘

    En cualquier momento:
    ├── CANCEL (con validación)
    └── REFUND (requiere humano)
```

---

## 5. Flujo de Pedido Completo

```
CLIENTE: "Quiero una pizza familiar"
    │
    ▼
IA: "¿Margarita, Pepperoni o BBQ?"
    │
    ▼
CLIENTE: "Pepperoni"
    │
    ▼
IA: "¿Deseas algún extra?"
    │
    ▼
CLIENTE: "Queso"
    │
    ▼
IA: [Cálculo en Backend]
    │
    ▼
IA:
🛒 TU PEDIDO
1 × Pizza Pepperoni Familiar    $14
1 × Extra queso                  $1.50
1 × Coca-Cola 1.5L               $2
────────────────────────────────
Subtotal                         $17.50
Delivery                          $2
TOTAL                            $19.50
    │
    ▼
CLIENTE: "Confirmar"
    │
    ▼
IA: [Crear pedido en DB]
    │
    ▼
IA: "Pedido #5821 confirmado. Estará listo en 35-45 minutos."
```

---

## 6. Flujo de Reserva

```
CLIENTE: "Somos 6 y queremos cenar mañana"
    │
    ▼
IA: [Detectar: reserva, 6 personas, mañana, cena]
    │
    ▼
IA: [Consultar disponibilidad]
    │
    ▼
IA: "Tengo disponibilidad para 6 personas a las 19:30, 20:00 y 21:00. ¿Cuál prefieres?"
    │
    ▼
CLIENTE: "20:00"
    │
    ▼
IA: "Perfecto. ¿A nombre de quién hago la reserva?"
    │
    ▼
CLIENTE: "Carlos Pérez"
    │
    ▼
IA: [Crear reserva en DB + Google Calendar]
    │
    ▼
IA: "Reserva confirmada para 6 personas el martes 16/01 a las 20:00. A nombre de Carlos Pérez. Te enviaré un recordatorio 24 horas antes."
```

---

## 7. Human Handoff

```
CLIENTE: "Quiero organizar cumpleaños de 15 personas"
    │
    ▼
IA: [Detectar: evento especial, alta intención]
    │
    ▼
IA: [Verificar confidence < 0.85]
    │
    ▼
IA: "Déjame conectarte con nuestro encargado de eventos."
    │
    ▼
HUMAN HANDOFF
    │
    ▼
GERENTE RECIBE:
┌─────────────────────────────────────┐
│ 🎂 Evento potencial                │
│ 15 personas                         │
│ Cumpleaños                          │
│ Solicita paquete especial           │
│ Fecha: sábado                       │
│ Presupuesto: pendiente              │
│ Contactar cliente                   │
│                                     │
│ [Tomar conversación]                │
└─────────────────────────────────────┘
```

---

## 8. Modelo de Datos (ER)

```
productos 1--* categorías
productos 1--* opciones_producto
productos 1--* pedido_items
pedidos 1--* pedido_items
pedidos 1--* pedido_estados
pedidos 1--* delivery_envios
clientes 1--* pedidos
clientes 1--* reservas
clientes 1--* cliente_preferencias
promociones 1--* promocion_reglas
reservas 1--* (google_calendar_event_id)
```

---

## 9. Páginas del CRM (14 páginas)

```
/                         Dashboard
/inbox                    Inbox Omnicanal
/clientes                 Customer 360
/pedidos                  Gestión de Pedidos
/reservas                 Gestión de Reservas
/menu                     Catálogo de Productos
/promociones              Promociones
/delivery                 Estado de Deliveries
/analytics                Métricas e AI Intelligence
/ai-intelligence          Análisis de IA
/ai-governance            Control de IA
/configuración            Settings
/cliente/{id}             Historial del Cliente
```

---

## 10. Dashboard del Gerente

```
┌─────────────────────────────────────────────────────────┐
│ RESTAURANT AI                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Conversaciones    Pedidos     Reservas     Ventas     │
│      486             83          31        $2,840      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ PEDIDOS EN TIEMPO REAL                                  │
│                                                         │
│ #5821   $19.50    🟡 Preparando                         │
│ #5822   $34.00    🔵 Confirmado                         │
│ #5823   $52.00    🟢 Listo                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 🔥 OPORTUNIDADES                                       │
│                                                         │
│ Evento 15 personas        ALTA      👤 Asesor          │
│ Reserva grupo 10          ALTA      👤 Gerente         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 11. AI Intelligence

```
🤖 AI INTELLIGENCE

Conversaciones procesadas       4,281
Resueltas automáticamente      3,604
Human handoff                    677
AI Resolution Rate              84.2%

Pedidos generados               428
Reservas generadas              193

¿Qué está preguntando la gente?
Menú                         31%
Pedidos                      24%
Reservas                     19%
Horarios                     10%
Delivery                      8%
Promociones                   5%
Otros                         3%
```

---

## 12. AI Governance

```
AI CONTROL CENTER

Model                   GPT / Claude / Gemini
Prompt version          v3.4
Knowledge Base          v5.2
Confidence threshold    0.85
Human escalation        ✓
PII protection          ✓
Audit logs              ✓
Tool permissions        ✓

TOOL PERMISSIONS:
Consultar menú              ✓
Consultar disponibilidad    ✓
Crear pedido               ✓
Crear reserva              ✓
Cancelar pedido            → validación
Emitir reembolso           ✕
Modificar precios          ✕
Eliminar cliente           ✕
```
