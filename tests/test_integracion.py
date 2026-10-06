"""Tests de integracion."""

import pytest
from api.agent import process_message


@pytest.mark.llm
def test_procesar_mensaje_menu():
    respuesta = process_message("Que pizzas tienen?", thread_id="test1")
    assert isinstance(respuesta, str)
    assert len(respuesta) > 0
    # Should not be an error message
    assert "disculpa" not in respuesta.lower()
    assert "error" not in respuesta.lower()
    # Should mention pizza or menu
    assert any(word in respuesta.lower() for word in ["pizza", "menu", "tenemos", "disponible"])


@pytest.mark.llm
def test_procesar_mensaje_pedido():
    respuesta = process_message("Quiero una pizza familiar", thread_id="test2")
    assert isinstance(respuesta, str)
    assert len(respuesta) > 0
    assert "disculpa" not in respuesta.lower()
    assert "error" not in respuesta.lower()
    # Should acknowledge pedido
    assert any(word in respuesta.lower() for word in ["pedido", "confirmar", "precio", "total", "agradezco"])


@pytest.mark.llm
def test_procesar_mensaje_reserva():
    respuesta = process_message("Quiero reservar para 6 personas", thread_id="test3")
    assert isinstance(respuesta, str)
    assert len(respuesta) > 0
    assert "disculpa" not in respuesta.lower()
    assert "error" not in respuesta.lower()
    # Should mention reserva, disponibilidad, pedir datos
    assert any(word in respuesta.lower() for word in ["reserva", "horario", "disponible", "fecha", "hora", "personas", "nombre", "telefono"])


@pytest.mark.llm
def test_conversacion_completa():
    r1 = process_message("Hola", thread_id="test4")
    r2 = process_message("Quiero una pizza", thread_id="test4")
    r3 = process_message("Pepperoni", thread_id="test4")
    r4 = process_message("Familiar", thread_id="test4")
    r5 = process_message("Confirmar", thread_id="test4")
    assert all(isinstance(r, str) for r in [r1, r2, r3, r4, r5])
    assert all(len(r) > 0 for r in [r1, r2, r3, r4, r5])
    # No error messages
    for r in [r1, r2, r3, r4, r5]:
        assert "disculpa" not in r.lower()
        assert "error" not in r.lower()
    # Final confirmation should indicate success
    assert any(word in r5.lower() for word in ["confirmado", "éxito", "gracias", "pedido", "numero"])
