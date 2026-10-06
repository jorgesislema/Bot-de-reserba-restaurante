"""Tests de API."""

import pytest
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


def test_api_metricas():
    response = client.get("/api/metricas")
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


def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    # Check that some expected text appears
    assert "Restaurant AI Platform" in response.text


def test_menu_page():
    response = client.get("/menu")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Menu" in response.text or "Producto" in response.text
