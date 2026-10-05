# PROMPT 09: tools/ - Herramientas LangGraph del Restaurante

## Objetivo
Crear todas las herramientas de LangGraph que el agente ReAct utilizará para interactuar con el sistema del restaurante.

## Instrucciones Detalladas

Crear los siguientes archivos en `tools/`:

```
tools/
├── __init__.py
├── menu_tool.py
├── order_tool.py
├── reservation_tool.py
├── delivery_tool.py
├── customer_tool.py
├── channel_tool.py
└── analytics_tool.py
```

### menu_tool.py

```python
"""Herramientas de menú para LangGraph."""

from langchain_core.tools import tool
from skills.menu.menu_skill import MenuSkill


_menu_skill = MenuSkill()
_menu_skill.initialize({})


@tool
def buscar_producto(query: str) -> str:
    """Busca productos en el menú por nombre o ingrediente.
    
    Args:
        query: Término de búsqueda (nombre, ingrediente, categoría)
    
    Returns:
        Lista de productos encontrados con precios
    """
    resultados = _menu_skill.execute("buscar", {"query": query})
    
    if not resultados:
        return "No encontré productos con esa búsqueda."
    
    respuesta = "Encontré estos productos:\n\n"
    for p in resultados:
        respuesta += f"• {p['nombre']} - ${p['precio']:.2f}"
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
        return "No encontré ese producto."
    
    respuesta = f"**{producto['nombre']}**\n"
    respuesta += f"{producto['descripcion']}\n\n"
    respuesta += f"Precio base: ${producto['precio']:.2f}\n"
    
    if producto.get('ingredientes'):
        respuesta += f"Ingredientes: {', '.join(producto['ingredientes'])}\n"
    
    if producto.get('opciones'):
        respuesta += "\nOpciones disponibles:\n"
        for op in producto['opciones']:
            precio_str = f" (+${op['precio']:.2f})" if op['precio'] > 0 else ""
            respuesta += f"  • {op['tipo']}: {op['nombre']}{precio_str}\n"
    
    return respuesta


@tool
def calcular_precio_pedido(producto_id: int, tamano: str = None, extras: str = None) -> str:
    """Calcula el precio de un producto con sus opciones.
    
    Args:
        producto_id: ID del producto
        tamano: Tamaño seleccionado (personal, mediana, familiar)
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
    """Verifica si un producto está disponible.
    
    Args:
        producto_id: ID del producto
    
    Returns:
        Estado de disponibilidad
    """
    disponible = _menu_skill.execute("verificar_disponibilidad", {"producto_id": producto_id})
    
    if disponible:
        return "✓ Producto disponible"
    else:
        return "✗ Producto no disponible en este momento"


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
        return "No tengo recomendaciones específicas en este momento."
    
    respuesta = "Te recomiendo estas opciones:\n\n"
    for p in recomendaciones:
        respuesta += f"• {p['nombre']} — ${p['precio']:.2f}\n"
    
    return respuesta
```

### order_tool.py

