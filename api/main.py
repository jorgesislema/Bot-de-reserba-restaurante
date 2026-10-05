"""Servidor FastAPI para Restaurant AI Platform."""

import os
import sys
import json
import hashlib
from datetime import datetime, date, timedelta
from typing import Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.check_env import check_environment
from api.agent import process_message
from database.db_manager import RestaurantDB

load_dotenv()

app = FastAPI(title="Restaurant AI Platform", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent

# Crear directorios necesarios
(BASE_DIR / "static").mkdir(exist_ok=True)
(BASE_DIR / "templates").mkdir(exist_ok=True)
(BASE_DIR / "templates" / "partials").mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

db = RestaurantDB()
processed_messages = set()

# Rate limiting
rate_limit_store = {}


@app.on_event("startup")
async def startup_event():
    ok, errors = check_environment()
    if not ok:
        print(f"Advertencias: {errors}")
    print("Restaurant AI Platform iniciado en http://localhost:8000")


def ctx(request: Request, **kwargs):
    return {
        "request": request,
        "now": datetime.now().strftime("%d/%m/%Y %H:%M"),
        **kwargs
    }


# ===========================================
# WEBHOOK WHATSAPP
# ===========================================

@app.get("/webhook/whatsapp")
async def whatsapp_verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    """Verificacion del webhook de WhatsApp."""
    if hub_mode == "subscribe" and hub_token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token invalido")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Recibe mensajes de WhatsApp."""
    data = await request.json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "ok"}

        message = value["messages"][0]
        phone = message["from"]
        text = message["text"]["body"]
        message_id = message["id"]

        # Idempotencia
        if message_id in processed_messages:
            return {"status": "ok"}
        processed_messages.add(message_id)

        # Procesar con agente
        response = process_message(text, thread_id=phone, channel="whatsapp")

        # Enviar respuesta (simplificado)
        print(f"Respuesta a {phone}: {response}")

        return {"status": "ok"}

    except Exception as e:
        print(f"Error procesando webhook: {e}")
        return {"status": "error"}


