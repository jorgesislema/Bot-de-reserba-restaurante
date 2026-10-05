"""Tests de herramientas LangGraph."""

import pytest
from tools.menu_tool import buscar_producto, obtener_detalle_producto
from tools.order_tool import crear_pedido, consultar_estado_pedido


def test_buscar_producto():
    resultado = buscar_producto.invoke("pizza")
    assert isinstance(resultado, str)
    assert len(resultado) > 0


def test_crear_pedido():
    resultado = crear_pedido.invoke(1, "whatsapp")
    assert "Pedido creado" in resultado


def test_consultar_estado_pedido():
    resultado = consultar_estado_pedido.invoke(999)
    assert "No encontre" in resultado
