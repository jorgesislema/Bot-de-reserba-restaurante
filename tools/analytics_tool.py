"""Herramientas de analytics para LangGraph."""

from langchain_core.tools import tool
from skills.analytics.analytics_skill import AnalyticsSkill


_analytics_skill = AnalyticsSkill()
_analytics_skill.initialize({})


@tool
def registrar_interaccion(tipo: str, intencion: str, canal: str = "whatsapp", resuelto_por_ia: bool = True, confidence: float = 0.9) -> str:
    """Registra una interaccion para analytics.

    Args:
        tipo: Tipo de interaccion (mensaje, pedido, reserva)
        intencion: Intencion detectada (menu, pedido, reserva, delivery)
        canal: Canal de origen
        resuelto_por_ia: Si fue resuelto por IA
        confidence: Nivel de confianza

    Returns:
        Confirmacion del registro
    """
    _analytics_skill.execute("registrar_interaccion", {
        "tipo": tipo,
        "intencion": intencion,
        "canal": canal,
        "resuelto_por_ia": resuelto_por_ia,
        "confidence": confidence
    })

    return "Interaccion registrada."


@tool
def obtener_metricas() -> str:
    """Obtiene las metricas generales del restaurante.

    Returns:
        Metricas del dia
    """
    metricas = _analytics_skill.execute("obtener_metricas", {})

    respuesta = "**Metricas de Hoy**\n\n"
    respuesta += f"Conversaciones: {metricas.get('conversaciones_hoy', 0)}\n"
    respuesta += f"Pedidos: {metricas.get('pedidos_hoy', 0)}\n"
    respuesta += f"Reservas: {metricas.get('reservas_hoy', 0)}\n"
    respuesta += f"Ventas: ${metricas.get('ventas_hoy', 0):.2f}"

    return respuesta
