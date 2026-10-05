# Orden de Creación - Restaurant AI Platform

**ESTADO**: v1.0 - Fundación

---

## FASE 0: FUNDACIÓN

| Archivo | Estado |
|---------|--------|
| `.gitignore` | ⏳ |
| `.env.example` | ⏳ |
| `.env` | ⏳ (credenciales configuradas) |
| `requirements.txt` | ⏳ |
| `pyrightconfig.json` | ⏳ |
| `pyproject.toml` | ⏳ |
| `docker-compose.yml` | ⏳ |

---

## FASE 1: DATABASE

| Archivo | Estado |
|---------|--------|
| `database/models.py` | ⏳ |
| `database/db_manager.py` | ⏳ |

### Tablas
- productos, categorías, opciones_producto
- pedidos, pedido_items, pedido_estados
- reservas
- clientes, cliente_preferencias
- promociones, promocion_reglas
- delivery_zonas, delivery_envios
- analytics_interacciones
- mensajes_pendientes
- configuracion
- handoff_pendiente
- audit_log

---

## FASE 2: SKILLS

| Skill | Estado |
|-------|--------|
| `base_skill.py` | ⏳ |
| `skill_manager.py` | ⏳ |
| `menu_skill.py` | ⏳ |
| `order_skill.py` | ⏳ |
| `reservation_skill.py` | ⏳ |
| `delivery_skill.py` | ⏳ |
| `customer_skill.py` | ⏳ |
| `promotion_skill.py` | ⏳ |
| `channel_skill.py` | ⏳ |
| `analytics_skill.py` | ⏳ |
| `monitoring_skill.py` | ⏳ |
| `knowledge_skill.py` | ⏳ |

---

## FASE 3: TOOLS

| Tool | Estado |
|------|--------|
| `menu_tool.py` | ⏳ |
| `order_tool.py` | ⏳ |
| `reservation_tool.py` | ⏳ |
| `delivery_tool.py` | ⏳ |
| `customer_tool.py` | ⏳ |
| `channel_tool.py` | ⏳ |
| `analytics_tool.py` | ⏳ |

---

## FASE 4: AGENT

| Archivo | Estado |
|---------|--------|
| `api/agent.py` | ⏳ (LangGraph ReAct + failover) |
| `api/orchestrator.py` | ⏳ (Intent Engine + Tool Router) |

---

## FASE 5: API + CRM

| Archivo | Estado |
|---------|--------|
| `api/main.py` | ⏳ (FastAPI + Jinja2 + 20+ rutas) |
| `api/check_env.py` | ⏳ |
| `api/webhooks/whatsapp.py` | ⏳ |
| `api/webhooks/telegram.py` | ⏳ |

### Rutas API

#### CRM Web
- `/` Dashboard
- `/inbox` Inbox omnicanal
- `/clientes` Customer 360
- `/pedidos` Gestión de pedidos
- `/reservas` Gestión de reservas
- `/menu` Catálogo de productos
- `/promociones` Promociones
- `/delivery` Estado de deliveries
- `/analytics` Métricas e AI Intelligence
- `/ai-governance` Control de IA
- `/configuración` Settings

#### API REST
- `/api/productos` CRUD productos
- `/api/pedidos` CRUD pedidos
- `/api/reservas` CRUD reservas
- `/api/clientes` CRUD clientes
- `/api/delivery` Gestión de envíos
- `/api/analytics` Métricas
- `/api/health` Health check
- `/api/chat` Chat síncrono (dashboard)

#### Webhooks
- `/webhook/whatsapp` GET + POST
- `/webhook/telegram` GET + POST

---

## FASE 6: TEMPLATES

| Template | Estado |
|----------|--------|
| `base.html` | ⏳ Layout CRM + sidebar |
| `dashboard.html` | ⏳ Resumen del día |
| `inbox.html` | ⏳ Conversaciones omnicanal |
| `clientes.html` | ⏳ Customer 360 |
| `pedidos.html` | ⏳ Gestión de pedidos |
| `reservas.html` | ⏳ Gestión de reservas |
| `menu.html` | ⏳ Catálogo de productos |
| `promociones.html` | ⏳ Promociones |
| `delivery.html` | ⏳ Estado de deliveries |
| `analytics.html` | ⏳ Métricas |
| `ai_intelligence.html` | ⏳ Análisis de IA |
| `ai_governance.html` | ⏳ Control de IA |
| `configuracion.html` | ⏳ Settings |
| `cliente_historial.html` | ⏳ Historial del cliente |

---

## FASE 7: FRONTEND MODERNO (Next.js + shadcn/ui)

