"""Servidor FastAPI para Restaurant AI Platform."""

import json
import logging
import os
import secrets
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from api.agent import process_message
from api.check_env import check_environment
from api.security import (
    TOKEN_TTL_SEGUNDOS,
    crear_token,
    verificar_firma_whatsapp,
    verificar_token,
)
from database.db_manager import ReservaError, RestaurantDB
from skills.channels.channel_skill import ChannelSkill

_channel_skill = ChannelSkill()
_channel_skill.initialize({})

logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Restaurant AI Platform", version="1.0.0")

# CORS: origenes explicitos desde variables de entorno
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

# ===========================================
# SEGURIDAD: API KEY + RATE LIMITING
# ===========================================
# En produccion (REQUIRE_API_KEY=true) toda /api/* (salvo health) exige
# el header X-API-Key. En desarrollo se puede desactivar.
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
API_KEY = os.getenv("API_KEY", "")

# Idempotencia de mensajes (DEV: en memoria; PROD: ver docs/DESPLIEGUE.md)
processed_messages: set = set()
PROCESSED_MESSAGES_MAX = 10000

# Rate limiting (DEV: en memoria; PROD: ver docs/DESPLIEGUE.md)
rate_limit_store = {}


@app.middleware("http")
async def seguridad_api_key(request: Request, call_next):
    path = request.url.path
    if REQUIRE_API_KEY and path.startswith("/api/") and path != "/api/health":
        clave = request.headers.get("X-API-Key", "")
        if not API_KEY or not clave or not secrets.compare_digest(clave, API_KEY):
            return JSONResponse(
                status_code=401,
                content={"detail": "API key invalida o ausente"},
            )
    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    ok, errors = check_environment()
    if not ok:
        logger.warning("Advertencias de configuracion: %s", errors)
    logger.info("Restaurant AI Platform iniciado en http://localhost:8000")


