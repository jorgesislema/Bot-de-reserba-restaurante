# Restaurant AI Platform

**AI Restaurant Commerce & Operations Platform**

Sistema omnicanal de IA para atencion al cliente, pedidos, reservas, delivery, CRM y automatizacion comercial via WhatsApp, Telegram y web.

## Caracteristicas

- **Conversacion natural** con clientes via WhatsApp/Telegram
- **RAG** sobre menu y conocimiento del restaurante
- **Pedidos completos** dentro del chat
- **Reservas** con disponibilidad en tiempo real
- **Delivery** con calculo de costos por zona
- **CRM** con Customer 360
- **AI Intelligence** con metricas y analytics
- **AI Governance** con control de herramientas
- **Human Handoff** automatico cuando es necesario

## Prerrequisitos

- Python 3.11+
- PostgreSQL (o SQLite para desarrollo)
- Redis (opcional)
- WhatsApp Business API account
- Telegram Bot Token

## Instalacion

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

## Estructura del Proyecto

```
restaurant-ai/
  api/                    # FastAPI backend
    main.py               # Servidor principal
    agent.py              # LangGraph ReAct Agent
    check_env.py          # Verificacion de variables
  database/               # Modelos y gestor de BD
    models.py             # SQLAlchemy models
    db_manager.py         # Operaciones CRUD
  skills/                 # Skills modulares
    menu/                 # Consulta de menu
    orders/               # Gestion de pedidos
    reservations/         # Gestion de reservas
    delivery/             # Delivery
    customers/            # CRM
    analytics/            # Metricas
  tools/                  # Herramientas LangGraph
  templates/              # Frontend Jinja2
  tests/                  # Tests
  scripts/                # Scripts de utilidad
  AGENTS/                 # Documentacion AI
```

## Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=api --cov=database --cov=skills --cov=tools --cov-report=html

# Ver reporte
open htmlcov/index.html
```

## Despliegue

```bash
# Docker
docker-compose up -d

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Documentacion

- [Arquitectura](docs/ARQUITECTURA.md)
- [API](docs/API.md)
- [Despliegue](docs/DESPLIEGUE.md)
- [Guia de Usuario](docs/GUIA_USUARIO.md)

## Licencia

MIT License
