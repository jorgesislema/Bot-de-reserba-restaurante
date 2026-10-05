"""Herramientas de clientes para LangGraph."""

from langchain_core.tools import tool
from skills.customers.customer_skill import CustomerSkill


_customer_skill = CustomerSkill()
_customer_skill.initialize({})


@tool
def buscar_cliente(telefono: str) -> str:
    """Busca un cliente por telefono.

    Args:
        telefono: Numero de telefono del cliente

    Returns:
        Informacion del cliente o indicacion de crear uno nuevo
    """
    cliente = _customer_skill.execute("obtener_cliente", {"telefono": telefono})

    if not cliente:
        return f"Cliente no encontrado con el telefono {telefono}. Deseas crear un nuevo cliente?"

    respuesta = f"Cliente: {cliente['nombre']}\n"
    respuesta += f"Pedidos totales: {cliente['total_pedidos']}\n"
    respuesta += f"Segmento: {cliente.get('segmento', 'nuevo')}"

    return respuesta


@tool
def crear_cliente(nombre: str, telefono: str, email: str = None, canal: str = "whatsapp") -> str:
    """Crea un nuevo cliente.

    Args:
        nombre: Nombre completo del cliente
        telefono: Numero de telefono
        email: Email (opcional)
        canal: Canal preferido

    Returns:
        Confirmacion de creacion
    """
    cliente_id = _customer_skill.execute("crear_cliente", {
        "nombre": nombre,
        "telefono": telefono,
        "email": email,
        "canal": canal
    })

    return f"Cliente {nombre} registrado correctamente."


@tool
def obtener_historial_cliente(cliente_id: int) -> str:
    """Obtiene el historial de pedidos y reservas de un cliente.

    Args:
        cliente_id: ID del cliente

    Returns:
        Resumen del historial
    """
    historial = _customer_skill.execute("obtener_historial", {"cliente_id": cliente_id})

    if not historial:
        return "No hay historial para este cliente."

    respuesta = "Tu historial:\n\n"

    if historial.get("pedidos"):
        respuesta += "Ultimos pedidos:\n"
        for p in historial["pedidos"][:5]:
            respuesta += f"  - {p['numero']} - ${p['total']:.2f} ({p['estado']})\n"

    if historial.get("reservas"):
        respuesta += "\nUltimas reservas:\n"
        for r in historial["reservas"][:3]:
            respuesta += f"  - {r['fecha']} {r['hora']} - {r['personas']} personas ({r['estado']})\n"

    return respuesta


@tool
def customer_360(cliente_id: int) -> str:
    """Obtiene vista completa 360 de un cliente.

    Args:
        cliente_id: ID del cliente

    Returns:
        Customer 360 completo
    """
    cliente = _customer_skill.execute("obtener_cliente", {"telefono": ""})
    historial = _customer_skill.execute("obtener_historial", {"cliente_id": cliente_id})

    if not cliente:
        return "No encontre informacion del cliente."

    respuesta = f"**Customer 360 - {cliente['nombre']}**\n\n"
    respuesta += f"Cliente desde: {cliente.get('fecha_registro', 'N/A')}\n"
    respuesta += f"Pedidos: {cliente['total_pedidos']}\n"
    respuesta += f"Valor acumulado: ${cliente['valor_acumulado']:.2f}\n"
    respuesta += f"Segmento: {cliente.get('segmento', 'nuevo')}\n"
    respuesta += f"Frecuencia: {cliente.get('frecuencia', 0)} pedidos/mes"

    return respuesta
