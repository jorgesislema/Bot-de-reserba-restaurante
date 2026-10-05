"""Clase base abstracta para todas las skills."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseSkill(ABC):
    """Interfaz base para todas las skills."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa la skill con configuracion. Retorna True si OK."""
        pass

    @abstractmethod
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Ejecuta una accion especifica de la skill."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retorna lista de acciones disponibles."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Retorna estado de salud de la skill."""
        pass
