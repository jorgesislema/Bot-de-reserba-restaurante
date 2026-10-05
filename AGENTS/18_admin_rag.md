# PROMPT 18: Admin RAG - Panel para Editar Conocimiento

## Objetivo
Crear panel administrativo que permita al dueño del restaurante modificar todo el conocimiento que usa la IA: menu, horarios, politicas, FAQ, zonas de delivery e informacion general.

## Por que es importante

La IA no debe tener conocimiento hardcodeado. Todo debe ser editable desde un panel para que:
- El dueño cambie precios sin tocar codigo
- Se actualicen horarios de temporada
- Se agreguen nuevas politicas
- Se mejoren respuestas de la IA

## Estructura

```
app/(dashboard)/
├── admin/
│   ├── page.tsx              # Dashboard admin
│   ├── menu/page.tsx         # Editar menu
│   ├── horarios/page.tsx     # Editar horarios
│   ├── politicas/page.tsx    # Editar politicas
│   ├── faq/page.tsx          # Editar FAQ
│   ├── delivery-zonas/page.tsx # Editar zonas
│   └── restaurante/page.tsx  # Info del restaurante

components/admin/
├── menu-editor.tsx
├── schedule-editor.tsx
├── policy-editor.tsx
├── faq-editor.tsx
└── knowledge-preview.tsx

api/
├── admin/
│   ├── menu/route.ts
│   ├── horarios/route.ts
│   ├── politicas/route.ts
│   ├── faq/route.ts
│   └── restaurante/route.ts
```

---

## menu-editor.tsx