```python
"""Herramientas de pedidos para LangGraph."""

from langchain_core.tools import tool
from skills.orders.order_skill import OrderSkill


_order_skill = OrderSkill()
_order_skill.initialize({})


@tool
def crear_pedido(cliente_id: int, canal: str = "whatsapp") -> str:
    """Crea un nuevo pedido para un cliente.
    
    Args:
        cliente_id: ID del cliente
        canal: Canal de origen (whatsapp, telegram, webchat)
    
    Returns:
        Confirmación con número de pedido
    """
    pedido_id = _order_skill.execute("crear_pedido", {
        "cliente_id": cliente_id,
        "canal": canal
    })
    
    pedido = _order_skill.execute("obtener_pedido", {"pedido_id": pedido_id})
    
    return f"Pedido creado: {pedido['numero']}"


@tool
def agregar_item_pedido(pedido_id: int, producto_id: int, cantidad: int = 1, tamano: str = None, extras: str = None) -> str:
    """Agrega un producto al pedido.
    
    Args:
        pedido_id: ID del pedido
        producto_id: ID del producto
        cantidad: Cantidad (default: 1)
        tamano: Tamaño del producto
        extras: Extras separados por coma
    
    Returns:
        Confirmación del item agregado
    """
    opciones = {}
    if tamano:
        opciones["tamano"] = tamano
    if extras:
        opciones["extras"] = [e.strip() for e in extras.split(",")]
    
    exito = _order_skill.execute("agregar_item", {
        "pedido_id": pedido_id,
        "producto_id": producto_id,
        "cantidad": cantidad,
        "opciones": opciones
    })
    
    if exito:
        total = _order_skill.execute("calcular_total", {"pedido_id": pedido_id})
        return f"✓ Item agregado. Total del pedido: ${total:.2f}"
    else:
        return "No pude agregar el item. Verifica el estado del pedido."


@tool
def confirmar_pedido(pedido_id: int) -> str:
    """Confirma un pedido para preparación.
    
    Args:
        pedido_id: ID del pedido
    
    Returns:
        Confirmación del pedido
    """
    exito = _order_skill.execute("confirmar_pedido", {"pedido_id": pedido_id})
    
    if exito:
        pedido = _order_skill.execute("obtener_pedido", {"pedido_id": pedido_id})
        return f"✓ Pedido {pedido['numero']} confirmado. Total: ${pedido['total']:.2f}"
    else:
        return "No pude confirmar el pedido."


@tool
def cancelar_pedido(pedido_id: int, motivo: str = "Cancelado por cliente") -> str:
    """Cancela un pedido.
    
    Args:
        pedido_id: ID del pedido
        motivo: Motivo de la cancelación
    
    Returns:
        Confirmación de cancelación
    """
    exito = _order_skill.execute("cancelar_pedido", {
        "pedido_id": pedido_id,
        "motivo": motivo
    })
    
    if exito:
        return "✓ Pedido cancelado correctamente."
    else:
        return "No pude cancelar el pedido. Puede que ya esté en preparación."


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
        return "No encontré ese pedido."
    
    estado_emoji = {
        "draft": "📝",
        "confirmed": "✓",
        "paid": "💰",
        "preparing": "🍳",
        "ready": "🟢",
        "delivering": "🚚",
        "completed": "✅",
        "cancelled": "❌"
    }
    
    emoji = estado_emoji.get(pedido['estado'], "❓")
    
    respuesta = f"Pedido {pedido['numero']}\n"
    respuesta += f"Estado: {emoji} {pedido['estado'].upper()}\n"
    respuesta += f"Total: ${pedido['total']:.2f}\n\n"
    respuesta += "Items:\n"
    
    for item in pedido['items']:
        respuesta += f"  {item['cantidad']}x {item['producto']} - ${item['precio_total']:.2f}\n"
    
    return respuesta


@tool
def consultar_pedido_cliente(cliente_id: int) -> str:
    """Consulta el último pedido de un cliente.
    
    Args:
        cliente_id: ID del cliente
    
    Returns:
        Información del último pedido
    """
    historial = _order_skill.execute("obtener_historial", {"cliente_id": cliente_id})
    
    if not historial or not historial.get("pedidos"):
        return "No tienes pedidos recientes."
    
    ultimo = historial["pedidos"][0]
    
    return f"Tu último pedido fue {ultimo['numero']} por ${ultimo['total']:.2f} el {ultimo['fecha']}"
```

### reservation_tool.py

```python
"""Herramientas de reservas para LangGraph."""

from langchain_core.tools import tool
from skills.reservations.reservation_skill import ReservationSkill


_reservation_skill = ReservationSkill()
_reservation_skill.initialize({})


@tool
def verificar_disponibilidad_reserva(fecha: str, personas: int, hora_preferida: str = None) -> str:
    """Verifica disponibilidad de mesas para una reserva.
    
    Args:
        fecha: Fecha de la reserva (YYYY-MM-DD)
        personas: Número de personas
        hora_preferida: Hora preferida (HH:MM) - opcional
    
    Returns:
        Horarios disponibles
    """
    disponibilidad = _reservation_skill.execute("verificar_disponibilidad", {
        "fecha": fecha,
        "hora": hora_preferida,
        "personas": personas
    })
    
    if not disponibilidad:
        return "No tengo disponibilidad para esa fecha y hora."
    
    respuesta = f"Para {personas} personas el {fecha} tengo disponibilidad:\n\n"
    for slot in disponibilidad:
        respuesta += f"• {slot['hora']}\n"
    
    respuesta += "\n¿Cuál prefieres?"
    
    return respuesta


@tool
def crear_reserva(fecha: str, hora: str, personas: int, nombre: str, telefono: str, preferencias: str = None) -> str:
    """Crea una reserva en el restaurante.
    
    Args:
        fecha: Fecha de la reserva (YYYY-MM-DD)
        hora: Hora de la reserva (HH:MM)
        personas: Número de personas
        nombre: Nombre del contacto
        telefono: Teléfono de contacto
        preferencias: Preferencias (terraza, interior, privado)
    
    Returns:
        Confirmación de la reserva
    """
    prefs = {}
    if preferencias:
        for pref in preferencias.split(","):
            prefs[pref.strip()] = True
    
    reserva_id = _reservation_skill.execute("crear_reserva", {
        "fecha": fecha,
        "hora": hora,
        "personas": personas,
        "nombre_contacto": nombre,
        "telefono": telefono,
        "preferencias": prefs
    })
    
    return f"✓ Reserva confirmada para {personas} personas el {fecha} a las {hora}. A nombre de {nombre}."


@tool
def cancelar_reserva(reserva_id: int, motivo: str = None) -> str:
    """Cancela una reserva.
    
    Args:
        reserva_id: ID de la reserva
        motivo: Motivo de cancelación
    
    Returns:
        Confirmación de cancelación
    """
    exito = _reservation_skill.execute("cancelar_reserva", {
        "reserva_id": reserva_id,
        "motivo": motivo
    })
    
    if exito:
        return "✓ Reserva cancelada correctamente."
    else:
        return "No pude cancelar la reserva."
```

