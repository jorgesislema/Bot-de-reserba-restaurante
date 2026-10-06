"""Tests de herramientas LangGraph."""

import pytest
from tools.menu_tool import buscar_producto, obtener_detalle_producto
from tools.order_tool import crear_pedido, consultar_estado_pedido


def test_buscar_producto():
    resultado = buscar_producto.invoke("pizza")
    assert isinstance(resultado, str)
    assert len(resultado) > 0
    # Should contain some product info
    assert "Pizza" in resultado or "Producto" in resultado


def test_crear_pedido():
    from database.db_manager import RestaurantDB
    db = RestaurantDB()
    cliente_id = db.crear_cliente({
        "nombre": "Cliente Tools",
        "telefono": "+593911111111",
    })
    resultado = crear_pedido.invoke({
        "cliente_id": cliente_id,
        "canal": "whatsapp",
    })
    assert isinstance(resultado, str)
    assert "Pedido creado:" in resultado
    # Extract number after colon: el formato real es #YYYYMMDDNNNN
    # (el test anterior esperaba solo digitos; se corrige al contrato real)
    numero_part = resultado.split(":")[1].strip()
    assert numero_part.startswith("#")
    assert numero_part[1:].isdigit()
    assert int(numero_part[1:]) > 0


def test_crear_pedido_cliente_inexistente():
    resultado = crear_pedido.invoke({"cliente_id": 999999, "canal": "whatsapp"})
    assert isinstance(resultado, str)
    assert "No pude crear" in resultado
    assert "no existe" in resultado.lower()


def test_consultar_estado_pedido():
    resultado = consultar_estado_pedido.invoke({"pedido_id": 999999})
    assert isinstance(resultado, str)
    assert "No encontre" in resultado
    assert "pedido" in resultado.lower()