```tsx
/**
 * Editor de menu para el administrador.
 * 
 * Permite:
 * - Agregar, editar y eliminar productos
 * - Cambiar precios, categorias, ingredientes
 * - Subir fotos de productos
 * - Activar/desactivar productos
 * - Reordenar productos
 */

"use client"

import { useState } from "react"
import { Plus, Edit2, Trash2, Save, X, Upload, GripVertical } from "lucide-react"

/** Estructura de un producto del menu */
interface Producto {
  id: string
  nombre: string
  descripcion: string
  precio: number
  categoria: string
  ingredientes: string[]
  alergenos: string[]
  disponible: boolean
  imagen: string | null
  opciones: OpcionProducto[]
}

/** Opcion de personalizacion */
interface OpcionProducto {
  tipo: string
  nombre: string
  precio_adicional: number
}

/** Categorias disponibles */
const CATEGORIAS = [
  "Pizzas",
  "Hamburguesas",
  "Ensaladas",
  "Pastas",
  "Bebidas",
  "Postres",
  "Combos",
]

export function MenuEditor() {
  const [productos, setProductos] = useState<Producto[]>([
    {
      id: "1",
      nombre: "Pizza Margarita",
      descripcion: "Tomate, mozzarella, albahaca fresca",
      precio: 12.50,
      categoria: "Pizzas",
      ingredientes: ["tomate", "mozzarella", "albahaca"],
      alergenos: ["gluten", "lactosa"],
      disponible: true,
      imagen: null,
      opciones: [
        { tipo: "tamano", nombre: "Personal", precio_adicional: 7.00 },
        { tipo: "tamano", nombre: "Mediana", precio_adicional: 10.00 },
        { tipo: "tamano", nombre: "Familiar", precio_adicional: 12.50 },
        { tipo: "extra", nombre: "Queso extra", precio_adicional: 1.50 },
      ],
    },
  ])

  const [editando, setEditando] = useState<Producto | null>(null)
  const [esNuevo, setEsNuevo] = useState(false)

  /** Producto vacio para crear nuevo */
  const productoVacio: Producto = {
    id: `prod-${Date.now()}`,
    nombre: "",
    descripcion: "",
    precio: 0,
    categoria: "Pizzas",
    ingredientes: [],
    alergenos: [],
    disponible: true,
    imagen: null,
    opciones: [],
  }

  const crearNuevo = () => {
    setEditando({ ...productoVacio })
    setEsNuevo(true)
  }

  const editarProducto = (producto: Producto) => {
    setEditando({ ...producto })
    setEsNuevo(false)
  }

  const guardarProducto = () => {
    if (!editando) return

    if (esNuevo) {
      setProductos([...productos, editando])
    } else {
      setProductos(
        productos.map((p) => (p.id === editando.id ? editando : p))
      )
    }

    setEditando(null)
  }

  const eliminarProducto = (id: string) => {
    if (confirm("Eliminar este producto?")) {
      setProductos(productos.filter((p) => p.id !== id))
    }
  }

  const toggleDisponible = (id: string) => {
    setProductos(
      productos.map((p) =>
        p.id === id ? { ...p, disponible: !p.disponible } : p
      )
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Editor de Menu</h2>
          <p className="text-gray-500 text-sm">
            Los cambios se reflejan automaticamente en la IA
          </p>
        </div>
        <button
          onClick={crearNuevo}
          className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
        >
          <Plus size={16} />
          Nuevo Producto
        </button>
      </div>

      {/* Lista de productos */}
      <div className="bg-white rounded-xl shadow-sm border divide-y">
        {productos.map((producto) => (
          <div key={producto.id} className="p-4 flex items-center gap-4">
            <GripVertical size={16} className="text-gray-300 cursor-move" />

            {/* Imagen */}
            <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
              {producto.imagen ? (
                <img
                  src={producto.imagen}
                  className="w-full h-full object-cover rounded-lg"
                />
              ) : (
                <span className="text-gray-400 text-xs">Sin foto</span>
              )}
            </div>

            {/* Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium">{producto.nombre}</span>
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                  {producto.categoria}
                </span>
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {producto.descripcion}
              </div>
              <div className="flex items-center gap-3 mt-1 text-sm">
                <span className="font-bold text-green-600">
                  ${producto.precio.toFixed(2)}
                </span>
                <span className="text-gray-400">
                  {producto.ingredientes.length} ingredientes
                </span>
              </div>
            </div>

            {/* Disponibilidad */}
            <button
              onClick={() => toggleDisponible(producto.id)}
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                producto.disponible
                  ? "bg-green-100 text-green-700"
                  : "bg-red-100 text-red-700"
              }`}
            >
              {producto.disponible ? "Disponible" : "Agotado"}
            </button>

            {/* Acciones */}
            <div className="flex gap-1">
              <button
                onClick={() => editarProducto(producto)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <Edit2 size={16} />
              </button>
              <button
                onClick={() => eliminarProducto(producto.id)}
                className="p-2 hover:bg-red-50 text-red-500 rounded-lg"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal de edicion */}
      {editando && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 my-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {esNuevo ? "Nuevo Producto" : "Editar Producto"}
              </h3>
              <button
                onClick={() => setEditando(null)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Nombre y categoria */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre
                  </label>
                  <input
                    type="text"
                    value={editando.nombre}
                    onChange={(e) =>
                      setEditando({ ...editando, nombre: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Categoria
                  </label>
                  <select
                    value={editando.categoria}
                    onChange={(e) =>
                      setEditando({ ...editando, categoria: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    {CATEGORIAS.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Descripcion */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripcion
                </label>
                <textarea
                  value={editando.descripcion}
                  onChange={(e) =>
                    setEditando({
                      ...editando,
                      descripcion: e.target.value,
                    })
                  }
                  rows={2}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              {/* Precio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Precio base ($)
                </label>
                <input
                  type="number"
                  value={editando.precio}
                  onChange={(e) =>
                    setEditando({
                      ...editando,
                      precio: parseFloat(e.target.value) || 0,
                    })
                  }
                  min="0"
                  step="0.50"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              {/* Ingredientes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ingredientes (separados por coma)
                </label>
                <input
                  type="text"
                  value={editando.ingredientes.join(", ")}
                  onChange={(e) =>
                    setEditando({
                      ...editando,
                      ingredientes: e.target.value
                        .split(",")
                        .map((i) => i.trim())
                        .filter(Boolean),
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              {/* Alergenos */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alergenos (separados por coma)
                </label>
                <input
                  type="text"
                  value={editando.alergenos.join(", ")}
                  onChange={(e) =>
                    setEditando({
                      ...editando,
                      alergenos: e.target.value
                        .split(",")
                        .map((a) => a.trim())
                        .filter(Boolean),
                    })
                  }
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              {/* Imagen */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Foto del producto
                </label>
                <div className="flex items-center gap-4">
                  <button className="flex items-center gap-2 px-4 py-2 border border-dashed rounded-lg hover:bg-gray-50">
                    <Upload size={16} />
                    Subir imagen
                  </button>
                  {editando.imagen && (
                    <img
                      src={editando.imagen}
                      className="w-16 h-16 object-cover rounded-lg"
                    />
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setEditando(null)}
                className="flex-1 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={guardarProducto}
                className="flex-1 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 flex items-center justify-center gap-2"
              >
                <Save size={16} />
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

---

## schedule-editor.tsx

```tsx
/**
 * Editor de horarios de funcionamiento.
 * 
 * Permite configurar:
 * - Horario de apertura y cierre por dia
 * - Dias de descanso
 * - Horarios especiales (feriados, eventos)
 * - Mensaje fuera de horario para la IA
 */

"use client"

import { useState } from "react"
import { Save, Plus, Trash2 } from "lucide-react"

/** Horario de un dia */
interface HorarioDia {
  dia: string
  activo: boolean
  apertura: string
  cierre: string
}

/** Horario especial (feriado, evento) */
interface HorarioEspecial {
  id: string
  fecha: string
  descripcion: string
  apertura: string | null
  cierre: string | null
  cerrado: boolean
}

const DIAS_SEMANA = [
  "Lunes",
  "Martes",
  "Miercoles",
  "Jueves",
  "Viernes",
  "Sabado",
  "Domingo",
]

export function ScheduleEditor() {
  const [horarios, setHorarios] = useState<HorarioDia[]>([
    { dia: "Lunes", activo: true, apertura: "09:00", cierre: "22:00" },
    { dia: "Martes", activo: true, apertura: "09:00", cierre: "22:00" },
    { dia: "Miercoles", activo: true, apertura: "09:00", cierre: "22:00" },
    { dia: "Jueves", activo: true, apertura: "09:00", cierre: "22:00" },
    { dia: "Viernes", activo: true, apertura: "09:00", cierre: "23:00" },
    { dia: "Sabado", activo: true, apertura: "10:00", cierre: "23:00" },
    { dia: "Domingo", activo: true, apertura: "10:00", cierre: "21:00" },
  ])

  const [especiales, setEspeciales] = useState<HorarioEspecial[]>([
    {
      id: "1",
      fecha: "2026-12-25",
      descripcion: "Navidad",
      apertura: null,
      cierre: null,
      cerrado: true,
    },
  ])

  const [mensajeFueraHorario, setMensajeFueraHorario] = useState(
    "Lo sentimos, en este momento estamos cerrados. Nuestro horario es de Lunes a Domingo de 9:00 a 22:00. Puedes dejarnos tu pedido y lo procesaremos al abrir."
  )

  const toggleDia = (index: number) => {
    setHorarios(
      horarios.map((h, i) => (i === index ? { ...h, activo: !h.activo } : h))
    )
  }

  const actualizarHorario = (
    index: number,
    campo: keyof HorarioDia,
    valor: string | boolean
  ) => {
    setHorarios(
      horarios.map((h, i) =>
        i === index ? { ...h, [campo]: valor } : h
      )
    )
  }

  const agregarEspecial = () => {
    setEspeciales([
      ...especiales,
      {
        id: `esp-${Date.now()}`,
        fecha: "",
        descripcion: "",
        apertura: null,
        cierre: null,
        cerrado: false,
      },
    ])
  }

  const eliminarEspecial = (id: string) => {
    setEspeciales(especiales.filter((e) => e.id !== id))
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Horarios de Funcionamiento</h2>
        <p className="text-gray-500 text-sm">
          Configura los horarios que la IA usara para responder
        </p>
      </div>

      {/* Horarios por dia */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <h3 className="font-semibold mb-4">Horario semanal</h3>
        <div className="space-y-3">
          {horarios.map((horario, index) => (
            <div key={horario.dia} className="flex items-center gap-4">
              <button
                onClick={() => toggleDia(index)}
                className={`w-24 text-left text-sm font-medium ${
                  horario.activo ? "text-gray-900" : "text-gray-400"
                }`}
              >
                {horario.dia}
              </button>

              {horario.activo ? (
                <>
                  <input
                    type="time"
                    value={horario.apertura}
                    onChange={(e) =>
                      actualizarHorario(index, "apertura", e.target.value)
                    }
                    className="px-3 py-1 border rounded text-sm"
                  />
                  <span className="text-gray-400">a</span>
                  <input
                    type="time"
                    value={horario.cierre}
                    onChange={(e) =>
                      actualizarHorario(index, "cierre", e.target.value)
                    }
                    className="px-3 py-1 border rounded text-sm"
                  />
                </>
              ) : (
                <span className="text-sm text-gray-400">Cerrado</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Horarios especiales */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Horarios especiales</h3>
          <button
            onClick={agregarEspecial}
            className="flex items-center gap-1 px-3 py-1 text-sm bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            <Plus size={14} />
            Agregar
          </button>
        </div>

        <div className="space-y-2">
          {especiales.map((especial) => (
            <div key={especial.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <input
                type="date"
                value={especial.fecha}
                className="px-3 py-1 border rounded text-sm"
              />
              <input
                type="text"
                value={especial.descripcion}
                placeholder="Descripcion"
                className="flex-1 px-3 py-1 border rounded text-sm"
              />
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={especial.cerrado} />
                Cerrado
              </label>
              <button
                onClick={() => eliminarEspecial(especial.id)}
                className="p-1 hover:bg-red-100 text-red-500 rounded"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Mensaje fuera de horario */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <h3 className="font-semibold mb-2">Mensaje fuera de horario</h3>
        <p className="text-sm text-gray-500 mb-3">
          Este mensaje se enviara cuando un cliente escriba fuera del horario
        </p>
        <textarea
          value={mensajeFueraHorario}
          onChange={(e) => setMensajeFueraHorario(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border rounded-lg text-sm"
        />
      </div>

      <button className="flex items-center gap-2 px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">
        <Save size={16} />
        Guardar horarios
      </button>
    </div>
  )
}
```

---

## policy-editor.tsx

```tsx
/**
 * Editor de politicas del restaurante.
 * 
 * Permite configurar:
 * - Politica de cancelacion
 * - Politica de reembolso
 * - Politica de delivery
 * - Politica de reservas
 * - Terminos y condiciones
 * - Cualquier otra politica
 */

"use client"

import { useState } from "react"
import { Save, HelpCircle } from "lucide-react"

/** Politica del restaurante */
interface Politica {
  id: string
  titulo: string
  contenido: string
  activa: boolean
  paraIA: boolean
}

export function PolicyEditor() {
  const [politicas, setPoliticas] = useState<Politica[]>([
    {
      id: "1",
      titulo: "Cancelacion",
      contenido:
        "Las cancelaciones son gratuitas hasta 2 horas antes de la hora de la reserva. Despues se cobra el 50% del monto total.",
      activa: true,
      paraIA: true,
    },
    {
      id: "2",
      titulo: "Reembolso",
      contenuido:
        "Los reembolsos se procesan en un plazo de 3-5 dias habiles. Para solicitar uno, comunicate con nuestro equipo.",
      activa: true,
      paraIA: true,
    },
    {
      id: "3",
      titulo: "Delivery",
      contenido:
        "El tiempo de entrega es estimado y puede variar. No nos hacemos responsables por retrasos por clima o trafico.",
      activa: true,
      paraIA: true,
    },
    {
      id: "4",
      titulo: "Reservas",
      contenido:
        "Las reservas se mantienen por 15 minutos despues de la hora acordada. Pasado ese tiempo, la mesa puede ser liberada.",
      activa: true,
      paraIA: true,
    },
  ])

  const [editandoId, setEditandoId] = useState<string | null>(null)

  const actualizarPolitica = (
    id: string,
    campo: keyof Politica,
    valor: string | boolean
  ) => {
    setPoliticas(
      politicas.map((p) => (p.id === id ? { ...p, [campo]: valor } : p))
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Politicas del Restaurante</h2>
        <p className="text-gray-500 text-sm">
          Estas politicas se usan en las respuestas de la IA
        </p>
      </div>

      <div className="space-y-4">
        {politicas.map((politica) => (
          <div
            key={politica.id}
            className="bg-white rounded-xl shadow-sm border p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <h3 className="font-semibold">{politica.titulo}</h3>
                <label className="flex items-center gap-1 text-xs text-gray-500">
                  <input
                    type="checkbox"
                    checked={politica.paraIA}
                    onChange={(e) =>
                      actualizarPolitica(
                        politica.id,
                        "paraIA",
                        e.target.checked
                      )
                    }
                  />
                  Usar en respuestas IA
                </label>
              </div>
              <button
                onClick={() =>
                  setEditandoId(editandoId === politica.id ? null : politica.id)
                }
                className="text-sm text-orange-500 hover:text-orange-600"
              >
                {editandoId === politica.id ? "Cerrar" : "Editar"}
              </button>
            </div>

            {editandoId === politica.id ? (
              <textarea
                value={politica.contenido}
                onChange={(e) =>
                  actualizarPolitica(politica.id, "contenido", e.target.value)
                }
                rows={4}
                className="w-full px-3 py-2 border rounded-lg text-sm"
              />
            ) : (
              <p className="text-sm text-gray-600">{politica.contenido}</p>
            )}
          </div>
        ))}
      </div>

      <button className="flex items-center gap-2 px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">
        <Save size={16} />
        Guardar politicas
      </button>
    </div>
  )
}
```

---

## faq-editor.tsx

```tsx
/**
 * Editor de preguntas frecuentes (FAQ).
 * 
 * Permite agregar preguntas y respuestas que la IA
 * usara para responder automaticamente.
 */

"use client"

import { useState } from "react"
import { Plus, Edit2, Trash2, Save, X } from "lucide-react"

/** Pregunta frecuente */
interface FAQ {
  id: string
  pregunta: string
  respuesta: string
  categoria: string
  activa: boolean
}

const CATEGORIAS_FAQ = [
  "General",
  "Menu",
  "Reservas",
  "Delivery",
  "Pagos",
  "Eventos",
]

export function FAQEditor() {
  const [faqs, setFaqs] = useState<FAQ[]>([
    {
      id: "1",
      pregunta: "Aceptan mascotas?",
      respuesta:
        "Si, aceptamos mascotas en nuestra terraza. Por favor indica al hacer tu reserva si vendra acompanado de tu mascota.",
      categoria: "General",
      activa: true,
    },
    {
      id: "2",
      pregunta: "Tienen opciones sin gluten?",
      respuesta:
        "Si, contamos con opciones sin gluten en nuestro menu. Pide a tu mesero la carta especial.",
      categoria: "Menu",
      activa: true,
    },
    {
      id: "3",
      pregunta: "Hay estacionamiento?",
      respuesta:
        "Contamos con estacionamiento propio para 20 vehiculos. Tambien hay parking publico a una cuadra.",
      categoria: "General",
      activa: true,
    },
  ])

  const [editando, setEditando] = useState<FAQ | null>(null)
  const [esNueva, setEsNueva] = useState(false)

  const crearNueva = () => {
    setEditando({
      id: `faq-${Date.now()}`,
      pregunta: "",
      respuesta: "",
      categoria: "General",
      activa: true,
    })
    setEsNueva(true)
  }

  const guardar = () => {
    if (!editando) return

    if (esNueva) {
      setFaqs([...faqs, editando])
    } else {
      setFaqs(faqs.map((f) => (f.id === editando.id ? editando : f)))
    }

    setEditando(null)
  }

  const eliminar = (id: string) => {
    if (confirm("Eliminar esta pregunta?")) {
      setFaqs(faqs.filter((f) => f.id !== id))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Preguntas Frecuentes</h2>
          <p className="text-gray-500 text-sm">
            La IA usara estas respuestas automaticamente
          </p>
        </div>
        <button
          onClick={crearNueva}
          className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
        >
          <Plus size={16} />
          Nueva Pregunta
        </button>
      </div>

      {/* Lista de FAQ */}
      <div className="bg-white rounded-xl shadow-sm border divide-y">
        {faqs.map((faq) => (
          <div key={faq.id} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">{faq.pregunta}</span>
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                    {faq.categoria}
                  </span>
                </div>
                <p className="text-sm text-gray-500">{faq.respuesta}</p>
              </div>
              <div className="flex gap-1 ml-4">
                <button
                  onClick={() => {
                    setEditando(faq)
                    setEsNueva(false)
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <Edit2 size={14} />
                </button>
                <button
                  onClick={() => eliminar(faq.id)}
                  className="p-2 hover:bg-red-50 text-red-500 rounded-lg"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal de edicion */}
      {editando && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {esNueva ? "Nueva Pregunta" : "Editar Pregunta"}
              </h3>
              <button
                onClick={() => setEditando(null)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pregunta
                </label>
                <input
                  type="text"
                  value={editando.pregunta}
                  onChange={(e) =>
                    setEditando({ ...editando, pregunta: e.target.value })
                  }
                  placeholder="Ej: Aceptan mascotas?"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Respuesta
                </label>
                <textarea
                  value={editando.respuesta}
                  onChange={(e) =>
                    setEditando({ ...editando, respuesta: e.target.value })
                  }
                  rows={3}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Categoria
                </label>
                <select
                  value={editando.categoria}
                  onChange={(e) =>
                    setEditando({ ...editando, categoria: e.target.value })
                  }
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  {CATEGORIAS_FAQ.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setEditando(null)}
                className="flex-1 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={guardar}
                className="flex-1 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 flex items-center justify-center gap-2"
              >
                <Save size={16} />
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

---

## knowledge-preview.tsx

```tsx
/**
 * Vista previa del conocimiento de la IA.
 * 
 * Muestra como la IA veria la informacion configurada.
 * Util para verificar que todo esta correcto antes de publicar.
 */

"use client"

import { useState } from "react"
import { Eye, Code, RefreshCw } from "lucide-react"

export function KnowledgePreview() {
  const [pestana, setPestana] = useState<"vista" | "json">("vista")

  /** Conocimiento actual de la IA (simulado) */
  const conocimiento = {
    restaurante: {
      nombre: "La Terraza",
      direccion: "Av. Principal 123, Quito",
      telefono: "+593999999999",
    },
    horarios: {
      lunes_a_viernes: "09:00 - 22:00",
      sabado: "10:00 - 23:00",
      domingo: "10:00 - 21:00",
    },
    menu: {
      categorias: 7,
      productos: 45,
      precio_promedio: 12.50,
    },
    faq: {
      total: 15,
      activas: 12,
    },
    politicas: {
      cancelacion: "2 horas antes",
      reembolso: "3-5 dias habiles",
    },
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Vista Previa del Conocimiento</h2>
          <p className="text-gray-500 text-sm">
            Asi es como la IA ve la informacion de tu restaurante
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPestana("vista")}
            className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${
              pestana === "vista" ? "bg-orange-100 text-orange-700" : "bg-gray-100"
            }`}
          >
            <Eye size={14} />
            Vista
          </button>
          <button
            onClick={() => setPestana("json")}
            className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${
              pestana === "json" ? "bg-orange-100 text-orange-700" : "bg-gray-100"
            }`}
          >
            <Code size={14} />
            JSON
          </button>
        </div>
      </div>

      {pestana === "vista" ? (
        <div className="grid grid-cols-2 gap-4">
          {/* Restaurante */}
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold mb-3 text-orange-500">Restaurante</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500">Nombre: </span>
                <span className="font-medium">{conocimiento.restaurante.nombre}</span>
              </div>
              <div>
                <span className="text-gray-500">Direccion: </span>
                <span>{conocimiento.restaurante.direccion}</span>
              </div>
              <div>
                <span className="text-gray-500">Telefono: </span>
                <span>{conocimiento.restaurante.telefono}</span>
              </div>
            </div>
          </div>

          {/* Horarios */}
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold mb-3 text-orange-500">Horarios</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500">Lunes a Viernes: </span>
                <span className="font-medium">{conocimiento.horarios.lunes_a_viernes}</span>
              </div>
              <div>
                <span className="text-gray-500">Sabado: </span>
                <span className="font-medium">{conocimiento.horarios.sabado}</span>
              </div>
              <div>
                <span className="text-gray-500">Domingo: </span>
                <span className="font-medium">{conocimiento.horarios.domingo}</span>
              </div>
            </div>
          </div>

          {/* Menu */}
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold mb-3 text-orange-500">Menu</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500">Categorias: </span>
                <span className="font-medium">{conocimiento.menu.categorias}</span>
              </div>
              <div>
                <span className="text-gray-500">Productos: </span>
                <span className="font-medium">{conocimiento.menu.productos}</span>
              </div>
              <div>
                <span className="text-gray-500">Precio promedio: </span>
                <span className="font-medium">${conocimiento.menu.precio_promedio}</span>
              </div>
            </div>
          </div>

          {/* FAQ y Politicas */}
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold mb-3 text-orange-500">FAQ y Politicas</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500">Preguntas frecuentes: </span>
                <span className="font-medium">{conocimiento.faq.total}</span>
              </div>
              <div>
                <span className="text-gray-500">Activas para IA: </span>
                <span className="font-medium">{conocimiento.faq.activas}</span>
              </div>
              <div>
                <span className="text-gray-500">Cancelacion: </span>
                <span>{conocimiento.politicas.cancelacion}</span>
              </div>
              <div>
                <span className="text-gray-500">Reembolso: </span>
                <span>{conocimiento.politicas.reembolso}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-gray-900 rounded-xl p-4 overflow-auto max-h-96">
          <pre className="text-green-400 text-sm">
            {JSON.stringify(conocimiento, null, 2)}
          </pre>
        </div>
      )}

      <button className="flex items-center gap-2 px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">
        <RefreshCw size={16} />
        Actualizar conocimiento de la IA
      </button>
    </div>
  )
}
```

---

## Backend - API de Administracion (Python)

```python
"""
Endpoints para administracion del conocimiento de la IA.

Permite:
- CRUD de menu
- CRUD de horarios
- CRUD de politicas
- CRUD de FAQ
- Actualizar conocimiento de la IA
"""

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/api/admin", tags=["admin"])


# ===========================================
# MODELOS
# ===========================================

class ProductoAdmin(BaseModel):
    """Modelo de producto para administracion."""
    nombre: str
    descripcion: str
    precio: float
    categoria: str
    ingredientes: List[str]
    alergenos: List[str]
    disponible: bool = True


class HorarioAdmin(BaseModel):
    """Modelo de horario para administracion."""
    dia: str
    activo: bool
    apertura: str
    cierre: str


class PoliticaAdmin(BaseModel):
    """Modelo de politica para administracion."""
    titulo: str
    contenido: str
    activa: bool = True
    para_ia: bool = True


class FAQAdmin(BaseModel):
    """Modelo de FAQ para administracion."""
    pregunta: str
    respuesta: str
    categoria: str
    activa: bool = True


# ===========================================
# ENDPOINTS DE MENU
# ===========================================

@router.get("/menu")
async def obtener_menu():
    """Obtiene todo el menu para administracion."""
    return {"productos": [], "categorias": []}


@router.post("/menu")
async def crear_producto(producto: ProductoAdmin):
    """Crea un producto nuevo en el menu."""
    return {"message": "Producto creado", "producto": producto.dict()}


@router.put("/menu/{producto_id}")
async def actualizar_producto(producto_id: str, producto: ProductoAdmin):
    """Actualiza un producto existente."""
    return {"message": "Producto actualizado", "id": producto_id}


@router.delete("/menu/{producto_id}")
async def eliminar_producto(producto_id: str):
    """Elimina un producto del menu."""
    return {"message": "Producto eliminado", "id": producto_id}


# ===========================================
# ENDPOINTS DE HORARIOS
# ===========================================

@router.get("/horarios")
async def obtener_horarios():
    """Obtiene los horarios configurados."""
    return {"horarios": [], "especiales": []}


@router.put("/horarios")
async def actualizar_horarios(horarios: List[HorarioAdmin]):
    """Actualiza los horarios de funcionamiento."""
    return {"message": "Horarios actualizados"}


# ===========================================
# ENDPOINTS DE POLITICAS
# ===========================================

@router.get("/politicas")
async def obtener_politicas():
    """Obtiene las politicas configuradas."""
    return {"politicas": []}


@router.post("/politicas")
async def crear_politica(politica: PoliticaAdmin):
    """Crea una nueva politica."""
    return {"message": "Politica creada", "politica": politica.dict()}


@router.put("/politicas/{politica_id}")
async def actualizar_politica(politica_id: str, politica: PoliticaAdmin):
    """Actualiza una politica existente."""
    return {"message": "Politica actualizada", "id": politica_id}


@router.delete("/politicas/{politica_id}")
async def eliminar_politica(politica_id: str):
    """Elimina una politica."""
    return {"message": "Politica eliminada", "id": politica_id}


# ===========================================
# ENDPOINTS DE FAQ
# ===========================================

@router.get("/faq")
async def obtener_faq():
    """Obtiene las preguntas frecuentes."""
    return {"faqs": []}


@router.post("/faq")
async def crear_faq(faq: FAQAdmin):
    """Crea una nueva pregunta frecuente."""
    return {"message": "FAQ creada", "faq": faq.dict()}


@router.put("/faq/{faq_id}")
async def actualizar_faq(faq_id: str, faq: FAQAdmin):
    """Actualiza una pregunta frecuente."""
    return {"message": "FAQ actualizada", "id": faq_id}


@router.delete("/faq/{faq_id}")
async def eliminar_faq(faq_id: str):
    """Elimina una pregunta frecuente."""
    return {"message": "FAQ eliminada", "id": faq_id}


# ===========================================
# ENDPOINTS DE KNOWLEDGE
# ===========================================

@router.post("/knowledge/sync")
async def sincronizar_conocimiento():
    """
    Sincroniza el conocimiento editado con la IA.
    
    Actualiza:
    - Menu y precios
    - Horarios
    - Politicas
    - FAQ
    - Informacion del restaurante
    """
    return {
        "message": "Conocimiento sincronizado correctamente",
        "actualizado": {
            "menu": True,
            "horarios": True,
            "politicas": True,
            "faq": True,
        },
    }


@router.get("/knowledge/preview")
async def vista_previa_conocimiento():
    """Retorna el conocimiento actual que tiene la IA."""
    return {
        "restaurante": {
            "nombre": "La Terraza",
            "direccion": "Av. Principal 123",
        },
        "menu": {"productos": 45, "categorias": 7},
        "faq": {"total": 15, "activas": 12},
    }
```

---

## Verificacion

- [ ] Editor de menu con CRUD completo
- [ ] Editor de horarios por dia
- [ ] Horarios especiales (feriados)
- [ ] Editor de politicas
- [ ] Editor de FAQ
- [ ] Vista previa del conocimiento
- [ ] Boton para sincronizar con IA
- [ ] Backend API para cada seccion
- [ ] Codigo sin emojis
- [ ] Comentarios explicativos
- [ ] Todo en espanol
