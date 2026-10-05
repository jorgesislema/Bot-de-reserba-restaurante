# PROMPT 16: Frontend Moderno - Next.js + shadcn/ui

## Objetivo
Crear un frontend moderno con Next.js 14 App Router, TypeScript, shadcn/ui y Tailwind CSS que sea visualmente DIFERENTE al CRM de la veterinaria.

## Por qué Next.js en vez de Jinja2

| Característica | Jinja2 (VetCRM) | Next.js (Restaurant AI) |
|----------------|-----------------|------------------------|
| Rendering | Server-side | Server + Client |
| Componentes | Templates estáticos | React interactivos |
| Real-time | Polling | WebSockets nativos |
| UI | Tailwind básico | shadcn/ui premium |
| Estado | Variables de template | React hooks + Zustand |
| Chat | Texto plano | Burbujas interactivas |
| Mobile | Responsive básico | PWA + gestures |

## Estructura del Proyecto Frontend

```
frontend/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── components.json          # shadcn/ui config
│
├── app/                     # App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Redirect a /dashboard
│   │
│   ├── (auth)/
│   │   └── login/page.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx       # Layout con sidebar
│   │   ├── dashboard/page.tsx
│   │   ├── inbox/page.tsx
│   │   ├── clientes/page.tsx
│   │   ├── pedidos/page.tsx
│   │   ├── reservas/page.tsx
│   │   ├── menu/page.tsx
│   │   ├── promociones/page.tsx
│   │   ├── delivery/page.tsx
│   │   ├── analytics/page.tsx
│   │   ├── ai-intelligence/page.tsx
│   │   ├── ai-governance/page.tsx
│   │   └── configuracion/page.tsx
│   │
│   └── api/                 # API routes (proxy al backend)
│       ├── chat/route.ts
│       ├── productos/route.ts
│       ├── pedidos/route.ts
│       └── ...
│
├── components/
│   ├── ui/                  # shadcn/ui primitives
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── table.tsx
│   │   ├── badge.tsx
│   │   ├── avatar.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── sheet.tsx
│   │   ├── tabs.tsx
│   │   └── ...
│   │
│   ├── layout/
│   │   ├── sidebar.tsx      # Sidebar colapsable
│   │   ├── header.tsx       # Header con notificaciones
│   │   ├── command.tsx      # Command palette (Cmd+K)
│   │   └── theme-toggle.tsx # Dark/Light mode
│   │
│   ├── chat/
│   │   ├── chat-widget.tsx  # Widget flotante
│   │   ├── chat-bubble.tsx  # Burbujas de mensaje
│   │   ├── chat-input.tsx   # Input con emojis
│   │   ├── chat-panel.tsx   # Panel completo
│   │   └── typing-indicator.tsx
│   │
│   ├── inbox/
│   │   ├── conversation-list.tsx
│   │   ├── conversation-item.tsx
│   │   ├── message-thread.tsx
│   │   └── customer-sidebar.tsx
│   │
│   ├── dashboard/
│   │   ├── stats-cards.tsx
│   │   ├── realtime-orders.tsx
│   │   ├── revenue-chart.tsx
│   │   └── opportunities.tsx
│   │
│   ├── menu/
│   │   ├── product-grid.tsx
│   │   ├── product-card.tsx
│   │   ├── product-dialog.tsx
│   │   └── category-filter.tsx
│   │
│   └── pedidos/
│       ├── order-board.tsx   # Kanban board
│       ├── order-card.tsx
│       ├── order-detail.tsx
│       └── order-timeline.tsx
│
├── lib/
│   ├── api.ts               # API client
│   ├── websocket.ts         # WebSocket client
│   ├── utils.ts             # Utilities
│   └── types.ts             # TypeScript types
│
├── hooks/
│   ├── use-chat.ts          # Chat hook
│   ├── use-orders.ts        # Orders hook
│   ├── use-websocket.ts     # WebSocket hook
│   └── use-realtime.ts      # Real-time updates
│
├── stores/
│   ├── chat-store.ts        # Zustand chat store
│   └── order-store.ts       # Zustand orders store
│
└── styles/
    └── globals.css          # Custom styles
```

