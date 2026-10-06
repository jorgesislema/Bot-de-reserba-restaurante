"""Tests de autorizacion en el borde de las tools.

La identidad verificada del canal (WhatsApp) acota las tools a los
recursos propios. Sin identidad (contexto interno) el acceso se mantiene.
El LLM no puede setear la identidad: solo el punto de entrada verificado.
"""

from datetime import date, timedelta

import pytest

from database.db_manager import RestaurantDB
from tools import (
    analytics_tool,
    autorizacion,
    channel_tool,
    customer_tool,
    delivery_tool,
    order_tool,
    reservation_tool,
)

FUTURA = (date.today() + timedelta(days=25)).isoformat()  # noqa: DTZ011


@pytest.fixture
def entorno(monkeypatch):
    """BD en memoria compartida por todas las skills involucradas."""
    db = RestaurantDB("sqlite:///:memory:")
    monkeypatch.setattr(customer_tool._customer_skill, "db", db)  # noqa: SLF001
    monkeypatch.setattr(order_tool._order_skill, "db", db)  # noqa: SLF001
    monkeypatch.setattr(order_tool._customer_skill, "db", db)  # noqa: SLF001
    monkeypatch.setattr(reservation_tool._reservation_skill, "db", db)  # noqa: SLF001
    monkeypatch.setattr(analytics_tool._analytics_skill, "db", db)  # noqa: SLF001
    monkeypatch.setattr(delivery_tool._order_skill, "db", db)  # noqa: SLF001
    return db


@pytest.fixture
def clientes(entorno):
    a = entorno.crear_cliente({"nombre": "Cliente A", "telefono": "+593991111111"})
    b = entorno.crear_cliente({"nombre": "Cliente B", "telefono": "+593992222222"})
    return a, b


class _Identidad:
    """Context manager que deja la identidad limpia siempre."""

    def __init__(self, valor):
        self.valor = valor

    def __enter__(self):
        self.token = autorizacion.establecer_identidad(self.valor)
        return self

    def __exit__(self, *args):
        autorizacion.limpiar_identidad(self.token)


DENEGADO = autorizacion.DENEGADO


# ===========================================
# CLIENTES
# ===========================================

def test_customer_360_de_otro_cliente_denegado(clientes):
    a, b = clientes
    with _Identidad("+593991111111"):
        resultado = customer_tool.customer_360.invoke({"cliente_id": b})
        assert resultado == DENEGADO
        resultado = customer_tool.obtener_historial_cliente.invoke(
            {"cliente_id": b},
        )
        assert resultado == DENEGADO
        resultado = customer_tool.buscar_cliente.invoke(
            {"telefono": "+593992222222"},
        )
        assert resultado == DENEGADO
        resultado = customer_tool.crear_cliente.invoke(
            {"nombre": "Falso", "telefono": "+593992222222"},
        )
        assert resultado == DENEGADO

        # Recurso propio: permitido
        resultado = customer_tool.customer_360.invoke({"cliente_id": a})
        assert "Customer 360" in resultado
        assert "Cliente A" in resultado


def test_customer_360_sin_identidad_contexto_interno(clientes):
    """Sin identidad verificada (backend interno) el acceso no se acota."""
    _a, b = clientes
    resultado = customer_tool.customer_360.invoke({"cliente_id": b})
    assert "Customer 360" in resultado


# ===========================================
# PEDIDOS
# ===========================================

def test_pedido_ajeno_denegado_en_tools(entorno, clientes):
    a, b = clientes
    pedido_b = entorno.crear_pedido(b, "whatsapp")

    with _Identidad("+593991111111"):
        assert order_tool.consultar_estado_pedido.invoke(
            {"pedido_id": pedido_b},
        ) == DENEGADO
        assert order_tool.cancelar_pedido.invoke(
            {"pedido_id": pedido_b, "motivo": "ataque"},
        ) == DENEGADO
        assert order_tool.agregar_item_pedido.invoke(
            {"pedido_id": pedido_b, "producto_id": 1, "cantidad": 3},
        ) == DENEGADO
        assert order_tool.crear_pedido.invoke(
            {"cliente_id": b, "canal": "whatsapp"},
        ) == DENEGADO
        assert order_tool.consultar_pedido_cliente.invoke(
            {"cliente_id": b},
        ) == DENEGADO

        # El pedido de B sigue intacto
        assert entorno.obtener_pedido(pedido_b)["estado"] == "draft"

        # Recurso propio: permitido
        pedido_a = entorno.crear_pedido(a, "whatsapp")
        assert "Pedido" in order_tool.consultar_estado_pedido.invoke(
            {"pedido_id": pedido_a},
        )


