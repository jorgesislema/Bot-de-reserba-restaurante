# PROMPT 08: skills/ - Skills Modulares del Restaurante

## Objetivo
Crear todas las skills modulares para el dominio del restaurante, incluyendo:
- BaseSkill y SkillManager
- MenuSkill (consulta de menú)
- OrderSkill (pedidos)
- ReservationSkill (reservas)
- DeliverySkill (delivery)
- CustomerSkill (CRM)
- PromotionSkill (promociones)
- ChannelSkill (omnicanal)
- AnalyticsSkill (métricas)
- MonitoringSkill (monitoreo)
- KnowledgeSkill (RAG)

## Instrucciones Detalladas

Crear la estructura de carpetas y archivos:

```
skills/
├── __init__.py
├── base_skill.py
├── skill_manager.py
├── menu/
│   ├── __init__.py
│   └── menu_skill.py
├── orders/
│   ├── __init__.py
│   └── order_skill.py
├── reservations/
│   ├── __init__.py
│   └── reservation_skill.py
├── delivery/
│   ├── __init__.py
│   └── delivery_skill.py
├── customers/
│   ├── __init__.py
│   └── customer_skill.py
├── promotions/
│   ├── __init__.py
│   └── promotion_skill.py
├── channels/
│   ├── __init__.py
│   └── channel_skill.py
├── analytics/
│   ├── __init__.py
│   └── analytics_skill.py
├── monitoring/
│   ├── __init__.py
│   └── monitoring_skill.py
└── knowledge/
    ├── __init__.py
    └── knowledge_skill.py
```

### base_skill.py

```python
"""Clase base abstracta para todas las skills."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseSkill(ABC):
    """Interfaz base para todas las skills."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa la skill con configuración. Retorna True si OK."""
        pass
    
    @abstractmethod
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Ejecuta una acción específica de la skill."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retorna lista de acciones disponibles."""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Retorna estado de salud de la skill."""
        pass
```

### skill_manager.py

```python
"""Gestor de skills del restaurante."""

from typing import Dict, Any, Optional
from skills.base_skill import BaseSkill


class SkillManager:
    """Administra todas las skills del sistema."""
    
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
    
    def register(self, name: str, skill: BaseSkill) -> None:
        """Registra una skill."""
        self._skills[name] = skill
    
    def get(self, name: str) -> Optional[BaseSkill]:
        """Obtiene una skill por nombre."""
        return self._skills.get(name)
    
    def execute(self, skill_name: str, action: str, params: Dict = None) -> Any:
        """Ejecuta una acción de una skill."""
        skill = self.get(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")
        return skill.execute(action, params)
    
    def list_skills(self) -> Dict[str, List[str]]:
        """Lista todas las skills y sus capacidades."""
        return {
            name: skill.get_capabilities()
            for name, skill in self._skills.items()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica salud de todas las skills."""
        return {
            name: skill.health_check()
            for name, skill in self._skills.items()
        }
```

### menu_skill.py

```python
"""Skill de menú del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class MenuSkill(BaseSkill):
    """Skill para consulta del menú."""
    
    def __init__(self):
        self.db: Optional[RestaurantDB] = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "buscar": self._buscar,
            "obtener_producto": self._obtener_producto,
            "obtener_categorias": self._obtener_categorias,
            "verificar_disponibilidad": self._verificar_disponibilidad,
            "calcular_precio": self._calcular_precio,
            "recomendar": self._recomendar,
        }
        
        if action not in actions:
            raise ValueError(f"Acción '{action}' no soportada")
        
        return actions[action](params)
    
    def _buscar(self, params: Dict) -> List[Dict]:
        return self.db.buscar_producto(params.get("query", ""))
    
    def _obtener_producto(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_producto(params["producto_id"])
    
    def _obtener_categorias(self, params: Dict) -> List[Dict]:
        return self.db.obtener_categorias()
    
    def _verificar_disponibilidad(self, params: Dict) -> bool:
        producto = self.db.obtener_producto(params["producto_id"])
        return producto is not None and producto.get("disponible", False)
    
    def _calcular_precio(self, params: Dict) -> float:
        return self.db.calcular_precio(
            params["producto_id"],
            params.get("opciones", {})
        )
    
    def _recomendar(self, params: Dict) -> List[Dict]:
        # Lógica de recomendación basada en historial
        productos = self.db.obtener_productos()
        return productos[:3]  # Simplificado
    
    def get_capabilities(self) -> List[str]:
        return ["buscar", "obtener_producto", "obtener_categorias", 
                "verificar_disponibilidad", "calcular_precio", "recomendar"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "menu"}
```

### order_skill.py

