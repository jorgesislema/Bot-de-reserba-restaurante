"""Autorizacion en el borde de las tools.

La identidad se propaga por ContextVar desde el punto de entrada verificado
(webhook de WhatsApp autenticado por firma). NUNCA llega como argumento del
LLM: los argumentos de las tools no son credenciales.

Si no hay identidad (webchat del dashboard, llamadas internas del backend,
Telegram -fuera de alcance en esta fase-), se asume contexto interno de
confianza y no se aplica restriccion de dueno.
"""

from contextvars import ContextVar

_identidad_ctx: ContextVar[str | None] = ContextVar(
    "identidad_canal_verificado", default=None,
)

DENEGADO = "No tienes autorizacion para acceder a ese recurso."


def establecer_identidad(valor: str | None) -> object:
    return _identidad_ctx.set(valor)


def limpiar_identidad(token: object) -> None:
    _identidad_ctx.reset(token)


def obtener_identidad() -> str | None:
    return _identidad_ctx.get()


def cliente_identificado() -> bool:
    """True si hay una identidad de cliente verificada en este contexto."""
    return _identidad_ctx.get() is not None


def _digitos(valor: str | None) -> str:
    return "".join(c for c in str(valor or "") if c.isdigit())


def acceso_permitido(propietario: str | None) -> bool:
    """True si la identidad actual puede acceder al recurso.

    - Sin identidad (contexto interno): permitido.
    - Con identidad: el dueno del recurso debe ser la misma persona
      (comparacion por digitos: ignora '+' y formato).
    """
    identidad = _identidad_ctx.get()
    if identidad is None:
        return True
    if propietario is None:
        return False
    a, b = _digitos(identidad), _digitos(propietario)
    return bool(a) and a == b
