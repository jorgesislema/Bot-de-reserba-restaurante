"""Script para poblar la base de datos con datos de ejemplo."""

import sys
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import RestaurantDB
from database.models import (
    Category, Product, ProductOption,
    Customer, CustomerPreference, CustomerSegment,
    Order, OrderItem, OrderStateHistory, OrderStatus,
    Reservation, ReservationStatus,
    Delivery, DeliveryStatus, DeliveryZone,
    Promotion, PromotionRule,
    AnalyticsInteraction, ChannelType
)


def seed_database():
    db = RestaurantDB()

    # Limpiar tablas existentes
    from database.models import Base
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)

    print("Tablas reiniciadas")

    session = db._get_session()

    try:
        # ===========================================
        # CATEGORIAS
        # ===========================================
        categorias = [
            Category(nombre="Pizzas", descripcion="Pizzas artesanales al horno de lena", orden=1),
            Category(nombre="Hamburguesas", descripcion="Hamburguesas premium 100% carne angus", orden=2),
            Category(nombre="Ensaladas", descripcion="Ensaladas frescas de la finca", orden=3),
            Category(nombre="Pastas", descripcion="Pastas italianas caseras", orden=4),
            Category(nombre="Bebidas", descripcion="Bebidas frias y calientes", orden=5),
            Category(nombre="Postres", descripcion="Postres artesanales", orden=6),
            Category(nombre="Combos", descripcion="Combos especiales", orden=7),
            Category(nombre="Entradas", descripcion="Para compartir", orden=8),
        ]
        session.add_all(categorias)
        session.commit()

        # ===========================================
        # PRODUCTOS
        # ===========================================
        productos = [
            # PIZZAS
            Product(categoria_id=1, nombre="Pizza Margarita",
                    descripcion="Tomate, mozzarella, albahaca fresca",
                    precio_base=12.50, ingredientes=["tomate", "mozzarella", "albahaca"],
                    alergenos=["gluten", "lactosa"], personalizable=True, tiempo_preparacion_min=20),
            Product(categoria_id=1, nombre="Pizza Pepperoni",
                    descripcion="Pepperoni artesanal, mozzarella, salsa de tomate",
                    precio_base=14.00, ingredientes=["pepperoni", "mozzarella", "tomate"],
                    alergenos=["gluten", "lactosa"], personalizable=True, tiempo_preparacion_min=20),
            Product(categoria_id=1, nombre="Pizza BBQ Pollo",
                    descripcion="Pollo deshebrado, salsa BBQ, cebolla, mozzarella",
                    precio_base=16.00, ingredientes=["pollo", "bbq", "cebolla", "mozzarella"],
                    alergenos=["gluten", "lactosa"], personalizable=True, tiempo_preparacion_min=20),
            Product(categoria_id=1, nombre="Pizza Cuatro Quesos",
                    descripcion="Mozzarella, gorgonzola, parmesano, fontina",
                    precio_base=15.00, ingredientes=["mozzarella", "gorgonzola", "parmesano", "fontina"],
                    alergenos=["gluten", "lactosa"], personalizable=True, tiempo_preparacion_min=20),
            Product(categoria_id=1, nombre="Pizza Vegetariana",
                    descripcion="Pimiento, champinon, aceituna, cebolla, tomate",
                    precio_base=13.00, ingredientes=["pimiento", "champinon", "aceituna", "cebolla", "tomate"],
                    alergenos=["gluten"], personalizable=True, tiempo_preparacion_min=20),
            Product(categoria_id=1, nombre="Pizza Hawaiana",
                    descripcion="Jamón, piña, mozzarella",
                    precio_base=14.50, ingredientes=["jamón", "piña", "mozzarella"],
                    alergenos=["gluten", "lactosa"], personalizable=True, tiempo_preparacion_min=20),

            # HAMBURGUESAS
            Product(categoria_id=2, nombre="Hamburguesa Clasica",
                    descripcion="Carne 200g, lechuga, tomate, cebolla, salsa especial",
                    precio_base=9.00, ingredientes=["carne", "lechuga", "tomate", "cebolla"],
                    alergenos=["gluten"], personalizable=True, tiempo_preparacion_min=15),
            Product(categoria_id=2, nombre="Hamburguesa BBQ Bacon",
                    descripcion="Carne 200g, salsa BBQ, bacon crocante, cebolla caramelizada",
                    precio_base=11.50, ingredientes=["carne", "bbq", "bacon", "cebolla"],
                    alergenos=["gluten"], personalizable=True, tiempo_preparacion_min=15),
            Product(categoria_id=2, nombre="Hamburguesa Doble",
                    descripcion="Doble carne 400g, doble queso, lechuga, tomate",
                    precio_base=14.00, ingredientes=["carne", "doble queso", "lechuga", "tomate"],
                    alergenos=["gluten", "lactosa"], personalizable=True, tiempo_preparacion_min=18),
            Product(categoria_id=2, nombre="Hamburguesa Vegana",
                    descripcion="Patty de lentejas, aguacate, tomate, lechuga",
                    precio_base=10.00, ingredientes=["lentejas", "aguacate", "tomate", "lechuga"],
                    personalizable=True, tiempo_preparacion_min=15),

            # ENSALADAS
            Product(categoria_id=3, nombre="Ensalada Cesar",
                    descripcion="Lechuga romana, crutones, parmesano, adereso Cesar",
                    precio_base=7.50, ingredientes=["lechuga", "crutones", "parmesano"],
                    alergenos=["gluten", "lactosa", "huevo"]),
            Product(categoria_id=3, nombre="Ensalada Mediterranea",
                    descripcion="Tomate, pepino, aceituna, queso feta, aceite de oliva",
                    precio_base=8.00, ingredientes=["tomate", "pepino", "aceituna", "queso feta"],
                    alergenos=["lactosa"]),
            Product(categoria_id=3, nombre="Ensalada de Pollo",
                    descripcion="Pollo a la parrilla, aguacate, mango, vinagreta",
                    precio_base=9.50, ingredientes=["pollo", "aguacate", "mango"],
                    personalizable=True),

            # PASTAS
            Product(categoria_id=4, nombre="Espagueti Bolognesa",
                    descripcion="Espagueti casero, ragu de carne, parmesano",
                    precio_base=10.00, ingredientes=["espagueti", "carne", "tomate", "parmesano"],
                    alergenos=["gluten", "lactosa"], tiempo_preparacion_min=18),
            Product(categoria_id=4, nombre="Fettuccini Alfredo",
                    descripcion="Fettuccini, salsa cremosa de queso parmesano",
                    precio_base=11.00, ingredientes=["fettuccini", "crema", "parmesano"],
                    alergenos=["gluten", "lactosa"], tiempo_preparacion_min=18),
            Product(categoria_id=4, nombre="Penne Arrabiata",
                    descripcion="Penne, salsa de tomate picante, albahaca",
                    precio_base=9.00, ingredientes=["penne", "tomate", "albahaca"],
                    alergenos=["gluten"], tiempo_preparacion_min=15),
            Product(categoria_id=4, nombre="Lasagna Classica",
                    descripcion="Laminas de pasta, ragu, bechamel, mozzarella",
                    precio_base=13.00, ingredientes=["pasta", "carne", "bechamel", "mozzarella"],
                    alergenos=["gluten", "lactosa"], tiempo_preparacion_min=25),

            # BEBIDAS
            Product(categoria_id=5, nombre="Coca-Cola 1.5L",
                    descripcion="Coca-Cola original 1.5 litros",
                    precio_base=2.50, ingredientes=["coca-cola"]),
            Product(categoria_id=5, nombre="Coca-Cola 350ml",
                    descripcion="Lata de Coca-Cola",
                    precio_base=1.25, ingredientes=["coca-cola"]),
            Product(categoria_id=5, nombre="Agua Mineral 500ml",
                    descripcion="Agua sin gas",
                    precio_base=1.00, ingredientes=["agua"]),
            Product(categoria_id=5, nombre="Jugo Natural",
                    descripcion="Naranja, maracuya o limon",
                    precio_base=2.00, ingredientes=["fruta natural"]),
            Product(categoria_id=5, nombre="Cerveza Artesanal",
                    descripcion="Rubia, roja o negra - 355ml",
                    precio_base=3.50, ingredientes=["cerveza"]),
            Product(categoria_id=5, nombre="Limonada Natural",
                    descripcion="Limonada fresca con hierbabuena",
                    precio_base=2.00, ingredientes=["limon", "hierbabuena"]),
            Product(categoria_id=5, nombre="Cafe Americano",
                    descripcion="Cafe recien preparado",
                    precio_base=1.50, ingredientes=["cafe"]),
            Product(categoria_id=5, nombre="Te Caliente",
                    descripcion="Te verde, negro o de manzanilla",
                    precio_base=1.25, ingredientes=["te"]),

            # POSTRES
            Product(categoria_id=6, nombre="Tiramisu",
                    descripcion="Postre italiano con cafe y mascarpone",
                    precio_base=5.50, ingredientes=["cafe", "mascarpone", "cacao"],
                    alergenos=["gluten", "lactosa", "huevo"]),
            Product(categoria_id=6, nombre="Brownie con Helado",
                    descripcion="Brownie de chocolate con helado de vainilla",
                    precio_base=6.00, ingredientes=["chocolate", "helado"],
                    alergenos=["gluten", "lactosa", "huevo"]),
            Product(categoria_id=6, nombre="Cheesecake",
                    descripcion="Torta de queso con frutos rojos",
                    precio_base=5.00, ingredientes=["queso crema", "frutos rojos"],
                    alergenos=["gluten", "lactosa", "huevo"]),
            Product(categoria_id=6, nombre="Helado Artesanal",
                    descripcion="3 bolas: vainilla, chocolate, fresa",
                    precio_base=4.00, ingredientes=["leche", "crema"],
                    alergenos=["lactosa"]),

            # ENTRADAS
            Product(categoria_id=8, nombre="Alitas BBQ",
                    descripcion="12 alitas de pollo con salsa BBQ",
                    precio_base=7.00, ingredientes=["pollo", "bbq"],
                    alergenos=["gluten"]),
            Product(categoria_id=8, nombre="Nachos Supreme",
                    descripcion="Nachos con queso, guacamole, crema, jalapeños",
                    precio_base=6.50, ingredientes=["nachos", "queso", "aguacate", "crema"],
                    alergenos=["lactosa"]),
            Product(categoria_id=8, nombre="Croquetas de Jamon",
                    descripcion="6 croquetas caseras de jamon",
                    precio_base=5.50, ingredientes=["jamon", "bechamel"],
                    alergenos=["gluten", "lactosa"]),
            Product(categoria_id=8, nombre="Bruschetta",
                    descripcion="Pan tostado con tomate, albahaca y aceite de oliva",
                    precio_base=4.50, ingredientes=["pan", "tomate", "albahaca"],
                    alergenos=["gluten"]),

            # COMBOS
            Product(categoria_id=7, nombre="Combo Pareja",
                    descripcion="Pizza mediana + 2 bebidas + postre",
                    precio_base=22.00, ingredientes=["pizza", "bebida", "postre"],
                    personalizable=True),
            Product(categoria_id=7, nombre="Combo Familiar",
                    descripcion="Pizza familiar + 2 hamburguesas + 4 bebidas",
                    precio_base=35.00, ingredientes=["pizza", "hamburguesa", "bebida"],
                    personalizable=True),
            Product(categoria_id=7, nombre="Combo Ejecutivo",
                    descripcion="Ensalada + pasta + bebida",
                    precio_base=15.00, ingredientes=["ensalada", "pasta", "bebida"]),
        ]
        session.add_all(productos)
        session.commit()

        # ===========================================
        # OPCIONES DE PRODUCTOS
        # ===========================================
        # Pizza Margarita
        pizza_margarita = session.query(Product).filter_by(nombre="Pizza Margarita").first()
        session.add_all([
            ProductOption(producto_id=pizza_margarita.id, tipo="tamano", nombre="Personal", precio_adicional=7.00),
            ProductOption(producto_id=pizza_margarita.id, tipo="tamano", nombre="Mediana", precio_adicional=10.00),
            ProductOption(producto_id=pizza_margarita.id, tipo="tamano", nombre="Familiar", precio_adicional=12.50),
            ProductOption(producto_id=pizza_margarita.id, tipo="extra", nombre="Queso extra", precio_adicional=1.50),
            ProductOption(producto_id=pizza_margarita.id, tipo="extra", nombre="Pepperoni", precio_adicional=2.00),
            ProductOption(producto_id=pizza_margarita.id, tipo="extra", nombre="Champinones", precio_adicional=1.00),
        ])

        # Hamburguesa Clasica
        hamburguesa = session.query(Product).filter_by(nombre="Hamburguesa Clasica").first()
        session.add_all([
            ProductOption(producto_id=hamburguesa.id, tipo="extra", nombre="Bacon", precio_adicional=1.50),
            ProductOption(producto_id=hamburguesa.id, tipo="extra", nombre="Queso cheddar", precio_adicional=1.00),
            ProductOption(producto_id=hamburguesa.id, tipo="extra", nombre="Aguacate", precio_adicional=1.50),
            ProductOption(producto_id=hamburguesa.id, tipo="tamano", nombre="Doble carne", precio_adicional=4.00),
        ])

        # Espagueti
        espagueti = session.query(Product).filter_by(nombre="Espagueti Bolognesa").first()
        session.add_all([
            ProductOption(producto_id=espagueti.id, tipo="extra", nombre="Queso parmesano", precio_adicional=1.00),
            ProductOption(producto_id=espagueti.id, tipo="extra", nombre="Tocino", precio_adicional=1.50),
        ])

        session.commit()

        # ===========================================
        # CLIENTES
        # ===========================================
        clientes_datos = [
            {"nombre": "Carlos Perez", "telefono": "+593991234567", "email": "carlos@gmail.com", "canal": "whatsapp", "total_pedidos": 42, "valor": 1250.00, "segmento": CustomerSegment.HIGH_VALUE},
            {"nombre": "Maria Lopez", "telefono": "+593992345678", "email": "maria@hotmail.com", "canal": "whatsapp", "total_pedidos": 28, "valor": 680.50, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Andres Martinez", "telefono": "+593993456789", "email": "andres@yahoo.com", "canal": "telegram", "total_pedidos": 5, "valor": 95.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Laura Garcia", "telefono": "+593994567890", "email": "laura@gmail.com", "canal": "whatsapp", "total_pedidos": 56, "valor": 1580.00, "segmento": CustomerSegment.VIP},
            {"nombre": "Roberto Sanchez", "telefono": "+593995678901", "email": "roberto@outlook.com", "canal": "webchat", "total_pedidos": 2, "valor": 45.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Elena Rodriguez", "telefono": "+593996789012", "email": "elena@gmail.com", "canal": "whatsapp", "total_pedidos": 73, "valor": 2100.00, "segmento": CustomerSegment.VIP},
            {"nombre": "Diego Torres", "telefono": "+593997890123", "email": "diego@yahoo.com", "canal": "telegram", "total_pedidos": 19, "valor": 425.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Sofia Hernandez", "telefono": "+593998901234", "email": "sofia@gmail.com", "canal": "whatsapp", "total_pedidos": 8, "valor": 195.50, "segmento": CustomerSegment.NEW},
            {"nombre": "Javier Morales", "telefono": "+593999012345", "email": "javier@hotmail.com", "canal": "whatsapp", "total_pedidos": 3, "valor": 67.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Camila Vargas", "telefono": "+593990123456", "email": "camila@gmail.com", "canal": "telegram", "total_pedidos": 45, "valor": 1320.00, "segmento": CustomerSegment.HIGH_VALUE},
            {"nombre": "Miguel Flores", "telefono": "+593991112233", "email": "miguel@outlook.com", "canal": "whatsapp", "total_pedidos": 31, "valor": 780.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Isabella Castro", "telefono": "+593992223344", "email": "isabella@gmail.com", "canal": "webchat", "total_pedidos": 12, "valor": 285.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Pablo Ruiz", "telefono": "+593993334455", "email": "pablo@gmail.com", "canal": "whatsapp", "total_pedidos": 67, "valor": 1890.00, "segmento": CustomerSegment.VIP},
            {"nombre": "Ana Gutierrez", "telefono": "+593994445566", "email": "ana@yahoo.com", "canal": "telegram", "total_pedidos": 15, "valor": 340.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Luis Mendoza", "telefono": "+593995556677", "email": "luis@hotmail.com", "canal": "whatsapp", "total_pedidos": 4, "valor": 88.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Carmen Silva", "telefono": "+593996667788", "email": "carmen@gmail.com", "canal": "whatsapp", "total_pedidos": 38, "valor": 920.00, "segmento": CustomerSegment.HIGH_VALUE},
            {"nombre": "Fernando Reyes", "telefono": "+593997778899", "email": "fernando@outlook.com", "canal": "telegram", "total_pedidos": 22, "valor": 510.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Patricia Luna", "telefono": "+593998889900", "email": "patricia@gmail.com", "canal": "webchat", "total_pedidos": 7, "valor": 155.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Ricardo Ortega", "telefono": "+593999990011", "email": "ricardo@yahoo.com", "canal": "whatsapp", "total_pedidos": 51, "valor": 1450.00, "segmento": CustomerSegment.VIP},
            {"nombre": "Monica Delgado", "telefono": "+593990001122", "email": "monica@hotmail.com", "canal": "whatsapp", "total_pedidos": 11, "valor": 265.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Alejandro Vega", "telefono": "+593991113344", "email": "alejandro@gmail.com", "canal": "telegram", "total_pedidos": 33, "valor": 810.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Lucia Ramos", "telefono": "+593992224455", "email": "lucia@outlook.com", "canal": "whatsapp", "total_pedidos": 18, "valor": 420.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Gabriel Torres", "telefono": "+593993335566", "email": "gabriel@yahoo.com", "canal": "webchat", "total_pedidos": 6, "valor": 130.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Valeria Cruz", "telefono": "+593994446677", "email": "valeria@gmail.com", "canal": "whatsapp", "total_pedidos": 48, "valor": 1380.00, "segmento": CustomerSegment.HIGH_VALUE},
            {"nombre": "Oscar Medina", "telefono": "+593995557788", "email": "oscar@hotmail.com", "canal": "telegram", "total_pedidos": 9, "valor": 210.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Teresa Navarro", "telefono": "+593996668899", "email": "teresa@gmail.com", "canal": "whatsapp", "total_pedidos": 25, "valor": 590.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Jorge Castillo", "telefono": "+593997779900", "email": "jorge@outlook.com", "canal": "whatsapp", "total_pedidos": 40, "valor": 1100.00, "segmento": CustomerSegment.HIGH_VALUE},
            {"nombre": "Adriana Rojas", "telefono": "+593998880011", "email": "adriana@yahoo.com", "canal": "telegram", "total_pedidos": 14, "valor": 320.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Fernando Aguilar", "telefono": "+593999991122", "email": "fernando@gmail.com", "canal": "webchat", "total_pedidos": 2, "valor": 38.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Diana Paredes", "telefono": "+593990002233", "email": "diana@hotmail.com", "canal": "whatsapp", "total_pedidos": 36, "valor": 850.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Sergio Fuentes", "telefono": "+593991114455", "email": "sergio@gmail.com", "canal": "telegram", "total_pedidos": 60, "valor": 1720.00, "segmento": CustomerSegment.VIP},
            {"nombre": "Gloria Espinoza", "telefono": "+593992225566", "email": "gloria@outlook.com", "canal": "whatsapp", "total_pedidos": 10, "valor": 230.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Hector Salazar", "telefono": "+593993336677", "email": "hector@yahoo.com", "canal": "whatsapp", "total_pedidos": 27, "valor": 640.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Rosa Jimenez", "telefono": "+593994447788", "email": "rosa@gmail.com", "canal": "telegram", "total_pedidos": 44, "valor": 1280.00, "segmento": CustomerSegment.HIGH_VALUE},
            {"nombre": "Marco Diaz", "telefono": "+593995558899", "email": "marco@hotmail.com", "canal": "webchat", "total_pedidos": 5, "valor": 110.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Claudia Herrera", "telefono": "+593996669900", "email": "claudia@gmail.com", "canal": "whatsapp", "total_pedidos": 55, "valor": 1540.00, "segmento": CustomerSegment.VIP},
            {"nombre": "Victor Soto", "telefono": "+593997770011", "email": "victor@outlook.com", "canal": "telegram", "total_pedidos": 16, "valor": 370.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Marta Peña", "telefono": "+593998881122", "email": "marta@yahoo.com", "canal": "whatsapp", "total_pedidos": 8, "valor": 185.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Andres Copa", "telefono": "+593999992233", "email": "andres@gmail.com", "canal": "whatsapp", "total_pedidos": 30, "valor": 720.00, "segmento": CustomerSegment.FREQUENT},
            {"nombre": "Paola Carrion", "telefono": "+593990003344", "email": "paola@hotmail.com", "canal": "telegram", "total_pedidos": 13, "valor": 295.00, "segmento": CustomerSegment.NEW},
            {"nombre": "Eduardo Plaza", "telefono": "+593991115566", "email": "eduardo@gmail.com", "canal": "webchat", "total_pedidos": 21, "valor": 480.00, "segmento": CustomerSegment.FREQUENT},
        ]

        clientes_ids = []
        for c in clientes_datos:
            cliente = Customer(
                nombre=c["nombre"], telefono=c["telefono"], email=c["email"],
                canal_preferido=ChannelType(c["canal"]),
                total_pedidos=c["total_pedidos"],
                valor_acumulado=Decimal(str(c["valor"])),
                segmento=c["segmento"],
                ultimo_pedido=datetime.utcnow() - timedelta(days=1)
            )
            session.add(cliente)
            session.commit()
            clientes_ids.append(cliente.id)

        # ===========================================
        # PREFERENCIAS DE CLIENTES
        # ===========================================
        preferencias = [
            CustomerPreference(cliente_id=clientes_ids[0], tipo="favorito", valor="Pizza Pepperoni"),
            CustomerPreference(cliente_id=clientes_ids[0], tipo="favorito", valor="Coca-Cola"),
            CustomerPreference(cliente_id=clientes_ids[1], tipo="favorito", valor="Ensalada Cesar"),
            CustomerPreference(cliente_id=clientes_ids[1], tipo="favorito", valor="Jugo Natural"),
            CustomerPreference(cliente_id=clientes_ids[3], tipo="favorito", valor="Pizza BBQ Pollo"),
            CustomerPreference(cliente_id=clientes_ids[3], tipo="favorito", valor="Cerveza Artesanal"),
            CustomerPreference(cliente_id=clientes_ids[3], tipo="alergia", valor="Gluten"),
            CustomerPreference(cliente_id=clientes_ids[5], tipo="favorito", valor="Lasagna Classica"),
            CustomerPreference(cliente_id=clientes_ids[5], tipo="favorito", valor="Tiramisu"),
            CustomerPreference(cliente_id=clientes_ids[9], tipo="favorito", valor="Hamburguesa Doble"),
            CustomerPreference(cliente_id=clientes_ids[9], tipo="dislikes", valor="Picante"),
            CustomerPreference(cliente_id=clientes_ids[12], tipo="favorito", valor="Pizza Cuatro Quesos"),
            CustomerPreference(cliente_id=clientes_ids[12], tipo="favorito", valor="Brownie con Helado"),
            CustomerPreference(cliente_id=clientes_ids[15], tipo="favorito", valor="Fettuccini Alfredo"),
            CustomerPreference(cliente_id=clientes_ids[15], tipo="alergia", valor="Frutos secos"),
            CustomerPreference(cliente_id=clientes_ids[18], tipo="favorito", valor="Combo Familiar"),
            CustomerPreference(cliente_id=clientes_ids[18], tipo="favorito", valor="Cerveza Artesanal"),
            CustomerPreference(cliente_id=clientes_ids[20], tipo="favorito", valor="Penne Arrabiata"),
            CustomerPreference(cliente_id=clientes_ids[23], tipo="favorito", valor="Hamburguesa Vegana"),
            CustomerPreference(cliente_id=clientes_ids[26], tipo="favorito", valor="Ensalada Mediterranea"),
            CustomerPreference(cliente_id=clientes_ids[30], tipo="favorito", valor="Espagueti Bolognesa"),
            CustomerPreference(cliente_id=clientes_ids[30], tipo="favorito", valor="Cheesecake"),
            CustomerPreference(cliente_id=clientes_ids[35], tipo="favorito", valor="Pizza Hawaiana"),
            CustomerPreference(cliente_id=clientes_ids[37], tipo="alergia", valor="Lactosa"),
        ]
        session.add_all(preferencias)
        session.commit()

        # ===========================================
        # PEDIDOS
        # ===========================================
        ahora = datetime.utcnow()
        pedidos_datos = []
        estados = [OrderStatus.COMPLETED, OrderStatus.COMPLETED, OrderStatus.COMPLETED,
                   OrderStatus.COMPLETED, OrderStatus.COMPLETED, OrderStatus.COMPLETED,
                   OrderStatus.PREPARING, OrderStatus.CONFIRMED, OrderStatus.READY,
                   OrderStatus.DELIVERING, OrderStatus.DRAFT]
        canales_pedidos = ["whatsapp", "telegram", "webchat"]

        for i in range(65):
            estado = estados[i % len(estados)]
            total = round(15 + (i * 3.7) % 55, 2)
            delivery = 2.00 if i % 3 != 0 else 0
            descuento = 5.00 if i % 7 == 0 else 0
            subtotal = round(total + descuento - delivery, 2)
            dia = i // 8
            horas_atras = (i % 8) * 3 + dia * 24
            numero = f"#2026{9:02d}{18 - dia:02d}{i + 1:04d}"
            pedidos_datos.append((
                clientes_ids[i % len(clientes_ids)], numero, estado,
                subtotal, delivery, 0, descuento, round(subtotal + delivery - descuento, 2),
                canales_pedidos[i % 3], horas_atras
            ))

        pedidos_ids = []
        for p in pedidos_datos:
            pedido = Order(
                cliente_id=p[0], numero_pedido=p[1], estado=p[2],
                subtotal=Decimal(str(p[3])), delivery_cost=Decimal(str(p[4])),
                impuestos=Decimal(str(p[5])), descuento=Decimal(str(p[6])),
                total=Decimal(str(p[7])), canal=ChannelType(p[8]),
                created_at=ahora - timedelta(hours=p[9])
            )
            session.add(pedido)
            session.commit()
            pedidos_ids.append(pedido.id)

            historial = OrderStateHistory(
                pedido_id=pedido.id, estado=p[2],
                comentario="Estado actual"
            )
            session.add(historial)
        session.commit()

        # ===========================================
        # ITEMS DE PEDIDOS (generados automaticamente)
        # ===========================================
        pizza_pep = session.query(Product).filter_by(nombre="Pizza Pepperoni").first()
        pizza_bbq = session.query(Product).filter_by(nombre="Pizza BBQ Pollo").first()
        pizza_marg = session.query(Product).filter_by(nombre="Pizza Margarita").first()
        hamb_clas = session.query(Product).filter_by(nombre="Hamburguesa Clasica").first()
        hamb_bbq = session.query(Product).filter_by(nombre="Hamburguesa BBQ Bacon").first()
        ensalada = session.query(Product).filter_by(nombre="Ensalada Cesar").first()
        espagueti = session.query(Product).filter_by(nombre="Espagueti Bolognesa").first()
        lasagna = session.query(Product).filter_by(nombre="Lasagna Classica").first()
        tiramisu = session.query(Product).filter_by(nombre="Tiramisu").first()
        coca15 = session.query(Product).filter_by(nombre="Coca-Cola 1.5L").first()
        coca350 = session.query(Product).filter_by(nombre="Coca-Cola 350ml").first()
        agua = session.query(Product).filter_by(nombre="Agua Mineral 500ml").first()
        jugo = session.query(Product).filter_by(nombre="Jugo Natural").first()
        cerveza = session.query(Product).filter_by(nombre="Cerveza Artesanal").first()
        alitas = session.query(Product).filter_by(nombre="Alitas BBQ").first()
        nachos = session.query(Product).filter_by(nombre="Nachos Supreme").first()
        combo_pareja = session.query(Product).filter_by(nombre="Combo Pareja").first()
        combo_familiar = session.query(Product).filter_by(nombre="Combo Familiar").first()
        brownie = session.query(Product).filter_by(nombre="Brownie con Helado").first()
        cheesecake = session.query(Product).filter_by(nombre="Cheesecake").first()
        croquetas = session.query(Product).filter_by(nombre="Croquetas de Jamon").first()
        bruschetta = session.query(Product).filter_by(nombre="Bruschetta").first()
        hamb_doble = session.query(Product).filter_by(nombre="Hamburguesa Doble").first()
        hamb_vegana = session.query(Product).filter_by(nombre="Hamburguesa Vegana").first()
        pizza_4quesos = session.query(Product).filter_by(nombre="Pizza Cuatro Quesos").first()
        pizza_veg = session.query(Product).filter_by(nombre="Pizza Vegetariana").first()
        pizza_haw = session.query(Product).filter_by(nombre="Pizza Hawaiana").first()
        fettuccini = session.query(Product).filter_by(nombre="Fettuccini Alfredo").first()
        penne = session.query(Product).filter_by(nombre="Penne Arrabiata").first()
        ens_med = session.query(Product).filter_by(nombre="Ensalada Mediterranea").first()
        ens_pollo = session.query(Product).filter_by(nombre="Ensalada de Pollo").first()
        limonada = session.query(Product).filter_by(nombre="Limonada Natural").first()
        cafe = session.query(Product).filter_by(nombre="Cafe Americano").first()
        te = session.query(Product).filter_by(nombre="Te Caliente").first()
        helado = session.query(Product).filter_by(nombre="Helado Artesanal").first()

        todos_productos = [pizza_pep, pizza_bbq, pizza_marg, hamb_clas, hamb_bbq,
                          ensalada, espagueti, lasagna, tiramisu, coca15, coca350,
                          agua, jugo, cerveza, alitas, nachos, combo_pareja, combo_familiar,
                          brownie, cheesecake, croquetas, bruschetta, hamb_doble, hamb_vegana,
                          pizza_4quesos, pizza_veg, pizza_haw, fettuccini, penne, ens_med,
                          ens_pollo, limonada, cafe, te, helado]

        items_datos = []
        precios = {
            pizza_pep.id: 14.00, pizza_bbq.id: 16.00, pizza_marg.id: 12.50,
            hamb_clas.id: 9.00, hamb_bbq.id: 11.50, ensalada.id: 7.50,
            espagueti.id: 10.00, lasagna.id: 13.00, tiramisu.id: 5.50,
            coca15.id: 2.50, coca350.id: 1.25, agua.id: 1.00,
            jugo.id: 2.00, cerveza.id: 3.50, alitas.id: 7.00,
            nachos.id: 6.50, combo_pareja.id: 22.00, combo_familiar.id: 35.00,
            brownie.id: 6.00, cheesecake.id: 5.00, croquetas.id: 5.50,
            bruschetta.id: 4.50, hamb_doble.id: 14.00, hamb_vegana.id: 10.00,
            pizza_4quesos.id: 15.00, pizza_veg.id: 13.00, pizza_haw.id: 14.50,
            fettuccini.id: 11.00, penne.id: 9.00, ens_med.id: 8.00,
            ens_pollo.id: 9.50, limonada.id: 2.00, cafe.id: 1.50,
            te.id: 1.25, helado.id: 4.00,
        }

        for pedido_idx in range(len(pedidos_ids)):
            num_items = 1 + (pedido_idx % 4)
            for j in range(num_items):
                prod = todos_productos[(pedido_idx * 3 + j) % len(todos_productos)]
                precio = precios.get(prod.id, 10.00)
                cant = 1 if j == 0 else (1 + j % 2)
                items_datos.append((
                    pedidos_ids[pedido_idx], prod.id, cant,
                    precio, round(precio * cant, 2), None
                ))

        for item in items_datos:
            order_item = OrderItem(
                pedido_id=item[0], producto_id=item[1], cantidad=item[2],
                precio_unitario=Decimal(str(item[3])),
                precio_total=Decimal(str(item[4])),
                opciones_seleccionadas=item[5]
            )
            session.add(order_item)
        session.commit()

        # ===========================================
        # RESERVAS
        # ===========================================
        hoy = date.today()
        nombres_reservas = ["Carlos Perez", "Maria Lopez", "Laura Garcia", "Elena Rodriguez",
                           "Camila Vargas", "Diego Torres", "Isabella Castro", "Pablo Ruiz",
                           "Carmen Silva", "Fernando Reyes", "Ricardo Ortega", "Alejandro Vega",
                           "Lucia Ramos", "Valeria Cruz", "Teresa Navarro", "Jorge Castillo",
                           "Claudia Herrera", "Victor Soto", "Sergio Fuentes", "Rosa Jimenez",
                           "Marco Diaz", "Andres Copa", "Eduardo Plaza", "Hector Salazar",
                           "Adriana Rojas", "Diana Paredes", "Monica Delgado", "Gloria Espinoza",
                           "Marta Pena", "Paola Carrion"]
        tel_reservas = ["+593991234567", "+593992345678", "+593994567890", "+593996789012",
                       "+593990123456", "+593997890123", "+593992223344", "+593993334455",
                       "+593996667788", "+593997778899", "+593999990011", "+593991113344",
                       "+593992224455", "+593994446677", "+593996668899", "+593997779900",
                       "+593996669900", "+593997770011", "+593991115566", "+593994447788",
                       "+593995558899", "+593999992233", "+593991115566", "+593997770011",
                       "+593998881122", "+593990002233", "+593990001122", "+593998880011",
                       "+593998881122", "+593990003344"]
        horas_reserva = [time(19, 0), time(19, 30), time(20, 0), time(20, 30), time(21, 0)]
        personas_res = [2, 4, 6, 8, 10, 12, 15, 3, 5, 7]

        reservas_datos = []
        for i in range(30):
            dia_offset = (i // 5) - 2
            fecha = hoy + timedelta(days=dia_offset)
            hora = horas_reserva[i % 5]
            personas = personas_res[i % 10]
            estado_r = ReservationStatus.CONFIRMED if i < 20 else ReservationStatus.PENDING
            if dia_offset < -3:
                estado_r = ReservationStatus.COMPLETED

            reservas_datos.append((
                clientes_ids[i % len(clientes_ids)], fecha, hora, personas,
                nombres_reservas[i], tel_reservas[i], estado_r,
                {"terraza": True} if i % 3 == 0 else ({"interior": True} if i % 3 == 1 else {"privado": True})
            ))

        for r in reservas_datos:
            reserva = Reservation(
                cliente_id=r[0], fecha=r[1], hora=r[2], personas=r[3],
                nombre_contacto=r[4], telefono=r[5], estado=r[6], preferencias=r[7]
            )
            session.add(reserva)
        session.commit()

        # ===========================================
        # DELIVERIES
        # ===========================================
        direcciones = [
            ("Av. Amazonas N36-50 y Naciones Unidas", "Torre 2, piso 5", -0.1807, -78.4678, "Zona 1"),
            ("Calle Larga 123 y 10 de Agosto", "Frente al parque", -0.1850, -78.4700, "Zona 2"),
            ("Av. Eloy Alfaro 456", "Conjunto Las Flores", -0.1750, -78.4650, "Zona 1"),
            ("Calle Principal 789", "Casa esquinera", -0.1900, -78.4720, "Zona 3"),
            ("Av. Republica del Salvador 321", "Edificio torre alta", -0.1820, -78.4690, "Zona 1"),
            ("Calle Toledo N14-23", "Local 2, placa baja", -0.1865, -78.4710, "Zona 2"),
            ("Av. 6 de Diciembre 2345", "Penthouse piso 12", -0.1780, -78.4660, "Zona 1"),
            ("Calle Whymper 1234", "Torre 1, apartamento 502", -0.1830, -78.4680, "Zona 2"),
            ("Av. Olof Palme 456", "Casa con jardin", -0.1790, -78.4640, "Zona 1"),
            ("Calle Juan Leon Mera 789", "Departamento 301", -0.1815, -78.4695, "Zona 1"),
            ("Av. De los Shyris 3456", "Complejo comercial local 8", -0.1775, -78.4655, "Zona 2"),
            ("Calle Foch 1010", "Restaurante zona sur", -0.1870, -78.4715, "Zona 3"),
            ("Av. America 2468", "Conjunto habitacional torre 3", -0.1765, -78.4645, "Zona 1"),
            ("Calle Cordero 555", "Casa amarilla esquinera", -0.1845, -78.4695, "Zona 2"),
            ("Av. Granda Centro 1357", "Oficina 404", -0.1810, -78.4675, "Zona 1"),
            ("Calle Pastrana 222", "Duplex moderno", -0.1835, -78.4685, "Zona 2"),
            ("Av. Eloy Alfaro 9876", "Planta baja local 3", -0.1760, -78.4635, "Zona 1"),
            ("Calle Bolivia 432", "Casa antigua restaurada", -0.1855, -78.4705, "Zona 3"),
            ("Av. Amazonas 15975", "Torre corporativa piso 8", -0.1770, -78.4650, "Zona 2"),
            ("Calle Rumiñahui 864", "Complejo Los Pinos", -0.1840, -78.4690, "Zona 1"),
        ]

        repartidores = ["Juan Reparto", "Pedro Veloz", "Ana Rápida", "Luis Express", "Marco Entrega"]
        deliveries = []
        for i in range(20):
            d = direcciones[i]
            costo = 2.00 if d[4] == "Zona 1" else (3.50 if d[4] == "Zona 2" else 5.00)
            tiempo = 25 if d[4] == "Zona 1" else (40 if d[4] == "Zona 2" else 55)
            estados_d = [DeliveryStatus.IN_TRANSIT, DeliveryStatus.DELIVERED, DeliveryStatus.DELIVERED,
                        DeliveryStatus.DELIVERED, DeliveryStatus.ASSIGNED]
            estado_d = estados_d[i % 5]

            deliveries.append((
                pedidos_ids[i % len(pedidos_ids)], d[0], d[1], d[2], d[3],
                d[4], costo, tiempo, estado_d, repartidores[i % 5], i * 2
            ))

        for d in deliveries:
            delivery = Delivery(
                pedido_id=d[0], direccion=d[1], referencia=d[2],
                latitud=d[3], longitud=d[4], zona=d[5],
                costo=Decimal(str(d[6])), tiempo_estimado_min=d[7],
                estado=d[8], repartidor_nombre=d[9],
                created_at=ahora - timedelta(hours=d[10])
            )
            session.add(delivery)
        session.commit()

        # ===========================================
        # ZONAS DE DELIVERY
        # ===========================================
        zonas = [
            DeliveryZone(nombre="Zona 1 - Centro", radio_km=3.0, costo=2.00, tiempo_estimado_min=25, activa=True),
            DeliveryZone(nombre="Zona 2 - Intermedia", radio_km=6.0, costo=3.50, tiempo_estimado_min=40, activa=True),
            DeliveryZone(nombre="Zona 3 - Periferia", radio_km=10.0, costo=5.00, tiempo_estimado_min=55, activa=True),
        ]
        session.add_all(zonas)
        session.commit()

        # ===========================================
        # PROMOCIONES
        # ===========================================
        promociones = [
            Promotion(nombre="2x1 en Pizzas", descripcion="Todos los martes 2x1 en pizzas personales",
                      tipo="2x1", valor=0, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=90),
                      activa=True, canales_aplicables=["whatsapp", "telegram"]),
            Promotion(nombre="10% DESCUENTO", descripcion="10% de descuento en pedidos mayores a $30",
                      tipo="descuento", valor=10, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=30),
                      activa=True, condiciones={"minimo_pedido": 30}),
            Promotion(nombre="Delivery Gratis", descripcion="Delivery gratis en pedidos mayores a $25",
                      tipo="descuento", valor=0, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=60),
                      activa=True, condiciones={"minimo_pedido": 25, "delivery_gratis": True}),
            Promotion(nombre="Combo Pareja $18", descripcion="Combo especial parejas: 2 entradas + 2 postres",
                      tipo="combo", valor=18.00, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=45),
                      activa=True, canales_aplicables=["whatsapp"]),
            Promotion(nombre="Martes de Pastas", descripcion="20% de descuento en todas las pastas los martes",
                      tipo="descuento", valor=20, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=120),
                      activa=True, condiciones={"dia": "martes", "categoria": "pastas"}),
            Promotion(nombre="Cumpleanos Happy", descripcion="Postre gratis en tu cumpleanos",
                      tipo="regalo", valor=0, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=365),
                      activa=True, condiciones={"requiere_fecha_cumpleanos": True}),
            Promotion(nombre="3x2 en Bebidas", descripcion="Lleva 3 bebidas y paga solo 2",
                      tipo="3x2", valor=0, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=60),
                      activa=True, canales_aplicables=["whatsapp", "telegram", "webchat"]),
            Promotion(nombre="15% Fin de Semana", descripcion="15% de descuento sabados y domingos",
                      tipo="descuento", valor=15, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=90),
                      activa=True, condiciones={"dias": ["sabado", "domingo"]}),
            Promotion(nombre="Entrada Gratis", descripcion="Entrada gratis en pedidos mayores a $40",
                      tipo="regalo", valor=0, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=30),
                      activa=True, condiciones={"minimo_pedido": 40, "producto_gratis": "entrada"}),
            Promotion(nombre="Noche Italiana", descripcion="25% en combos de pizza + pasta + postre",
                      tipo="descuento", valor=25, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=60),
                      activa=True, condiciones={"dia": "viernes", "combo_italiano": True}),
            Promotion(nombre="Anticipo 50%", descripcion="Paga 50% al reservar y 50% al llegar",
                      tipo="condicional", valor=50, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=180),
                      activa=True, condiciones={"tipo_reserva": "evento"}),
            Promotion(nombre="Referido $5", descripcion="Tu amigo gana $5 en su primer pedido",
                      tipo="referido", valor=5.00, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=365),
                      activa=True, condiciones={"primer_pedido_amigo": True}),
        ]
        session.add_all(promociones)
        session.commit()

        # ===========================================
        # INTERACCIONES ANALYTICS
        # ===========================================
        interacciones = []
        tipos = ["mensaje", "pedido", "reserva", "consulta"]
        intenciones = ["menu", "pedido", "reserva", "delivery", "horarios", "promociones", "general", "quejas", "eventos"]
        canales = ["whatsapp", "telegram", "webchat"]

        for i in range(200):
            interacciones.append(AnalyticsInteraction(
                cliente_id=clientes_ids[i % len(clientes_ids)],
                canal=ChannelType(canales[i % len(canales)]),
                tipo=tipos[i % len(tipos)],
                intencion=intenciones[i % len(intenciones)],
                resuelto_por_ia=(i % 8 != 0),
                confidence=0.65 + (i % 35) / 100.0,
                created_at=ahora - timedelta(hours=i // 3, minutes=i % 60)
            ))
        session.add_all(interacciones)
        session.commit()

        print("Base de datos poblada correctamente")
        print(f"  - {len(categorias)} categorias")
        print(f"  - {len(productos)} productos")
        print(f"  - {len(clientes_datos)} clientes")
        print(f"  - {len(pedidos_datos)} pedidos")
        print(f"  - {len(items_datos)} items de pedidos")
        print(f"  - {len(reservas_datos)} reservas")
        print(f"  - {len(deliveries)} deliveries")
        print(f"  - {len(promociones)} promociones")
        print(f"  - 200 interacciones analytics")

    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