def marcar_procesado(message_id: str) -> bool:
    """Idempotencia DEV: devuelve True si el mensaje ya fue procesado."""
    if not message_id:
        return False
    if message_id in processed_messages:
        return True
    processed_messages.add(message_id)
    if len(processed_messages) > PROCESSED_MESSAGES_MAX:
        # Podar los mas antiguos (set conserva orden de insercion)
        for _ in range(PROCESSED_MESSAGES_MAX // 10):
            processed_messages.pop()
    return False


def ctx(request: Request, **kwargs):
    return {
        "request": request,
        "now": datetime.now().strftime("%d/%m/%Y %H:%M"),  # noqa: DTZ005
        **kwargs,
    }


# ===========================================
# AUTENTICACION Y AUTORIZACION
# ===========================================
# Dos capas:
#  1. Servicio (integraciones/CRM): X-API-Key, exigida en produccion
#     con REQUIRE_API_KEY=true (ver middleware seguro_api_key).
#  2. Cliente (recursos propios): JWT Bearer emitido por
#     POST /api/auth/token con la X-API-Key del servicio.
# La identidad NUNCA se toma de headers declarativos ni de argumentos
# del LLM: solo del token firmado o del webhook verificado por firma.

_HDR_401 = {"WWW-Authenticate": "Bearer"}


class AuthTokenRequest(BaseModel):
    cliente_id: int


def cliente_autenticado(request: Request) -> int:
    """Extrae y valida el cliente dueño del recurso (JWT Bearer)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente", headers=_HDR_401)
    cliente_id = verificar_token(auth[len("Bearer "):].strip())
    if cliente_id is None:
        raise HTTPException(
            status_code=401, detail="Token invalido o expirado", headers=_HDR_401,
        )
    if db.obtener_cliente_por_id(cliente_id) is None:
        raise HTTPException(
            status_code=401, detail="Token invalido o expirado", headers=_HDR_401,
        )
    return cliente_id


def servicio_autenticado(request: Request) -> None:
    """X-API-Key del servicio (integraciones/CRM). Siempre exigida."""
    clave = request.headers.get("X-API-Key", "")
    if not API_KEY or not clave or not secrets.compare_digest(clave, API_KEY):
        raise HTTPException(status_code=401, detail="API key invalida o ausente")


def _solo_digitos(valor) -> str:
    return "".join(c for c in str(valor or "") if c.isdigit())


def _mismo_telefono(a: str | None, b: str | None) -> bool:
    da, db_ = _solo_digitos(a), _solo_digitos(b)
    return bool(da) and da == db_


def _pedido_propio(pedido_id: int, dueno: int) -> dict:
    """404 si no existe, 403 si pertenece a otro cliente."""
    pedido = db.obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.get("cliente_id") != dueno:
        raise HTTPException(status_code=403, detail="No autorizado")
    return pedido



# ===========================================
# WEBHOOK WHATSAPP
# ===========================================

@app.get("/webhook/whatsapp")
async def whatsapp_verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    """Verificacion del webhook de WhatsApp."""
    esperado = os.getenv("WHATSAPP_VERIFY_TOKEN") or ""
    if (
        hub_mode == "subscribe"
        and esperado
        and secrets.compare_digest(hub_token, esperado)
    ):
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token invalido")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Recibe mensajes de WhatsApp.

    Autenticacion: X-Hub-Signature-256 (HMAC-SHA256 del body crudo con
    WHATSAPP_APP_SECRET). Fail-closed: sin secreto configurado o con firma
    invalida se responde 403 y NO se procesa nada.
    """
    body = await request.body()
    app_secret = os.getenv("WHATSAPP_APP_SECRET", "")
    firma = request.headers.get("X-Hub-Signature-256", "")

    if not app_secret:
        logger.error(
            "WHATSAPP_APP_SECRET no configurado: webhook de WhatsApp rechazado",
        )
        return JSONResponse(status_code=403, content={"status": "forbidden"})

    if not verificar_firma_whatsapp(body, firma, app_secret):
        logger.warning("Webhook WhatsApp rechazado: firma invalida")
        return JSONResponse(status_code=403, content={"status": "forbidden"})

    try:
        data = json.loads(body)
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "ok"}

        message = value["messages"][0]
        phone = message["from"]
        text = message["text"]["body"]
        message_id = message["id"]

        # Rate limiting
        if not check_rate_limit(phone):
            logger.info("Rate limit alcanzado para %s", phone)
            return {"status": "rate_limited"}

        # Idempotencia: no procesar dos veces el mismo evento
        if marcar_procesado(message_id):
            return {"status": "ok"}

        # Procesar con agente en threadpool (no bloquea el event loop).
        # La identidad del cliente sale SOLO de un payload verificado por
        # firma: es la que acota las tools a los recursos propios.
        response = await run_in_threadpool(
            process_message, text, phone, "whatsapp", phone,
        )
        logger.info("Respuesta a %s: %s", phone, response)

        # Enviar respuesta real por WhatsApp (no simula exito)
        envio = _channel_skill.execute("enviar_respuesta", {
            "channel": "whatsapp", "to": phone, "message": response,
        })
        if not envio.get("success"):
            logger.info("Respuesta no enviada (whatsapp): %s", envio.get("error"))

        return {"status": "ok"}

    except Exception:
        logger.exception("Error procesando webhook de WhatsApp")
        return JSONResponse(status_code=500, content={"status": "error"})


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
        update_id = str(data.get("update_id", ""))

        if not text:
            return {"status": "ok"}

        # Rate limiting
        if not check_rate_limit(chat_id):
            logger.info("Rate limit alcanzado para telegram %s", chat_id)
            return {"status": "rate_limited"}

        # Idempotencia
        if marcar_procesado(f"tg:{update_id}:{chat_id}"):
            return {"status": "ok"}

        # Procesar con agente en threadpool (no bloquea el event loop)
        response = await run_in_threadpool(
            process_message, text, chat_id, "telegram",
        )
        logger.info("Respuesta a Telegram %s: %s", chat_id, response)

        # Enviar respuesta real por Telegram (no simula exito)
        envio = _channel_skill.execute("enviar_respuesta", {
            "channel": "telegram", "to": chat_id, "message": response,
        })
        if not envio.get("success"):
            logger.info("Respuesta no enviada (telegram): %s", envio.get("error"))

        return {"status": "ok"}

    except Exception:
        logger.exception("Error procesando webhook de Telegram")
        return JSONResponse(status_code=500, content={"status": "error"})


# ===========================================
# PAGINAS HTML - CRM
# ===========================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    metricas = db.obtener_metricas()
    return templates.TemplateResponse(request, "dashboard.html", ctx(
        request, active_page="dashboard", metricas=metricas,
    ))


@app.get("/inbox", response_class=HTMLResponse)
async def inbox(request: Request):
    return templates.TemplateResponse(request, "inbox.html", ctx(
        request, active_page="inbox",
    ))


