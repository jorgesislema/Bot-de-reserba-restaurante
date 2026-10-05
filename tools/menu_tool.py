"""Herramientas de menu para LangGraph."""

from langchain_core.tools import tool
from skills.menu.menu_skill import MenuSkill


_menu_skill = MenuSkill()
_menu_skill.initialize({})


@tool
def buscar_producto(query: str) -> str:
    """Busca productos en el menu por nombre o ingrediente.

    Args:
        query: Termino de busqueda (nombre, ingrediente, categoria)

    Returns:
        Lista de productos encontrados con precios
    """
    resultados = _menu_skill.execute("buscar", {"query": query})

    if not resultados:
        return "No encontre productos con esa busqueda."

    respuesta = "Encontre estos productos:\n\n"
    for p in resultados:
        respuesta += f"- {p['nombre']} - ${p['precio']:.2f}"
        if p.get('categoria'):
            respuesta += f" ({p['categoria']})"
        respuesta += "\n"

    return respuesta


@tool
def obtener_detalle_producto(producto_id: int) -> str:
    """Obtiene el detalle completo de un producto incluyendo opciones y precios.

    Args:
        producto_id: ID del producto a consultar

    Returns:
        Detalle del producto con opciones disponibles
    """
    producto = _menu_skill.execute("obtener_producto", {"producto_id": producto_id})

    if not producto:
        return "No encontre ese producto."

    respuesta = f"**{producto['nombre']}**\n"
    respuesta += f"{producto['descripcion']}\n\n"
    respuesta += f"Precio base: ${producto['precio']:.2f}\n"

    if producto.get('ingredientes'):
        respuesta += f"Ingredientes: {', '.join(producto['ingredientes'])}\n"

    if producto.get('opciones'):
        respuesta += "\nOpciones disponibles:\n"
        for op in producto['opciones']:
            precio_str = f" (+${op['precio']:.2f})" if op['precio'] > 0 else ""
            respuesta += f"  - {op['tipo']}: {op['nombre']}{precio_str}\n"

    return respuesta


@tool
def calcular_precio_pedido(producto_id: int, tamano: str = None, extras: str = None) -> str:
    """Calcula el precio de un producto con sus opciones.

    Args:
        producto_id: ID del producto
        tamano: Tamano seleccionado (personal, mediana, familiar)
        extras: Extras seleccionados separados por coma

    Returns:
        Precio total calculado
    """
    opciones = {}
    if tamano:
        opciones["tamano"] = tamano
    if extras:
        opciones["extras"] = [e.strip() for e in extras.split(",")]

    precio = _menu_skill.execute("calcular_precio", {
        "producto_id": producto_id,
        "opciones": opciones
    })

    return f"El precio total es: ${precio:.2f}"


@tool
def verificar_disponibilidad_producto(producto_id: int) -> str:
    """Verifica si un producto esta disponible.

    Args:
        producto_id: ID del producto

    Returns:
        Estado de disponibilidad
    """
    disponible = _menu_skill.execute("verificar_disponibilidad", {"producto_id": producto_id})

    if disponible:
        return "Producto disponible"
    else:
        return "Producto no disponible en este momento"


@tool
def recomendar_producto(preferencias: str = None) -> str:
    """Recomienda productos basado en preferencias.

    Args:
        preferencias: Preferencias del cliente (ej: "pollo, no picante, familiar")

    Returns:
        Lista de recomendaciones
    """
    recomendaciones = _menu_skill.execute("recomendar", {"preferencias": preferencias})

    if not recomendaciones:
        return "No tengo recomendaciones especificas en este momento."

    respuesta = "Te recomiendo estas opciones:\n\n"
    for p in recomendaciones:
        respuesta += f"- {p['nombre']} -- ${p['precio']:.2f}\n"

    return respuesta
