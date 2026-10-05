# Arquitectura - Restaurant AI Platform

## Vision General

```
                    CLIENTE
                       |
           +-----------+-----------+
           |           |           |
        WhatsApp     Telegram     WebChat
           |           |           |
           +-----------+-----------+
                       v
              CHANNEL GATEWAY
                       |
                       v
              AI ORCHESTRATOR
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
  INTENT ENGINE       RAG         TOOL ROUTER
       |               |               |
       |               |        +------+------+
       |               |        v      v      v
       |               |      Menu  Orders  Booking
       |               |
       +---------------+---------------+
                       |
                  BUSINESS LOGIC
                       |
              +--------+--------+
              v        v        v
           POSTGRES   REDIS   VECTOR
```

## Componentes

### Channel Gateway
- Normaliza mensajes de diferentes canales
- Maneja webhooks de WhatsApp y Telegram
- Rate limiting por usuario

### AI Orchestrator
- LangGraph ReAct Agent
- Intent Engine para detectar intenciones
- Tool Router para ejecutar acciones
- MemorySaver para contexto por usuario

### Business Logic
- Order State Machine (DRAFT -> COMPLETED)
- Reservation System
- Delivery Engine
- CRM con Customer 360

### Data Layer
- PostgreSQL: Datos transaccionales
- Redis: Cache y sesiones
- Vector DB: Embeddings para RAG

## Patrones de Diseno

### Separacion de Responsabilidades
```
LLM = Lenguaje / Interpretacion
Backend = Reglas de Negocio
Database = Verdad
```

### Order State Machine
```
DRAFT -> CONFIRMED -> PAID -> PREPARING -> READY -> DELIVERING -> COMPLETED
```

### Human Handoff
- Confidence < 0.85
- Eventos especiales (>10 personas)
- Reclamos
- Solicitud de reembolso
