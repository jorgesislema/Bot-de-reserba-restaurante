"""Skill de monitoreo del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill


class MonitoringSkill(BaseSkill):
    """Skill para monitoreo y alertas."""

    def initialize(self, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "health_check": self._health_check,
            "registrar_fallo": self._registrar_fallo,
        }

        return actions[action](params)

    def _health_check(self, params: Dict) -> Dict:
        return {"status": "ok", "components": {}}

    def _registrar_fallo(self, params: Dict) -> None:
        pass

    def get_capabilities(self) -> List[str]:
        return ["health_check", "registrar_fallo"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "monitoring"}
