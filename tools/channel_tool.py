"""Herramientas de canales para LangGraph."""

from langchain_core.tools import tool
from skills.channels.channel_skill import ChannelSkill


_channel_skill = ChannelSkill()
_channel_skill.initialize({})


@tool
def enviar_mensaje_whatsapp(numero: str, mensaje: str) -> str:
    """Envia un mensaje por WhatsApp.

    Args:
        numero: Numero de telefono del destinatario
        mensaje: Mensaje a enviar

    Returns:
        Estado del envio
    """
    exito = _channel_skill.execute("enviar_respuesta", {
        "channel": "whatsapp",
        "to": numero,
        "message": mensaje
    })

    if exito:
        return "Mensaje enviado por WhatsApp."
    else:
        return "No pude enviar el mensaje por WhatsApp."


@tool
def enviar_mensaje_telegram(chat_id: str, mensaje: str) -> str:
    """Envia un mensaje por Telegram.

    Args:
        chat_id: ID del chat de Telegram
        mensaje: Mensaje a enviar

    Returns:
        Estado del envio
    """
    exito = _channel_skill.execute("enviar_respuesta", {
        "channel": "telegram",
        "to": chat_id,
        "message": mensaje
    })

    if exito:
        return "Mensaje enviado por Telegram."
    else:
        return "No pude enviar el mensaje por Telegram."
