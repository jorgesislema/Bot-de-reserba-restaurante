"""Skill de pedidos del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB
from database.models import OrderStatus


class OrderSkill(BaseSkill):
    """Skill para gestion de pedidos."""

    def __init__(self):
        self.db: Optional[RestaurantDB] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "crear_pedido": self._crear_pedido,
            "agregar_item": self._agregar_item,
            "obtener_pedido": self._obtener_pedido,
            "calcular_total": self._calcular_total,
            "confirmar_pedido": self._confirmar_pedido,
            "cancelar_pedido": self._cancelar_pedido,
            "obtener_estado": self._obtener_estado,
        }

        return actions[action](params)

    def _crear_pedido(self, params: Dict) -> int:
        return self.db.crear_pedido(
            params["cliente_id"],
            params.get("canal", "whatsapp")
        )

    def _agregar_item(self, params: Dict) -> bool:
        return self.db.agregar_item_pedido(
            params["pedido_id"],
            params["producto_id"],
            params.get("cantidad", 1),
            params.get("opciones")
        )

    def _obtener_pedido(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_pedido(params["pedido_id"])

    def _calcular_total(self, params: Dict) -> float:
        pedido = self.db.obtener_pedido(params["pedido_id"])
        return pedido["total"] if pedido else 0

    def _confirmar_pedido(self, params: Dict) -> bool:
        return self.db.actualizar_estado_pedido(
            params["pedido_id"],
            OrderStatus.CONFIRMED
        )

    def _cancelar_pedido(self, params: Dict) -> bool:
        return self.db.cancelar_pedido(
            params["pedido_id"],
            params.get("motivo", "Cancelado por cliente")
        )

    def _obtener_estado(self, params: Dict) -> Optional[str]:
        pedido = self.db.obtener_pedido(params["pedido_id"])
        return pedido["estado"] if pedido else None

    def get_capabilities(self) -> List[str]:
        return ["crear_pedido", "agregar_item", "obtener_pedido",
                "calcular_total", "confirmar_pedido", "cancelar_pedido",
                "obtener_estado"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "orders"}
