"""Modelos de base de datos para Restaurant AI Platform."""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, Date, Time,
    ForeignKey, Numeric, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


# ===========================================
# ENUMS
# ===========================================

class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKING_UP = "picking_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CustomerSegment(str, Enum):
    NEW = "new"
    FREQUENT = "frequent"
    INACTIVE = "inactive"
    HIGH_VALUE = "high_value"
    VIP = "vip"


class ChannelType(str, Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    WEBCHAT = "webchat"


class HandoffStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


# ===========================================
# MODELS
# ===========================================

class Category(Base):
    """Categorias de productos."""
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    imagen = Column(String(500))
    orden = Column(Integer, default=0)
    activa = Column(Boolean, default=True)

    productos = relationship("Product", back_populates="categoria")


class Product(Base):
    """Productos del menu."""
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    precio_base = Column(Numeric(10, 2), nullable=False)
    imagen = Column(String(500))
    ingredientes = Column(JSON)
    alergenos = Column(JSON)
    disponible = Column(Boolean, default=True)
    personalizable = Column(Boolean, default=False)
    tiempo_preparacion_min = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categoria = relationship("Category", back_populates="productos")
    opciones = relationship("ProductOption", back_populates="producto")
    items_pedido = relationship("OrderItem", back_populates="producto")


class ProductOption(Base):
    """Opciones de personalizacion de productos."""
    __tablename__ = "opciones_producto"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    tipo = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    precio_adicional = Column(Numeric(10, 2), default=0)
    disponible = Column(Boolean, default=True)

    producto = relationship("Product", back_populates="opciones")


class Customer(Base):
    """Clientes del restaurante."""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    telefono = Column(String(20), unique=True)
    email = Column(String(200))
    canal_preferido = Column(SQLEnum(ChannelType), default=ChannelType.WHATSAPP)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    total_pedidos = Column(Integer, default=0)
    valor_acumulado = Column(Numeric(10, 2), default=0)
    ultimo_pedido = Column(DateTime)
    segmento = Column(SQLEnum(CustomerSegment), default=CustomerSegment.NEW)
    notas = Column(Text)

    preferencias = relationship("CustomerPreference", back_populates="cliente")
    pedidos = relationship("Order", back_populates="cliente")
    reservas = relationship("Reservation", back_populates="cliente")


class CustomerPreference(Base):
    """Preferencias de los clientes."""
    __tablename__ = "cliente_preferencias"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    tipo = Column(String(50), nullable=False)
    valor = Column(String(200), nullable=False)

    cliente = relationship("Customer", back_populates="preferencias")


class Order(Base):
    """Pedidos."""
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    numero_pedido = Column(String(20), unique=True, nullable=False)
    estado = Column(SQLEnum(OrderStatus), default=OrderStatus.DRAFT)
    subtotal = Column(Numeric(10, 2), default=0)
    delivery_cost = Column(Numeric(10, 2), default=0)
    impuestos = Column(Numeric(10, 2), default=0)
    descuento = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), default=0)
    canal = Column(SQLEnum(ChannelType))
    notas = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = relationship("Customer", back_populates="pedidos")
    items = relationship("OrderItem", back_populates="pedido")
    estados = relationship("OrderStateHistory", back_populates="pedido")
    delivery = relationship("Delivery", back_populates="pedido", uselist=False)


class OrderItem(Base):
    """Items de un pedido."""
    __tablename__ = "pedido_items"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    precio_total = Column(Numeric(10, 2), nullable=False)
    opciones_seleccionadas = Column(JSON)
    notas = Column(Text)

    pedido = relationship("Order", back_populates="items")
    producto = relationship("Product", back_populates="items_pedido")


class OrderStateHistory(Base):
    """Historial de estados del pedido."""
    __tablename__ = "pedido_estados"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    estado = Column(SQLEnum(OrderStatus), nullable=False)
    comentario = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    pedido = relationship("Order", back_populates="estados")


class Reservation(Base):
    """Reservas."""
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    personas = Column(Integer, nullable=False)
    nombre_contacto = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=False)
    preferencias = Column(JSON)
    observaciones = Column(Text)
    estado = Column(SQLEnum(ReservationStatus), default=ReservationStatus.PENDING)
    google_calendar_event_id = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Customer", back_populates="reservas")


class Delivery(Base):
    """Envios de delivery."""
    __tablename__ = "delivery_envios"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), unique=True)
    direccion = Column(Text, nullable=False)
    referencia = Column(Text)
    latitud = Column(Float)
    longitud = Column(Float)
    zona = Column(String(50))
    costo = Column(Numeric(10, 2), default=0)
    tiempo_estimado_min = Column(Integer)
    estado = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING)
    repartidor_nombre = Column(String(200))
    repartidor_telefono = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pedido = relationship("Order", back_populates="delivery")


class DeliveryZone(Base):
    """Zonas de delivery."""
    __tablename__ = "delivery_zonas"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    radio_km = Column(Float, nullable=False)
    costo = Column(Numeric(10, 2), nullable=False)
    tiempo_estimado_min = Column(Integer, nullable=False)
    activa = Column(Boolean, default=True)


class Promotion(Base):
    """Promociones."""
    __tablename__ = "promociones"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    tipo = Column(String(50), nullable=False)
    valor = Column(Numeric(10, 2))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    activa = Column(Boolean, default=True)
    condiciones = Column(JSON)
    canales_aplicables = Column(JSON)

    reglas = relationship("PromotionRule", back_populates="promocion")


class PromotionRule(Base):
    """Reglas de promociones."""
    __tablename__ = "promocion_reglas"

    id = Column(Integer, primary_key=True)
    promocion_id = Column(Integer, ForeignKey("promociones.id"))
    tipo = Column(String(50), nullable=False)
    valor = Column(String(200), nullable=False)

    promocion = relationship("Promotion", back_populates="reglas")


class AnalyticsInteraction(Base):
    """Interacciones para analytics."""
    __tablename__ = "analytics_interacciones"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    canal = Column(SQLEnum(ChannelType))
    tipo = Column(String(50))
    intencion = Column(String(100))
    resuelto_por_ia = Column(Boolean, default=False)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Handoff(Base):
    """Transferencias a humanos."""
    __tablename__ = "handoff_pendiente"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    canal = Column(SQLEnum(ChannelType))
    motivo = Column(Text, nullable=False)
    urgencia = Column(String(20))
    estado = Column(SQLEnum(HandoffStatus), default=HandoffStatus.PENDING)
    asignado_a = Column(String(200))
    notas_resolucion = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)


class AuditLog(Base):
    """Log de auditoria para AI Governance."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    accion = Column(String(100), nullable=False)
    entidad = Column(String(100))
    entidad_id = Column(Integer)
    usuario = Column(String(200))
    canal = Column(SQLEnum(ChannelType))
    detalles = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Configuration(Base):
    """Configuracion del sistema."""
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    descripcion = Column(Text)
