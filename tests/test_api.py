"""Tests de API."""

import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_api_productos():
    response = client.get("/api/productos")
    assert response.status_code == 200


def test_api_metricas():
    response = client.get("/api/metricas")
    assert response.status_code == 200


def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200


def test_menu_page():
    response = client.get("/menu")
    assert response.status_code == 200
