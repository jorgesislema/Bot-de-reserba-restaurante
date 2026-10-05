# PROMPT 17: Delivery con Mapa - Leaflet + Zonas de Entrega

## Objetivo
Crear componente de delivery con mapa interactivo que muestre las zonas de cobertura, permita validar direcciones y calcule costos automaticamente.

## Dependencias

```bash
npm install leaflet react-leaflet @types/leaflet
```

## Estructura

```
components/delivery/
├── delivery-map.tsx        # Mapa principal con zonas
├── zone-manager.tsx        # Admin para crear/editar zonas
├── address-validator.tsx   # Validador de direcciones
├── delivery-tracker.tsx    # Tracking en tiempo real
└── delivery-page.tsx       # Pagina completa

lib/
└── delivery-utils.ts       # Utilidades de calculo
```

---

## delivery-map.tsx

```tsx
/**
 * Mapa de delivery con zonas de cobertura.
 * 
 * Muestra poligonos de colores representando cada zona.
 * Valida si una direccion esta dentro del radio de cobertura.
 * Calcula costo y tiempo estimado automaticamente.
 */

"use client"

import { useState } from "react"
import {
  MapContainer,
  TileLayer,
  Polygon,
  CircleMarker,
  useMapEvents,
} from "react-leaflet"
import "leaflet/dist/leaflet.css"
import { Search, XCircle } from "lucide-react"

// ===========================================
// INTERFACES
// ===========================================

/** Zona de delivery configurada en el sistema */
interface DeliveryZone {
  id: string
  nombre: string
  radio_km: number
  costo: number
  tiempo_min: number
  color: string
  center: [number, number]
  activa: boolean
}

/** Resultado de validacion de direccion */
interface DireccionResultado {
  posicion: [number, number]
  zona: DeliveryZone | null
  costo: number
  tiempo: number
}

// ===========================================
// CONFIGURACION POR DEFECTO
// ===========================================

const ZONAS_DEFECTO: DeliveryZone[] = [
  {
    id: "zona-1",
    nombre: "Zona 1 - Centro",
    radio_km: 3,
    costo: 2.00,
    tiempo_min: 25,
    color: "#22c55e",
    center: [-0.1807, -78.4678],
    activa: true,
  },
  {
    id: "zona-2",
    nombre: "Zona 2 - Intermedia",
    radio_km: 6,
    costo: 3.50,
    tiempo_min: 40,
    color: "#f59e0b",
    center: [-0.1807, -78.4678],
    activa: true,
  },
  {
    id: "zona-3",
    nombre: "Zona 3 - Periferia",
    radio_km: 10,
    costo: 5.00,
    tiempo_min: 55,
    color: "#ef4444",
    center: [-0.1807, -78.4678],
    activa: true,
  },
]

// ===========================================
// FUNCIONES DE CALCULO
// ===========================================

/**
 * Genera puntos para dibujar un circulo como poligono en el mapa.
 * Calcula coordenadas usando trigonometria basada en el radio en km.
 */
function generarPuntosCirculo(
  center: [number, number],
  radioKm: number,
  totalPuntos: number = 64
): [number, number][] {
  const puntos: [number, number][] = []
  const [lat, lng] = center

  for (let i = 0; i < totalPuntos; i++) {
    const angulo = (i / totalPuntos) * 2 * Math.PI
    const dLat = (radioKm / 111) * Math.cos(angulo)
    const dLng =
      (radioKm / (111 * Math.cos((lat * Math.PI) / 180))) * Math.sin(angulo)
    puntos.push([lat + dLat, lng + dLng])
  }

  return puntos
}

/**
 * Calcula distancia entre dos puntos geograficos usando formula de Haversine.
 * Retorna distancia en kilometros.
 */
function calcularDistancia(
  punto1: [number, number],
  punto2: [number, number]
): number {
  const [lat1, lng1] = punto1
  const [lat2, lng2] = punto2
  const R = 6371 // Radio de la Tierra en km

  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLng = ((lng2 - lng1) * Math.PI) / 180

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

/**
 * Encuentra la zona de cobertura para una posicion dada.
 * Ordena zonas por radio ascendente y retorna la primera que cubra la distancia.
 */
function encontrarZona(
  posicion: [number, number],
  centro: [number, number],
  zonas: DeliveryZone[]
): { zona: DeliveryZone | null; distancia: number } {
  const distancia = calcularDistancia(centro, posicion)

  const zonasActivas = zonas
    .filter((z) => z.activa)
    .sort((a, b) => a.radio_km - b.radio_km)

  for (const zona of zonasActivas) {
    if (distancia <= zona.radio_km) {
      return { zona, distancia }
    }
  }

  return { zona: null, distancia }
}

// ===========================================
// COMPONENTES INTERNOS
// ===========================================

/**
 * Buscador de direcciones usando Nominatim (OpenStreetMap).
 * Permite buscar por nombre de calle y volar al resultado en el mapa.
 */
function BuscadorDireccion({
  onDireccionEncontrada,
}: {
  onDireccionEncontrada: (pos: [number, number]) => void
}) {
  const [query, setQuery] = useState("")
  const [resultados, setResultados] = useState<any[]>([])
  const map = useMapEvents({})

  const buscar = async () => {
    if (!query.trim()) return

    try {
      const respuesta = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`
      )
      const datos = await respuesta.json()
      setResultados(datos)
    } catch (error) {
      console.error("Error al buscar direccion:", error)
    }
  }

  const seleccionar = (resultado: any) => {
    const pos: [number, number] = [
      parseFloat(resultado.lat),
      parseFloat(resultado.lon),
    ]
    map.flyTo(pos, 16)
    onDireccionEncontrada(pos)
    setResultados([])
  }

  return (
    <div className="absolute top-4 left-4 z-[1000] w-80">
      <div className="bg-white rounded-lg shadow-lg p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && buscar()}
            placeholder="Buscar direccion..."
            className="flex-1 px-3 py-2 border rounded-lg text-sm"
          />
          <button
            onClick={buscar}
            className="px-3 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          >
            <Search size={16} />
          </button>
        </div>

        {resultados.length > 0 && (
          <div className="mt-2 border rounded-lg max-h-48 overflow-y-auto">
            {resultados.map((r, i) => (
              <button
                key={i}
                onClick={() => seleccionar(r)}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm border-b last:border-0"
              >
                {r.display_name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Panel que muestra informacion de la zona seleccionada.
 * Muestra zona, costo y tiempo estimado.
 */
function PanelZona({
  zona,
  distancia,
}: {
  zona: DeliveryZone | null
  distancia: number | null
}) {
  if (!zona) {
    return (
      <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4 w-72">
        <div className="flex items-center gap-2 text-gray-500">
          <XCircle size={20} />
          <span>Fuera de zona de cobertura</span>
        </div>
      </div>
    )
  }

  return (
    <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4 w-72">
      <h3 className="font-semibold mb-2" style={{ color: zona.color }}>
        {zona.nombre}
      </h3>
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Distancia:</span>
          <span className="font-medium">{distancia?.toFixed(1)} km</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Costo envio:</span>
          <span className="font-medium text-green-600">
            ${zona.costo.toFixed(2)}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Tiempo estimado:</span>
          <span className="font-medium">{zona.tiempo_min} min</span>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t">
        <button className="w-full py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 text-sm font-medium">
          Confirmar envio
        </button>
      </div>
    </div>
  )
}

/**
 * Componente que captura clics en el mapa y retorna la posicion.
 */
function MapaInteractivo({
  onSeleccionar,
}: {
  onSeleccionar: (pos: [number, number]) => void
}) {
  useMapEvents({
    click: (e) => {
      onSeleccionar([e.latlng.lat, e.latlng.lng])
    },
  })
  return null
}

// ===========================================
// COMPONENTE PRINCIPAL
// ===========================================

/**
 * Mapa principal de delivery.
 * 
 * Props:
 * - zonas: Lista de zonas de cobertura (opcional, usa defecto)
 * - onDireccionSeleccionada: Callback cuando se selecciona una direccion
 */
export function DeliveryMap({
  zonas = ZONAS_DEFECTO,
  onDireccionSeleccionada,
}: {
  zonas?: DeliveryZone[]
  onDireccionSeleccionada?: (resultado: DireccionResultado) => void
}) {
  const [posSeleccionada, setPosSeleccionada] = useState<
    [number, number] | null
  >(null)
  const [zonaActual, setZonaActual] = useState<DeliveryZone | null>(null)
  const [distancia, setDistancia] = useState<number | null>(null)

  const centroRestaurante: [number, number] = [-0.1807, -78.4678]

  /** Maneja seleccion de posicion en el mapa */
  const manejarSeleccion = (pos: [number, number]) => {
    setPosSeleccionada(pos)

    const { zona, distancia: dist } = encontrarZona(
      pos,
      centroRestaurante,
      zonas
    )

    setZonaActual(zona)
    setDistancia(dist)

    if (onDireccionSeleccionada) {
      onDireccionSeleccionada({
        posicion: pos,
        zona,
        costo: zona?.costo ?? 0,
        tiempo: zona?.tiempo_min ?? 0,
      })
    }
  }

  return (
    <div className="relative w-full h-[500px] rounded-xl overflow-hidden border">
      <MapContainer
        center={centroRestaurante}
        zoom={13}
        className="w-full h-full"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Dibujar zonas de mayor a menor para que la mas grande quede atras */}
        {zonas
          .filter((z) => z.activa)
          .sort((a, b) => b.radio_km - a.radio_km)
          .map((zona) => (
            <Polygon
              key={zona.id}
              positions={generarPuntosCirculo(zona.center, zona.radio_km)}
              pathOptions={{
                color: zona.color,
                fillColor: zona.color,
                fillOpacity: 0.15,
                weight: 2,
              }}
            />
          ))}

        {/* Marcador del restaurante */}
        <CircleMarker
          center={centroRestaurante}
          radius={8}
          pathOptions={{
            color: "#1f2937",
            fillColor: "#f97316",
            fillOpacity: 1,
            weight: 3,
          }}
        />

        {/* Marcador de direccion seleccionada */}
        {posSeleccionada && (
          <CircleMarker
            center={posSeleccionada}
            radius={6}
            pathOptions={{
              color: zonaActual?.color ?? "#9ca3af",
              fillColor: zonaActual?.color ?? "#9ca3af",
              fillOpacity: 1,
              weight: 2,
            }}
          />
        )}

        <MapaInteractivo onSeleccionar={manejarSeleccion} />
      </MapContainer>

      <BuscadorDireccion onDireccionEncontrada={manejarSeleccion} />
      <PanelZona zona={zonaActual} distancia={distancia} />
    </div>
  )
}
```

---

## zone-manager.tsx

```tsx
/**
 * Administrador de zonas de delivery.
 * 
 * Permite crear, editar y eliminar zonas de cobertura.
 * Incluye formulario con validacion y selector de colores.
 */

"use client"

import { useState } from "react"
import { Plus, Edit2, Trash2, Save, X } from "lucide-react"
import { DeliveryZone, ZONAS_DEFECTO } from "./delivery-map"

export function ZoneManager() {
  const [zonas, setZonas] = useState<DeliveryZone[]>(ZONAS_DEFECTO)
  const [editando, setEditando] = useState<DeliveryZone | null>(null)
  const [esNueva, setEsNueva] = useState(false)

  /** Zona vacia para crear nueva */
  const zonaVacia: DeliveryZone = {
    id: `zona-${Date.now()}`,
    nombre: "",
    radio_km: 3,
    costo: 2.00,
    tiempo_min: 30,
    color: "#3b82f6",
    center: [-0.1807, -78.4678],
    activa: true,
  }

  const crearNueva = () => {
    setEditando({ ...zonaVacia })
    setEsNueva(true)
  }

  const editarZona = (zona: DeliveryZone) => {
    setEditando({ ...zona })
    setEsNueva(false)
  }

  const guardarZona = () => {
    if (!editando) return

    if (esNueva) {
      setZonas([...zonas, editando])
    } else {
      setZonas(zonas.map((z) => (z.id === editando.id ? editando : z)))
    }

    setEditando(null)
  }

  const eliminarZona = (id: string) => {
    if (confirm("Esta seguro de eliminar esta zona?")) {
      setZonas(zonas.filter((z) => z.id !== id))
    }
  }

  const toggleActiva = (id: string) => {
    setZonas(
      zonas.map((z) => (z.id === id ? { ...z, activa: !z.activa } : z))
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Zonas de Delivery</h2>
        <button
          onClick={crearNueva}
          className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
        >
          <Plus size={16} />
          Nueva Zona
        </button>
      </div>

      {/* Lista de zonas */}
      <div className="bg-white rounded-xl shadow-sm border divide-y">
        {zonas.map((zona) => (
          <div key={zona.id} className="p-4 flex items-center gap-4">
            <div
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: zona.color }}
            />
            <div className="flex-1">
              <div className="font-medium">{zona.nombre}</div>
              <div className="text-sm text-gray-500">
                Radio: {zona.radio_km} km | Costo: ${zona.costo.toFixed(2)} |
                Tiempo: {zona.tiempo_min} min
              </div>
            </div>
            <button
              onClick={() => toggleActiva(zona.id)}
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                zona.activa
                  ? "bg-green-100 text-green-700"
                  : "bg-gray-100 text-gray-500"
              }`}
            >
              {zona.activa ? "Activa" : "Inactiva"}
            </button>
            <div className="flex gap-1">
              <button
                onClick={() => editarZona(zona)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <Edit2 size={16} />
              </button>
              <button
                onClick={() => eliminarZona(zona.id)}
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {esNueva ? "Nueva Zona" : "Editar Zona"}
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
                  Nombre
                </label>
                <input
                  type="text"
                  value={editando.nombre}
                  onChange={(e) =>
                    setEditando({ ...editando, nombre: e.target.value })
                  }
                  placeholder="Ej: Zona Centro"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Radio (km)
                </label>
                <input
                  type="number"
                  value={editando.radio_km}
                  onChange={(e) =>
                    setEditando({
                      ...editando,
                      radio_km: parseFloat(e.target.value) || 0,
                    })
                  }
                  min="0.5"
                  max="50"
                  step="0.5"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Costo de envio ($)
                </label>
                <input
                  type="number"
                  value={editando.costo}
                  onChange={(e) =>
                    setEditando({
                      ...editando,
                      costo: parseFloat(e.target.value) || 0,
                    })
                  }
                  min="0"
                  step="0.50"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tiempo estimado (minutos)
                </label>
                <input
                  type="number"
                  value={editando.tiempo_min}
                  onChange={(e) =>
                    setEditando({
                      ...editando,
                      tiempo_min: parseInt(e.target.value) || 0,
                    })
                  }
                  min="5"
                  max="120"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Color
                </label>
                <div className="flex gap-2">
                  {["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6"].map(
                    (color) => (
                      <button
                        key={color}
                        onClick={() => setEditando({ ...editando, color })}
                        className={`w-8 h-8 rounded-full border-2 ${
                          editando.color === color
                            ? "border-gray-800"
                            : "border-transparent"
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    )
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
                onClick={guardarZona}
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

## delivery-page.tsx

```tsx
/**
 * Pagina completa de delivery.
 * 
 * Muestra mapa con zonas, formulario de direccion,
 * resumen de envio y historial reciente.
 */

"use client"

import { useState } from "react"
import { DeliveryMap, DeliveryZone } from "./delivery-map"
import { MapPin, Clock, DollarSign } from "lucide-react"

/** Informacion de delivery calculada */
interface DeliveryInfo {
  posicion: [number, number]
  zona: DeliveryZone | null
  costo: number
  tiempo: number
}

export function DeliveryPage() {
  const [direccionSeleccionada, setDireccionSeleccionada] =
    useState<DeliveryInfo | null>(null)
  const [direccionTexto, setDireccionTexto] = useState("")
  const [referencia, setReferencia] = useState("")

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Delivery</h1>
        <p className="text-gray-500">
          Selecciona tu direccion en el mapa
        </p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Mapa - ocupa 2/3 del ancho */}
        <div className="col-span-2">
          <DeliveryMap onDireccionSeleccionada={setDireccionSeleccionada} />
        </div>

        {/* Panel lateral */}
        <div className="space-y-4">
          {/* Formulario de direccion */}
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <MapPin size={18} />
              Direccion de entrega
            </h3>
            <input
              type="text"
              value={direccionTexto}
              onChange={(e) => setDireccionTexto(e.target.value)}
              placeholder="Escribe tu direccion..."
              className="w-full px-3 py-2 border rounded-lg text-sm mb-2"
            />
            <textarea
              value={referencia}
              onChange={(e) => setReferencia(e.target.value)}
              placeholder="Referencia (opcional): frente al parque, torre 2..."
              className="w-full px-3 py-2 border rounded-lg text-sm"
              rows={2}
            />
          </div>

          {/* Resumen de envio */}
          {direccionSeleccionada && (
            <div className="bg-white rounded-xl shadow-sm border p-4">
              <h3 className="font-semibold mb-3">Resumen del envio</h3>

              {direccionSeleccionada.zona ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Zona:</span>
                    <span
                      className="font-medium"
                      style={{ color: direccionSeleccionada.zona.color }}
                    >
                      {direccionSeleccionada.zona.nombre}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 flex items-center gap-1">
                      <DollarSign size={14} />
                      Costo:
                    </span>
                    <span className="font-bold text-green-600 text-lg">
                      ${direccionSeleccionada.costo.toFixed(2)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 flex items-center gap-1">
                      <Clock size={14} />
                      Tiempo estimado:
                    </span>
                    <span className="font-medium">
                      {direccionSeleccionada.tiempo} min
                    </span>
                  </div>

                  <button className="w-full py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium mt-4">
                    Confirmar direccion de envio
                  </button>
                </div>
              ) : (
                <div className="text-center py-4 text-gray-500">
                  <p>Esta direccion esta fuera de nuestra zona de cobertura</p>
                  <p className="text-sm mt-1">
                    Intenta con otra direccion mas cercana
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Envios recientes */}
          <div className="bg-white rounded-xl shadow-sm border p-4">
            <h3 className="font-semibold mb-3">Envios recientes</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm font-medium">Av. Amazonas 123</div>
                  <div className="text-xs text-gray-500">Hace 2 horas</div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                  Entregado
                </span>
              </div>
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm font-medium">Calle Larga 456</div>
                  <div className="text-xs text-gray-500">Ayer</div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                  Entregado
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

## lib/delivery-utils.ts

```typescript
/**
 * Utilidades para calculo de delivery.
 * 
 * Funciones puras para:
 * - Calcular distancia entre puntos (Haversine)
 * - Determinar zona de cobertura
 * - Estimar tiempo de entrega
 */

const RADIO_TIERRA_KM = 6371

/** Convierte grados a radianes */
function toRad(grados: number): number {
  return grados * (Math.PI / 180)
}

/**
 * Calcula distancia entre dos puntos geograficos (Haversine).
 * @returns Distancia en kilometros
 */
export function calcularDistanciaKm(
  point1: [number, number],
  point2: [number, number]
): number {
  const [lat1, lng1] = point1
  const [lat2, lng2] = point2

  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return RADIO_TIERRA_KM * c
}

/**
 * Determina la zona de cobertura para una posicion.
 * @returns Zona encontrada o null si esta fuera de cobertura
 */
export function determinarZona(
  posicion: [number, number],
  centroRestaurante: [number, number],
  zonas: Array<{
    radio_km: number
    costo: number
    tiempo_min: number
    nombre: string
    activa: boolean
  }>
): { zona: typeof zonas[0] | null; distancia: number } {
  const distancia = calcularDistanciaKm(centroRestaurante, posicion)

  const zonasActivas = zonas
    .filter((z) => z.activa)
    .sort((a, b) => a.radio_km - b.radio_km)

  for (const zona of zonasActivas) {
    if (distancia <= zona.radio_km) {
      return { zona, distancia }
    }
  }

  return { zona: null, distancia }
}

/**
 * Estima tiempo de entrega en base a distancia y zona.
 * @returns Minutos estimados
 */
export function estimarTiempoEntrega(
  distanciaKm: number,
  tiempoBaseZona: number
): number {
  const minutosPorKm = 2
  const adicional = Math.max(0, (distanciaKm - 1) * minutosPorKm)
  return Math.round(tiempoBaseZona + adicional)
}

/**
 * Verifica si una posicion esta dentro del radio maximo de cobertura.
 */
export function estaEnZonaCobertura(
  posicion: [number, number],
  centroRestaurante: [number, number],
  radioMaximoKm: number
): boolean {
  return calcularDistanciaKm(centroRestaurante, posicion) <= radioMaximoKm
}
```

---

## Backend - API de Zonas (Python)

```python
"""
Endpoints para gestion de zonas de delivery.

Permite al administrador:
- Obtener zonas configuradas
- Crear nuevas zonas
- Actualizar zonas existentes
- Eliminar zonas
- Validar direcciones
"""

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/api/delivery-zonas", tags=["delivery"])


class ZonaDeliveryCrear(BaseModel):
    """Modelo para crear zona de delivery."""
    nombre: str
    radio_km: float
    costo: float
    tiempo_estimado_min: int
    color: str = "#3b82f6"
    activa: bool = True


class ZonaDeliveryRespuesta(BaseModel):
    """Modelo de respuesta para zona de delivery."""
    id: int
    nombre: str
    radio_km: float
    costo: float
    tiempo_estimado_min: int
    color: str
    activa: bool


@router.get("/", response_model=List[ZonaDeliveryRespuesta])
async def obtener_zonas():
    """Obtiene todas las zonas de delivery configuradas."""
    return [
        ZonaDeliveryRespuesta(
            id=1, nombre="Zona 1 - Centro", radio_km=3,
            costo=2.00, tiempo_estimado_min=25,
            color="#22c55e", activa=True
        ),
        ZonaDeliveryRespuesta(
            id=2, nombre="Zona 2 - Intermedia", radio_km=6,
            costo=3.50, tiempo_estimado_min=40,
            color="#f59e0b", activa=True
        ),
        ZonaDeliveryRespuesta(
            id=3, nombre="Zona 3 - Periferia", radio_km=10,
            costo=5.00, tiempo_estimado_min=55,
            color="#ef4444", activa=True
        ),
    ]


@router.post("/", response_model=ZonaDeliveryRespuesta)
async def crear_zona(zona: ZonaDeliveryCrear):
    """Crea una nueva zona de delivery."""
    return ZonaDeliveryRespuesta(id=4, **zona.dict())


@router.put("/{zona_id}", response_model=ZonaDeliveryRespuesta)
async def actualizar_zona(zona_id: int, zona: ZonaDeliveryCrear):
    """Actualiza una zona de delivery existente."""
    return ZonaDeliveryRespuesta(id=zona_id, **zona.dict())


@router.delete("/{zona_id}")
async def eliminar_zona(zona_id: int):
    """Elimina una zona de delivery."""
    return {"message": "Zona eliminada correctamente"}


@router.post("/validar-direccion")
async def validar_direccion(lat: float, lng: float):
    """Valida si una direccion esta dentro de zona de cobertura."""
    centro = (-0.1807, -78.4678)
    zonas = await obtener_zonas()

    for zona in sorted(zonas, key=lambda z: z.radio_km):
        distancia = calcular_distancia(centro, (lat, lng))
        if distancia <= zona.radio_km:
            return {
                "valida": True,
                "zona": zona.nombre,
                "costo": zona.costo,
                "tiempo_estimado": zona.tiempo_estimado_min,
                "distancia_km": round(distancia, 2),
            }

    return {"valida": False, "mensaje": "Fuera de zona de cobertura"}


def calcular_distancia(p1, p2):
    """Calcula distancia usando Haversine."""
    import math
    lat1, lng1 = p1
    lat2, lng2 = p2
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
```

---

## Verificacion

- [ ] Mapa Leaflet funcional con zonas de colores
- [ ] Buscador de direcciones con OpenStreetMap
- [ ] Validacion de zona en tiempo real
- [ ] Calculo automatico de costo
- [ ] Estimacion de tiempo de entrega
- [ ] Admin de zonas (CRUD completo)
- [ ] Backend API para zonas
- [ ] Integracion con pagina de delivery
- [ ] Sin dependencias de APIs de pago
- [ ] Codigo bien comentado
- [ ] Sin emojis en el codigo
