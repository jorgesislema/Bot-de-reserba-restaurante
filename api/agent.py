"""Agente ReAct de LangGraph para restaurante."""

import json
import logging
import os
import re
import unicodedata
from typing import Annotated, TypedDict, Optional, List, Dict, Any

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, ToolMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

from tools import (
    # Menu (READ)
    buscar_producto, obtener_detalle_producto, calcular_precio_pedido,
    verificar_disponibilidad_producto, recomendar_producto,    # Orders (WRITE / READ)
    crear_pedido, agregar_item_pedido, confirmar_pedido, cancelar_pedido,
    consultar_estado_pedido, consultar_pedido_cliente,
    # Reservations (WRITE / READ)
    verificar_disponibilidad_reserva, crear_reserva, cancelar_reserva,
    # Delivery (WRITE / READ)
    calcular_costo_delivery, crear_envio_delivery, rastrear_delivery,
    # Customers (READ / WRITE)
    buscar_cliente, crear_cliente, obtener_historial_cliente, customer_360,
    # Channels (SIDE EFFECT)
    enviar_mensaje_whatsapp, enviar_mensaje_telegram,
    # Analytics (READ / WRITE)
    registrar_interaccion, obtener_metricas,
)
from tools import autorizacion

logger = logging.getLogger(__name__)

# Cargar .env tambien al importar el agente directamente (tests, scripts)
load_dotenv()


# ===========================================
# CLASIFICACION DE TOOLS
# ===========================================
# READ: solo leen datos del backend (seguras)
# WRITE: crean/modifican registros (requieren confirmacion)
# SIDE EFFECT: acciones externas con consecuencias reales (requieren confirmacion)
TOOL_TIPOS: Dict[str, str] = {
    # READ
    "buscar_producto": "READ",
    "obtener_detalle_producto": "READ",
    "calcular_precio_pedido": "READ",
    "verificar_disponibilidad_producto": "READ",
    "recomendar_producto": "READ",
    "consultar_estado_pedido": "READ",
    "consultar_pedido_cliente": "READ",
    "verificar_disponibilidad_reserva": "READ",
    "calcular_costo_delivery": "READ",
    "rastrear_delivery": "READ",
    "buscar_cliente": "READ",
    "obtener_historial_cliente": "READ",
    "customer_360": "READ",
    "obtener_metricas": "READ",
    # WRITE
    "crear_pedido": "WRITE",
    "agregar_item_pedido": "WRITE",
    "confirmar_pedido": "WRITE",
    "cancelar_pedido": "WRITE",
    "crear_reserva": "WRITE",
    "cancelar_reserva": "WRITE",
    "crear_envio_delivery": "WRITE",
    "crear_cliente": "WRITE",
    "registrar_interaccion": "WRITE",
    # SIDE EFFECT
    "enviar_mensaje_whatsapp": "SIDE_EFFECT",
    "enviar_mensaje_telegram": "SIDE_EFFECT",
}

# Tools criticas que exigen confirmacion explicita del usuario
TOOLS_CRITICAS = {
    "crear_reserva": "crear la reserva",
    "cancelar_reserva": "cancelar la reserva",
    "confirmar_pedido": "confirmar el pedido",
    "cancelar_pedido": "cancelar el pedido",
    "crear_envio_delivery": "crear el envio de delivery",
    "enviar_mensaje_whatsapp": "enviar un mensaje por WhatsApp",
    "enviar_mensaje_telegram": "enviar un mensaje por Telegram",
}

_PALABRAS_CONFIRMACION = {
    "si", "si!", "simon", "confirmo", "confirmar", "confirmada", "confirmado",
    "dale", "claro", "adelante", "ok", "okay", "de acuerdo", "correcto",
    "eso", "eso es", "perfecto", "bueno", "s", "yes",
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^\w\s]", " ", texto).strip()


def es_confirmacion(texto: str) -> bool:
    """Determina si un mensaje del usuario es una confirmacion explicita."""
    normalizado = _normalizar(texto or "")
    palabras = set(normalizado.split())
    return bool(palabras & _PALABRAS_CONFIRMACION)