## Diferencias Clave con la Veterinaria

### 1. Chat Widget Flotante (no página dedicada)

```tsx
// components/chat/chat-widget.tsx
"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MessageCircle, X, Send } from "lucide-react"
import { ChatBubble } from "./chat-bubble"

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")

  return (
    <>
      {/* Botón flotante */}
      <motion.button
        className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-orange-500 to-red-500 
                   text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </motion.button>

      {/* Panel de chat */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-96 h-[500px] bg-white rounded-2xl 
                       shadow-2xl border flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  🍽️
                </div>
                <div>
                  <h3 className="font-semibold">La Terraza</h3>
                  <p className="text-xs opacity-80">En línea • Responde al instante</p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg) => (
                <ChatBubble key={msg.id} message={msg} />
              ))}
            </div>

            {/* Input */}
            <div className="p-4 border-t">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Escribe tu mensaje..."
                  className="flex-1 px-4 py-2 bg-gray-100 rounded-full text-sm 
                             focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                <button className="bg-orange-500 text-white p-2 rounded-full hover:bg-orange-600">
                  <Send size={18} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
```

### 2. Inbox con Drag & Drop

```tsx
// components/inbox/inbox-panel.tsx
"use client"

import { useState } from "react"
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd"
import { motion } from "framer-motion"
import { 
  MessageCircle, Clock, UserCheck, AlertTriangle,
  Phone, Mail, Globe
} from "lucide-react"

interface Conversation {
  id: string
  customerName: string
  lastMessage: string
  channel: "whatsapp" | "telegram" | "webchat"
  status: "active" | "pending" | "resolved"
  unread: number
  lastActivity: Date
}

export function InboxPanel() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const channelIcons = {
    whatsapp: <Phone className="w-4 h-4 text-green-500" />,
    telegram: <Mail className="w-4 h-4 text-blue-500" />,
    webchat: <Globe className="w-4 h-4 text-purple-500" />,
  }

  const statusColors = {
    active: "bg-green-500",
    pending: "bg-yellow-500",
    resolved: "bg-gray-400",
  }

  return (
    <div className="flex h-[calc(100vh-200px)] bg-white rounded-xl shadow-sm border">
      {/* Lista de conversaciones */}
      <div className="w-80 border-r flex flex-col">
        <div className="p-4 border-b">
          <div className="relative">
            <input
              type="text"
              placeholder="Buscar conversación..."
              className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-lg text-sm"
            />
            <MessageCircle className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          </div>
          
          {/* Filtros */}
          <div className="flex gap-2 mt-3">
            <button className="px-3 py-1 bg-orange-500 text-white rounded-full text-xs">
              Todos (12)
            </button>
            <button className="px-3 py-1 bg-gray-100 rounded-full text-xs hover:bg-gray-200">
              Activos (8)
            </button>
            <button className="px-3 py-1 bg-gray-100 rounded-full text-xs hover:bg-gray-200">
              Pendientes (4)
            </button>
          </div>
        </div>

        <DragDropContext onDragEnd={(result) => {}}>
          <Droppable droppableId="conversations">
            {(provided) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="flex-1 overflow-y-auto"
              >
                {conversations.map((conv, index) => (
                  <Draggable key={conv.id} draggableId={conv.id} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        onClick={() => setSelectedId(conv.id)}
                        className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors
                          ${selectedId === conv.id ? "bg-orange-50 border-l-4 border-orange-500" : ""}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            <div className="relative">
                              <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-red-500 
                                              rounded-full flex items-center justify-center text-white font-bold">
                                {conv.customerName.charAt(0)}
                              </div>
                              <span className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white
                                ${statusColors[conv.status]}`} />
                            </div>
                            <div>
                              <div className="font-medium text-sm">{conv.customerName}</div>
                              <div className="flex items-center gap-1 text-xs text-gray-500">
                                {channelIcons[conv.channel]}
                                {conv.lastMessage.substring(0, 30)}...
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-gray-400">
                              {conv.lastActivity.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            {conv.unread > 0 && (
                              <span className="mt-1 inline-block bg-orange-500 text-white text-xs 
                                               rounded-full w-5 h-5 flex items-center justify-center">
                                {conv.unread}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header del chat */}
        <div className="p-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-red-500 
                            rounded-full flex items-center justify-center text-white font-bold">
              CP
            </div>
            <div>
              <div className="font-semibold">Carlos Pérez</div>
              <div className="text-sm text-gray-500">WhatsApp • 17 pedidos • $384 acumulados</div>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
              INTENT: Pedido
            </span>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
              $24.50
            </span>
          </div>
        </div>

        {/* Mensajes */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {/* Los mensajes se renderizan aquí */}
        </div>

        {/* Input */}
        <div className="p-4 border-t bg-white">
          <div className="flex items-center gap-2">
            <button className="p-2 text-gray-500 hover:text-gray-700">
              <span className="text-xl">😊</span>
            </button>
            <input
              type="text"
              placeholder="Escribe un mensaje..."
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 
                         focus:ring-orange-500"
            />
            <button className="p-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">
              <MessageCircle size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Panel derecho - Customer 360 */}
      <div className="w-72 border-l bg-white p-4 overflow-y-auto">
        <h3 className="font-semibold mb-4">Customer 360</h3>
        
        <div className="space-y-4">
          <div className="text-center pb-4 border-b">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-red-500 
                            rounded-full flex items-center justify-center text-white 
                            text-2xl font-bold mx-auto">
              CP
            </div>
            <h4 className="font-semibold mt-2">Carlos Pérez</h4>
            <p className="text-sm text-gray-500">Cliente desde Ene 2026</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-orange-500">17</div>
              <div className="text-xs text-gray-500">Pedidos</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-500">$384</div>
              <div className="text-xs text-gray-500">Acumulado</div>
            </div>
          </div>

          <div>
            <h5 className="text-sm font-medium text-gray-500 mb-2">Preferencias</h5>
            <div className="flex flex-wrap gap-1">
              <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                Pepperoni
              </span>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                Coca-Cola
              </span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                Delivery
              </span>
            </div>
          </div>

          <div>
            <h5 className="text-sm font-medium text-gray-500 mb-2">Frecuencia</h5>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div className="bg-orange-500 h-2 rounded-full" style={{ width: "65%" }} />
              </div>
              <span className="text-sm font-medium">2.3/mes</span>
            </div>
          </div>

          <button className="w-full py-2 bg-gray-100 rounded-lg text-sm hover:bg-gray-200 
                           transition-colors">
            Ver historial completo →
          </button>
        </div>
      </div>
    </div>
  )
}
```

### 3. Dashboard con Grafos en Tiempo Real

```tsx
// components/dashboard/dashboard.tsx
"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { 
  TrendingUp, ShoppingCart, Calendar, Users,
  ArrowUp, ArrowDown, Clock
} from "lucide-react"
import { 
  LineChart, Line, AreaChart, Area, 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from "recharts"

const stats = [
  { 
    label: "Conversaciones", 
    value: "486", 
    change: "+12%", 
    trend: "up",
    icon: MessageCircle,
    color: "from-blue-500 to-blue-600"
  },
  { 
    label: "Pedidos", 
    value: "83", 
    change: "+8%", 
    trend: "up",
    icon: ShoppingCart,
    color: "from-orange-500 to-red-500"
  },
  { 
    label: "Reservas", 
    value: "31", 
    change: "+15%", 
    trend: "up",
    icon: Calendar,
    color: "from-green-500 to-emerald-500"
  },
  { 
    label: "Ventas Hoy", 
    value: "$2,840", 
    change: "+22%", 
    trend: "up",
    icon: TrendingUp,
    color: "from-purple-500 to-pink-500"
  },
]

const realtimeOrders = [
  { id: "#5821", total: 19.50, status: "preparing", customer: "Carlos P." },
  { id: "#5822", total: 34.00, status: "confirmed", customer: "María L." },
  { id: "#5823", total: 52.00, status: "ready", customer: "Andrés M." },
  { id: "#5824", total: 28.00, status: "delivering", customer: "Laura G." },
]

const statusConfig = {
  preparing: { label: "Preparando", color: "bg-yellow-500", pulse: true },
  confirmed: { label: "Confirmado", color: "bg-blue-500", pulse: false },
  ready: { label: "Listo", color: "bg-green-500", pulse: true },
  delivering: { label: "En camino", color: "bg-purple-500", pulse: false },
  completed: { label: "Completado", color: "bg-gray-400", pulse: false },
}

export function Dashboard() {
  const [orders, setOrders] = useState(realtimeOrders)

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-3xl font-bold mt-1">{stat.value}</p>
                <div className={`flex items-center mt-2 text-sm ${
                  stat.trend === "up" ? "text-green-600" : "text-red-600"
                }`}>
                  {stat.trend === "up" ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                  <span className="ml-1">{stat.change}</span>
                  <span className="text-gray-400 ml-1">vs ayer</span>
                </div>
              </div>
              <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} text-white`}>
                <stat.icon size={20} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Gráfico de ventas */}
        <div className="col-span-2 bg-white rounded-xl shadow-sm border p-4">
          <h3 className="font-semibold mb-4">Ventas de la Semana</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={salesData}>
              <defs>
                <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="sales" 
                stroke="#f97316" 
                fillOpacity={1} 
                fill="url(#colorSales)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Pedidos en tiempo real */}
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Pedidos en Vivo</h3>
            <span className="flex items-center gap-1 text-sm text-green-600">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              Live
            </span>
          </div>
          
          <div className="space-y-3">
            {orders.map((order) => (
              <motion.div
                key={order.id}
                layout
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <div className="font-mono font-medium">{order.id}</div>
                  <div className="text-sm text-gray-500">{order.customer}</div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">${order.total.toFixed(2)}</div>
                  <div className="flex items-center gap-1">
                    <span className={`w-2 h-2 rounded-full ${statusConfig[order.status].color} 
                      ${statusConfig[order.status].pulse ? "animate-pulse" : ""}`} />
                    <span className="text-xs text-gray-500">
                      {statusConfig[order.status].label}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Oportunidades */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <h3 className="font-semibold mb-4">🔥 Oportunidades Activas</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-red-50 to-orange-50 
                          rounded-xl border-l-4 border-red-500">
            <div>
              <div className="font-medium">🎂 Evento: Cumpleaños 15 personas</div>
              <div className="text-sm text-gray-500">Solicita paquete especial • Sábado</div>
            </div>
            <div className="flex gap-2">
              <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">ALTA</span>
              <button className="px-3 py-1 bg-orange-500 text-white rounded-lg text-xs hover:bg-orange-600">
                Asignar
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-purple-50 
                          rounded-xl border-l-4 border-blue-500">
            <div>
              <div className="font-medium">👥 Reserva grupo 10 personas</div>
              <div className="text-sm text-gray-500">Cliente recurrente • Viernes</div>
            </div>
            <div className="flex gap-2">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">MEDIA</span>
              <button className="px-3 py-1 bg-orange-500 text-white rounded-lg text-xs hover:bg-orange-600">
                Asignar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 4. Pedidos con Kanban Board

```tsx
// components/pedidos/order-board.tsx
"use client"

import { useState } from "react"
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd"
import { motion } from "framer-motion"
import { Clock, ChefHat, CheckCircle, Truck, Package } from "lucide-react"

const columns = {
  confirmed: {
    title: "Confirmados",
    icon: CheckCircle,
    color: "bg-blue-500",
    items: [
      { id: "5822", total: 34.00, customer: "María L.", items: 3, time: "19:45" },
    ]
  },
  preparing: {
    title: "Preparando",
    icon: ChefHat,
    color: "bg-yellow-500",
    items: [
      { id: "5821", total: 19.50, customer: "Carlos P.", items: 2, time: "19:30" },
    ]
  },
  ready: {
    title: "Listos",
    icon: Package,
    color: "bg-green-500",
    items: [
      { id: "5823", total: 52.00, customer: "Andrés M.", items: 5, time: "19:15" },
    ]
  },
  delivering: {
    title: "En Camino",
    icon: Truck,
    color: "bg-purple-500",
    items: [
      { id: "5824", total: 28.00, customer: "Laura G.", items: 2, time: "19:00" },
    ]
  },
}

export function OrderBoard() {
  const [board, setBoard] = useState(columns)

  const onDragEnd = (result: any) => {
    // Mover pedido entre columnas
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="flex gap-4 h-[calc(100vh-200px)]">
        {Object.entries(board).map(([columnId, column]) => (
          <div key={columnId} className="flex-1 flex flex-col">
            {/* Column Header */}
            <div className="flex items-center gap-2 mb-4">
              <div className={`p-2 rounded-lg ${column.color} text-white`}>
                <column.icon size={16} />
              </div>
              <h3 className="font-semibold">{column.title}</h3>
              <span className="ml-auto bg-gray-200 text-gray-600 text-sm px-2 py-0.5 rounded-full">
                {column.items.length}
              </span>
            </div>

            {/* Column Content */}
            <Droppable droppableId={columnId}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`flex-1 space-y-2 p-2 rounded-xl transition-colors ${
                    snapshot.isDraggingOver ? "bg-orange-50" : "bg-gray-100"
                  }`}
                >
                  {column.items.map((item, index) => (
                    <Draggable key={item.id} draggableId={item.id} index={index}>
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className={`bg-white rounded-xl p-4 shadow-sm border 
                            ${snapshot.isDragging ? "shadow-lg rotate-2" : ""}`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <span className="font-mono font-bold text-lg">#{item.id}</span>
                            <span className="font-bold text-green-600">
                              ${item.total.toFixed(2)}
                            </span>
                          </div>
                          
                          <div className="text-sm text-gray-600 mb-3">
                            {item.customer} • {item.items} items
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1 text-xs text-gray-400">
                              <Clock size={12} />
                              {item.time}
                            </div>
                            <div className="flex gap-1">
                              <button className="p-1 hover:bg-gray-100 rounded">
                                👁️
                              </button>
                              <button className="p-1 hover:bg-gray-100 rounded">
                                ⏭️
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        ))}
      </div>
    </DragDropContext>
  )
}
```

### 5. Command Palette (Cmd+K)

```tsx
// components/layout/command-palette.tsx
"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, ShoppingCart, Calendar, Users, Settings, MessageCircle } from "lucide-react"

const commands = [
  { id: "pedidos", label: "Ver pedidos activos", icon: ShoppingCart, shortcut: "P" },
  { id: "reservas", label: "Ver reservas de hoy", icon: Calendar, shortcut: "R" },
  { id: "clientes", label: "Buscar cliente", icon: Users, shortcut: "C" },
  { id: "chat", label: "Abrir inbox", icon: MessageCircle, shortcut: "I" },
  { id: "config", label: "Configuración", icon: Settings, shortcut: "S" },
]

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState("")

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setIsOpen(!isOpen)
      }
    }
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [isOpen])

  const filtered = commands.filter(cmd => 
    cmd.label.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50"
            onClick={() => setIsOpen(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            className="fixed top-1/4 left-1/2 -translate-x-1/2 w-full max-w-lg bg-white 
                       rounded-2xl shadow-2xl z-50 overflow-hidden"
          >
            <div className="p-4 border-b">
              <div className="relative">
                <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Buscar comandos..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 text-lg focus:outline-none"
                  autoFocus
                />
              </div>
            </div>
            
            <div className="p-2 max-h-80 overflow-y-auto">
              {filtered.map((cmd) => (
                <button
                  key={cmd.id}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg 
                           hover:bg-gray-100 transition-colors text-left"
                  onClick={() => {
                    // Navegar al comando
                    setIsOpen(false)
                  }}
                >
                  <cmd.icon size={20} className="text-gray-500" />
                  <span className="flex-1">{cmd.label}</span>
                  <kbd className="px-2 py-1 bg-gray-200 rounded text-xs text-gray-500">
                    {cmd.shortcut}
                  </kbd>
                </button>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

### 6. Theme Toggle Dark/Light

```tsx
// components/layout/theme-toggle.tsx
"use client"

import { useState, useEffect } from "react"
import { Moon, Sun } from "lucide-react"
import { motion } from "framer-motion"

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark)
  }, [isDark])

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    >
      <motion.div
        initial={false}
        animate={{ rotate: isDark ? 180 : 0 }}
        transition={{ duration: 0.3 }}
      >
        {isDark ? <Sun size={20} /> : <Moon size={20} />}
      </motion.div>
    </button>
  )
}
```

### 7. WebSocket para Real-time

```tsx
// hooks/use-websocket.ts
"use client"

import { useEffect, useRef, useCallback } from "react"

export function useWebSocket(url: string, onMessage: (data: any) => void) {
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeout = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    ws.current = new WebSocket(url)
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }
    
    ws.current.onclose = () => {
      // Reconexión automática
      reconnectTimeout.current = setTimeout(connect, 3000)
    }
    
    ws.current.onerror = (error) => {
      console.error("WebSocket error:", error)
    }
  }, [url, onMessage])

  useEffect(() => {
    connect()
    return () => {
      ws.current?.close()
      clearTimeout(reconnectTimeout.current)
    }
  }, [connect])

  const send = useCallback((data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    }
  }, [])

  return { send }
}
```

## Paleta de Colores (Diferente a Veterinaria)

```css
/* styles/globals.css */
:root {
  /* Restaurant Theme - Warm Colors */
  --primary: #f97316;        /* Orange */
  --primary-dark: #ea580c;
  --secondary: #dc2626;      /* Red */
  --accent: #fbbf24;         /* Yellow */
  
  --background: #fafafa;
  --foreground: #171717;
  
  --card: #ffffff;
  --card-foreground: #171717;
  
  --muted: #f5f5f5;
  --muted-foreground: #737373;
  
  --border: #e5e5e5;
  --ring: #f97316;
}

.dark {
  --background: #0a0a0a;
  --foreground: #ededed;
  --card: #1a1a1a;
  --card-foreground: #ededed;
  --muted: #262626;
  --muted-foreground: #a3a3a3;
  --border: #2e2e2e;
}
```

## Instalación

```bash
# Crear proyecto Next.js
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir

cd frontend

# Instalar shadcn/ui
npx shadcn-ui@latest init

# Instalar componentes shadcn
npx shadcn-ui@latest add button card dialog input table badge avatar dropdown-menu sheet tabs

# Instalar dependencias adicionales
npm install framer-motion recharts @hello-pangea/dnd zustand lucide-react

# Iniciar desarrollo
npm run dev
```

## Verificación

- [ ] Next.js 14 App Router configurado
- [ ] TypeScript en todos los archivos
- [ ] shadcn/ui components instalados
- [ ] Dark/Light mode funcional
- [ ] Command Palette (Cmd+K)
- [ ] Chat widget flotante con animaciones
- [ ] Inbox con drag & drop
- [ ] Dashboard con gráficos reales
- [ ] Kanban board para pedidos
- [ ] WebSocket para real-time
- [ ] Mobile responsive
- [ ] Paleta de colores diferente (naranja/rojo vs azul de veterinaria)
