# PROMPT 13: scripts/ - Scripts de Utilidad

## Objetivo
Crear scripts para ingesta de datos, seeding y utilidades.

## Instrucciones Detalladas

Crear la estructura:

```
scripts/
├── seed_data.py
├── ingestar_menu.py
├── setup_google_calendar.py
└── deploy.sh
```

### seed_data.py

```python
"""Script para poblar la base de datos con datos de ejemplo."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import RestaurantDB
from database.models import Category, Product, ProductOption


def seed_database():
    db = RestaurantDB()
    session = db._get_session()
    
    try:
        # Categorías
        categorias = [
            Category(nombre="Pizzas", descripcion="Pizzas artesanales", orden=1),
            Category(nombre="Hamburguesas", descripcion="Hamburguesas premium", orden=2),
            Category(nombre="Ensaladas", descripcion="Ensaladas frescas", orden=3),
            Category(nombre="Pastas", descripcion="Pastas italianas", orden=4),
            Category(nombre="Bebidas", descripcion="Bebidas frías y calientes", orden=5),
            Category(nombre="Postres", descripcion="Postres y dulces", orden=6),
        ]
        session.add_all(categorias)
        session.commit()
        
        # Productos
        productos = [
            Product(
                categoria_id=1, nombre="Pizza Margarita",
                descripcion="Tomate, mozzarella, albahaca fresca",
                precio_base=12.50, ingredientes=["tomate", "mozzarella", "albahaca"],
                personalizable=True, tiempo_preparacion_min=20
            ),
            Product(
                categoria_id=1, nombre="Pizza Pepperoni",
                descripcion="Pepperoni artesanal, mozzarella, salsa de tomate",
                precio_base=14.00, ingredientes=["pepperoni", "mozzarella", "tomate"],
                personalizable=True, tiempo_preparacion_min=20
            ),
            Product(
                categoria_id=1, nombre="Pizza BBQ Pollo",
                descripcion="Pollo, salsa BBQ, cebolla, mozzarella",
                precio_base=16.00, ingredientes=["pollo", "bbq", "cebolla", "mozzarella"],
                personalizable=True, tiempo_preparacion_min=20
            ),
            Product(
                categoria_id=2, nombre="Hamburguesa Clásica",
                descripcion="Carne 200g, lechuga, tomate, cebolla",
                precio_base=9.00, ingredientes=["carne", "lechuga", "tomate", "cebolla"],
                personalizable=True, tiempo_preparacion_min=15
            ),
            Product(
                categoria_id=2, nombre="Hamburguesa BBQ",
                descripcion="Carne 200g, salsa BBQ, bacon, cebolla caramelizada",
                precio_base=11.00, ingredientes=["carne", "bbq", "bacon", "cebolla"],
                personalizable=True, tiempo_preparacion_min=15
            ),
            Product(
                categoria_id=5, nombre="Coca-Cola 1.5L",
                descripcion="Coca-Cola original",
                precio_base=2.00, ingredientes=["coca-cola"]
            ),
            Product(
                categoria_id=5, nombre="Agua Mineral",
                descripcion="Agua sin gas 500ml",
                precio_base=1.00, ingredientes=["agua"]
            ),
        ]
        session.add_all(productos)
        session.commit()
        
        # Opciones de Pizza Margarita
        pizza_margarita = session.query(Product).filter_by(nombre="Pizza Margarita").first()
        opciones = [
            ProductOption(producto_id=pizza_margarita.id, tipo="tamano", nombre="Personal", precio_adicional=7.00),
            ProductOption(producto_id=pizza_margarita.id, tipo="tamano", nombre="Mediana", precio_adicional=10.00),
            ProductOption(producto_id=pizza_margarita.id, tipo="tamano", nombre="Familiar", precio_adicional=12.50),
            ProductOption(producto_id=pizza_margarita.id, tipo="extra", nombre="Queso extra", precio_adicional=1.50),
            ProductOption(producto_id=pizza_margarita.id, tipo="extra", nombre="Pepperoni", precio_adicional=2.00),
            ProductOption(producto_id=pizza_margarita.id, tipo="extra", nombre="Champiñones", precio_adicional=1.00),
        ]
        session.add_all(opciones)
        session.commit()
        
        print("✓ Base de datos poblada correctamente")
        
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
```

### ingestar_menu.py

```python
"""Script para ingestar menú desde archivo JSON."""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import RestaurantDB


def ingestar_menu(json_path: str = "data/menu.json"):
    db = RestaurantDB()
    
    with open(json_path, "r", encoding="utf-8") as f:
        menu_data = json.load(f)
    
    session = db._get_session()
    
    try:
        for item in menu_data["productos"]:
            # Buscar o crear categoría
            categoria = session.query(Category).filter_by(
                nombre=item["categoria"]
            ).first()
            
            if not categoria:
                categoria = Category(nombre=item["categoria"])
                session.add(categoria)
                session.commit()
            
            # Crear producto
            producto = Product(
                categoria_id=categoria.id,
                nombre=item["nombre"],
                descripcion=item.get("descripcion", ""),
                precio_base=item["precio"],
                ingredientes=item.get("ingredientes", []),
                alergenos=item.get("alergenos", []),
                personalizable=item.get("personalizable", False),
                tiempo_preparacion_min=item.get("tiempo_preparacion", 15)
            )
            session.add(producto)
            session.commit()
            
            # Agregar opciones
            for opcion in item.get("opciones", []):
                opt = ProductOption(
                    producto_id=producto.id,
                    tipo=opcion["tipo"],
                    nombre=opcion["nombre"],
                    precio_adicional=opcion.get("precio", 0)
                )
                session.add(opt)
            
            session.commit()
            print(f"✓ {producto.nombre} agregado")
        
        print(f"\n✓ Menú ingestado: {len(menu_data['productos'])} productos")
        
    finally:
        session.close()


if __name__ == "__main__":
    ingestar_menu()
```

## Verificación
- [ ] seed_data.py crea datos de ejemplo
- [ ] ingestar_menu.py carga desde JSON
- [ ] Datos consistentes
- [ ] Scripts ejecutables
