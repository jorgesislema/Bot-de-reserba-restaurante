# Despliegue - Restaurant AI Platform

## Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Poblar base de datos
python scripts/seed_data.py

# Iniciar servidor
uvicorn api.main:app --reload --port 8000
```

## Docker

```bash
# Construir imagen
docker build -t restaurant-ai .

# Ejecutar
docker-compose up -d
```

## Produccion

```bash
# VPS
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Con Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/restaurant-ai
sudo certbot --nginx -d tu-dominio.com
```

## Variables de Entorno

Ver `.env.example` para la lista completa de variables requeridas.

Hosting: AWS/GCP/Azure ($20-50/mes)
