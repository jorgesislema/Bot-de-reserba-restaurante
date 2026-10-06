"""Tests de autenticacion (JWT) y autorizacion (IDOR) de la API.

Contrato verificado aqui:
- Recursos de cliente: 401 sin token / token invalido / token expirado.
- Recursos ajenos: 403 (accion) o 404 (pedido inexistente).
- Emision de tokens y busqueda de clientes: X-API-Key del servicio.
"""

import base64
import json
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from api import main
from api.security import crear_token
from database.db_manager import RestaurantDB

TEST_SECRET = "unit-test-secret-key"
TEST_API_KEY = "unit-test-service-key"

FUTURA = (date.today() + timedelta(days=20)).isoformat()  # noqa: DTZ011


def _b64url(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


@pytest.fixture
def api_db(monkeypatch):
    """BD en memoria para la app + claves de prueba (nunca secretos reales)."""
    bd = RestaurantDB("sqlite:///:memory:")
    monkeypatch.setattr(main, "db", bd)
    monkeypatch.setattr(main, "API_KEY", TEST_API_KEY)
    monkeypatch.setattr(main, "REQUIRE_API_KEY", False)
    monkeypatch.setenv("SECRET_KEY", TEST_SECRET)
    return bd


@pytest.fixture
def clientes(api_db):
    a = api_db.crear_cliente({"nombre": "Cliente A", "telefono": "+593991111111"})
    b = api_db.crear_cliente({"nombre": "Cliente B", "telefono": "+593992222222"})
    return a, b


@pytest.fixture
def client(api_db):  # noqa: ARG001 - fija main.db antes del TestClient
    return TestClient(main.app)


def _hdr(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ===========================================
# AUTENTICACION
# ===========================================

def test_recursos_sin_token_devuelven_401(client, clientes):
    a, b = clientes
    for metodo, url in [
        ("get", f"/api/clientes/{a}"),
        ("get", "/api/pedidos/1"),
        ("post", "/api/pedidos"),
    ]:
        resp = getattr(client, metodo)(url)
        assert resp.status_code == 401, f"{metodo} {url} -> {resp.status_code}"


def test_token_firmado_con_otra_clave_es_rechazado(client, clientes, monkeypatch):
    a, _b = clientes
    token = crear_token(a)
    monkeypatch.setenv("SECRET_KEY", "otra-clave-diferente")
    resp = client.get(f"/api/clientes/{a}", headers=_hdr(token))
    assert resp.status_code == 401


def test_token_expirado_es_rechazado(client, clientes):
    a, _b = clientes
    token = crear_token(a, ttl_segundos=-10)
    resp = client.get(f"/api/clientes/{a}", headers=_hdr(token))
    assert resp.status_code == 401
    assert "Bearer" in resp.headers.get("WWW-Authenticate", "")


def test_token_con_alg_none_es_rechazado(client, clientes):
    a, _b = clientes
    cabecera = _b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = _b64url(
        json.dumps({"sub": a, "exp": 4102444800}).encode(),
    )
    resp = client.get(
        f"/api/clientes/{a}", headers=_hdr(f"{cabecera}.{payload}."),
    )
    assert resp.status_code == 401


def test_token_con_firma_alterada_es_rechazado(client, clientes):
    a, _b = clientes
    partes = crear_token(a).split(".")
    partes[1] = _b64url(json.dumps({"sub": a, "exp": 4102444800}).encode())
    resp = client.get(f"/api/clientes/{a}", headers=_hdr(".".join(partes)))
    assert resp.status_code == 401


def test_emision_de_token_requiere_api_key(client, clientes):
    a, _b = clientes

    # Sin X-API-Key -> 401
    resp = client.post("/api/auth/token", json={"cliente_id": a})
    assert resp.status_code == 401

    # Con X-API-Key invalida -> 401
    resp = client.post(
        "/api/auth/token",
        json={"cliente_id": a},
        headers={"X-API-Key": "clave-mala"},
    )
    assert resp.status_code == 401

    # Con X-API-Key valida pero cliente inexistente -> 404
    resp = client.post(
        "/api/auth/token",
        json={"cliente_id": 999999},
        headers={"X-API-Key": TEST_API_KEY},
    )
    assert resp.status_code == 404

    # Emision valida
    resp = client.post(
        "/api/auth/token",
        json={"cliente_id": a},
        headers={"X-API-Key": TEST_API_KEY},
    )
    assert resp.status_code == 200
    datos = resp.json()
    assert datos["token_type"] == "Bearer"
    assert datos["expires_in"] > 0

    # El token emitido da acceso al recurso propio
    resp = client.get(f"/api/clientes/{a}", headers=_hdr(datos["access_token"]))
    assert resp.status_code == 200
    assert resp.json()["id"] == a


# ===========================================
# IDOR CLIENTES
# ===========================================

def test_cliente_no_puede_leer_a_otro_cliente(client, clientes):
    a, b = clientes
    token_a = crear_token(a)

    resp = client.get(f"/api/clientes/{b}", headers=_hdr(token_a))
    assert resp.status_code == 403

    resp = client.get(f"/api/clientes/{a}", headers=_hdr(token_a))
    assert resp.status_code == 200
    assert resp.json()["id"] == a


def test_buscar_clientes_requiere_api_key(client, clientes):
    resp = client.get("/api/clientes/buscar", params={"q": "Cliente"})
    assert resp.status_code == 401

    resp = client.get(
        "/api/clientes/buscar",
        params={"q": "Cliente"},
        headers={"X-API-Key": TEST_API_KEY},
    )
    assert resp.status_code == 200
    assert {c["id"] for c in resp.json()} == {clientes[0], clientes[1]}


# ===========================================
# IDOR PEDIDOS
# ===========================================

def test_lectura_pedido_ajeno_403_y_inexistente_404(client, clientes, api_db):
    a, b = clientes
    token_a = crear_token(a)
    pedido_b = api_db.crear_pedido(b, "whatsapp")

    resp = client.get(f"/api/pedidos/{pedido_b}", headers=_hdr(token_a))
    assert resp.status_code == 403

    resp = client.get("/api/pedidos/999999", headers=_hdr(token_a))
    assert resp.status_code == 404

    resp = client.get(f"/api/pedidos/{pedido_b}", headers=_hdr(crear_token(b)))
    assert resp.status_code == 200
    assert resp.json()["cliente_id"] == b


def test_modificacion_pedido_ajeno_403_y_estado_intacto(client, clientes, api_db):
    a, b = clientes
    token_a = crear_token(a)
    pedido_b = api_db.crear_pedido(b, "whatsapp")

    resp = client.post(
        f"/api/pedidos/{pedido_b}/confirmar", headers=_hdr(token_a),
    )
    assert resp.status_code == 403

    resp = client.post(
        f"/api/pedidos/{pedido_b}/cancelar",
        data={"motivo": "ataque"},
        headers=_hdr(token_a),
    )
    assert resp.status_code == 403

    resp = client.post(
        f"/api/pedidos/{pedido_b}/items",
        data={"producto_id": 1, "cantidad": 5},
        headers=_hdr(token_a),
    )
    assert resp.status_code == 403

    # El pedido de B sigue sin cambios
    assert api_db.obtener_pedido(pedido_b)["estado"] == "draft"


def test_crear_pedido_para_cliente_ajeno_403(client, clientes):
    a, b = clientes
    token_a = crear_token(a)

    resp = client.post(
        "/api/pedidos",
        params={"cliente_id": b},
        headers=_hdr(token_a),
    )
    assert resp.status_code == 403

    resp = client.post(
        "/api/pedidos",
        params={"cliente_id": a},
        headers=_hdr(token_a),
    )
    assert resp.status_code == 200


# ===========================================
# IDOR RESERVAS
# ===========================================

def test_reserva_con_cliente_ajeno_403(client, clientes):
    a, b = clientes
    token_a = crear_token(a)

    resp = client.post(
        "/api/reservas",
        data={
            "fecha": FUTURA, "hora": "20:00", "personas": 2,
            "nombre": "Intruso", "telefono": "+593991111111",
            "cliente_id": b,
        },
        headers=_hdr(token_a),
    )
    assert resp.status_code == 403


def test_reserva_con_telefono_ajeno_403(client, clientes, api_db):
    a, b = clientes
    token_a = crear_token(a)

    resp = client.post(
        "/api/reservas",
        data={
            "fecha": FUTURA, "hora": "20:00", "personas": 2,
            "nombre": "Intruso", "telefono": "+593992222222",
            "cliente_id": a,
        },
        headers=_hdr(token_a),
    )
    assert resp.status_code == 403

    # Ninguna reserva fue creada
    assert api_db.obtener_reservas_por_fecha(FUTURA) == []


def test_reserva_propia_valida(client, clientes):
    a, _b = clientes
    token_a = crear_token(a)

    resp = client.post(
        "/api/reservas",
        data={
            "fecha": FUTURA, "hora": "20:00", "personas": 2,
            "nombre": "Cliente A", "telefono": "+593991111111",
            "cliente_id": a,
        },
        headers=_hdr(token_a),
    )
    assert resp.status_code == 200
    assert resp.json()["reserva_id"] > 0
