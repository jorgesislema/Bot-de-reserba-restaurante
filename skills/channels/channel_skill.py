"""Skill de canales omnicanal."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill


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

        return actions[action](params)

    def _normalizar_mensaje(self, params: Dict) -> Dict:
        """Normaliza mensaje de cualquier canal."""
        return {
            "channel": params.get("channel", "whatsapp"),
            "user_id": params.get("user_id"),
            "message": params.get("message"),
            "timestamp": params.get("timestamp")
        }

    def _enviar_respuesta(self, params: Dict) -> bool:
        """Envia respuesta por el canal correspondiente."""
        return True

    def get_capabilities(self) -> List[str]:
        return ["normalizar_mensaje", "enviar_respuesta"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "channels"}
