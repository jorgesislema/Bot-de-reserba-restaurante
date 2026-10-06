"""Herramientas de pedidos para LangGraph."""

import logging

from langchain_core.tools import tool
from skills.orders.order_skill import OrderSkill

logger = logging.getLogger(__name__)

_order_skill = OrderSkill()
_order_skill.initialize({})


@tool
def crear_pedido(cliente_id: int, canal: str = "whatsapp") -> str:
    """Crea un nuevo pedido para un cliente.

    Args:
        cliente_id: ID del cliente
        canal: Canal de origen (whatsapp, telegram, webchat)

    Returns:
        Confirmacion con numero de pedido
    """
    try:
        pedido_id = _order_skill.execute("crear_pedido", {
            "cliente_id": cliente_id,
            "canal": canal
        })
        pedido = _order_skill.execute("obtener_pedido", {"pedido_id": pedido_id})
    except ValueError as e:
        return f"No pude crear el pedido: {e}"
    except Exception:
        logger.exception("Error creando pedido cliente_id=%s", cliente_id)
        return "No pude crear el pedido en este momento."

    return f"Pedido creado: {pedido['numero']}"


@tool
def agregar_item_pedido(pedido_id: int, producto_id: int, cantidad: int = 1, tamano: str = None, extras: str = None) -> str:
    """Agrega un producto al pedido.

    Args:
        pedido_id: ID del pedido
        producto_id: ID del producto
        cantidad: Cantidad (default: 1)
        tamano: Tamano del producto
        extras: Extras separados por coma

    Returns:
        Confirmacion del item agregado
    """
    opciones = {}
    if tamano:
        opciones["tamano"] = tamano
    if extras:
        opciones["extras"] = [e.strip() for e in extras.split(",")]

    try:
        exito = _order_skill.execute("agregar_item", {
            "pedido_id": pedido_id,
            "producto_id": producto_id,
            "cantidad": cantidad,
            "opciones": opciones
        })
    except ValueError as e:
        return f"No pude agregar el item: {e}"
    except Exception:
        logger.exception(
            "Error agregando item pedido=%s producto=%s", pedido_id, producto_id
        )
        return "No pude agregar el item en este momento."

    if exito:
        total = _order_skill.execute("calcular_total", {"pedido_id": pedido_id})
        return f"Item agregado. Total del pedido: ${total:.2f}"
    else:
        return "No pude agregar el item. Verifica el estado del pedido."


@tool
def confirmar_pedido(pedido_id: int) -> str:
    """Confirma un pedido para preparacion.

    Args:
        pedido_id: ID del pedido

    Returns:
        Confirmacion del pedido
    """
    exito = _order_skill.execute("confirmar_pedido", {"pedido_id": pedido_id})

    if exito:
        pedido = _order_skill.execute("obtener_pedido", {"pedido_id": pedido_id})
        return f"Pedido {pedido['numero']} confirmado. Total: ${pedido['total']:.2f}"
    else:
        return "No pude confirmar el pedido."


@tool
def cancelar_pedido(pedido_id: int, motivo: str = "Cancelado por cliente") -> str:
    """Cancela un pedido.

    Args:
        pedido_id: ID del pedido
        motivo: Motivo de la cancelacion

    Returns:
        Confirmacion de cancelacion
    """
    exito = _order_skill.execute("cancelar_pedido", {
        "pedido_id": pedido_id,
        "motivo": motivo
    })

    if exito:
        return "Pedido cancelado correctamente."
    else:
        return "No pude cancelar el pedido. Puede que ya este en preparacion."


@tool
def consultar_estado_pedido(pedido_id: int) -> str:
    """Consulta el estado actual de un pedido.

    Args:
        pedido_id: ID del pedido

    Returns:
        Estado del pedido con detalles
    """
    pedido = _order_skill.execute("obtener_pedido", {"pedido_id": pedido_id})

    if not pedido:
        return "No encontre ese pedido."

    respuesta = f"Pedido {pedido['numero']}\n"
    respuesta += f"Estado: {pedido['estado'].upper()}\n"
    respuesta += f"Total: ${pedido['total']:.2f}\n\n"
    respuesta += "Items:\n"

    for item in pedido['items']:
        respuesta += f"  {item['cantidad']}x {item['producto']} - ${item['precio_total']:.2f}\n"

    return respuesta


@tool
def consultar_pedido_cliente(cliente_id: int) -> str:
    """Consulta el ultimo pedido de un cliente.

    Args:
        cliente_id: ID del cliente

    Returns:
        Informacion del ultimo pedido
    """
    historial = _order_skill.execute("obtener_historial", {"cliente_id": cliente_id})

    if not historial or not historial.get("pedidos"):
        return "No tienes pedidos recientes."

    ultimo = historial["pedidos"][0]

    return f"Tu ultimo pedido fue {ultimo['numero']} por ${ultimo['total']:.2f} el {ultimo['fecha']}"
