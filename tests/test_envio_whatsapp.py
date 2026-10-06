"""Tests de envio real de WhatsApp: el fallo NUNCA se reporta como exito."""

import httpx
import pytest

from skills.channels.channel_skill import ChannelSkill


@pytest.fixture
def skill():
    s = ChannelSkill()
    s.initialize({})
    return s


def _configurar(monkeypatch, token="unit-test-token", phone_id="1234567890"):
    monkeypatch.setenv("WHATSAPP_TOKEN", token)
    monkeypatch.setenv("WHATSAPP_PHONE_ID", phone_id)


def test_error_http_500_no_es_exito(skill, monkeypatch):
    _configurar(monkeypatch)

    class _Resp:
        status_code = 500
        text = "Internal Server Error"

    monkeypatch.setattr(
        "skills.channels.channel_skill.httpx.post", lambda *_a, **_k: _Resp(),
    )
    resultado = skill.execute("enviar_respuesta", {
        "channel": "whatsapp", "to": "+593991111111", "message": "hola",
    })
    assert resultado["success"] is False
    assert resultado["error"] == "channel_error"


def test_error_de_conexion_no_es_exito(skill, monkeypatch):
    _configurar(monkeypatch)

    def _explorar(*_args, **_kwargs):
        raise httpx.ConnectError("conexion rechazada")

    monkeypatch.setattr(
        "skills.channels.channel_skill.httpx.post", _explorar,
    )
    resultado = skill.execute("enviar_respuesta", {
        "channel": "whatsapp", "to": "+593991111111", "message": "hola",
    })
    assert resultado["success"] is False
    assert resultado["error"].startswith("channel_error")


def test_timeout_no_es_exito(skill, monkeypatch):
    _configurar(monkeypatch)

    def _explorar(*_args, **_kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(
        "skills.channels.channel_skill.httpx.post", _explorar,
    )
    resultado = skill.execute("enviar_respuesta", {
        "channel": "whatsapp", "to": "+593991111111", "message": "hola",
    })
    assert resultado["success"] is False


def test_sin_credenciales_no_simula_exito(skill, monkeypatch):
    monkeypatch.delenv("WHATSAPP_TOKEN", raising=False)
    monkeypatch.delenv("WHATSAPP_PHONE_ID", raising=False)
    resultado = skill.execute("enviar_respuesta", {
        "channel": "whatsapp", "to": "+593991111111", "message": "hola",
    })
    assert resultado["success"] is False
    assert resultado["error"] == "channel_not_configured"


def test_envio_exitoso_reporta_exito(skill, monkeypatch):
    _configurar(monkeypatch)

    class _Resp:
        status_code = 200
        text = "{}"

        def json(self):
            return {"messages": [{"id": "wamid.OK"}]}

    llamada = {}

    def _post(url, **kwargs):
        llamada["url"] = url
        llamada.update(kwargs)
        return _Resp()

    monkeypatch.setattr("skills.channels.channel_skill.httpx.post", _post)
    resultado = skill.execute("enviar_respuesta", {
        "channel": "whatsapp", "to": "+593991111111", "message": "hola",
    })
    assert resultado["success"] is True

    # El token va solo en el header Authorization, nunca en el payload
    assert "unit-test-token" not in str(llamada.get("json") or {})
    assert "Authorization" in llamada["headers"]


def test_resultado_no_contiene_el_token(skill, monkeypatch):
    """Ni el resultado ni su representacion contienen credenciales."""
    _configurar(monkeypatch, token="unit-test-token-secreto")

    def _explorar(*_args, **_kwargs):
        raise httpx.ConnectError("fallo")

    monkeypatch.setattr("skills.channels.channel_skill.httpx.post", _explorar)
    resultado = skill.execute("enviar_respuesta", {
        "channel": "whatsapp", "to": "+593991111111", "message": "hola",
    })
    assert "unit-test-token-secreto" not in str(resultado)
