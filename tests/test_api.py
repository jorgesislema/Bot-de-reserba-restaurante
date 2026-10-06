"""Tests de API."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_api_productos():
    response = client.get("/api/productos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least one product if seed data loaded, but we can't guarantee; just check structure
    if len(data) > 0:
        item = data[0]
        assert "id" in item
        assert "nombre" in item
        assert "precio" in item


def test_api_metricas(monkeypatch):
    # Contrato actualizado: /api/metricas es un endpoint de negocio (staff)
    # y exige X-API-Key de servicio siempre (antes respondia 200 sin auth;
    # el test verificaba el contrato antiguo, ahora se ajusta al nuevo).
    from api import main

    monkeypatch.setattr(main, "API_KEY", "test-api-key-metricas")
    response = client.get("/api/metricas", headers={"X-API-Key": "test-api-key-metricas"})
    assert response.status_code == 200
    data = response.json()
    assert "conversaciones_hoy" in data
    assert "pedidos_hoy" in data
    assert "reservas_hoy" in data
    assert "ventas_hoy" in data
    assert isinstance(data["conversaciones_hoy"], int)
    assert isinstance(data["pedidos_hoy"], int)
    assert isinstance(data["reservas_hoy"], int)
    assert isinstance(data["ventas_hoy"], float)
    # Sin API key -> 401
    sin = client.get("/api/metricas")
    assert sin.status_code == 401


def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    # El dashboard real usa la plantilla Dashboard - Restaurant AI
    # (el test anterior buscaba "Restaurant AI Platform", texto inexistente
    # en templates/; se corrige la asercion al contrato real de la UI)
    assert "Dashboard" in response.text


def test_menu_page():
    response = client.get("/menu")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Menu" in response.text or "Producto" in response.text
