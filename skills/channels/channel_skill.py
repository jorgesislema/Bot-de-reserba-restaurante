"""Skill de canales omnicanal.

Envio REAL a APIs oficiales. Si el canal no esta configurado se devuelve
{"success": False, "error": "channel_not_configured"}: NUNCA se simula exito.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

WHATSAPP_GRAPH_URL = "https://graph.facebook.com/v20.0"


class ChannelSkill(BaseSkill):
    """Skill para gestion de canales (WhatsApp, Telegram, Web)."""

    def initialize(self, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "normalizar_mensaje": self._normalizar_mensaje,
            "enviar_respuesta": self._enviar_respuesta,
        }

        if action not in actions:
            raise ValueError(f"Accion '{action}' no soportada")

        return actions[action](params)

    def _normalizar_mensaje(self, params: Dict) -> Dict:
        """Normaliza mensaje de cualquier canal."""
        return {
            "channel": params.get("channel", "whatsapp"),
            "user_id": params.get("user_id"),
            "message": params.get("message"),
            "timestamp": params.get("timestamp")
        }

    def _enviar_respuesta(self, params: Dict) -> Dict:
        """Envia un mensaje real por el canal indicado.

        Returns:
            {"success": bool, "data": {...}|None, "error": str|None}
        """
        channel = params.get("channel", "whatsapp")
        destino = params.get("to")
        mensaje = params.get("message")

        if not destino or not mensaje:
            return {"success": False, "data": None, "error": "missing_parameters"}

        if channel == "whatsapp":
            return self._enviar_whatsapp(destino, mensaje)
        if channel == "telegram":
            return self._enviar_telegram(destino, mensaje)

        return {"success": False, "data": None, "error": "channel_not_supported"}

    def _enviar_whatsapp(self, telefono: str, mensaje: str) -> Dict:
        token = os.getenv("WHATSAPP_TOKEN", "")
        phone_id = os.getenv("WHATSAPP_PHONE_ID", "")

        # Placeholders del .env.example no cuentan como configurado
        if not token or not phone_id or token.startswith("your-"):
            logger.warning("WhatsApp no configurado (WHATSAPP_TOKEN/PHONE_ID)")
            return {"success": False, "data": None, "error": "channel_not_configured"}

        url = f"{WHATSAPP_GRAPH_URL}/{phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "text",
            "text": {"preview_url": False, "body": mensaje},
        }
        try:
            resp = httpx.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=15.0,
            )
            if resp.status_code >= 400:
                logger.error(
                    "WhatsApp API error %s: %s", resp.status_code, resp.text[:500]
                )
                return {"success": False, "data": None, "error": "channel_error"}
            return {"success": True, "data": resp.json(), "error": None}
        except httpx.HTTPError as e:
            logger.exception("Fallo de conexion con WhatsApp API")
            return {"success": False, "data": None, "error": f"channel_error: {e}"}

    def _enviar_telegram(self, chat_id: str, mensaje: str) -> Dict:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token or token.startswith("your-"):
            logger.warning("Telegram no configurado (TELEGRAM_BOT_TOKEN)")
            return {"success": False, "data": None, "error": "channel_not_configured"}

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            resp = httpx.post(
                url,
                json={"chat_id": chat_id, "text": mensaje},
                timeout=15.0,
            )
            if resp.status_code >= 400:
                logger.error(
                    "Telegram API error %s: %s", resp.status_code, resp.text[:500]
                )
                return {"success": False, "data": None, "error": "channel_error"}
            return {"success": True, "data": resp.json(), "error": None}
        except httpx.HTTPError as e:
            logger.exception("Fallo de conexion con Telegram API")
            return {"success": False, "data": None, "error": f"channel_error: {e}"}

    def get_capabilities(self) -> List[str]:
        return ["normalizar_mensaje", "enviar_respuesta"]

    def health_check(self) -> Dict[str, Any]:
        whatsapp_ok = bool(os.getenv("WHATSAPP_TOKEN")) and bool(
            os.getenv("WHATSAPP_PHONE_ID")
        )
        telegram_ok = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
        return {
            "status": "ok",
            "skill": "channels",
            "whatsapp": "configured" if whatsapp_ok else "not_configured",
            "telegram": "configured" if telegram_ok else "not_configured",
        }
