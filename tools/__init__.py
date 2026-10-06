"""Tools for Restaurant AI Platform."""

from tools.menu_tool import (
    buscar_producto,
    obtener_detalle_producto,
    calcular_precio_pedido,
    verificar_disponibilidad_producto,
    recomendar_producto,
)
from tools.order_tool import (
    crear_pedido,
    agregar_item_pedido,
    confirmar_pedido,
    cancelar_pedido,
    consultar_estado_pedido,
    consultar_pedido_cliente,
)
from tools.reservation_tool import (
    verificar_disponibilidad_reserva,
    crear_reserva,
    cancelar_reserva,
)
from tools.delivery_tool import (
    calcular_costo_delivery,
    crear_envio_delivery,
    rastrear_delivery,
)
from tools.customer_tool import (
    buscar_cliente,
    crear_cliente,
    obtener_historial_cliente,
    customer_360,
)
from tools.channel_tool import (
    enviar_mensaje_whatsapp,
    enviar_mensaje_telegram,
)
from tools.analytics_tool import (
    registrar_interaccion,
    obtener_metricas,
)

__all__ = [
    # Menu
    "buscar_producto",
    "obtener_detalle_producto",
    "calcular_precio_pedido",
    "verificar_disponibilidad_producto",
    "recomendar_producto",
    # Orders
    "crear_pedido",
    "agregar_item_pedido",
    "confirmar_pedido",
    "cancelar_pedido",
    "consultar_estado_pedido",
    "consultar_pedido_cliente",
    # Reservations
    "verificar_disponibilidad_reserva",
    "crear_reserva",
    "cancelar_reserva",
    # Delivery
    "calcular_costo_delivery",
    "crear_envio_delivery",
    "rastrear_delivery",
    # Customers
    "buscar_cliente",
    "crear_cliente",
    "obtener_historial_cliente",
    "customer_360",
    # Channels
    "enviar_mensaje_whatsapp",
    "enviar_mensaje_telegram",
    # Analytics
    "registrar_interaccion",
    "obtener_metricas",
]

ALL_TOOL_NAMES = list(__all__)
