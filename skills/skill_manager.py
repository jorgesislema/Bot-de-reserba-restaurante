"""Gestor de skills del restaurante."""

from typing import Dict, Any, Optional, List
from skills.base_skill import BaseSkill


class SkillManager:
    """Administra todas las skills del sistema."""

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}

    def register(self, name: str, skill: BaseSkill) -> None:
        """Registra una skill."""
        self._skills[name] = skill

    def get(self, name: str) -> Optional[BaseSkill]:
        """Obtiene una skill por nombre."""
        return self._skills.get(name)

    def execute(self, skill_name: str, action: str, params: Dict = None) -> Any:
        """Ejecuta una accion de una skill."""
        skill = self.get(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")
        return skill.execute(action, params)

    def list_skills(self) -> Dict[str, List[str]]:
        """Lista todas las skills y sus capacidades."""
        return {
            name: skill.get_capabilities()
            for name, skill in self._skills.items()
        }

    def health_check(self) -> Dict[str, Any]:
        """Verifica salud de todas las skills."""
        return {
            name: skill.health_check()
            for name, skill in self._skills.items()
        }
