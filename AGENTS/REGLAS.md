# Reglas de Desarrollo - Restaurant AI Platform v1.0

## Arquitectura Actual

```
FastAPI (puerto 8000)
├── CRM Web (Next.js + Tailwind + shadcn/ui)
├── API REST (/api/*)
├── Channel Gateway (WhatsApp + Telegram + Web)
├── AI Orchestrator (LangGraph ReAct)
├── Order State Machine
├── Reservation System
├── Delivery Engine (con mapa Leaflet)
├── Admin RAG (editor de conocimiento)
└── PostgreSQL + Redis + Vector DB
```

**NO es un chatbot simple.** Es una plataforma de IA integral.

---

## Ejecucion

```bash
# Instalar dependencias del backend
pip install -r requirements.txt

# Instalar dependencias del frontend
cd frontend && npm install

# Ingestar datos del menu
python scripts/ingestar_menu.py

# Poblar base de datos
python scripts/seed_data.py

# Iniciar backend
uvicorn api.main:app --reload --port 8000

# Iniciar frontend (otra terminal)
cd frontend && npm run dev

# Abrir CRM
http://localhost:3000
```

---

## Variables de Entorno (.env)

```env
# LLM
OPENROUTER_API_KEY=sk-or-v1-...
KILO_BASE_URL=https://openrouter.ai/api/v1
KILO_CHAT_MODEL=nvidia/nemotron-3.5-lightning:free

# WhatsApp
WHATSAPP_TOKEN=...
WHATSAPP_PHONE_ID=...
WHATSAPP_VERIFY_TOKEN=...

# Telegram
TELEGRAM_BOT_TOKEN=...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/restaurant_ai
REDIS_URL=redis://localhost:6379

# Delivery (usa OpenStreetMap, no requiere API key)
# Leaflet es gratuito y no necesita configuracion

# Email (alertas)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
```

---

## Produccion

```bash
# VPS
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Docker
docker-compose up -d

# Con Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/restaurant-ai
sudo certbot --nginx -d tu-dominio.com
```

Hosting: AWS/GCP/Azure ($20-50/mes)

---

## Calidad

```bash
ruff check .     # Linting
pyright          # Type checking
pytest           # Tests
```

---

## Principios de Arquitectura

### Separacion de Responsabilidades

```
LLM = Lenguaje / Interpretacion
Backend = Reglas de Negocio
Database = Verdad
```

**El LLM NUNCA debe:**
- Inventar precios
- Modificar inventario directamente
- Crear pedidos sin validacion
- Emitir reembolsos
- Eliminar clientes

### Order State Machine

```
DRAFT -> CONFIRMED -> PAID -> PREPARING -> READY -> DELIVERING -> COMPLETED
  |         |         |         |          |         |           |
Cancel    Cancel    Refund    Cancel    -         -           Return
```

### AI Governance

```
PERMISOS DE HERRAMIENTAS:
- Consultar menu:              Permitido
- Consultar disponibilidad:    Permitido
- Crear pedido:                Permitido (con validacion)
- Crear reserva:               Permitido
- Cancelar pedido:             Requiere validacion
- Emitir reembolso:            Denegado
- Modificar precios:           Denegado
- Eliminar cliente:            Denegado
```

### Human Handoff

El sistema debe escalar a humano cuando:
- Confidence < 0.85
- Requiere negociacion de precios
- Eventos especiales (>10 personas)
- Reclamos o problemas
- Solicitud de reembolso
- Preguntas fuera de dominio

---

## Delivery con Mapa

El sistema de delivery usa **Leaflet** (OpenStreetMap) para:
- Visualizar zonas de cobertura en un mapa
- Validar si una direccion esta dentro del radio
- Calcular costo y tiempo estimado por zona
- Permitir al administrador crear/editar zonas

**Zonas por defecto:**
- Zona 1 (0-3km): $2.00 - 25 min
- Zona 2 (3-6km): $3.50 - 40 min
- Zona 3 (6-10km): $5.00 - 55 min

Las zonas se configuran desde el panel de administracion.

---

## Admin RAG (Conocimiento Editable)

Todo el conocimiento que usa la IA es editable desde el panel de administracion:
- **Menu**: Productos, precios, categorias, ingredientes, fotos
- **Horarios**: Por dia, horarios especiales, feriados
- **Politicas**: Cancelacion, reembolso, delivery, reservas
- **FAQ**: Preguntas y respuestas frecuentes
- **Info del restaurante**: Nombre, direccion, telefono

Los cambios se reflejan inmediatamente en las respuestas de la IA.

---

## Seguridad

- Nunca registrar datos sensibles (tarjetas, contrasenas)
- Rate limiting: 30 mensajes/minuto por usuario
- Validacion de entrada en todos los endpoints
- HTTPS obligatorio en produccion
- Auditoria de acciones del AI
