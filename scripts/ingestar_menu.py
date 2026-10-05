"""Script para ingestar menu desde archivo JSON."""

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
            # Buscar o crear categoria
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
            print(f"Producto {producto.nombre} agregado")

        print(f"\nMenu ingestado: {len(menu_data['productos'])} productos")

    finally:
        session.close()


if __name__ == "__main__":
    ingestar_menu()