# ===========================================
# WEBHOOK TELEGRAM
# ===========================================

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Recibe mensajes de Telegram."""
    data = await request.json()

    try:
        message = data.get("message")
        if not message:
            return {"status": "ok"}

        chat_id = str(message["chat"]["id"])
        text = message.get("text", "")

        if not text:
            return {"status": "ok"}

        # Procesar con agente
        response = process_message(text, thread_id=chat_id, channel="telegram")

        # Enviar respuesta (simplificado)
        print(f"Respuesta a Telegram {chat_id}: {response}")

        return {"status": "ok"}

    except Exception as e:
        print(f"Error procesando webhook Telegram: {e}")
        return {"status": "error"}


# ===========================================
# PAGINAS HTML - CRM
# ===========================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    metricas = db.obtener_metricas()
    return templates.TemplateResponse(request, "dashboard.html", ctx(
        request, active_page="dashboard", metricas=metricas
    ))


@app.get("/inbox", response_class=HTMLResponse)
async def inbox(request: Request):
    return templates.TemplateResponse(request, "inbox.html", ctx(
        request, active_page="inbox"
    ))


@app.get("/clientes", response_class=HTMLResponse)
async def clientes(request: Request):
    return templates.TemplateResponse(request, "clientes.html", ctx(
        request, active_page="clientes"
    ))


@app.get("/pedidos", response_class=HTMLResponse)
async def pedidos(request: Request):
    return templates.TemplateResponse(request, "pedidos.html", ctx(
        request, active_page="pedidos"
    ))


@app.get("/reservas", response_class=HTMLResponse)
async def reservas(request: Request):
    return templates.TemplateResponse(request, "reservas.html", ctx(
        request, active_page="reservas"
    ))


@app.get("/menu", response_class=HTMLResponse)
async def menu(request: Request):
    categorias = db.obtener_categorias()
    productos = db.obtener_productos()
    return templates.TemplateResponse(request, "menu.html", ctx(
        request, active_page="menu", categorias=categorias, productos=productos
    ))


@app.get("/promociones", response_class=HTMLResponse)
async def promociones(request: Request):
    return templates.TemplateResponse(request, "promociones.html", ctx(
        request, active_page="promociones"
    ))


@app.get("/delivery", response_class=HTMLResponse)
async def delivery(request: Request):
    return templates.TemplateResponse(request, "delivery.html", ctx(
        request, active_page="delivery"
    ))


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    return templates.TemplateResponse(request, "analytics.html", ctx(
        request, active_page="analytics"
    ))


@app.get("/ai-intelligence", response_class=HTMLResponse)
async def ai_intelligence(request: Request):
    return templates.TemplateResponse(request, "ai_intelligence.html", ctx(
        request, active_page="ai-intelligence"
    ))


@app.get("/ai-governance", response_class=HTMLResponse)
async def ai_governance(request: Request):
    return templates.TemplateResponse(request, "ai_governance.html", ctx(
        request, active_page="ai-governance"
    ))


@app.get("/configuracion", response_class=HTMLResponse)
async def configuracion(request: Request):
    return templates.TemplateResponse(request, "configuracion.html", ctx(
        request, active_page="configuracion"
    ))


@app.get("/cliente/{cliente_id}", response_class=HTMLResponse)
async def cliente_historial(request: Request, cliente_id: int):
    cliente = db.obtener_cliente("")
    historial = db.obtener_historial(cliente_id)
    return templates.TemplateResponse(request, "cliente_historial.html", ctx(
        request, cliente=cliente, historial=historial
    ))


# ===========================================
# API REST
# ===========================================

@app.get("/api/productos")
async def api_productos(categoria_id: int = None):
    return db.obtener_productos(categoria_id)


@app.get("/api/productos/{producto_id}")
async def api_producto(producto_id: int):
    producto = db.obtener_producto(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@app.post("/api/pedidos")
async def api_crear_pedido(cliente_id: int, canal: str = "web"):
    pedido_id = db.crear_pedido(cliente_id, canal)
    return {"pedido_id": pedido_id}


@app.get("/api/pedidos/{pedido_id}")
async def api_pedido(pedido_id: int):
    pedido = db.obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@app.post("/api/pedidos/{pedido_id}/items")
async def api_agregar_item(
    pedido_id: int,
    producto_id: int = Form(...),
    cantidad: int = Form(1),
    tamano: str = Form(None),
    extras: str = Form(None)
):
    opciones = {}
    if tamano:
        opciones["tamano"] = tamano
    if extras:
        opciones["extras"] = extras.split(",")

    exito = db.agregar_item_pedido(pedido_id, producto_id, cantidad, opciones)
    return {"success": exito}


@app.post("/api/pedidos/{pedido_id}/confirmar")
async def api_confirmar_pedido(pedido_id: int):
    from database.models import OrderStatus
    exito = db.actualizar_estado_pedido(pedido_id, OrderStatus.CONFIRMED)
    return {"success": exito}


@app.post("/api/pedidos/{pedido_id}/cancelar")
async def api_cancelar_pedido(pedido_id: int, motivo: str = Form(...)):
    exito = db.cancelar_pedido(pedido_id, motivo)
    return {"success": exito}


@app.post("/api/reservas")
async def api_crear_reserva(
    fecha: str = Form(...),
    hora: str = Form(...),
    personas: int = Form(...),
    nombre: str = Form(...),
    telefono: str = Form(...)
):
    reserva_id = db.crear_reserva({
        "fecha": fecha,
        "hora": hora,
        "personas": personas,
        "nombre_contacto": nombre,
        "telefono": telefono
    })
    return {"reserva_id": reserva_id}


@app.get("/api/reservas/disponibilidad")
async def api_disponibilidad(fecha: str, personas: int):
    return db.verificar_disponibilidad(fecha, None, personas)


@app.get("/api/clientes/buscar")
async def api_buscar_cliente(q: str):
    return db.buscar_cliente(q)


@app.get("/api/clientes/{cliente_id}")
async def api_cliente(cliente_id: int):
    cliente = db.obtener_cliente("")
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.get("/api/metricas")
async def api_metricas():
    return db.obtener_metricas()


@app.get("/api/health")
async def api_health():
    return db.health_check()


@app.post("/api/chat")
async def api_chat(mensaje: str = Form(...), canal: str = Form("web")):
    response = process_message(mensaje, thread_id="dashboard", channel=canal)
    return {"response": response}


@app.get("/api/handoffs")
async def api_handoffs():
    return db.obtener_handoffs_pendientes()


# ===========================================
# RATE LIMITING
# ===========================================

def check_rate_limit(ip: str) -> bool:
    """Verifica rate limiting por IP."""
    now = datetime.now()
    limit = int(os.getenv("RATE_LIMIT_MESSAGES_PER_MINUTE", "30"))

    if ip not in rate_limit_store:
        rate_limit_store[ip] = []

    # Limpiar mensajes antiguos
    rate_limit_store[ip] = [
        t for t in rate_limit_store[ip]
        if (now - t).seconds < 60
    ]

    if len(rate_limit_store[ip]) >= limit:
        return False

    rate_limit_store[ip].append(now)
    return True
