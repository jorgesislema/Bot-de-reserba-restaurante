"""Tests de base de datos."""

from datetime import date, timedelta

import pytest
from database.models import OrderStatus


def test_crear_cliente(db):
    cliente_id = db.crear_cliente({
        "nombre": "Maria Lopez",
        "telefono": "+593888888888"
    })
    assert cliente_id > 0


def test_obtener_cliente(db):
    db.crear_cliente({
        "nombre": "Test",
        "telefono": "+593777777777"
    })
    cliente = db.obtener_cliente_por_telefono("+593777777777")
    assert cliente is not None
    assert cliente["nombre"] == "Test"


def test_crear_pedido(db, sample_customer):
    pedido_id = db.crear_pedido(sample_customer, "whatsapp")
    assert pedido_id > 0

    pedido = db.obtener_pedido(pedido_id)
    assert pedido["estado"] == "draft"


def test_agregar_item_pedido(db, sample_customer, sample_product):
    pedido_id = db.crear_pedido(sample_customer, "whatsapp")
    exito = db.agregar_item_pedido(pedido_id, sample_product, 2)
    assert exito is True

    pedido = db.obtener_pedido(pedido_id)
    assert len(pedido["items"]) == 1
    assert pedido["items"][0]["cantidad"] == 2


def test_confirmar_pedido(db, sample_customer, sample_product):
    pedido_id = db.crear_pedido(sample_customer, "whatsapp")
    db.agregar_item_pedido(pedido_id, sample_product, 1)

    exito = db.actualizar_estado_pedido(pedido_id, OrderStatus.CONFIRMED)
    assert exito is True

    pedido = db.obtener_pedido(pedido_id)
    assert pedido["estado"] == "confirmed"


def test_cancelar_pedido(db, sample_customer, sample_product):
    pedido_id = db.crear_pedido(sample_customer, "whatsapp")
    db.agregar_item_pedido(pedido_id, sample_product, 1)

    exito = db.cancelar_pedido(pedido_id, "Cambio de opinion")
    assert exito is True


def test_verificar_disponibilidad(db):
    fecha = (date.today() + timedelta(days=7)).isoformat()
    disponibilidad = db.verificar_disponibilidad(fecha, None, 6)
    assert len(disponibilidad) > 0


def test_crear_reserva(db, sample_customer):
    fecha = (date.today() + timedelta(days=7)).isoformat()
    reserva_id = db.crear_reserva({
        "cliente_id": sample_customer,
        "fecha": fecha,
        "hora": "20:00",
        "personas": 6,
        "nombre_contacto": "Carlos Perez",
        "telefono": "+593999999999"
    })
    assert reserva_id > 0