### delivery_tool.py

```python
"""Herramientas de delivery para LangGraph."""

from langchain_core.tools import tool
from skills.delivery.delivery_skill import DeliverySkill


_delivery_skill = DeliverySkill()
_delivery_skill.initialize({})


@tool
def calcular_costo_delivery(direccion: str) -> str:
    """Calcula el costo de envío a una dirección.
    
    Args:
        direccion: Dirección de entrega
    
    Returns:
        Costo y tiempo estimado
    """
    resultado = _delivery_skill.execute("calcular_costo", {"direccion": direccion})
    
    if not resultado.get("disponible"):
        return "Lo siento, no cubrimos esa zona de delivery."
    
    respuesta = f"Envío a {direccion}:\n"
    respuesta += f"• Zona: {resultado['zona']}\n"
    respuesta += f"• Costo: ${resultado['costo']:.2f}\n"
    respuesta += f"• Tiempo estimado: {resultado['tiempo_estimado_min']} minutos"
    
    return respuesta


@tool
def crear_envio_delivery(pedido_id: int, direccion: str, referencia: str = None) -> str:
    """Crea un envío de delivery para un pedido.
    
    Args:
        pedido_id: ID del pedido
        direccion: Dirección de entrega
        referencia: Referencia adicional
    
    Returns:
        Confirmación del envío
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
    
    return f"✓ Envío creado. Tiempo estimado: {costo_info.get('tiempo_estimado_min')} minutos"


@tool
def rastrear_delivery(pedido_id: int) -> str:
    """Rastrea el estado de un delivery.
    
    Args:
        pedido_id: ID del pedido
    
    Returns:
        Estado del envío
    """
    estado = _delivery_skill.execute("obtener_estado", {"pedido_id": pedido_id})
    
    if not estado:
        return "No encontré información de envío para ese pedido."
    
    estado_emoji = {
        "pending": "⏳",
        "assigned": "👤",
        "picking_up": "📍",
        "in_transit": "🚚",
        "delivered": "✅",
        "cancelled": "❌"
    }
    
    emoji = estado_emoji.get(estado['estado'], "❓")
    
    respuesta = f"Estado del envío: {emoji} {estado['estado'].upper()}\n"
    respuesta += f"Dirección: {estado['direccion']}\n"
    
    if estado.get('repartidor'):
        respuesta += f"Repartidor: {estado['repartidor']}\n"
    
    respuesta += f"Tiempo estimado: {estado.get('tiempo_estimado', 'N/A')} minutos"
    
    return respuesta
```

### customer_tool.py

```python
"""Herramientas de clientes para LangGraph."""

from langchain_core.tools import tool
from skills.customers.customer_skill import CustomerSkill


_customer_skill = CustomerSkill()
_customer_skill.initialize({})


@tool
def buscar_cliente(telefono: str) -> str:
    """Busca un cliente por teléfono.
    
    Args:
        telefono: Número de teléfono del cliente
    
    Returns:
        Información del cliente o indicación de crear uno nuevo
    """
    cliente = _customer_skill.execute("obtener_cliente", {"telefono": telefono})
    
    if not cliente:
        return f"Cliente no encontrado con el teléfono {telefono}. ¿Deseas crear un nuevo cliente?"
    
    respuesta = f"Cliente: {cliente['nombre']}\n"
    respuesta += f"Pedidos totales: {cliente['total_pedidos']}\n"
    respuesta += f"Segmento: {cliente.get('segmento', 'nuevo')}"
    
    return respuesta


@tool
def crear_cliente(nombre: str, telefono: str, email: str = None, canal: str = "whatsapp") -> str:
    """Crea un nuevo cliente.
    
    Args:
        nombre: Nombre completo del cliente
        telefono: Número de teléfono
        email: Email (opcional)
        canal: Canal preferido
    
    Returns:
        Confirmación de creación
    """
    cliente_id = _customer_skill.execute("crear_cliente", {
        "nombre": nombre,
        "telefono": telefono,
        "email": email,
        "canal": canal
    })
    
    return f"✓ Cliente {nombre} registrado correctamente."


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
        respuesta += "Últimos pedidos:\n"
        for p in historial["pedidos"][:5]:
            respuesta += f"  • {p['numero']} - ${p['total']:.2f} ({p['estado']})\n"
    
    if historial.get("reservas"):
        respuesta += "\nÚltimas reservas:\n"
        for r in historial["reservas"][:3]:
            respuesta += f"  • {r['fecha']} {r['hora']} - {r['personas']} personas ({r['estado']})\n"
    
    return respuesta


@tool
def customer_360(cliente_id: int) -> str:
    """Obtiene vista completa 360° de un cliente.
    
    Args:
        cliente_id: ID del cliente
    
    Returns:
        Customer 360 completo
    """
    cliente = _customer_skill.execute("obtener_cliente", {"telefono": ""})
    historial = _customer_skill.execute("obtener_historial", {"cliente_id": cliente_id})
    
    if not cliente:
        return "No encontré información del cliente."
    
    respuesta = f"**Customer 360 - {cliente['nombre']}**\n\n"
    respuesta += f"Cliente desde: {cliente.get('fecha_registro', 'N/A')}\n"
    respuesta += f"Pedidos: {cliente['total_pedidos']}\n"
    respuesta += f"Valor acumulado: ${cliente['valor_acumulado']:.2f}\n"
    respuesta += f"Segmento: {cliente.get('segmento', 'nuevo')}\n"
    respuesta += f"Frecuencia: {cliente.get('frecuencia', 0)} pedidos/mes"
    
    return respuesta
```