| Componente | Estado |
|------------|--------|
| `app/layout.tsx` | Pendiente - Root layout |
| `components/ui/` | Pendiente - shadcn/ui (button, card, dialog...) |
| `components/layout/` | Pendiente - Sidebar, Header, Command Palette |
| `components/chat/` | Pendiente - Chat widget flotante |
| `components/inbox/` | Pendiente - Inbox con drag & drop |
| `components/dashboard/` | Pendiente - Stats, graficos, oportunidades |
| `components/pedidos/` | Pendiente - Kanban board |
| `components/menu/` | Pendiente - Product grid |
| `components/delivery/` | Pendiente - Mapa Leaflet + zonas |
| `components/admin/` | Pendiente - Editor de menu, horarios, FAQ |
| `hooks/` | Pendiente - useWebSocket, useChat |
| `stores/` | Pendiente - Zustand stores |
| `styles/globals.css` | Pendiente - Dark/Light mode |

**Diferencias con Veterinaria:**
- Next.js 14 App Router (no Jinja2)
- shadcn/ui premium (no Tailwind basico)
- Chat flotante con Framer Motion
- Kanban board con drag & drop
- Command Palette (Cmd+K)
- WebSocket real-time
- Dark/Light mode
- Paleta naranja/rojo (no azul)
- Delivery con mapa Leaflet (OpenStreetMap)
- Admin RAG para editar conocimiento

---

## FASE 9: DELIVERY CON MAPA (Leaflet)

| Componente | Estado |
|------------|--------|
| `components/delivery/delivery-map.tsx` | Pendiente - Mapa con zonas |
| `components/delivery/zone-manager.tsx` | Pendiente - Admin de zonas |
| `components/delivery/delivery-page.tsx` | Pendiente - Pagina completa |
| `lib/delivery-utils.ts` | Pendiente - Calculo Haversine |
| `api/delivery-zonas/` | Pendiente - CRUD zonas |

**Caracteristicas:**
- Mapa OpenStreetMap (gratis, sin API key)
- Poligonos de colores por zona
- Buscador de direcciones
- Validacion en tiempo real
- Calculo automatico de costo
- Estimacion de tiempo de entrega
- Admin para crear/editar zonas

---

## FASE 10: ADMIN RAG (Conocimiento Editable)

| Componente | Estado |
|------------|--------|
| `components/admin/menu-editor.tsx` | Pendiente - Editor de menu |
| `components/admin/schedule-editor.tsx` | Pendiente - Editor de horarios |
| `components/admin/policy-editor.tsx` | Pendiente - Editor de politicas |
| `components/admin/faq-editor.tsx` | Pendiente - Editor de FAQ |
| `components/admin/knowledge-preview.tsx` | Pendiente - Vista previa |
| `api/admin/` | Pendiente - CRUD conocimiento |

**Funcionalidades:**
- Editar menu (productos, precios, fotos)
- Editar horarios por dia
- Configurar horarios especiales
- Editar politicas (cancelacion, reembolso)
- Gestionar preguntas frecuentes
- Vista previa del conocimiento de la IA
- Sincronizar cambios con la IA

---

## FASE 8: INFRAESTRUCTURA

| Archivo | Estado |
|---------|--------|
| `Dockerfile` | ⏳ |
| `docker-compose.yml` | ⏳ |
| `deploy/nginx.conf` | ⏳ |
| `deploy/ssl.sh` | ⏳ |
| `.github/workflows/ci.yml` | ⏳ |

---

## COMANDOS

```bash
# Instalar dependencias
pip install -r requirements.txt

# Poblar base de datos
python scripts/seed_data.py

# Ingestar menú
python scripts/ingestar_menu.py

# Iniciar servidor
uvicorn api.main:app --reload --port 8000

# Abrir CRM
http://localhost:8000

# Docker
docker-compose up -d
```

---

## VERIFICACION FINAL

- [ ] Conversacion natural funciona
- [ ] RAG sobre menu funciona
- [ ] Pedidos se crean correctamente
- [ ] Reservas se crean correctamente
- [ ] Delivery con mapa funcional
- [ ] Zonas de delivery editables
- [ ] Admin RAG permite editar menu
- [ ] Admin RAG permite editar horarios
- [ ] Admin RAG permite editar politicas
- [ ] Admin RAG permite editar FAQ
- [ ] CRM muestra Customer 360
- [ ] Human handoff funciona
- [ ] Analytics muestra metricas
- [ ] AI Governance configurado
- [ ] Codigo sin emojis
- [ ] Comentarios en el codigo
- [ ] Todo en espanol
- [ ] Tests pasan (>90% coverage)
- [ ] Deploy en produccion
