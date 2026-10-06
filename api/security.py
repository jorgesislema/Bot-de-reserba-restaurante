"""Primitivas de seguridad de la API.

- Tokens de cliente: JWT HS256 firmados con SECRET_KEY (stdlib, sin libs externas).
- Firma de webhooks de WhatsApp: X-Hub-Signature-256 (HMAC-SHA256 sobre el
  body CRUDO con WHATSAPP_APP_SECRET).

Ninguna funcion de aqui imprime ni registra secretos.
"""

import base64
import hashlib
import hmac
import json
import os
import time

# TTL de los tokens de cliente (1 hora)
TOKEN_TTL_SEGUNDOS = 3600


def _b64url(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode("ascii")


def _b64url_decode(texto: str) -> bytes:
    padding = "=" * (-len(texto) % 4)
    return base64.urlsafe_b64decode(texto + padding)


def _secreto() -> str:
    return os.getenv("SECRET_KEY", "")


def crear_token(cliente_id: int, ttl_segundos: int = TOKEN_TTL_SEGUNDOS) -> str:
    """Emite un JWT HS256 para un cliente. Falla si SECRET_KEY no esta definido."""
    secreto = _secreto()
    if not secreto:
        raise RuntimeError("SECRET_KEY no configurado: no se puede emitir tokens")

    cabecera = {"alg": "HS256", "typ": "JWT"}
    ahora = int(time.time())
    payload = {
        "sub": int(cliente_id),
        "iat": ahora,
        "exp": ahora + int(ttl_segundos),
    }
    parte_firmada = (
        f"{_b64url(json.dumps(cabecera, separators=(',', ':')).encode())}."
        f"{_b64url(json.dumps(payload, separators=(',', ':')).encode())}"
    )
    firma = hmac.new(
        secreto.encode(), parte_firmada.encode(), hashlib.sha256,
    ).digest()
    return f"{parte_firmada}.{_b64url(firma)}"


def verificar_token(token: str) -> int | None:
    """Valida firma y expiracion. Devuelve el cliente_id (sub) o None.

    Solo se acepta HS256: se ignora cualquier 'alg' distinto (proteccion
    contra confusion de algoritmos: 'none', RS256, etc.).
    """
    if not token:
        return None
    partes = token.split(".")
    if len(partes) != 3:
        return None
    cabecera_b64, payload_b64, firma_b64 = partes

    try:
        cabecera = json.loads(_b64url_decode(cabecera_b64))
        firma = _b64url_decode(firma_b64)
    except (ValueError, json.JSONDecodeError):
        return None

    if cabecera.get("alg") != "HS256" or cabecera.get("typ", "JWT") != "JWT":
        return None

    secreto = _secreto()
    if not secreto:
        return None

    esperada = hmac.new(
        secreto.encode(), f"{cabecera_b64}.{payload_b64}".encode(), hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(esperada, firma):
        return None

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, json.JSONDecodeError):
        return None

    if int(payload.get("exp", 0)) < time.time():
        return None

    sub = payload.get("sub")
    if isinstance(sub, bool) or not isinstance(sub, int):
        return None
    return sub


def verificar_firma_whatsapp(body: bytes, cabecera: str, app_secret: str) -> bool:
    """Verifica X-Hub-Signature-256 ('sha256=<hex>') sobre el body crudo.

    Meta calcula el HMAC con el App Secret de la aplicacion. Si falta el
    header, el secreto o el prefijo, se rechaza (fail-closed).
    """
    if not app_secret or not cabecera:
        return False
    if not cabecera.startswith("sha256="):
        return False
    hex_firma = cabecera[len("sha256="):]
    esperada = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, hex_firma)