# ===========================================
# RESERVAS
# ===========================================

def test_cancelar_reserva_ajena_denegada(entorno, clientes):
    _a, b = clientes
    reserva_b = entorno.crear_reserva({
        "fecha": FUTURA, "hora": "19:00", "personas": 2,
        "nombre_contacto": "Cliente B", "telefono": "+593992222222",
    })

    with _Identidad("+593991111111"):
        resultado = reservation_tool.cancelar_reserva.invoke(
            {"reserva_id": reserva_b},
        )
        assert resultado == DENEGADO

    # Sigue activa (no fue cancelada)
    reserva = entorno.obtener_reserva(reserva_b)
    assert reserva["estado"] == "pending"


def test_cancelar_reserva_propia_permitida(entorno, clientes):
    _a, _b = clientes
    reserva_a = entorno.crear_reserva({
        "fecha": FUTURA, "hora": "19:30", "personas": 2,
        "nombre_contacto": "Cliente A", "telefono": "+593991111111",
    })

    with _Identidad("+593991111111"):
        resultado = reservation_tool.cancelar_reserva.invoke(
            {"reserva_id": reserva_a},
        )
        assert "cancelada" in resultado.lower()
    assert entorno.obtener_reserva(reserva_a)["estado"] == "cancelled"


def test_crear_reserva_con_telefono_ajeno_denegada(entorno, clientes):
    _a, _b = clientes
    with _Identidad("+593991111111"):
        resultado = reservation_tool.crear_reserva.invoke({
            "fecha": FUTURA, "hora": "18:00", "personas": 2,
            "nombre": "Intruso", "telefono": "+593992222222",
        })
        assert resultado == DENEGADO

        # Con telefono propio si se crea
        resultado = reservation_tool.crear_reserva.invoke({
            "fecha": FUTURA, "hora": "18:00", "personas": 2,
            "nombre": "Cliente A", "telefono": "+593991111111",
        })
        assert "confirmada" in resultado.lower()

    reservas = entorno.obtener_reservas_por_fecha(FUTURA)
    assert len(reservas) == 1
    creada = entorno.obtener_reserva(reservas[0]["id"])
    assert creada["telefono"] == "+593991111111"


# ===========================================
# DATOS DEL NEGOCIO Y ENVIO WHATSAPP
# ===========================================

def test_metricas_solo_contexto_interno(entorno):
    assert entorno is not None
    with _Identidad("+593991111111"):
        assert analytics_tool.obtener_metricas.invoke({}) == DENEGADO

    resultado = analytics_tool.obtener_metricas.invoke({})
    assert "Metricas" in resultado


def test_envio_whatsapp_solo_al_interlocutor():
    with _Identidad("+593991111111"):
        # Nunca llega a la API real: se rechaza antes de enviar
        resultado = channel_tool.enviar_mensaje_whatsapp.invoke({
            "numero": "+593992222222",
            "mensaje": "spam",
        })
        assert resultado == DENEGADO


def test_delivery_ajeno_denegado(entorno, clientes):
    _a, b = clientes
    pedido_b = entorno.crear_pedido(b, "whatsapp")

    with _Identidad("+593991111111"):
        resultado = delivery_tool.rastrear_delivery.invoke(
            {"pedido_id": pedido_b},
        )
        assert resultado == DENEGADO
        resultado = delivery_tool.crear_envio_delivery.invoke({
            "pedido_id": pedido_b, "direccion": "Av. Falsa 123",
        })
        assert resultado == DENEGADO
