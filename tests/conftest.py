"""Configuracion de tests."""

import pytest
from database.db_manager import RestaurantDB


@pytest.fixture
def db():
    """Base de datos de prueba en memoria."""
    database = RestaurantDB("sqlite:///:memory:")
    return database


@pytest.fixture
def sample_customer(db):
    """Cliente de ejemplo."""
    return db.crear_cliente({
        "nombre": "Carlos Perez",
        "telefono": "+593999999999",
        "email": "carlos@test.com"
    })


@pytest.fixture
def sample_product(db):
    """Producto de ejemplo."""
    from database.models import Category, Product
    session = db._get_session()
    try:
        cat = Category(nombre="Pizzas")
        session.add(cat)
        session.commit()

        prod = Product(
            categoria_id=cat.id,
            nombre="Pizza Margarita",
            precio_base=12.50,
            ingredientes=["tomate", "mozzarella"]
        )
        session.add(prod)
        session.commit()
        return prod.id
    finally:
        session.close()
