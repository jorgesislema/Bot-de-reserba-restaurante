"""Herramientas de canales para LangGraph (SIDE EFFECT)."""

import logging

from langchain_core.tools import tool
from skills.channels.channel_skill import ChannelSkill
from tools.autorizacion import DENEGADO, acceso_permitido, cliente_identificado

logger = logging.getLogger(__name__)

_channel_skill = ChannelSkill()
_channel_skill.initialize({})


@tool
def enviar_mensaje_whatsapp(numero: str, mensaje: str) -> str:
    """Envia un mensaje por WhatsApp (requiere confirmacion del usuario previa).

    Args:
        numero: Numero de telefono del destinatario
        mensaje: Mensaje a enviar

    Returns:
        Estado real del envio
    """
    if cliente_identificado() and not acceso_permitido(numero):
        # Con identidad verificada solo se puede escribir al interlocutor
        return DENEGADO

    resultado = _channel_skill.execute("enviar_respuesta", {
        "channel": "whatsapp",
        "to": numero,
        "message": mensaje
    })

    if resultado.get("success"):
        return "Mensaje enviado por WhatsApp."

    error = resultado.get("error")
    if error == "channel_not_configured":
        return ('{"success": false, "error": "channel_not_configured", '
                '"detail": "WhatsApp no esta configurado en este entorno."}')
    logger.warning("Fallo envio WhatsApp a %s: %s", numero, error)
    return f'{{"success": false, "error": "{error}"}}'


@tool
def enviar_mensaje_telegram(chat_id: str, mensaje: str) -> str:
    """Envia un mensaje por Telegram (requiere confirmacion del usuario previa).

    Args:
        chat_id: ID del chat de Telegram
        mensaje: Mensaje a enviar

    Returns:
        Estado real del envio
    """
    resultado = _channel_skill.execute("enviar_respuesta", {
        "channel": "telegram",
        "to": chat_id,
        "message": mensaje
    })

    if resultado.get("success"):
        return "Mensaje enviado por Telegram."

    error = resultado.get("error")
    if error == "channel_not_configured":
        return ('{"success": false, "error": "channel_not_configured", '
                '"detail": "Telegram no esta configurado en este entorno."}')
    logger.warning("Fallo envio Telegram a %s: %s", chat_id, error)
    return f'{{"success": false, "error": "{error}"}}'