@app.get("/clientes", response_class=HTMLResponse)
async def clientes(request: Request):
    return templates.TemplateResponse(request, "clientes.html", ctx(
        request, active_page="clientes",
    ))


@app.get("/pedidos", response_class=HTMLResponse)
async def pedidos(request: Request):
    return templates.TemplateResponse(request, "pedidos.html", ctx(
        request, active_page="pedidos",
    ))


@app.get("/reservas", response_class=HTMLResponse)
async def reservas(request: Request):
    return templates.TemplateResponse(request, "reservas.html", ctx(
        request, active_page="reservas",
    ))


@app.get("/menu", response_class=HTMLResponse)
async def menu(request: Request):
    categorias = db.obtener_categorias()
    productos = db.obtener_productos()
    return templates.TemplateResponse(request, "menu.html", ctx(
        request, active_page="menu", categorias=categorias, productos=productos,
    ))


@app.get("/promociones", response_class=HTMLResponse)
async def promociones(request: Request):
    return templates.TemplateResponse(request, "promociones.html", ctx(
        request, active_page="promociones",
    ))


@app.get("/delivery", response_class=HTMLResponse)
async def delivery(request: Request):
    return templates.TemplateResponse(request, "delivery.html", ctx(
        request, active_page="delivery",
    ))


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    return templates.TemplateResponse(request, "analytics.html", ctx(
        request, active_page="analytics",
    ))


@app.get("/ai-intelligence", response_class=HTMLResponse)
async def ai_intelligence(request: Request):
    return templates.TemplateResponse(request, "ai_intelligence.html", ctx(
        request, active_page="ai-intelligence",
    ))


@app.get("/ai-governance", response_class=HTMLResponse)
async def ai_governance(request: Request):
    return templates.TemplateResponse(request, "ai_governance.html", ctx(
        request, active_page="ai-governance",
    ))


@app.get("/configuracion", response_class=HTMLResponse)
async def configuracion(request: Request):
    return templates.TemplateResponse(request, "configuracion.html", ctx(
        request, active_page="configuracion",
    ))


@app.get("/cliente/{cliente_id}", response_class=HTMLResponse)
async def cliente_historial(request: Request, cliente_id: int):
    cliente = db.obtener_cliente_por_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    historial = db.obtener_historial(cliente_id)
    return templates.TemplateResponse(request, "cliente_historial.html", ctx(
        request, cliente=cliente, historial=historial,
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


@app.post("/api/auth/token")
async def api_auth_token(
    payload: AuthTokenRequest,
    _: None = Depends(servicio_autenticado),
):
    """Emite un JWT de cliente. Requiere la X-API-Key del servicio.

    La identidad de cliente se entrega solo a credenciales de servicio
    verificadas (en produccion, la emision al usuario final se hace por
    WhatsApp/OTP: fuera de alcance de esta fase).
    """
    if db.obtener_cliente_por_id(payload.cliente_id) is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    try:
        token = crear_token(payload.cliente_id)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503, detail="SECRET_KEY no configurado",
        ) from e
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": TOKEN_TTL_SEGUNDOS,
    }


@app.post("/api/pedidos")
async def api_crear_pedido(
    cliente_id: int | None = None,
    canal: str = "webchat",
    dueno: int = Depends(cliente_autenticado),
):
    if cliente_id is not None and cliente_id != dueno:
        raise HTTPException(status_code=403, detail="No autorizado")
    try:
        pedido_id = db.crear_pedido(dueno, canal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"pedido_id": pedido_id}


@app.get("/api/pedidos/{pedido_id}")
async def api_pedido(pedido_id: int, dueno: int = Depends(cliente_autenticado)):
    return _pedido_propio(pedido_id, dueno)


@app.post("/api/pedidos/{pedido_id}/items")
async def api_agregar_item(
    pedido_id: int,
    producto_id: int = Form(...),
    cantidad: int = Form(1),
    tamano: str = Form(None),
    extras: str = Form(None),
    dueno: int = Depends(cliente_autenticado),
):
    _pedido_propio(pedido_id, dueno)
    opciones = {}
    if tamano:
        opciones["tamano"] = tamano
    if extras:
        opciones["extras"] = [e.strip() for e in extras.split(",") if e.strip()]

    try:
        exito = db.agregar_item_pedido(pedido_id, producto_id, cantidad, opciones)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not exito:
        raise HTTPException(
            status_code=409, detail="El pedido no admite items en su estado actual",
        )
    return {"success": exito}


