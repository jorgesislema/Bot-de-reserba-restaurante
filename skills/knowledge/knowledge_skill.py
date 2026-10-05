"""Skill de conocimiento (RAG) del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill


class KnowledgeSkill(BaseSkill):
    """Skill para RAG sobre menu y politicas."""

    def initialize(self, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}

        actions = {
            "buscar_conocimiento": self._buscar_conocimiento,
        }

        return actions[action](params)

    def _buscar_conocimiento(self, params: Dict) -> List[Dict]:
        return []

    def get_capabilities(self) -> List[str]:
        return ["buscar_conocimiento"]

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "knowledge"}
