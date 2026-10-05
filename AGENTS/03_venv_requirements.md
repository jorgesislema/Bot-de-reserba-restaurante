# PROMPT 03: requirements.txt

## Objetivo
Crear el archivo requirements.txt con todas las dependencias del proyecto.

## Instrucciones Detalladas

Crear el archivo `requirements.txt`:

```txt
# ===========================================
# CORE
# ===========================================
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.10.0
pydantic-settings>=2.6.0
python-dotenv>=1.0.1
python-multipart>=0.0.10

# ===========================================
# AGENTE LLM
# ===========================================
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
openai>=1.55.0

# ===========================================
# VECTOR DATABASE
# ===========================================
qdrant-client>=1.13.0
langchain-qdrant>=0.1.0

# ===========================================
# EMBEDDINGS
# ===========================================
sentence-transformers>=3.3.0
torch>=2.6.0
transformers>=4.48.0
accelerate>=1.3.0
safetensors>=0.5.0

# ===========================================
# DATABASE
# ===========================================
sqlalchemy>=2.0.36
asyncpg>=0.30.0
aiosqlite>=0.20.0
alembic>=1.14.0

# ===========================================
# REDIS
# ===========================================
redis>=5.2.0
hiredis>=3.1.0

# ===========================================
# GOOGLE CALENDAR
# ===========================================
google-api-python-client>=2.150.0
google-auth-httplib2>=0.2.0
google-auth-oauthlib>=1.2.0
google-auth>=2.35.0

# ===========================================
# GOOGLE MAPS (Delivery)
# ===========================================
googlemaps>=4.10.0

# ===========================================
# WHATSAPP / TELEGRAM
# ===========================================
httpx>=0.27.0
requests>=2.32.0
python-telegram-bot>=21.0

# ===========================================
# FRONTEND (Jinja2 + Forms)
# ===========================================
jinja2>=3.1.0
aiofiles>=24.1.0

# ===========================================
# UTILITIES
# ===========================================
python-dateutil>=2.9.0
pytz>=2024.2
pyyaml>=6.0.0
celery>=5.4.0

# ===========================================
# TESTING
# ===========================================
pytest>=8.3.0
pytest-cov>=6.0.0
pytest-asyncio>=0.24.0
pytest-mock>=3.14.0
httpx>=0.27.0

# ===========================================
# LINTING
# ===========================================
ruff>=0.8.0
pyright>=1.1.380
mypy>=1.13.0
types-requests>=2.32.0

# ===========================================
# DEV TOOLS
# ===========================================
pre-commit>=3.8.0
ipython>=8.28.0
ipdb>=0.13.13

# ===========================================
# MONITORING
# ===========================================
sentry-sdk>=2.19.0
prometheus-client>=0.21.0
```

## Verificación
- [ ] Archivo requirements.txt creado
- [ ] Todas las dependencias incluidas
- [ ] Versiones mínimas especificadas
- [ ] Separado por secciones