@app.post("/api/pedidos/{pedido_id}/confirmar")
async def api_confirmar_pedido(
    pedido_id: int, dueno: int = Depends(cliente_autenticado),
):
    from database.models import OrderStatus
    _pedido_propio(pedido_id, dueno)
    exito = db.actualizar_estado_pedido(pedido_id, OrderStatus.CONFIRMED)
    return {"success": exito}


@app.post("/api/pedidos/{pedido_id}/cancelar")
async def api_cancelar_pedido(
    pedido_id: int,
    motivo: str = Form(...),
    dueno: int = Depends(cliente_autenticado),
):
    _pedido_propio(pedido_id, dueno)
    exito = db.cancelar_pedido(pedido_id, motivo)
    return {"success": exito}


@app.post("/api/reservas")
async def api_crear_reserva(
    fecha: str = Form(...),
    hora: str = Form(...),
    personas: int = Form(...),
    nombre: str = Form(...),
    telefono: str = Form(...),
    cliente_id: int | None = Form(None),
    dueno: int = Depends(cliente_autenticado),
):
    if cliente_id is not None and cliente_id != dueno:
        raise HTTPException(status_code=403, detail="No autorizado")

    cliente = db.obtener_cliente_por_id(dueno)
    if not cliente:
        raise HTTPException(status_code=401, detail="Token invalido o expirado",
                            headers=_HDR_401)
    if not cliente.get("telefono"):
        raise HTTPException(status_code=400, detail="El cliente no tiene telefono")
    if telefono and not _mismo_telefono(telefono, cliente["telefono"]):
        # Impide reservar a nombre de otro telefono (y agotar su slot via indice unico)
        raise HTTPException(status_code=403, detail="No autorizado")

    try:
        reserva_id = db.crear_reserva({
            "cliente_id": dueno,
            "fecha": fecha,
            "hora": hora,
            "personas": personas,
            "nombre_contacto": nombre,
            "telefono": cliente["telefono"],
        })
    except (ReservaError, ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"reserva_id": reserva_id}


@app.get("/api/reservas/disponibilidad")
async def api_disponibilidad(fecha: str, personas: int):
    return db.verificar_disponibilidad(fecha, None, personas)


@app.get("/api/clientes/buscar")
async def api_buscar_cliente(q: str, _: None = Depends(servicio_autenticado)):
    if not q or len(q) > 100:
        raise HTTPException(status_code=400, detail="Consulta invalida")
    return db.buscar_cliente(q)


@app.get("/api/clientes/{cliente_id}")
async def api_cliente(cliente_id: int, dueno: int = Depends(cliente_autenticado)):
    if cliente_id != dueno:
        raise HTTPException(status_code=403, detail="No autorizado")
    cliente = db.obtener_cliente_por_id(dueno)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.get("/api/metricas")
async def api_metricas(_: None = Depends(servicio_autenticado)):
    return db.obtener_metricas()


@app.get("/api/health")
async def api_health():
    return db.health_check()


@app.post("/api/chat")
async def api_chat(request: Request, mensaje: str = Form(...), canal: str = Form("webchat")):
    if not check_rate_limit(request.client.host if request.client else "unknown"):
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes")
    if canal not in ("whatsapp", "telegram", "webchat"):
        raise HTTPException(status_code=400, detail="Canal invalido")
    response = await run_in_threadpool(
        process_message, mensaje, "dashboard", canal,
    )
    return {"response": response}


@app.get("/api/handoffs")
async def api_handoffs(_: None = Depends(servicio_autenticado)):
    return db.obtener_handoffs_pendientes()


# ===========================================
# RATE LIMITING (DEV: memoria; PROD: Redis)
# ===========================================

RATE_LIMIT_STORE_MAX = 5000


def check_rate_limit(ip: str) -> bool:
    """Verifica rate limiting por IP/identificador de canal."""
    now = datetime.now()  # noqa: DTZ005
    limit = int(os.getenv("RATE_LIMIT_MESSAGES_PER_MINUTE", "30"))

    if len(rate_limit_store) >= RATE_LIMIT_STORE_MAX and ip not in rate_limit_store:
        # Protegerse contra inundacion de claves nuevas
        return False

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
