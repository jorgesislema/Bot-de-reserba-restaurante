"""Verificacion de variables de entorno."""

import os
from typing import Tuple, List


def check_environment() -> Tuple[bool, List[str]]:
    """Verifica que las variables de entorno criticas esten configuradas.

    Returns:
        Tuple con (is_ok, lista_de_errores)
    """
    errors = []

    # LLM (critico)
    if not os.getenv("OPENROUTER_API_KEY"):
        errors.append("OPENROUTER_API_KEY no configurada")

    # Database (critico)
    if not os.getenv("DATABASE_URL"):
        errors.append("DATABASE_URL no configurada (usando SQLite)")

    # WhatsApp (advertencia)
    if not os.getenv("WHATSAPP_TOKEN"):
        errors.append("WHATSAPP_TOKEN no configurada (WhatsApp deshabilitado)")

    # Telegram (advertencia)
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        errors.append("TELEGRAM_BOT_TOKEN no configurada (Telegram deshabilitado)")

    is_ok = len(errors) == 0
    return is_ok, errors