### channel_tool.py

```python
"""Herramientas de canales para LangGraph."""

from langchain_core.tools import tool
from skills.channels.channel_skill import ChannelSkill


_channel_skill = ChannelSkill()
_channel_skill.initialize({})


@tool
def enviar_mensaje_whatsapp(numero: str, mensaje: str) -> str:
    """Envía un mensaje por WhatsApp.
    
    Args:
        numero: Número de teléfono del destinatario
        mensaje: Mensaje a enviar
    
    Returns:
        Estado del envío
    """
    exito = _channel_skill.execute("enviar_respuesta", {
        "channel": "whatsapp",
        "to": numero,
        "message": mensaje
    })
    
    if exito:
        return "✓ Mensaje enviado por WhatsApp."
    else:
        return "No pude enviar el mensaje por WhatsApp."


@tool
def enviar_mensaje_telegram(chat_id: str, mensaje: str) -> str:
    """Envía un mensaje por Telegram.
    
    Args:
        chat_id: ID del chat de Telegram
        mensaje: Mensaje a enviar
    
    Returns:
        Estado del envío
    """
    exito = _channel_skill.execute("enviar_respuesta", {
        "channel": "telegram",
        "to": chat_id,
        "message": mensaje
    })
    
    if exito:
        return "✓ Mensaje enviado por Telegram."
    else:
        return "No pude enviar el mensaje por Telegram."
```

### analytics_tool.py

```python
"""Herramientas de analytics para LangGraph."""

from langchain_core.tools import tool
from skills.analytics.analytics_skill import AnalyticsSkill


_analytics_skill = AnalyticsSkill()
_analytics_skill.initialize({})


@tool
def registrar_interaccion(tipo: str, intencion: str, canal: str = "whatsapp", resuelto_por_ia: bool = True, confidence: float = 0.9) -> str:
    """Registra una interacción para analytics.
    
    Args:
        tipo: Tipo de interacción (mensaje, pedido, reserva)
        intencion: Intención detectada (menu, pedido, reserva, delivery)
        canal: Canal de origen
        resuelto_por_ia: Si fue resuelto por IA
        confidence: Nivel de confianza
    
    Returns:
        Confirmación del registro
    """
    _analytics_skill.execute("registrar_interaccion", {
        "tipo": tipo,
        "intencion": intencion,
        "canal": canal,
        "resuelto_por_ia": resuelto_por_ia,
        "confidence": confidence
    })
    
    return "✓ Interacción registrada."


@tool
def obtener_metricas() -> str:
    """Obtiene las métricas generales del restaurante.
    
    Returns:
        Métricas del día
    """
    metricas = _analytics_skill.execute("obtener_metricas", {})
    
    respuesta = "**Métricas de Hoy**\n\n"
    respuesta += f"Conversaciones: {metricas.get('conversaciones_hoy', 0)}\n"
    respuesta += f"Pedidos: {metricas.get('pedidos_hoy', 0)}\n"
    respuesta += f"Reservas: {metricas.get('reservas_hoy', 0)}\n"
    respuesta += f"Ventas: ${metricas.get('ventas_hoy', 0):.2f}"
    
    return respuesta
```

### __init__.py

```python
"""Tools para Restaurant AI Platform."""

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
```

## Verificación
- [ ] Todas las herramientas creadas y decoradas con @tool
- [ ] Integración con skills funcional
- [ ] Manejo adecuado de errores
- [ ] Documentación completa de Args
- [ ] Tests unitarios para cada herramienta (>90% coverage)
