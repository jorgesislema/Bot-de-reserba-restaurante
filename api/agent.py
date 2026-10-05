"""Agente ReAct de LangGraph para restaurante."""

import os
from typing import Annotated, TypedDict, Optional
from datetime import datetime, timedelta

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from tools import (
    # Menu
    buscar_producto, obtener_detalle_producto, calcular_precio_pedido,
    verificar_disponibilidad_producto, recomendar_producto,
    # Orders
    crear_pedido, agregar_item_pedido, confirmar_pedido, cancelar_pedido,
    consultar_estado_pedido, consultar_pedido_cliente,
    # Reservations
    verificar_disponibilidad_reserva, crear_reserva, cancelar_reserva,
    # Delivery
    calcular_costo_delivery, crear_envio_delivery, rastrear_delivery,
    # Customers
    buscar_cliente, crear_cliente, obtener_historial_cliente, customer_360,
    # Channels
    enviar_mensaje_whatsapp, enviar_mensaje_telegram,
    # Analytics
    registrar_interaccion, obtener_metricas,
)


SYSTEM_PROMPT = """Eres un asistente virtual de La Terraza, un restaurante en Ecuador. Tu objetivo es ayudar a los clientes con:

1. **Consultar el menu**: precios, ingredientes, disponibilidad, personalizaciones
2. **Crear pedidos**: tomar pedidos completos con extras y tamanos
3. **Gestionar reservas**: verificar disponibilidad y crear reservas
4. **Delivery**: calcular costos y crear envios
5. **Atencion al cliente**: historial, preferencias, Customer 360

REGLAS IMPORTANTES:
- Los precios son calculados por el backend, NUNCA los inventes
- Maximo 1 sugerencia de upselling por pedido
- Horario: Lunes a Domingo 9am-10pm
- Zona horaria: Ecuador (UTC-5)
- Se amable y profesional
- Si no sabes algo, ofrece conectar con un humano

FLUJO DE PEDIDO:
1. Cliente pide algo -> buscar en menu
2. Ofrece opciones (tamano, extras)
3. Calcula precio real desde backend
4. Muestra resumen del pedido
5. Confirma y crea el pedido

FLUJO DE RESERVA:
1. Cliente quiere reservar -> verificar disponibilidad
2. Ofrece horarios disponibles
3. Pide nombre y telefono
4. Crea la reserva

IMPORTANTE: El LLM no es la fuente de verdad. El backend calcula precios, verifica disponibilidad y crea registros reales."""


tools = [
    # Menu
    buscar_producto, obtener_detalle_producto, calcular_precio_pedido,
    verificar_disponibilidad_producto, recomendar_producto,
    # Orders
    crear_pedido, agregar_item_pedido, confirmar_pedido, cancelar_pedido,
    consultar_estado_pedido, consultar_pedido_cliente,
    # Reservations
    verificar_disponibilidad_reserva, crear_reserva, cancelar_reserva,
    # Delivery
    calcular_costo_delivery, crear_envio_delivery, rastrear_delivery,
    # Customers
    buscar_cliente, crear_cliente, obtener_historial_cliente, customer_360,
    # Channels
    enviar_mensaje_whatsapp, enviar_mensaje_telegram,
    # Analytics
    registrar_interaccion, obtener_metricas,
]


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def create_agent():
    """Crea el agente ReAct con LangGraph."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    base_url = os.getenv("KILO_BASE_URL", "https://api.kilo.ai/v1")
    model_name = os.getenv("KILO_CHAT_MODEL", "nvidia/nemotron-3.5-lightning:free")

    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.7,
        max_tokens=1024
    )

    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState) -> dict:
        messages = state["messages"]
        system_message = {"role": "system", "content": SYSTEM_PROMPT}
        all_messages = [system_message] + messages
        response = llm_with_tools.invoke(all_messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)

    return app


app_graph = None


def get_agent():
    """Obtiene o crea la instancia del agente."""
    global app_graph
    if app_graph is None:
        app_graph = create_agent()
    return app_graph


def process_message(message: str, thread_id: str = "default", channel: str = "whatsapp") -> str:
    """Procesa un mensaje y retorna la respuesta.

    Args:
        message: Mensaje del cliente
        thread_id: ID del hilo (telefono del cliente)
        channel: Canal de origen (whatsapp, telegram, webchat)

    Returns:
        Respuesta del agente
    """
    try:
        agent = get_agent()

        # Configurar thread_id con canal
        config = {"configurable": {"thread_id": f"{channel}:{thread_id}"}}

        # Crear mensaje con contexto del canal
        input_message = HumanMessage(content=f"[Canal: {channel}] {message}")

        # Ejecutar agente
        result = agent.invoke(
            {"messages": [input_message]},
            config=config
        )

        # Obtener ultima respuesta
        ai_message = result["messages"][-1]

        return ai_message.content

    except Exception as e:
        return "Disculpa, tuve un problema procesando tu mensaje. Puedes intentar de nuevo?"
