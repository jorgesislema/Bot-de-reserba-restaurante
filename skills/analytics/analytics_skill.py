"""Skill de analytics del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class AnalyticsSkill(BaseSkill):
    """Skill para metricas y analytics."""

    def __init__(self):
        self.db: Optional[RestaurantDB] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "registrar_interaccion": self._registrar_interaccion,
            "obtener_metricas": self._obtener_metricas,
        }

        return actions[action](params)

    def _registrar_interaccion(self, params: Dict) -> None:
        self.db.registrar_interaccion(params)

    def _obtener_metricas(self, params: Dict) -> Dict:
        return self.db.obtener_metricas()

    def get_capabilities(self) -> List[str]:
        return ["registrar_interaccion", "obtener_metricas"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "analytics"}
