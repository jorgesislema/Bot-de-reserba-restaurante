"""Skill de menu del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class MenuSkill(BaseSkill):
    """Skill para consulta del menu."""

    def __init__(self):
        self.db: Optional[RestaurantDB] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "buscar": self._buscar,
            "obtener_producto": self._obtener_producto,
            "obtener_categorias": self._obtener_categorias,
            "verificar_disponibilidad": self._verificar_disponibilidad,
            "calcular_precio": self._calcular_precio,
            "recomendar": self._recomendar,
        }

        if action not in actions:
            raise ValueError(f"Accion '{action}' no soportada")

        return actions[action](params)

    def _buscar(self, params: Dict) -> List[Dict]:
        return self.db.buscar_producto(params.get("query", ""))

    def _obtener_producto(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_producto(params["producto_id"])

    def _obtener_categorias(self, params: Dict) -> List[Dict]:
        return self.db.obtener_categorias()

    def _verificar_disponibilidad(self, params: Dict) -> bool:
        producto = self.db.obtener_producto(params["producto_id"])
        return producto is not None and producto.get("disponible", False)

    def _calcular_precio(self, params: Dict) -> float:
        return self.db.calcular_precio(
            params["producto_id"],
            params.get("opciones", {})
        )

    def _recomendar(self, params: Dict) -> List[Dict]:
        productos = self.db.obtener_productos()
        return productos[:3]

    def get_capabilities(self) -> List[str]:
        return ["buscar", "obtener_producto", "obtener_categorias",
                "verificar_disponibilidad", "calcular_precio", "recomendar"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "menu"}
