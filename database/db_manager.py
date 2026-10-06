"""Gestor de base de datos para Restaurant AI Platform."""

import logging
import os
import threading
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pathlib import Path
from time import sleep as time_sleep

from sqlalchemy import create_engine, text, func, event
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

from database.models import (
    Base, Category, Product, ProductOption,
    Customer, CustomerPreference, CustomerSegment,
    Order, OrderItem, OrderStateHistory, OrderStatus,
    Reservation, ReservationStatus,
    Delivery, DeliveryStatus, DeliveryZone,
    Promotion, PromotionRule,
    AnalyticsInteraction, Handoff, HandoffStatus,
    AuditLog, Configuration, ChannelType
)


# ===========================================
# EXCEPCIONES DE RESERVAS
# ===========================================

class ReservaError(Exception):
    """Error base de reservas."""


class ReservaInvalidaError(ReservaError):
    """Datos de entrada invalidos."""


class ReservaFueraDeHorarioError(ReservaError):
    """Hora fuera del horario de servicio."""


class ReservaNoDisponibleError(ReservaError):
    """No hay capacidad/horario disponible."""


class ReservaDuplicadaError(ReservaError):
    """Reserva duplicada detectada por constraint de la base de datos."""


class RestaurantDB:
    """Gestor de base de datos del restaurante."""

    _MAX_INTENTOS_BLOQUEO = 3

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            f"sqlite:///{Path(__file__).parent.parent / 'restaurant_ai.db'}"
        )

        # Configuracion de reservas (variables de entorno con defaults)
        self.capacidad_total = int(os.getenv("RESTAURANT_TOTAL_CAPACITY", "40"))
        self.max_personas_por_reserva = int(os.getenv("RESERVATION_MAX_PARTY", "20"))
        self.duracion_reserva_min = int(os.getenv("RESERVATION_DURATION_MIN", "90"))
        self.intervalo_slot_min = int(os.getenv("RESERVATION_SLOT_MINUTES", "30"))
        self.horario_reservas_inicio = time(int(os.getenv("RESERVATION_OPEN_HOUR", "11")), 0)
        self.horario_reservas_fin = time(int(os.getenv("RESERVATION_CLOSE_HOUR", "23")), 0)

        # Mutex por slot (fecha+hora) para serializar check+insert en el
        # mismo proceso. En SQLite (dev, conexion unica) es la proteccion
        # efectiva; en PostgreSQL se suma el advisory lock transaccional.
        self._slot_locks: Dict[str, threading.Lock] = {}
        self._slot_locks_guard = threading.Lock()

        # SQLite necesita StaticPool para threads
        if "sqlite" in self.database_url:
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False, "timeout": 30},
                poolclass=StaticPool
            )
            self._configurar_sqlite()
        else:
            self.engine = create_engine(self.database_url)

        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self._crear_constraints_reservas()

    def _configurar_sqlite(self) -> None:
        """Pragmas SQLite: busy_timeout para esperar locks de escritura."""
        @event.listens_for(self.engine, "connect")
        def _pragmas(dbapi_conn, _record):
            try:
                dbapi_conn.execute("PRAGMA busy_timeout=30000")
            except Exception:  # pragma: no cover
                pass

    def _crear_constraints_reservas(self) -> None:
        """Crea (idempotente) el indice unico que impide reservas duplicadas.

        Unico (fecha, hora, telefono) entre estados activos: es la ultima
        defensa de la base de datos contra doble reserva del mismo cliente
        en el mismo slot, sea cual sea la via de acceso (API, tool, script).
        """
        stmts = [
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_reserva_slot_cliente "
            "ON reservas (fecha, hora, telefono) "
            "WHERE estado IN ('PENDING', 'CONFIRMED')",
        ]
        try:
            with self.engine.begin() as conn:
                for stmt in stmts:
                    conn.execute(text(stmt))
        except Exception as e:
            # Si ya existen duplicados historicos, no bloquear el arranque
            logger.warning("No se pudo crear indice de reservas: %s", e)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    @staticmethod
    def _coerce_fecha(fecha: Any) -> date:
        """Convierte entrada de fecha (str ISO o date) a objeto date."""
        if isinstance(fecha, datetime):
            return fecha.date()
        if isinstance(fecha, date):
            return fecha
        return date.fromisoformat(str(fecha).strip())

    @staticmethod
    def _coerce_hora(hora: Any) -> time:
        """Convierte entrada de hora (str HH:MM o time) a objeto time."""
        if isinstance(hora, time):
            return hora
        partes = str(hora).strip().split(":")
        if len(partes) < 2:
            raise ValueError(f"Hora invalida: {hora}")
        return time(int(partes[0]), int(partes[1]))

    # ===========================================
    # PRODUCTOS / MENU
    # ===========================================

    def obtener_categorias(self) -> List[Dict]:
        """Obtiene todas las categorias activas."""
        session = self._get_session()
        try:
            categorias = session.query(Category).filter_by(activa=True).order_by(Category.orden).all()
            return [{"id": c.id, "nombre": c.nombre, "descripcion": c.descripcion} for c in categorias]
        finally:
            session.close()

    def obtener_productos(self, categoria_id: Optional[int] = None) -> List[Dict]:
        """Obtiene productos disponibles."""
        session = self._get_session()
        try:
            query = session.query(Product).filter_by(disponible=True)
            if categoria_id:
                query = query.filter_by(categoria_id=categoria_id)
            productos = query.all()
            return [{
                "id": p.id, "nombre": p.nombre, "descripcion": p.descripcion,
                "precio": float(p.precio_base), "imagen": p.imagen,
                "ingredientes": p.ingredientes or [], "alergenos": p.alergenos or [],
                "personalizable": p.personalizable,
                "tiempo_preparacion": p.tiempo_preparacion_min,
                "disponible": p.disponible
            } for p in productos]
        finally:
            session.close()

    def buscar_producto(self, query: str) -> List[Dict]:
        """Busqueda de productos por nombre o ingrediente."""
        session = self._get_session()
        try:
            productos = session.query(Product).filter(
                Product.disponible == True,
                (Product.nombre.ilike(f"%{query}%")) |
                (Product.descripcion.ilike(f"%{query}%"))
            ).all()
            return [{
                "id": p.id, "nombre": p.nombre, "precio": float(p.precio_base),
                "categoria": p.categoria.nombre if p.categoria else None
            } for p in productos]
        finally:
            session.close()

    def obtener_producto(self, producto_id: int) -> Optional[Dict]:
        """Obtiene un producto especifico con sus opciones."""
        session = self._get_session()
        try:
            producto = session.query(Product).filter_by(id=producto_id).first()
            if not producto:
                return None

            opciones = session.query(ProductOption).filter_by(
                producto_id=producto_id, disponible=True
            ).all()

            return {
                "id": producto.id,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "precio": float(producto.precio_base),
                "imagen": producto.imagen,
                "ingredientes": producto.ingredientes or [],
                "alergenos": producto.alergenos or [],
                "personalizable": producto.personalizable,
                "disponible": producto.disponible,
                "opciones": [
                    {"tipo": o.tipo, "nombre": o.nombre, "precio": float(o.precio_adicional)}
                    for o in opciones
                ]
            }
        finally:
            session.close()

    def calcular_precio(self, producto_id: int, opciones: Dict) -> float:
        """Calcula el precio total del backend (base + tamano + extras).

        El LLM NUNCA calcula precios: esta es la unica fuente de verdad.
        """
        opciones = opciones or {}
        session = self._get_session()
        try:
            producto = session.query(Product).filter_by(id=producto_id).first()
            if not producto:
                raise ValueError(f"Producto {producto_id} no existe")

            # Precio base
            total = float(producto.precio_base)

            # Tamano: se SUMA el precio_adicional al precio base
            # (producto $10 + tamano $4 = $14, nunca $4)
            if opciones.get("tamano"):
                tamano = session.query(ProductOption).filter_by(
                    producto_id=producto_id,
                    tipo="tamano",
                    nombre=opciones["tamano"]
                ).first()
                if not tamano:
                    raise ValueError(
                        f"Tamano '{opciones['tamano']}' no disponible "
                        f"para {producto.nombre}"
                    )
                total += float(tamano.precio_adicional)

            # Extras: se SUMAN al precio
            for extra_nombre in opciones.get("extras", []):
                extra = session.query(ProductOption).filter_by(
                    producto_id=producto_id,
                    tipo="extra",
                    nombre=extra_nombre
                ).first()
                if not extra:
                    raise ValueError(
                        f"Extra '{extra_nombre}' no disponible "
                        f"para {producto.nombre}"
                    )
                total += float(extra.precio_adicional)

            return round(total, 2)
        finally:
            session.close()

    # ===========================================
    # CLIENTES
    # ===========================================

    def obtener_cliente_por_telefono(self, telefono: str) -> Optional[Dict]:
        """Obtiene cliente por telefono (Customer 360)."""
        session = self._get_session()
        try:
            cliente = session.query(Customer).filter_by(telefono=telefono).first()
            if not cliente:
                return None
            return self._serializar_cliente(session, cliente)
        finally:
            session.close()

    def obtener_cliente_por_id(self, cliente_id: int) -> Optional[Dict]:
        """Obtiene cliente por su ID interno."""
        session = self._get_session()
        try:
            cliente = session.query(Customer).filter_by(id=cliente_id).first()
            if not cliente:
                return None
            return self._serializar_cliente(session, cliente)
        finally:
            session.close()

    @staticmethod
    def _serializar_cliente(session: Session, cliente: Customer) -> Dict:
        """Serializa un cliente con su frecuencia de pedidos."""
        hace_30_dias = datetime.utcnow() - timedelta(days=30)
        pedidos_mes = session.query(Order).filter(
            Order.cliente_id == cliente.id,
            Order.created_at >= hace_30_dias,
            Order.estado == OrderStatus.COMPLETED
        ).count()

        return {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "telefono": cliente.telefono,
            "email": cliente.email,
            "canal_preferido": cliente.canal_preferido.value if cliente.canal_preferido else None,
            "fecha_registro": cliente.fecha_registro.isoformat() if cliente.fecha_registro else None,
            "total_pedidos": cliente.total_pedidos,
            "valor_acumulado": float(cliente.valor_acumulado),
            "ultimo_pedido": cliente.ultimo_pedido.isoformat() if cliente.ultimo_pedido else None,
            "segmento": cliente.segmento.value if cliente.segmento else None,
            "frecuencia": pedidos_mes
        }

    def buscar_cliente(self, busqueda: str) -> List[Dict]:
        """Busca clientes por nombre, telefono o email."""
        session = self._get_session()
        try:
            clientes = session.query(Customer).filter(
                (Customer.nombre.ilike(f"%{busqueda}%")) |
                (Customer.telefono.ilike(f"%{busqueda}%")) |
                (Customer.email.ilike(f"%{busqueda}%"))
            ).all()
            return [{
                "id": c.id, "nombre": c.nombre, "telefono": c.telefono,
                "segmento": c.segmento.value if c.segmento else None
            } for c in clientes]
        finally:
            session.close()

    def crear_cliente(self, datos: Dict) -> int:
        """Crea un nuevo cliente. Si el telefono ya existe, devuelve el existente."""
        session = self._get_session()
        try:
            telefono = (datos.get("telefono") or "").strip() or None
            if telefono:
                existente = session.query(Customer).filter_by(telefono=telefono).first()
                if existente:
                    return existente.id

            cliente = Customer(
                nombre=datos["nombre"],
                telefono=telefono,
                email=datos.get("email"),
                canal_preferido=ChannelType(datos.get("canal", "whatsapp"))
            )
            session.add(cliente)
            session.commit()
            return cliente.id
        except IntegrityError:
            # Carrera concurrente sobre el mismo telefono: devolver el existente
            session.rollback()
            if telefono:
                existente = session.query(Customer).filter_by(telefono=telefono).first()
                if existente:
                    return existente.id
            raise ValueError("No se pudo crear el cliente") from None
        finally:
            session.close()

    def actualizar_cliente(self, cliente_id: int, datos: Dict) -> bool:
        """Actualiza datos de un cliente."""
        session = self._get_session()
        try:
            cliente = session.query(Customer).filter_by(id=cliente_id).first()
            if not cliente:
                return False

            for key, value in datos.items():
                if hasattr(cliente, key):
                    setattr(cliente, key, value)

            session.commit()
            return True
        finally:
            session.close()

    def obtener_historial(self, cliente_id: int) -> Dict:
        """Obtiene historial completo de un cliente."""
        session = self._get_session()
        try:
            pedidos = session.query(Order).filter_by(
                cliente_id=cliente_id
            ).order_by(Order.created_at.desc()).limit(20).all()

            reservas = session.query(Reservation).filter_by(
                cliente_id=cliente_id
            ).order_by(Reservation.fecha.desc()).limit(10).all()

            return {
                "pedidos": [
                    {
                        "id": p.id, "numero": p.numero_pedido,
                        "total": float(p.total), "estado": p.estado.value,
                        "fecha": p.created_at.isoformat()
                    } for p in pedidos
                ],
                "reservas": [
                    {
                        "id": r.id, "fecha": r.fecha.isoformat(),
                        "hora": r.hora.strftime("%H:%M"), "personas": r.personas,
                        "estado": r.estado.value
                    } for r in reservas
                ]
            }
        finally:
            session.close()

    # ===========================================
    # PEDIDOS
    # ===========================================

    def crear_pedido(self, cliente_id: int, canal: str) -> int:
        """Crea un nuevo pedido. Valida que el cliente exista."""
        session = self._get_session()
        try:
            cliente = session.query(Customer).filter_by(id=cliente_id).first()
            if not cliente:
                raise ValueError(f"cliente_id {cliente_id} no existe")

            # Generar numero de pedido
            fecha = datetime.utcnow().strftime("%Y%m%d")
            ultimo = session.query(Order).filter(
                Order.numero_pedido.like(f"#{fecha}%")
            ).count()
            numero = f"#{fecha}{ultimo + 1:04d}"

            pedido = Order(
                cliente_id=cliente_id,
                numero_pedido=numero,
                canal=ChannelType(canal)
            )
            session.add(pedido)
            session.commit()
            return pedido.id
        except IntegrityError as e:
            session.rollback()
            raise ValueError(
                "No se pudo generar el numero de pedido, intenta de nuevo"
            ) from e
        finally:
            session.close()

    def agregar_item_pedido(self, pedido_id: int, producto_id: int, cantidad: int, opciones: Dict = None) -> bool:
        """Agrega un item al pedido. El precio lo calcula SIEMPRE el backend."""
        session = self._get_session()
        try:
            pedido = session.query(Order).filter_by(id=pedido_id).first()
            if not pedido or pedido.estado != OrderStatus.DRAFT:
                return False

            if cantidad < 1:
                raise ValueError("La cantidad debe ser al menos 1")

            # Fuente unica de verdad de precios (lanza si producto/opcion no existe)
            precio = self.calcular_precio(producto_id, opciones or {})

            item = OrderItem(
                pedido_id=pedido_id,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=precio,
                precio_total=round(precio * cantidad, 2),
                opciones_seleccionadas=opciones
            )
            session.add(item)

            # Actualizar subtotal/total del pedido
            subtotal = float(pedido.subtotal or 0) + (precio * cantidad)
            pedido.subtotal = Decimal(str(round(subtotal, 2)))
            pedido.total = Decimal(str(round(
                float(pedido.subtotal)
                + float(pedido.delivery_cost or 0)
                + float(pedido.impuestos or 0)
                - float(pedido.descuento or 0),
                2
            )))

            session.commit()
            return True
        except ValueError:
            session.rollback()
            raise
        finally:
            session.close()

    def obtener_pedido(self, pedido_id: int) -> Optional[Dict]:
        """Obtiene un pedido con sus items."""
        session = self._get_session()
        try:
            pedido = session.query(Order).filter_by(id=pedido_id).first()
            if not pedido:
                return None

            items = session.query(OrderItem).filter_by(pedido_id=pedido_id).all()

            dueno = session.get(Customer, pedido.cliente_id) if pedido.cliente_id else None

            return {
                "id": pedido.id,
                "cliente_id": pedido.cliente_id,
                "cliente_telefono": dueno.telefono if dueno else None,
                "numero": pedido.numero_pedido,
                "estado": pedido.estado.value,
                "subtotal": float(pedido.subtotal),
                "delivery_cost": float(pedido.delivery_cost),
                "impuestos": float(pedido.impuestos),
                "descuento": float(pedido.descuento),
                "total": float(pedido.total),
                "canal": pedido.canal.value if pedido.canal else None,
                "items": [
                    {
                        "producto": item.producto.nombre if item.producto else "Desconocido",
                        "cantidad": item.cantidad,
                        "precio_unitario": float(item.precio_unitario),
                        "precio_total": float(item.precio_total),
                        "opciones": item.opciones_seleccionadas
                    } for item in items
                ],
                "created_at": pedido.created_at.isoformat()
            }
        finally:
            session.close()

    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: OrderStatus, comentario: str = None) -> bool:
        """Actualiza el estado de un pedido."""
        session = self._get_session()
        try:
            pedido = session.query(Order).filter_by(id=pedido_id).first()
            if not pedido:
                return False

            pedido.estado = nuevo_estado

            # Registrar en historial
            historial = OrderStateHistory(
                pedido_id=pedido_id,
                estado=nuevo_estado,
                comentario=comentario
            )
            session.add(historial)

            session.commit()
            return True
        finally:
            session.close()

    def cancelar_pedido(self, pedido_id: int, motivo: str) -> bool:
        """Cancela un pedido."""
        session = self._get_session()
        try:
            pedido = session.query(Order).filter_by(id=pedido_id).first()
            if not pedido:
                return False

            if pedido.estado in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
                return False

            pedido.estado = OrderStatus.CANCELLED

            historial = OrderStateHistory(
                pedido_id=pedido_id,
                estado=OrderStatus.CANCELLED,
                comentario=motivo
            )
            session.add(historial)

            session.commit()
            return True
        finally:
            session.close()

    # ===========================================
    # RESERVAS
    # ===========================================

    def verificar_disponibilidad(self, fecha: str, hora: str, personas: int) -> List[Dict]:
        """Verifica disponibilidad de mesas."""
    def verificar_disponibilidad(self, fecha: str, hora: str, personas: int) -> List[Dict]:
        """Verifica disponibilidad real de la fecha/hora solicitada.

        Evalua: horario de servicio, duracion de la reserva, reservas
        existentes activas (solape de intervalos) y capacidad total.
        """
        session = self._get_session()
        try:
            fecha_date = self._coerce_fecha(fecha)
            slots = self._generar_slots()
            personas = int(personas or 0)

            resultado = []
            for slot in slots:
                ocupadas = self._personas_en_slot(session, fecha_date, slot)
                libre = self.capacidad_total - ocupadas
                disponible = libre >= personas
                resultado.append({
                    "hora": slot.strftime("%H:%M"),
                    "disponible": disponible,
                    "personas_ocupadas": ocupadas,
                    "capacidad_libre": libre,
                })

            if hora:
                hora_time = self._coerce_hora(hora)
                hora_str = hora_time.strftime("%H:%M")
                coincidencia = next((s for s in resultado if s["hora"] == hora_str), None)
                if coincidencia is None:
                    # Fuera del horario de servicio
                    resultado.append({
                        "hora": hora_str,
                        "disponible": False,
                        "motivo": "fuera_de_horario",
                        "personas_ocupadas": 0,
                        "capacidad_libre": 0,
                    })
            return resultado
        finally:
            session.close()

    def _generar_slots(self) -> List[time]:
        """Genera los slots de reserva dentro del horario de servicio."""
        slots = []
        ini_min = self._minutos(self.horario_reservas_inicio)
        fin_min = self._minutos(self.horario_reservas_fin) - self.duracion_reserva_min
        m = ini_min
        while m <= fin_min:
            slots.append(time(m // 60, m % 60))
            m += self.intervalo_slot_min
        return slots

    @staticmethod
    def _minutos(t: time) -> int:
        return t.hour * 60 + t.minute

    def _personas_en_slot(self, session: Session, fecha: date, hora: time) -> int:
        """Suma personas de reservas activas cuyo intervalo solapa con [hora, hora+duracion)."""
        ini = self._minutos(hora)
        fin = ini + self.duracion_reserva_min
        reservas = session.query(Reservation).filter(
            Reservation.fecha == fecha,
            Reservation.estado.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED])
        ).all()
        total = 0
        for r in reservas:
            r_ini = self._minutos(r.hora)
            r_fin = r_ini + self.duracion_reserva_min
            if r_ini < fin and r_fin > ini:
                total += r.personas
        return total

    def _hay_capacidad(self, session: Session, fecha: date, hora: time, personas: int) -> bool:
        ocupadas = self._personas_en_slot(session, fecha, hora)
        return (ocupadas + personas) <= self.capacidad_total

    @staticmethod
    def _lock_slot(session: Session, fecha: date, hora: time) -> None:
        """Lock a nivel de base de datos por slot (fecha+hora).

        - PostgreSQL: advisory lock transaccional -> serializa el check por slot.
        - SQLite: no expone advisory locks; la proteccion la dan el mutex
          de proceso (_slot_mutex), el indice unico parcial y los reintentos.
        """
        if session.bind is not None and session.bind.dialect.name == "postgresql":
            clave = f"{fecha.isoformat()}|{hora.strftime('%H:%M')}"
            session.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:clave))"),
                {"clave": clave},
            )

    def _slot_mutex(self, fecha: date, hora: time) -> threading.Lock:
        """Mutex de proceso por slot para serializar verificar+insertar."""
        clave = f"{fecha.isoformat()}|{hora.strftime('%H:%M')}"
        with self._slot_locks_guard:
            lock = self._slot_locks.get(clave)
            if lock is None:
                lock = threading.Lock()
                self._slot_locks[clave] = lock
            return lock

    def crear_reserva(self, datos: Dict) -> int:
        """Crea una nueva reserva de forma atomica.

        Normaliza fecha/hora, resuelve el cliente de forma determinista
        (nunca confia en un cliente_id inventado por el LLM) y verifica
        disponibilidad DENTRO de la misma transaccion que inserta.
        La base de datos es la ultima defensa contra reservas duplicadas:
        indice unico parcial (fecha, hora, telefono) para estados activos.
        """
        fecha = self._coerce_fecha(datos["fecha"])
        hora = self._coerce_hora(datos["hora"])
        telefono = (datos.get("telefono") or "").strip()
        nombre_contacto = datos.get("nombre_contacto")
        if not nombre_contacto:
            raise ReservaInvalidaError("nombre_contacto es obligatorio")

        personas = int(datos.get("personas") or 0)
        if personas <= 0:
            raise ReservaInvalidaError("El numero de personas debe ser mayor a 0")
        if personas > self.max_personas_por_reserva:
            raise ReservaInvalidaError(
                f"Maximo {self.max_personas_por_reserva} personas por reserva"
            )
        if fecha < date.today():
            raise ReservaInvalidaError("No se pueden crear reservas en fechas pasadas")
        if not any(s == hora for s in self._generar_slots()):
            raise ReservaFueraDeHorarioError(
                f"La hora {hora.strftime('%H:%M')} esta fuera del horario de reservas"
            )

        ultimo_error: Optional[Exception] = None
        # Mutex por slot: serializa verificar_disponibilidad + INSERT en este
        # proceso; en PostgreSQL se suma el advisory lock transaccional.
        with self._slot_mutex(fecha, hora):
            for intento in range(self._MAX_INTENTOS_BLOQUEO):
                session = self._get_session()
                try:
                    self._lock_slot(session, fecha, hora)

                    # Resolver cliente dentro de la transaccion
                    cliente_id = datos.get("cliente_id")
                    if cliente_id:
                        existe = session.query(Customer).filter_by(id=cliente_id).first()
                        if not existe:
                            raise ReservaInvalidaError(
                                f"cliente_id {cliente_id} no existe"
                            )
                    else:
                        if not telefono:
                            raise ReservaInvalidaError(
                                "Se requiere cliente_id o telefono para la reserva"
                            )
                        cliente = session.query(Customer).filter_by(
                            telefono=telefono
                        ).first()
                        if not cliente:
                            cliente = Customer(nombre=nombre_contacto, telefono=telefono)
                            session.add(cliente)
                            session.flush()
                        cliente_id = cliente.id

                    # Re-verificacion de capacidad en la MISMA transaccion
                    if not self._hay_capacidad(session, fecha, hora, personas):
                        raise ReservaNoDisponibleError(
                            f"No hay capacidad para {personas} personas "
                            f"el {fecha.isoformat()} a las {hora.strftime('%H:%M')}"
                        )

                    reserva = Reservation(
                        cliente_id=cliente_id,
                        fecha=fecha,
                        hora=hora,
                        personas=personas,
                        nombre_contacto=nombre_contacto,
                        telefono=telefono,
                        preferencias=datos.get("preferencias"),
                        observaciones=datos.get("observaciones")
                    )
                    session.add(reserva)
                    session.commit()
                    return reserva.id

                except ReservaError:
                    session.rollback()
                    raise
                except IntegrityError as e:
                    # El indice unico (fecha, hora, telefono) gano: duplicado exacto
                    session.rollback()
                    raise ReservaDuplicadaError(
                        "Ya existe una reserva activa para ese telefono, fecha y hora"
                    ) from e
                except OperationalError as e:
                    # Contencion de base de datos (SQLite busy) -> reintentar
                    session.rollback()
                    ultimo_error = e
                    time_sleep(0.05 * (intento + 1))
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()

        raise ReservaNoDisponibleError(
            "No se pudo confirmar la reserva por alta concurrencia. "
            "Intenta nuevamente."
        ) from ultimo_error

    def cancelar_reserva(self, reserva_id: int, motivo: str = None) -> bool:
        """Cancela una reserva."""
        session = self._get_session()
        try:
            reserva = session.query(Reservation).filter_by(id=reserva_id).first()
            if not reserva:
                return False

            reserva.estado = ReservationStatus.CANCELLED
            if motivo:
                reserva.observaciones = (
                    f"{reserva.observaciones or ''} | Cancelada: {motivo}".strip(" |")
                )
            session.commit()
            return True
        finally:
            session.close()

    def obtener_reserva(self, reserva_id: int) -> Optional[Dict]:
        """Obtiene una reserva por su ID (lectura para autorizacion)."""
        session = self._get_session()
        try:
            reserva = session.query(Reservation).filter_by(id=reserva_id).first()
            if not reserva:
                return None
            return {
                "id": reserva.id,
                "cliente_id": reserva.cliente_id,
                "fecha": reserva.fecha.isoformat(),
                "hora": reserva.hora.strftime("%H:%M"),
                "personas": reserva.personas,
                "nombre_contacto": reserva.nombre_contacto,
                "telefono": reserva.telefono,
                "estado": reserva.estado.value if reserva.estado else None,
            }
        finally:
            session.close()

    def obtener_reservas_por_fecha(
        self, fecha: str, estado: Optional[str] = None
    ) -> List[Dict]:
        """Lista las reservas de una fecha (opcionalmente filtradas por estado)."""
        session = self._get_session()
        try:
            fecha_date = self._coerce_fecha(fecha)
            query = session.query(Reservation).filter(Reservation.fecha == fecha_date)
            if estado:
                query = query.filter(
                    Reservation.estado == ReservationStatus(estado)
                )
            reservas = query.order_by(Reservation.hora).all()
            return [
                {
                    "id": r.id,
                    "fecha": r.fecha.isoformat(),
                    "hora": r.hora.strftime("%H:%M"),
                    "personas": r.personas,
                    "nombre_contacto": r.nombre_contacto,
                    "estado": r.estado.value,
                    "cliente_id": r.cliente_id,
                }
                for r in reservas
            ]
        finally:
            session.close()

    # ===========================================
    # DELIVERY
    # ===========================================

    def calcular_costo_delivery(self, direccion: str) -> Dict:
        """Calcula costo y tiempo de delivery."""
        return {
            "zona": "Zona 1",
            "costo": 2.00,
            "tiempo_estimado_min": 35,
            "disponible": True
        }

    def crear_delivery(self, pedido_id: int, datos: Dict) -> int:
        """Crea un envio de delivery."""
        session = self._get_session()
        try:
            delivery = Delivery(
                pedido_id=pedido_id,
                direccion=datos["direccion"],
                referencia=datos.get("referencia"),
                latitud=datos.get("latitud"),
                longitud=datos.get("longitud"),
                zona=datos.get("zona"),
                costo=datos.get("costo", 0),
                tiempo_estimado_min=datos.get("tiempo_estimado", 35)
            )
            session.add(delivery)
            session.commit()
            return delivery.id
        finally:
            session.close()

    def obtener_estado_delivery(self, pedido_id: int) -> Optional[Dict]:
        """Obtiene el estado de un delivery."""
        session = self._get_session()
        try:
            delivery = session.query(Delivery).filter_by(pedido_id=pedido_id).first()
            if not delivery:
                return None

            return {
                "id": delivery.id,
                "estado": delivery.estado.value,
                "direccion": delivery.direccion,
                "tiempo_estimado": delivery.tiempo_estimado_min,
                "repartidor": delivery.repartidor_nombre
            }
        finally:
            session.close()

    # ===========================================
    # PROMOCIONES
    # ===========================================

    def obtener_promociones_activas(self, canal: str = None) -> List[Dict]:
        """Obtiene promociones activas."""
        session = self._get_session()
        try:
            hoy = date.today()
            query = session.query(Promotion).filter(
                Promotion.activa == True,
                Promotion.fecha_inicio <= hoy,
                Promotion.fecha_fin >= hoy
            )

            promociones = query.all()
            return [{
                "id": p.id, "nombre": p.nombre, "descripcion": p.descripcion,
                "tipo": p.tipo, "valor": float(p.valor) if p.valor else None
            } for p in promociones]
        finally:
            session.close()

    # ===========================================
    # ANALYTICS
    # ===========================================

    def registrar_interaccion(self, datos: Dict) -> None:
        """Registra una interaccion para analytics."""
        session = self._get_session()
        try:
            interaccion = AnalyticsInteraction(
                cliente_id=datos.get("cliente_id"),
                canal=ChannelType(datos.get("canal", "whatsapp")),
                tipo=datos.get("tipo"),
                intencion=datos.get("intencion"),
                resuelto_por_ia=datos.get("resuelto_por_ia", False),
                confidence=datos.get("confidence")
            )
            session.add(interaccion)
            session.commit()
        finally:
            session.close()

    def obtener_metricas(self) -> Dict:
        """Obtiene metricas generales."""
        session = self._get_session()
        try:
            hoy = date.today()

            return {
                "conversaciones_hoy": session.query(AnalyticsInteraction).filter(
                    AnalyticsInteraction.created_at >= datetime.combine(hoy, datetime.min.time())
                ).count(),
                "pedidos_hoy": session.query(Order).filter(
                    Order.created_at >= datetime.combine(hoy, datetime.min.time())
                ).count(),
                "reservas_hoy": session.query(Reservation).filter(
                    Reservation.fecha == hoy
                ).count(),
                "ventas_hoy": float(session.query(
                    func.sum(Order.total)
                ).filter(
                    Order.created_at >= datetime.combine(hoy, datetime.min.time()),
                    Order.estado == OrderStatus.COMPLETED
                ).scalar() or 0)
            }
        finally:
            session.close()

    # ===========================================
    # HANDOFF
    # ===========================================

    def crear_handoff(self, cliente_id: int, canal: str, motivo: str, urgencia: str = "media") -> int:
        """Crea una transferencia a humano."""
        session = self._get_session()
        try:
            handoff = Handoff(
                cliente_id=cliente_id,
                canal=ChannelType(canal),
                motivo=motivo,
                urgencia=urgencia
            )
            session.add(handoff)
            session.commit()
            return handoff.id
        finally:
            session.close()

    def obtener_handoffs_pendientes(self) -> List[Dict]:
        """Obtiene handoffs pendientes."""
        session = self._get_session()
        try:
            handoffs = session.query(Handoff).filter_by(
                estado=HandoffStatus.PENDING
            ).order_by(Handoff.created_at.desc()).all()

            return [{
                "id": h.id, "motivo": h.motivo, "urgencia": h.urgencia,
                "canal": h.canal.value if h.canal else None,
                "created_at": h.created_at.isoformat()
            } for h in handoffs]
        finally:
            session.close()

    # ===========================================
    # AUDITORIA
    # ===========================================

    def registrar_auditoria(self, accion: str, entidad: str, entidad_id: int, detalles: Dict = None) -> None:
        """Registra una accion de auditoria."""
        session = self._get_session()
        try:
            log = AuditLog(
                accion=accion,
                entidad=entidad,
                entidad_id=entidad_id,
                detalles=detalles
            )
            session.add(log)
            session.commit()
        finally:
            session.close()

    # ===========================================
    # HEALTH CHECK
    # ===========================================

    def health_check(self) -> Dict:
        """Verifica el estado de la base de datos."""
        try:
            session = self._get_session()
            session.execute(text("SELECT 1"))
            session.close()
            return {"status": "ok", "database": "connected"}
        except Exception as e:
            return {"status": "error", "database": str(e)}
