"""Tests de calculo de precios: el backend es la unica fuente de verdad."""

import pytest
from database.models import Category, Product, ProductOption


@pytest.fixture
def producto_con_opciones(db):
    """Producto $10 con tamano +$4 y extra +$1.50."""
    session = db._get_session()
    try:
        cat = Category(nombre="Test Precios")
        session.add(cat)
        session.commit()

        prod = Product(categoria_id=cat.id, nombre="Producto Test", precio_base=10.00)
        session.add(prod)
        session.commit()

        session.add_all([
            ProductOption(producto_id=prod.id, tipo="tamano", nombre="Grande", precio_adicional=4.00),
            ProductOption(producto_id=prod.id, tipo="extra", nombre="Queso", precio_adicional=1.50),
            ProductOption(producto_id=prod.id, tipo="extra", nombre="Tocino", precio_adicional=2.00),
        ])
        session.commit()
        return prod.id
    finally:
        session.close()


def test_precio_base(db, producto_con_opciones):
    assert db.calcular_precio(producto_con_opciones, {}) == 10.00


def test_precio_base_mas_tamano(db, producto_con_opciones):
    # producto $10 + tamano $4 = $14 (NUNCA $4)
    assert db.calcular_precio(producto_con_opciones, {"tamano": "Grande"}) == 14.00


def test_precio_base_mas_extra(db, producto_con_opciones):
    # producto $10 + extra $1.50 = $11.50
    assert db.calcular_precio(
        producto_con_opciones, {"extras": ["Queso"]}
    ) == 11.50


def test_precio_tamano_mas_extras(db, producto_con_opciones):
    # 10 + 4 (tamano) + 1.50 + 2 (extras) = 17.50
    precio = db.calcular_precio(producto_con_opciones, {
        "tamano": "Grande",
        "extras": ["Queso", "Tocino"],
    })
    assert precio == 17.50


def test_precio_cantidad_multiplica(db, producto_con_opciones):
    """agregar_item_pedido usa precio_unitario del backend * cantidad."""
    cliente_id = db.crear_cliente({"nombre": "C", "telefono": "+593988888888"})
    pedido_id = db.crear_pedido(cliente_id, "whatsapp")

    exito = db.agregar_item_pedido(
        pedido_id, producto_con_opciones, 3, {"tamano": "Grande"}
    )
    assert exito is True

    pedido = db.obtener_pedido(pedido_id)
    # 14.00 * 3 = 42.00
    assert pedido["items"][0]["precio_unitario"] == 14.00
    assert pedido["items"][0]["precio_total"] == 42.00
    assert pedido["subtotal"] == 42.00
    assert pedido["total"] == 42.00


def test_precio_producto_inexistente(db):
    with pytest.raises(ValueError):
        db.calcular_precio(999999, {})


def test_precio_tamano_inexistente_rechazado(db, producto_con_opciones):
    with pytest.raises(ValueError):
        db.calcular_precio(producto_con_opciones, {"tamano": "Gigante"})


def test_precio_extra_inexistente_rechazado(db, producto_con_opciones):
    with pytest.raises(ValueError):
        db.calcular_precio(producto_con_opciones, {"extras": ["Inventado"]})


def test_agregar_item_rechaza_producto_inexistente(db):
    cliente_id = db.crear_cliente({"nombre": "C2", "telefono": "+593988888889"})
    pedido_id = db.crear_pedido(cliente_id, "whatsapp")
    with pytest.raises(ValueError):
        db.agregar_item_pedido(pedido_id, 999999, 1)
