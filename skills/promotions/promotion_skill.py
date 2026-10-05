"""Skill de promociones del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class PromotionSkill(BaseSkill):
    """Skill para promociones y upselling."""

    def __init__(self):
        self.db: Optional[RestaurantDB] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "obtener_promociones": self._obtener_promociones,
            "sugerir_upsell": self._sugerir_upsell,
        }

        return actions[action](params)

    def _obtener_promociones(self, params: Dict) -> List[Dict]:
        return self.db.obtener_promociones_activas(params.get("canal"))

    def _sugerir_upsell(self, params: Dict) -> Optional[str]:
        return "Deseas agregar 2 bebidas por $3 adicionales?"

    def get_capabilities(self) -> List[str]:
        return ["obtener_promociones", "sugerir_upsell"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "promotions"}
