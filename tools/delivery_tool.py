"""Herramientas de delivery para LangGraph."""

from langchain_core.tools import tool
from skills.delivery.delivery_skill import DeliverySkill


_delivery_skill = DeliverySkill()
_delivery_skill.initialize({})


@tool
def calcular_costo_delivery(direccion: str) -> str:
    """Calcula el costo de envio a una direccion.

    Args:
        direccion: Direccion de entrega

    Returns:
        Costo y tiempo estimado
    """
    resultado = _delivery_skill.execute("calcular_costo", {"direccion": direccion})

    if not resultado.get("disponible"):
        return "Lo siento, no cubrimos esa zona de delivery."

    respuesta = f"Envio a {direccion}:\n"
    respuesta += f"- Zona: {resultado['zona']}\n"
    respuesta += f"- Costo: ${resultado['costo']:.2f}\n"
    respuesta += f"- Tiempo estimado: {resultado['tiempo_estimado_min']} minutos"

    return respuesta


@tool
def crear_envio_delivery(pedido_id: int, direccion: str, referencia: str = None) -> str:
    """Crea un envio de delivery para un pedido.

    Args:
        pedido_id: ID del pedido
        direccion: Direccion de entrega
        referencia: Referencia adicional

    Returns:
        Confirmacion del envio
    """
    costo_info = _delivery_skill.execute("calcular_costo", {"direccion": direccion})

    envio_id = _delivery_skill.execute("crear_envio", {
        "pedido_id": pedido_id,
        "direccion": direccion,
        "referencia": referencia,
        "zona": costo_info.get("zona"),
        "costo": costo_info.get("costo"),
        "tiempo_estimado": costo_info.get("tiempo_estimado_min")
    })

    return f"Envio creado. Tiempo estimado: {costo_info.get('tiempo_estimado_min')} minutos"


@tool
def rastrear_delivery(pedido_id: int) -> str:
    """Rastrea el estado de un delivery.

    Args:
        pedido_id: ID del pedido

    Returns:
        Estado del envio
    """
    estado = _delivery_skill.execute("obtener_estado", {"pedido_id": pedido_id})

    if not estado:
        return "No encontre informacion de envio para ese pedido."

    respuesta = f"Estado del envio: {estado['estado'].upper()}\n"
    respuesta += f"Direccion: {estado['direccion']}\n"

    if estado.get('repartidor'):
        respuesta += f"Repartidor: {estado['repartidor']}\n"

    respuesta += f"Tiempo estimado: {estado.get('tiempo_estimado', 'N/A')} minutos"

    return respuesta
