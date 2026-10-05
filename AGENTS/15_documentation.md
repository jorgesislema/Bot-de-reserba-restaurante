# PROMPT 15: Documentación del Proyecto

## Objetivo
Crear documentación completa del proyecto.

## Instrucciones Detalladas

Crear:

```
├── README.md
├── docs/
│   ├── ARQUITECTURA.md
│   ├── API.md
│   ├── DESPLIEGUE.md
│   └── GUIA_USUARIO.md
```

### README.md

```markdown
# 🍽️ Restaurant AI Platform

**AI Restaurant Commerce & Operations Platform**

Sistema omnicanal de IA para atención al cliente, pedidos, reservas, delivery, CRM y automatización comercial mediante WhatsApp, Telegram y web.

## 🚀 Características

- **Conversación natural** con clientes via WhatsApp/Telegram
- **RAG** sobre menú y conocimiento del restaurante
- **Pedidos completos** dentro del chat
- **Reservas** con disponibilidad en tiempo real
- **Delivery** con cálculo de costos por zona
- **CRM** con Customer 360
- **AI Intelligence** con métricas y analytics
- **AI Governance** con control de herramientas
- **Human Handoff** automático cuando es necesario

## 📋 Prerrequisitos

- Python 3.11+
- PostgreSQL (o SQLite para desarrollo)
- Redis (opcional)
- WhatsApp Business API account
- Telegram Bot Token

## 🛠️ Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/restaurant-ai.git
cd restaurant-ai

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Poblar base de datos
python scripts/seed_data.py

# Iniciar servidor
uvicorn api.main:app --reload --port 8000
```

## 📁 Estructura del Proyecto

```
restaurant-ai/
├── api/                    # FastAPI backend
│   ├── main.py            # Servidor principal
│   ├── agent.py           # LangGraph ReAct Agent
│   └── check_env.py       # Verificación de variables
├── database/               # Modelos y gestor de BD
│   ├── models.py          # SQLAlchemy models
│   └── db_manager.py      # Operaciones CRUD
├── skills/                 # Skills modulares
│   ├── menu/              # Consulta de menú
│   ├── orders/            # Gestión de pedidos
│   ├── reservations/      # Gestión de reservas
│   ├── delivery/          # Delivery
│   ├── customers/         # CRM
│   └── analytics/         # Métricas
├── tools/                  # Herramientas LangGraph
├── templates/              # Frontend Jinja2
├── tests/                  # Tests
├── scripts/                # Scripts de utilidad
└── AGENTS/                 # Documentación AI
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=api --cov=database --cov=skills --cov=tools --cov-report=html

# Ver reporte
open htmlcov/index.html
```

## 🚀 Despliegue

```bash
# Docker
docker-compose up -d

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación

- [Arquitectura](docs/ARQUITECTURA.md)
- [API](docs/API.md)
- [Despliegue](docs/DESPLIEGUE.md)
- [Guía de Usuario](docs/GUIA_USUARIO.md)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/nueva-feature`)
3. Commit (`git commit -m 'Add nueva feature'`)
4. Push (`git push origin feature/nueva-feature`)
5. Abrir Pull Request

## 📄 Licencia

MIT License
```

### docs/ARQUITECTURA.md

```markdown
# Arquitectura - Restaurant AI Platform

## Visión General

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
- Order State Machine (DRAFT → COMPLETED)
- Reservation System
- Delivery Engine
- CRM con Customer 360

### Data Layer
- PostgreSQL: Datos transaccionales
- Redis: Cache y sesiones
- Vector DB: Embeddings para RAG

## Patrones de Diseño

### Separación de Responsabilidades
```
LLM = Lenguaje / Interpretación
Backend = Reglas de Negocio
Database = Verdad
```

### Order State Machine
```
DRAFT → CONFIRMED → PAID → PREPARING → READY → DELIVERING → COMPLETED
```

### Human Handoff
- Confidence < 0.85
- Eventos especiales (>10 personas)
- Reclamos
- Solicitud de reembolso
```

## Verificación
- [ ] README.md completo
- [ ] ARQUITECTURA.md con diagramas
- [ ] API.md documentada
- [ ] DESPLIEGUE.md con instrucciones
- [ ] GUIA_USUARIO.md para clientes
```

### INDICE_PROMPTS.md

```markdown
# Índice de Prompts - Restaurant AI Platform

## Estado: v1.0 - Fundación

### Prompts Ejecutados

| # | Prompt | Estado |
|---|--------|--------|
| 01 | gitignore | ⏳ |
| 02 | env_example | ⏳ |
| 03 | requirements | ⏳ |
| 04 | quality_config | ⏳ |
| 06 | database_models | ⏳ |
| 07 | database_manager | ⏳ |
| 08 | skills | ⏳ |
| 09 | tools | ⏳ |
| 10 | agent | ⏳ |
| 11 | api | ⏳ |
| 12 | ui (Jinja2 fallback) | ⏳ |
| 13 | scripts | ⏳ |
| 14 | tests | ⏳ |
| 15 | documentation | ⏳ |
| 16 | **frontend_modern** | ⏳ Next.js + shadcn/ui |

### Para Ejecutar

```bash
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn api.main:app --reload --port 8000
# http://localhost:8000
```

### API Configurada
- LLM: OpenRouter (nvidia/nemotron-3.5-lightning:free)
- WhatsApp: Meta Business API
- Telegram: Bot API
- Database: PostgreSQL (o SQLite para desarrollo)
```

## Verificación
- [ ] README.md con instrucciones claras
- [ ] ARQUITECTURA.md con diagramas
- [ ] Estructura documentada
- [ ] INDICE_PROMPTS.md actualizado
```