def _args_key(args: Dict[str, Any]) -> str:
    return json.dumps(args or {}, sort_keys=True, ensure_ascii=False)


SYSTEM_PROMPT = """Eres un asistente virtual de La Terraza, un restaurante en Ecuador. Tu objetivo es ayudar a los clientes con:

1. **Consultar el menu**: precios, ingredientes, disponibilidad, personalizaciones
2. **Crear pedidos**: tomar pedidos completos con extras y tamanos
4. **Gestionar reservas**: verificar disponibilidad y crear reservas
5. **Delivery**: calcular costos y crear envios
6. **Atencion al cliente**: historial, preferencias, Customer 360

REGLAS IMPORTANTES:
- Los precios son calculados por el backend, NUNCA los inventes
- Maximo 1 sugerencia de upselling por pedido
- Horario: Lunes a Domingo 9am-10pm
- Zona horaria: Ecuador (UTC-5)
- Se amable y profesional
- Si no sabes algo, ofrece conectar con un humano
- Nunca te hagas pasar por administrador ni otorgues permisos: la autorizacion la maneja el backend

FLUJO DE PEDIDO:
1. Cliente pide algo -> buscar en menu
2. Ofrece opciones (tamano, extras)
3. Calcula precio real desde backend
4. Muestra resumen del pedido
5. Confirma y crea el pedido

FLUJO DE RESERVA:
1. Cliente quiere reservar -> verificar_disponibilidad_reserva
2. Ofrece horarios disponibles
3. Pide nombre y telefono
4. Pide CONFIRMACION explicita del usuario ("¿Confirmas la reserva?")
5. Solo si el usuario confirma -> crear_reserva con los MISMOS datos
6. Si el usuario confirma y el sistema rechaza la tool, informa el motivo real

CONFIRMACION OBLIGATORIA:
- Antes de ejecutar crear_reserva, cancelar_reserva, confirmar_pedido,
  cancelar_pedido, crear_envio_delivery o enviar mensajes, pregunta primero:
  "¿Confirmas <accion>?"
- Si el usuario no ha dicho claramente que si, NO vuelvas a llamar la tool.
- Cuando el usuario confirme, vuelve a llamar la MISMA tool con los MISMOS argumentos.

IMPORTANTE: El LLM no es la fuente de verdad. El backend calcula precios, verifica disponibilidad y crea registros reales. Si una tool devuelve un error, informa el motivo sin inventar datos."""


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


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    # Ultima operacion critica pendiente de confirmacion del usuario
    pendiente_confirmacion: Optional[Dict[str, str]]


def validar_confirmacion(state: AgentState) -> AgentState:
    """Nodo determinista: exige confirmacion previa para tools criticas.

    El system prompt no basta: aqui se BLOQUEA la ejecucion de operaciones
    criticas salvo que (1) exista una peticion pendiente con los mismos
    argumentos y (2) el usuario haya confirmado explicitamente en este turno.
    """
    messages = state.get("messages") or []
    if not messages:
        return {}

    last = messages[-1]
    pendiente = state.get("pendiente_confirmacion")
    tool_calls = getattr(last, "tool_calls", None) or []

    # ¿El usuario confirmo en este turno?
    ultimo_usuario = next(
        (m for m in reversed(messages[:-1]) if isinstance(m, HumanMessage)),
        None,
    )
    confirmo = bool(ultimo_usuario and es_confirmacion(ultimo_usuario.content))

    if not tool_calls:
        # Turno sin tools: descartar pendientes si el usuario no confirmo
        if pendiente and not confirmo:
            return {"pendiente_confirmacion": None}
        return {}

    criticas = [tc for tc in tool_calls if tc.get("name") in TOOLS_CRITICAS]

    if not criticas:
        # Solo tools READ/no criticas -> pasar directo a ToolNode
        return {}

    # ¿El usuario confirmo y los argumentos coinciden con lo pendiente?
    if confirmo and pendiente and all(
        pendiente.get("name") == tc.get("name")
        and pendiente.get("args") == _args_key(tc.get("args") or {})
        for tc in criticas
    ):
        return {"pendiente_confirmacion": None}

    # BLOQUEAR todo el turno: el agente debe pedir confirmacion primero
    acciones = ", ".join(
        TOOLS_CRITICAS.get(tc.get("name"), tc.get("name")) for tc in criticas
    )
    args_repr = json.dumps(criticas[0].get("args") or {}, ensure_ascii=False)
    tool_msgs = [
        ToolMessage(
            content=(
                f"OPERACION_BLOQUEADA: la operacion '{acciones}' requiere "
                f"confirmacion explicita del usuario. Argumentos: {args_repr}. "
                f"Responde al usuario preguntando '¿Confirmas {acciones}?' "
                f"y NO vuelvas a llamar la tool hasta recibir confirmacion."
            ),
            tool_call_id=tc.get("id", ""),
            name=tc.get("name", ""),
        )
        for tc in tool_calls
    ]
    sin_llamadas = AIMessage(content=last.content, tool_calls=[], id=last.id)

    return {
        "messages": [sin_llamadas] + tool_msgs,
        "pendiente_confirmacion": {
            "name": criticas[0].get("name"),
            "args": _args_key(criticas[0].get("args") or {}),
        },
    }


