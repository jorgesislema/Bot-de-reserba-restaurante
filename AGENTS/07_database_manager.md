# PROMPT 07: database/db_manager.py - Gestor de Base de Datos

## Objetivo
Crear el archivo database/db_manager.py con todas las operaciones de base de datos.

## Instrucciones Detalladas

Crear el archivo `database/db_manager.py`:

```python
"""Gestor de base de datos para Restaurant AI Platform."""

import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

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


class RestaurantDB:
    """Gestor de base de datos del restaurante."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            f"sqlite:///{Path(__file__).parent.parent / 'restaurant_ai.db'}"
        )
        
        # SQLite necesita StaticPool para threads
        if "sqlite" in self.database_url:
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_engine(self.database_url)
        
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def _get_session(self) -> Session:
        return self.SessionLocal()
    
    # ===========================================
    # PRODUCTOS / MENÚ
    # ===========================================
    
    def obtener_categorias(self) -> List[Dict]:
        """Obtiene todas las categorías activas."""
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
                "tiempo_preparacion": p.tiempo_preparacion_min
            } for p in productos]
        finally:
            session.close()
    
    def buscar_producto(self, query: str) -> List[Dict]:
        """Búsqueda de productos por nombre o ingrediente."""
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
        """Obtiene un producto específico con sus opciones."""
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
                "opciones": [
                    {"tipo": o.tipo, "nombre": o.nombre, "precio": float(o.precio_adicional)}
                    for o in opciones
                ]
            }
        finally:
            session.close()
    
    def calcular_precio(self, producto_id: int, opciones: Dict) -> float:
        """Calcula el precio total con opciones seleccionadas."""
        session = self._get_session()
        try:
            producto = session.query(Product).filter_by(id=producto_id).first()
            if not producto:
                return 0.0
            
            total = float(producto.precio_base)
            
            # Agregar extras
            if "extras" in opciones:
                for extra_nombre in opciones["extras"]:
                    extra = session.query(ProductOption).filter_by(
                        producto_id=producto_id,
                        tipo="extra",
                        nombre=extra_nombre
                    ).first()
                    if extra:
                        total += float(extra.precio_adicional)
            
            # Agregar tamaño
            if "tamano" in opciones:
                tamano = session.query(ProductOption).filter_by(
                    producto_id=producto_id,
                    tipo="tamano",
                    nombre=opciones["tamano"]
                ).first()
                if tamano:
                    total = float(tamano.precio_adicional)  # Reemplaza precio base
            
            return round(total, 2)
        finally:
            session.close()
    
    # ===========================================
    # CLIENTES
    # ===========================================
    
    def obtener_cliente(self, telefono: str) -> Optional[Dict]:
        """Obtiene cliente por teléfono (Customer 360)."""
        session = self._get_session()
        try:
            cliente = session.query(Customer).filter_by(telefono=telefono).first()
            if not cliente:
                return None
            
            # Calcular frecuencia
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
        finally:
            session.close()
    
    def buscar_cliente(self, busqueda: str) -> List[Dict]:
        """Busca clientes por nombre, teléfono o email."""
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
        """Crea un nuevo cliente."""
        session = self._get_session()
        try:
            cliente = Customer(
                nombre=datos["nombre"],
                telefono=datos.get("telefono"),
                email=datos.get("email"),
                canal_preferido=ChannelType(datos.get("canal", "whatsapp"))
            )
            session.add(cliente)
            session.commit()
            return cliente.id
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
        """Crea un nuevo pedido."""
        session = self._get_session()
        try:
            # Generar número de pedido
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
        finally:
            session.close()
    
    def agregar_item_pedido(self, pedido_id: int, producto_id: int, cantidad: int, opciones: Dict = None) -> bool:
        """Agrega un item al pedido."""
        session = self._get_session()
        try:
            pedido = session.query(Order).filter_by(id=pedido_id).first()
            if not pedido or pedido.estado != OrderStatus.DRAFT:
                return False
            
            precio = self.calcular_precio(producto_id, opciones or {})
            
            item = OrderItem(
                pedido_id=pedido_id,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=precio,
                precio_total=precio * cantidad,
                opciones_seleccionadas=opciones
            )
            session.add(item)
            
            # Actualizar subtotal del pedido
            pedido.subtotal = Decimal(str(float(pedido.subtotal) + (precio * cantidad)))
            pedido.total = pedido.subtotal + pedido.delivery_cost + pedido.impuestos - pedido.descuento
            
            session.commit()
            return True
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
            
            return {
                "id": pedido.id,
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
        session = self._get_session()
        try:
            # Buscar reservas existentes para esa fecha/hora
            reservas_existentes = session.query(Reservation).filter(
                Reservation.fecha == fecha,
                Reservation.estado.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED])
            ).all()
            
            # Lógica de disponibilidad (simplificada)
            # En producción, esto verificaría mesas reales
            horas_ocupadas = [r.hora.strftime("%H:%M") for r in reservas_existentes]
            
            horas_disponibles = []
            for h in ["19:00", "19:30", "20:00", "20:30", "21:00", "21:30"]:
                if h not in horas_ocupadas:
                    horas_disponibles.append(h)
            
            return [{"hora": h, "disponible": True} for h in horas_disponibles]
        finally:
            session.close()
    
    def crear_reserva(self, datos: Dict) -> int:
        """Crea una nueva reserva."""
        session = self._get_session()
        try:
            reserva = Reservation(
                cliente_id=datos["cliente_id"],
                fecha=datos["fecha"],
                hora=datos["hora"],
                personas=datos["personas"],
                nombre_contacto=datos["nombre_contacto"],
                telefono=datos["telefono"],
                preferencias=datos.get("preferencias"),
                observaciones=datos.get("observaciones")
            )
            session.add(reserva)
            session.commit()
            return reserva.id
        finally:
            session.close()
    
    def cancelar_reserva(self, reserva_id: int, motivo: str = None) -> bool:
        """Cancela una reserva."""
        session = self._get_session()
        try:
            reserva = session.query(Reservation).filter_by(id=reserva_id).first()
            if not reserva:
                return False
            
            reserva.estado = ReservationStatus.CANCELLED
            session.commit()
            return True
        finally:
            session.close()
    
    # ===========================================
    # DELIVERY
    # ===========================================
    
    def calcular_costo_delivery(self, direccion: str) -> Dict:
        """Calcula costo y tiempo de delivery."""
        # En producción, esto usaría Google Maps API
        return {
            "zona": "Zona 1",
            "costo": 2.00,
            "tiempo_estimado_min": 35,
            "disponible": True
        }
    
    def crear_delivery(self, pedido_id: int, datos: Dict) -> int:
        """Crea un envío de delivery."""
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
        """Registra una interacción para analytics."""
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
        """Obtiene métricas generales."""
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
    # AUDITORÍA
    # ===========================================
    
    def registrar_auditoria(self, accion: str, entidad: str, entidad_id: int, detalles: Dict = None) -> None:
        """Registra una acción de auditoría."""
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
```

## Verificación
- [ ] Todas las operaciones CRUD implementadas
- [ ] Order State Machine funcional
- [ ] Customer 360 con cálculos
- [ ] Delivery con cálculo de costos
- [ ] Analytics y métricas
- [ ] Auditoría de acciones
- [ ] Health check
