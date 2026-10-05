"""Skill de clientes del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class CustomerSkill(BaseSkill):
    """Skill para CRM y Customer 360."""

    def __init__(self):
        self.db: Optional[RestaurantDB] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "obtener_cliente": self._obtener_cliente,
            "buscar_cliente": self._buscar_cliente,
            "crear_cliente": self._crear_cliente,
            "obtener_historial": self._obtener_historial,
        }

        return actions[action](params)

    def _obtener_cliente(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_cliente(params["telefono"])

    def _buscar_cliente(self, params: Dict) -> List[Dict]:
        return self.db.buscar_cliente(params["busqueda"])

    def _crear_cliente(self, params: Dict) -> int:
        return self.db.crear_cliente(params)

    def _obtener_historial(self, params: Dict) -> Dict:
        return self.db.obtener_historial(params["cliente_id"])

    def get_capabilities(self) -> List[str]:
        return ["obtener_cliente", "buscar_cliente", "crear_cliente",
                "obtener_historial"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "customers"}
