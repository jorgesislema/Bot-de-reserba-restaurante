# PROMPT 14: tests/ - Tests del Proyecto

## Objetivo
Crear tests unitarios y de integración para todos los componentes.

## Instrucciones Detalladas

Crear la estructura:

```
tests/
├── __init__.py
├── conftest.py
├── test_database.py
├── test_skills.py
├── test_tools.py
├── test_agent.py
├── test_api.py
└── test_integracion.py
```

### conftest.py

```python
"""Configuración de tests."""

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
        "nombre": "Carlos Pérez",
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
```

### test_database.py

```python
"""Tests de base de datos."""

import pytest
from database.models import OrderStatus


def test_crear_cliente(db):
    cliente_id = db.crear_cliente({
        "nombre": "María López",
        "telefono": "+593888888888"
    })
    assert cliente_id > 0


def test_obtener_cliente(db):
    db.crear_cliente({
        "nombre": "Test",
        "telefono": "+593777777777"
    })
    cliente = db.obtener_cliente("+593777777777")
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
    
    exito = db.cancelar_pedido(pedido_id, "Cambio de opinión")
    assert exito is True


def test_verificar_disponibilidad(db):
    disponibilidad = db.verificar_disponibilidad("2026-09-20", None, 6)
    assert len(disponibilidad) > 0


def test_crear_reserva(db, sample_customer):
    reserva_id = db.crear_reserva({
        "cliente_id": sample_customer,
        "fecha": "2026-09-20",
        "hora": "20:00",
        "personas": 6,
        "nombre_contacto": "Carlos Pérez",
        "telefono": "+593999999999"
    })
    assert reserva_id > 0
```

### test_skills.py

```python
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
```

### test_tools.py

```python
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
    assert "No encontré" in resultado
```

### test_api.py

```python
"""Tests de API."""

import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_api_productos():
    response = client.get("/api/productos")
    assert response.status_code == 200


def test_api_metricas():
    response = client.get("/api/metricas")
    assert response.status_code == 200


def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.text


def test_menu_page():
    response = client.get("/menu")
    assert response.status_code == 200
```

### test_integracion.py

```python
"""Tests de integración."""

import pytest
from api.agent import process_message


def test_procesar_mensaje_menu():
    respuesta = process_message("¿Qué pizzas tienen?", thread_id="test1")
    assert isinstance(respuesta, str)
    assert len(respuesta) > 0


def test_procesar_mensaje_pedido():
    respuesta = process_message("Quiero una pizza familiar", thread_id="test2")
    assert isinstance(respuesta, str)


def test_procesar_mensaje_reserva():
    respuesta = process_message("Quiero reservar para 6 personas", thread_id="test3")
    assert isinstance(respuesta, str)


def test_conversacion_completa():
    # Simular conversación completa
    r1 = process_message("Hola", thread_id="test4")
    r2 = process_message("Quiero una pizza", thread_id="test4")
    r3 = process_message("Pepperoni", thread_id="test4")
    r4 = process_message("Familiar", thread_id="test4")
    r5 = process_message("Confirmar", thread_id="test4")
    
    assert all(isinstance(r, str) for r in [r1, r2, r3, r4, r5])
```

## Verificación
- [ ] Tests unitarios para database
- [ ] Tests unitarios para skills
- [ ] Tests unitarios para tools
- [ ] Tests de API
- [ ] Tests de integración
- [ ] Coverage > 90%
- [ ] Todos los tests pasan
