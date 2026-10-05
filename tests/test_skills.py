"""Tests de skills."""

import pytest
from skills.menu.menu_skill import MenuSkill
from skills.orders.order_skill import OrderSkill


def test_menu_skill_initialize():
    skill = MenuSkill()
    assert skill.initialize({}) is True


def test_menu_skill_buscar():
    skill = MenuSkill()
    skill.initialize({})
    resultados = skill.execute("buscar", {"query": "pizza"})
    assert isinstance(resultados, list)


def test_order_skill_initialize():
    skill = OrderSkill()
    assert skill.initialize({}) is True


def test_order_skill_crear_pedido(db, sample_customer):
    skill = OrderSkill()
    skill.initialize({})
    pedido_id = skill.execute("crear_pedido", {
        "cliente_id": sample_customer,
        "canal": "whatsapp"
    })
    assert pedido_id > 0