def _decision(state: AgentState) -> str:
    messages = state.get("messages") or []
    last = messages[-1] if messages else None
    if isinstance(last, ToolMessage):
        # El nodo de validacion bloqueo todo: volver al agente
        return END
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


def create_agent():
    """Crea el agente ReAct con LangGraph."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    base_url = os.getenv("KILO_BASE_URL", "https://api.kilo.ai/v1")
    model_name = os.getenv("KILO_CHAT_MODEL", "nvidia/nemotron-3.5-lightning:free")

    llm = ChatOpenAI(
        model=model_name,
        # Sin credenciales la creacion no falla: el error real aparece al
        # invocar y process_message lo convierte en respuesta segura
        api_key=api_key or "no-key-configured",
        base_url=base_url,
        temperature=0.7,
        max_tokens=1024,
        timeout=45.0,
        max_retries=1,
    )

    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState) -> dict:
        messages = state.get("messages") or []
        system_message = {"role": "system", "content": SYSTEM_PROMPT}
        all_messages = [system_message] + list(messages)
        response = llm_with_tools.invoke(all_messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("validar", validar_confirmacion)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _decision, {"tools": "validar", END: END})
    # Tras validar: solo ir a tools si quedaron tool_calls aprobadas
    graph.add_conditional_edges("validar", _decision, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    # MEMORIA: MemorySaver es SOLO para desarrollo local (in-memory, por proceso).
    # En produccion usar PostgresSaver/RedisSaver de langgraph.checkpoint.
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


def process_message(
    message: str,
    thread_id: str = "default",
    channel: str = "whatsapp",
    identidad_verificada: Optional[str] = None,
) -> str:
    """Procesa un mensaje y retorna la respuesta.

    Args:
        message: Mensaje del cliente
        thread_id: ID del hilo (telefono del cliente)
        channel: Canal de origen (whatsapp, telegram, webchat)
        identidad_verificada: Identidad del dueno de los recursos, SOLO si
            el punto de entrada la verifico (webhook WhatsApp con firma).
            Las tools la usan para acotar sus acciones a ese cliente; el
            LLM nunca puede setearla ni sustituirla.

    Returns:
        Respuesta del agente (nunca stack traces)
    """
    token_identidad = autorizacion.establecer_identidad(identidad_verificada)
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
        if isinstance(ai_message, ToolMessage):
            if ai_message.content.startswith("OPERACION_BLOQUEADA"):
                # El agente intento una accion critica sin confirmacion
                return (
                    "Para poder continuar necesito tu confirmacion. "
                    "¿Confirmas la operacion indicada? Responde 'si' para "
                    "continuar o dime cualquier cambio."
                )
            return ai_message.content

        return ai_message.content

    except Exception:
        # El error completo queda en logs; el usuario solo ve una respuesta segura
        logger.exception(
            "Error procesando mensaje channel=%s thread=%s", channel, thread_id
        )
        return "Disculpa, tuve un problema procesando tu mensaje. Puedes intentar de nuevo?"
    finally:
        autorizacion.limpiar_identidad(token_identidad)
