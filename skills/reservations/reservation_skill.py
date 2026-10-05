"""Skill de reservas del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class ReservationSkill(BaseSkill):
    """Skill para gestion de reservas."""

    def __init__(self):
        self.db: Optional[RestaurantDB] = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "verificar_disponibilidad": self._verificar_disponibilidad,
            "crear_reserva": self._crear_reserva,
            "cancelar_reserva": self._cancelar_reserva,
            "obtener_reservas": self._obtener_reservas,
        }

        return actions[action](params)

    def _verificar_disponibilidad(self, params: Dict) -> List[Dict]:
        return self.db.verificar_disponibilidad(
            params["fecha"],
            params.get("hora"),
            params["personas"]
        )

    def _crear_reserva(self, params: Dict) -> int:
        return self.db.crear_reserva(params)

    def _cancelar_reserva(self, params: Dict) -> bool:
        return self.db.cancelar_reserva(
            params["reserva_id"],
            params.get("motivo")
        )

    def _obtener_reservas(self, params: Dict) -> List[Dict]:
        return []

    def get_capabilities(self) -> List[str]:
        return ["verificar_disponibilidad", "crear_reserva",
                "cancelar_reserva", "obtener_reservas"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "reservations"}
