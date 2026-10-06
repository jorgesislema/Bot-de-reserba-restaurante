"""Tests de seguridad del webhook de WhatsApp (canal real de produccion).

Verifica X-Hub-Signature-256 (fail-closed), GET de verificacion,
idempotencia y rate limit. Nunca se imprimen secretos: los usados aqui
son valores inventados para el test.
"""

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from api import main

APP_SECRET = "unit-test-app-secret"
VERIFY_TOKEN = "unit-test-verify-token"

PHONE = "+593991111111"


def _payload(message_id: str = "wamid.TEST.1", phone: str = PHONE,
             text: str = "hola") -> bytes:
    return json.dumps({
        "entry": [{
            "changes": [{
                "value": {"messages": [{
                    "from": phone,
                    "text": {"body": text},
                    "id": message_id,
                }]},
            }],
        }],
    }).encode()


def _firmar(body: bytes, secret: str = APP_SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


@pytest.fixture
def webhook_env(monkeypatch):
    """Entorno de prueba: secreto de firma, doble de process/envio, estado limpio."""
    monkeypatch.setenv("WHATSAPP_APP_SECRET", APP_SECRET)
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", VERIFY_TOKEN)

    llamadas = []

    def fake_process(mensaje, thread_id, channel, identidad_verificada=None):
        llamadas.append({
            "mensaje": mensaje,
            "thread_id": thread_id,
            "channel": channel,
            "identidad_verificada": identidad_verificada,
        })
        return "respuesta-segura"

    envios = []

    def fake_execute(_action, params):
        envios.append(params)
        return {"success": True, "data": {}, "error": None}

    monkeypatch.setattr(main, "process_message", fake_process)
    monkeypatch.setattr(main._channel_skill, "execute", fake_execute)  # noqa: SLF001
    main.processed_messages.clear()
    main.rate_limit_store.clear()

    yield {"llamadas": llamadas, "envios": envios}

    main.processed_messages.clear()
    main.rate_limit_store.clear()


def _post(body: bytes, firma: str = None, client: TestClient = None):
    headers = {"Content-Type": "application/json"}
    if firma is not None:
        headers["X-Hub-Signature-256"] = firma
    return client.post("/webhook/whatsapp", content=body, headers=headers)


# ===========================================
# FIRMA DEL WEBHOOK
# ===========================================

def test_firma_valida_procesa_una_vez(webhook_env):
    client = TestClient(main.app)
    body = _payload()

    resp = _post(body, _firmar(body), client)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert len(webhook_env["llamadas"]) == 1

    # La identidad verificada se pasa al agente (no se toma del LLM)
    llamada = webhook_env["llamadas"][0]
    assert llamada["identidad_verificada"] == PHONE
    assert llamada["channel"] == "whatsapp"

    # Respuesta enviada por WhatsApp real al remitente verificado
    assert webhook_env["envios"][0]["to"] == PHONE


def test_firma_invalida_rechazada_sin_procesar(webhook_env):
    client = TestClient(main.app)
    body = _payload(message_id="wamid.FAKESIG.1")

    resp = _post(body, _firmar(body, secret="otro-secreto"), client)
    assert resp.status_code == 403
    assert webhook_env["llamadas"] == []
    assert webhook_env["envios"] == []


def test_firma_ausente_rechazada(webhook_env):
    client = TestClient(main.app)
    resp = _post(_payload(message_id="wamid.NOSIG.1"), firma=None, client=client)
    assert resp.status_code == 403
    assert webhook_env["llamadas"] == []


def test_body_alterado_rechazado(webhook_env):
    client = TestClient(main.app)
    body_original = _payload(message_id="wamid.OK.1", text="hola")
    body_falsificado = _payload(message_id="wamid.OK.1", text="hola gratis")

    resp = _post(body_falsificado, _firmar(body_original), client)
    assert resp.status_code == 403
    assert webhook_env["llamadas"] == []


def test_sin_app_secret_configurado_fail_closed(webhook_env, monkeypatch):
    """Si WHATSAPP_APP_SECRET no existe, NUNCA se procesa (403)."""
    monkeypatch.delenv("WHATSAPP_APP_SECRET")
    client = TestClient(main.app)
    body = _payload(message_id="wamid.NOSECRET.1")

    resp = _post(body, _firmar(body), client)
    assert resp.status_code == 403
    assert webhook_env["llamadas"] == []


# ===========================================
# VERIFICACION GET (subscribe)
# ===========================================

def test_get_verify_token_correcto(webhook_env):  # noqa: ARG001
    client = TestClient(main.app)
    resp = client.get("/webhook/whatsapp", params={
        "hub.mode": "subscribe",
        "hub.verify_token": VERIFY_TOKEN,
        "hub.challenge": "12345",
    })
    assert resp.status_code == 200
    assert resp.text == "12345"


def test_get_verify_token_invalido(webhook_env):  # noqa: ARG001
    client = TestClient(main.app)
    resp = client.get("/webhook/whatsapp", params={
        "hub.mode": "subscribe",
        "hub.verify_token": "adivinado",
        "hub.challenge": "12345",
    })
    assert resp.status_code == 403


# ===========================================
# IDEMPOTENCIA Y RATE LIMIT EN EL FLUJO REAL
# ===========================================

def test_evento_duplicado_procesa_solo_una_vez(webhook_env):
    client = TestClient(main.app)
    body = _payload(message_id="wamid.DUP.1")

    resp1 = _post(body, _firmar(body), client)
    resp2 = _post(body, _firmar(body), client)

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp2.json() == {"status": "ok"}
    assert len(webhook_env["llamadas"]) == 1
    assert len(webhook_env["envios"]) == 1


def test_rate_limit_no_procesa(webhook_env, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_MESSAGES_PER_MINUTE", "1")
    client = TestClient(main.app)

    body1 = _payload(message_id="wamid.RL.1")
    resp1 = _post(body1, _firmar(body1), client)
    assert resp1.status_code == 200

    body2 = _payload(message_id="wamid.RL.2")
    resp2 = _post(body2, _firmar(body2), client)
    assert resp2.json() == {"status": "rate_limited"}
    assert len(webhook_env["llamadas"]) == 1
