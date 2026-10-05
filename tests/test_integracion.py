"""Tests de integracion."""

import pytest
from api.agent import process_message


def test_procesar_mensaje_menu():
    respuesta = process_message("Que pizzas tienen?", thread_id="test1")
    assert isinstance(respuesta, str)
    assert len(respuesta) > 0


def test_procesar_mensaje_pedido():
    respuesta = process_message("Quiero una pizza familiar", thread_id="test2")
    assert isinstance(respuesta, str)


def test_procesar_mensaje_reserva():
    respuesta = process_message("Quiero reservar para 6 personas", thread_id="test3")
    assert isinstance(respuesta, str)


def test_conversacion_completa():
    r1 = process_message("Hola", thread_id="test4")
    r2 = process_message("Quiero una pizza", thread_id="test4")
    r3 = process_message("Pepperoni", thread_id="test4")
    r4 = process_message("Familiar", thread_id="test4")
    r5 = process_message("Confirmar", thread_id="test4")

    assert all(isinstance(r, str) for r in [r1, r2, r3, r4, r5])
