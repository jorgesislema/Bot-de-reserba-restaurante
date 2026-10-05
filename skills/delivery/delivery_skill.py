"""Skill de delivery del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class DeliverySkill(BaseSkill):
    """Skill para gestion de delivery."""

    def __init__(self):
        self.db: Optional[RestaurantDB] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "calcular_costo": self._calcular_costo,
            "crear_envio": self._crear_envio,
            "obtener_estado": self._obtener_estado,
        }

        return actions[action](params)

    def _calcular_costo(self, params: Dict) -> Dict:
        return self.db.calcular_costo_delivery(params["direccion"])

    def _crear_envio(self, params: Dict) -> int:
        return self.db.crear_delivery(
            params["pedido_id"],
            params
        )

    def _obtener_estado(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_estado_delivery(params["pedido_id"])

    def get_capabilities(self) -> List[str]:
        return ["calcular_costo", "crear_envio", "obtener_estado"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "delivery"}
