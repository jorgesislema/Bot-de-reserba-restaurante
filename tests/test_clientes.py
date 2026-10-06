"""Tests de clientes: identificacion por ID vs telefono."""

import pytest


def test_crear_cliente(db):
    cliente_id = db.crear_cliente({
        "nombre": "Ana Test",
        "telefono": "+593977777771",
        "email": "ana@test.com",
    })
    assert cliente_id > 0


def test_crear_cliente_telefono_duplicado_devuelve_existente(db):
    id1 = db.crear_cliente({"nombre": "Uno", "telefono": "+593977777772"})
    id2 = db.crear_cliente({"nombre": "Dos", "telefono": "+593977777772"})
    assert id1 == id2


def test_buscar_cliente_por_telefono(db):
    db.crear_cliente({"nombre": "Busca Telefono", "telefono": "+593977777773"})
    cliente = db.obtener_cliente_por_telefono("+593977777773")
    assert cliente is not None
    assert cliente["nombre"] == "Busca Telefono"


def test_obtener_cliente_por_id(db):
    cliente_id = db.crear_cliente({"nombre": "Por ID", "telefono": "+593977777774"})
    cliente = db.obtener_cliente_por_id(cliente_id)
    assert cliente is not None
    assert cliente["id"] == cliente_id
    assert cliente["nombre"] == "Por ID"


def test_obtener_cliente_por_id_inexistente(db):
    assert db.obtener_cliente_por_id(999999) is None


def test_obtener_por_telefono_no_confunde_con_id(db):
    """obtener_cliente_por_telefono no debe buscar por ID."""
    db.crear_cliente({"nombre": "Confusion", "telefono": "+593977777775"})
    # Un ID que existe no debe devolver nada al buscarlo como telefono
    assert db.obtener_cliente_por_telefono("1") is None


def test_buscar_cliente_por_texto(db):
    db.crear_cliente({"nombre": "Carlos Uniquename", "telefono": "+593977777776"})
    resultados = db.buscar_cliente("Uniquename")
    assert len(resultados) == 1
    assert resultados[0]["nombre"] == "Carlos Uniquename"


def test_historial_cliente(db):
    cliente_id = db.crear_cliente({"nombre": "Hist", "telefono": "+593977777777"})
    historial = db.obtener_historial(cliente_id)
    assert "pedidos" in historial
    assert "reservas" in historial


def test_crear_cliente_skill_por_id_y_telefono(db):
    from skills.customers.customer_skill import CustomerSkill

    skill = CustomerSkill()
    skill.initialize({})

    cliente_id = skill.execute("crear_cliente", {
        "nombre": "Skill Test", "telefono": "+593977777778"
    })

    por_id = skill.execute("obtener_cliente_por_id", {"cliente_id": cliente_id})
    por_tel = skill.execute(
        "obtener_cliente_por_telefono", {"telefono": "+593977777778"}
    )

    assert por_id["id"] == cliente_id
    assert por_tel["id"] == cliente_id
    assert por_id["nombre"] == "Skill Test"


def test_customer_360_usa_cliente_id():
    """La tool customer_360 debe buscar por ID, no por telefono vacio.

    Las tools instancian su propia BD (la configurada por DATABASE_URL),
    por eso este test usa RestaurantDB() por defecto y limpia despues.
    """
    from database.db_manager import RestaurantDB
    from tools.customer_tool import customer_360

    db_default = RestaurantDB()
    cliente_id = db_default.crear_cliente(
        {"nombre": "Vista 360", "telefono": "+593977777779"}
    )
    try:
        resultado = customer_360.invoke({"cliente_id": cliente_id})
        assert "Vista 360" in resultado
        assert "No encontre" not in resultado
    finally:
        session = db_default._get_session()
        try:
            from database.models import Customer
            cliente = session.query(Customer).filter_by(id=cliente_id).first()
            if cliente:
                session.delete(cliente)
                session.commit()
        finally:
            session.close()


def test_customer_360_id_inexistente():
    from tools.customer_tool import customer_360

    resultado = customer_360.invoke({"cliente_id": 999999})
    assert "No encontre" in resultado