```python
"""Skill de pedidos del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB
from database.models import OrderStatus


class OrderSkill(BaseSkill):
    """Skill para gestión de pedidos."""
    
    def __init__(self):
        self.db: Optional[RestaurantDB] = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "crear_pedido": self._crear_pedido,
            "agregar_item": self._agregar_item,
            "obtener_pedido": self._obtener_pedido,
            "calcular_total": self._calcular_total,
            "confirmar_pedido": self._confirmar_pedido,
            "cancelar_pedido": self._cancelar_pedido,
            "obtener_estado": self._obtener_estado,
        }
        
        return actions[action](params)
    
    def _crear_pedido(self, params: Dict) -> int:
        return self.db.crear_pedido(
            params["cliente_id"],
            params.get("canal", "whatsapp")
        )
    
    def _agregar_item(self, params: Dict) -> bool:
        return self.db.agregar_item_pedido(
            params["pedido_id"],
            params["producto_id"],
            params.get("cantidad", 1),
            params.get("opciones")
        )
    
    def _obtener_pedido(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_pedido(params["pedido_id"])
    
    def _calcular_total(self, params: Dict) -> float:
        pedido = self.db.obtener_pedido(params["pedido_id"])
        return pedido["total"] if pedido else 0
    
    def _confirmar_pedido(self, params: Dict) -> bool:
        return self.db.actualizar_estado_pedido(
            params["pedido_id"],
            OrderStatus.CONFIRMED
        )
    
    def _cancelar_pedido(self, params: Dict) -> bool:
        return self.db.cancelar_pedido(
            params["pedido_id"],
            params.get("motivo", "Cancelado por cliente")
        )
    
    def _obtener_estado(self, params: Dict) -> Optional[str]:
        pedido = self.db.obtener_pedido(params["pedido_id"])
        return pedido["estado"] if pedido else None
    
    def get_capabilities(self) -> List[str]:
        return ["crear_pedido", "agregar_item", "obtener_pedido",
                "calcular_total", "confirmar_pedido", "cancelar_pedido",
                "obtener_estado"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "orders"}
```

### reservation_skill.py

```python
"""Skill de reservas del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class ReservationSkill(BaseSkill):
    """Skill para gestión de reservas."""
    
    def __init__(self):
        self.db: Optional[RestaurantDB] = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "verificar_disponibilidad": self._verificar_disponibilidad,
            "crear_reserva": self._crear_reserva,
            "cancelar_reserva": self._cancelar_reserva,
            "obtener_reservas": self._obtener_reservas,
        }
        
        return actions[action](params)
    
    def _verificar_disponibilidad(self, params: Dict) -> List[Dict]:
        return self.db.verificar_disponibilidad(
            params["fecha"],
            params.get("hora"),
            params["personas"]
        )
    
    def _crear_reserva(self, params: Dict) -> int:
        return self.db.crear_reserva(params)
    
    def _cancelar_reserva(self, params: Dict) -> bool:
        return self.db.cancelar_reserva(
            params["reserva_id"],
            params.get("motivo")
        )
    
    def _obtener_reservas(self, params: Dict) -> List[Dict]:
        # Implementar obtención de reservas
        return []
    
    def get_capabilities(self) -> List[str]:
        return ["verificar_disponibilidad", "crear_reserva",
                "cancelar_reserva", "obtener_reservas"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "reservations"}
```

### delivery_skill.py

```python
"""Skill de delivery del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class DeliverySkill(BaseSkill):
    """Skill para gestión de delivery."""
    
    def __init__(self):
        self.db: Optional[RestaurantDB] = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "calcular_costo": self._calcular_costo,
            "crear_envio": self._crear_envio,
            "obtener_estado": self._obtener_estado,
        }
        
        return actions[action](params)
    
    def _calcular_costo(self, params: Dict) -> Dict:
        return self.db.calcular_costo_delivery(params["direccion"])
    
    def _crear_envio(self, params: Dict) -> int:
        return self.db.crear_delivery(
            params["pedido_id"],
            params
        )
    
    def _obtener_estado(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_estado_delivery(params["pedido_id"])
    
    def get_capabilities(self) -> List[str]:
        return ["calcular_costo", "crear_envio", "obtener_estado"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "delivery"}
```

### customer_skill.py

```python
"""Skill de clientes del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class CustomerSkill(BaseSkill):
    """Skill para CRM y Customer 360."""
    
    def __init__(self):
        self.db: Optional[RestaurantDB] = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "obtener_cliente": self._obtener_cliente,
            "buscar_cliente": self._buscar_cliente,
            "crear_cliente": self._crear_cliente,
            "obtener_historial": self._obtener_historial,
        }
        
        return actions[action](params)
    
    def _obtener_cliente(self, params: Dict) -> Optional[Dict]:
        return self.db.obtener_cliente(params["telefono"])
    
    def _buscar_cliente(self, params: Dict) -> List[Dict]:
        return self.db.buscar_cliente(params["busqueda"])
    
    def _crear_cliente(self, params: Dict) -> int:
        return self.db.crear_cliente(params)
    
    def _obtener_historial(self, params: Dict) -> Dict:
        return self.db.obtener_historial(params["cliente_id"])
    
    def get_capabilities(self) -> List[str]:
        return ["obtener_cliente", "buscar_cliente", "crear_cliente",
                "obtener_historial"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "customers"}
```

### promotion_skill.py

```python
"""Skill de promociones del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class PromotionSkill(BaseSkill):
    """Skill para promociones y upselling."""
    
    def __init__(self):
        self.db: Optional[RestaurantDB] = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "obtener_promociones": self._obtener_promociones,
            "sugerir_upsell": self._sugerir_upsell,
        }
        
        return actions[action](params)
    
    def _obtener_promociones(self, params: Dict) -> List[Dict]:
        return self.db.obtener_promociones_activas(params.get("canal"))
    
    def _sugerir_upsell(self, params: Dict) -> Optional[str]:
        # Máximo 1 sugerencia por pedido
        # Lógica basada en historial
        return "¿Deseas agregar 2 bebidas por $3 adicionales?"
    
    def get_capabilities(self) -> List[str]:
        return ["obtener_promociones", "sugerir_upsell"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "promotions"}
```

### channel_skill.py

```python
"""Skill de canales omnicanal."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill


class ChannelSkill(BaseSkill):
    """Skill para gestión de canales (WhatsApp, Telegram, Web)."""
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "normalizar_mensaje": self._normalizar_mensaje,
            "enviar_respuesta": self._enviar_respuesta,
        }
        
        return actions[action](params)
    
    def _normalizar_mensaje(self, params: Dict) -> Dict:
        """Normaliza mensaje de cualquier canal."""
        return {
            "channel": params.get("channel", "whatsapp"),
            "user_id": params.get("user_id"),
            "message": params.get("message"),
            "timestamp": params.get("timestamp")
        }
    
    def _enviar_respuesta(self, params: Dict) -> bool:
        """Envía respuesta por el canal correspondiente."""
        canal = params.get("channel")
        destino = params.get("to")
        mensaje = params.get("message")
        
        # En producción, integrar con WhatsApp/Telegram API
        return True
    
    def get_capabilities(self) -> List[str]:
        return ["normalizar_mensaje", "enviar_respuesta"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "channels"}
```

### analytics_skill.py

```python
"""Skill de analytics del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill
from database.db_manager import RestaurantDB


class AnalyticsSkill(BaseSkill):
    """Skill para métricas y analytics."""
    
    def __init__(self):
        self.db: Optional[RestaurantDB] = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.db = RestaurantDB()
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "registrar_interaccion": self._registrar_interaccion,
            "obtener_metricas": self._obtener_metricas,
        }
        
        return actions[action](params)
    
    def _registrar_interaccion(self, params: Dict) -> None:
        self.db.registrar_interaccion(params)
    
    def _obtener_metricas(self, params: Dict) -> Dict:
        return self.db.obtener_metricas()
    
    def get_capabilities(self) -> List[str]:
        return ["registrar_interaccion", "obtener_metricas"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "analytics"}
```

### monitoring_skill.py

```python
"""Skill de monitoreo del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill


class MonitoringSkill(BaseSkill):
    """Skill para monitoreo y alertas."""
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "health_check": self._health_check,
            "registrar_fallo": self._registrar_fallo,
        }
        
        return actions[action](params)
    
    def _health_check(self, params: Dict) -> Dict:
        return {"status": "ok", "components": {}}
    
    def _registrar_fallo(self, params: Dict) -> None:
        # Log del fallo
        pass
    
    def get_capabilities(self) -> List[str]:
        return ["health_check", "registrar_fallo"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "monitoring"}
```

### knowledge_skill.py

```python
"""Skill de conocimiento (RAG) del restaurante."""

from typing import Any, Dict, List, Optional
from skills.base_skill import BaseSkill


class KnowledgeSkill(BaseSkill):
    """Skill para RAG sobre menú y políticas."""
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        params = params or {}
        
        actions = {
            "buscar_conocimiento": self._buscar_conocimiento,
        }
        
        return actions[action](params)
    
    def _buscar_conocimiento(self, params: Dict) -> List[Dict]:
        # RAG sobre documentos del restaurante
        return []
    
    def get_capabilities(self) -> List[str]:
        return ["buscar_conocimiento"]
    
    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "skill": "knowledge"}
```

## Verificación
- [ ] Todas las skills creadas con sus métodos implementados
- [ ] Cada skill sigue la interfaz BaseSkill
- [ ] Integración con RestaurantDB
- [ ] SkillManager funcional
- [ ] Tests unitarios para cada skill (>90% coverage)
