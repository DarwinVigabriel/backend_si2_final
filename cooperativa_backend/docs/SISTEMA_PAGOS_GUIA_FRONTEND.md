# 🎯 Sistema de Pagos - Guía Completa para Frontend

**Fecha:** Noviembre 2025  
**Versión:** 1.0 - Documentación Simplificada

---

## 📖 ¿Qué hace este sistema?

### El Flujo Real:

```
1. 🌾 SOCIO cosecha productos → Ya existe (ProductoCosechado)
2. 🏪 COOPERATIVA vende productos a CLIENTES → PEDIDO (nuevo)
3. 💰 CLIENTE paga a la COOPERATIVA → PAGO (nuevo)
```

### ¿Quién usa qué?

| ROL | INTERFAZ | QUÉ HACE |
|-----|----------|----------|
| **ADMINISTRADOR** | Django Admin<br>`/admin/` | • Registra VENTAS (pedidos)<br>• Registra PAGOS de clientes<br>• Ve historial completo<br>• Exporta reportes |
| **SOCIO** | React App<br>(Vite + Axios) | • Ve SUS productos cosechados<br>• Ve ventas de SUS productos<br>• Ve cuánto se vendió de su producción<br>• NO registra pagos |

---

## 🎭 ROL: ADMINISTRADOR (Django Admin)

### ¿Qué puede hacer el admin?

El administrador usa el **panel de Django Admin** para gestionar las ventas:

#### 1️⃣ Registrar una VENTA (Pedido)
```
Cliente: "Quiero comprar 50kg de tomate"
Admin: Crea un PEDIDO con los productos
```

#### 2️⃣ Registrar PAGOS del cliente
```
Cliente: "Aquí está el dinero"
Admin: Registra el PAGO (efectivo, transferencia, Stripe, etc)
```

#### 3️⃣ Ver historial y reportes
```
Admin: Ve todas las ventas, filtra por fecha, exporta CSV
```

### Acceso al Admin:

```bash
URL: http://localhost:8000/admin/

# Secciones disponibles:
- COOPERATIVA > Pedidos          # Ver/crear ventas
- COOPERATIVA > Pagos             # Ver/registrar pagos
- COOPERATIVA > Detalles de pedidos  # Ver items vendidos
```

---

## 👨‍🌾 ROL: SOCIO (React App)

### ¿Qué puede hacer el socio?

El socio usa la **aplicación React** para consultar información de SUS productos:

#### 1️⃣ Ver sus productos cosechados
```javascript
GET /api/productos-cosechados/?socio_id={mi_id}
```
"¿Qué productos tengo disponibles?"

#### 2️⃣ Ver ventas de SUS productos
```javascript
GET /api/pedidos/?socio_id={mi_id}
```
"¿Cuáles de mis productos se vendieron?"

#### 3️⃣ Ver pagos relacionados
```javascript
GET /api/pagos/?pedido__socio={mi_id}
```
"¿Cuánto dinero ingresó por la venta de mis productos?"

### ⚠️ Restricciones del Socio:
- ✅ Puede VER sus productos y ventas
- ❌ NO puede registrar pedidos (solo admin)
- ❌ NO puede registrar pagos (solo admin)
- ❌ NO ve productos de otros socios

---

## 🔌 API Endpoints - Guía Completa

### Base URL
```
http://localhost:8000/api/
```

### Autenticación
Todos los endpoints requieren token:
```javascript
headers: {
  'Authorization': 'Bearer tu_token_aqui'
}
```

---

## 📦 PEDIDOS (Ventas)

### 1. Listar Pedidos

**Endpoint:**
```http
GET /api/pedidos/
```

**Parámetros (query params):**
| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `socio_id` | integer | Filtrar por socio (para socios) | `?socio_id=5` |
| `estado` | string | PENDIENTE, CONFIRMADO, EN_PROCESO, COMPLETADO, CANCELADO | `?estado=CONFIRMADO` |
| `fecha_desde` | date | Desde fecha | `?fecha_desde=2025-11-01` |
| `fecha_hasta` | date | Hasta fecha | `?fecha_hasta=2025-11-30` |
| `cliente_nombre` | string | Buscar por nombre | `?cliente_nombre=María` |

**Ejemplo para ADMIN (ve todos):**
```javascript
// Ver todos los pedidos
axios.get('/api/pedidos/')

// Filtrar por estado
axios.get('/api/pedidos/?estado=COMPLETADO')

// Filtrar por fecha
axios.get('/api/pedidos/?fecha_desde=2025-11-01&fecha_hasta=2025-11-30')
```

**Ejemplo para SOCIO (solo ve los suyos):**
```javascript
// Ver pedidos que incluyen MIS productos
const miSocioId = 5; // ID del socio logueado
axios.get(`/api/pedidos/?socio_id=${miSocioId}`)
```

**Respuesta:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero_pedido": "PED-20251103143052",
      "fecha_pedido": "2025-11-03T10:30:00-04:00",
      "socio": 5,
      "socio_nombre": "Juan Pérez",
      "cliente_nombre": "María González",
      "cliente_email": "maria@example.com",
      "cliente_telefono": "+591 70123456",
      "cliente_direccion": "Av. Principal #123, La Paz",
      "items": [
        {
          "id": 1,
          "producto_cosechado": 10,
          "producto_nombre": "Tomate",
          "cantidad": "50.00",
          "unidad_medida": "kg",
          "precio_unitario": "15.00",
          "subtotal": "750.00"
        }
      ],
      "subtotal": "750.00",
      "impuestos": "97.50",
      "descuento": "0.00",
      "total": "847.50",
      "total_pagado": "500.00",
      "saldo_pendiente": "347.50",
      "estado": "CONFIRMADO",
      "estado_pago": "PARCIAL",
      "observaciones": "Entrega a domicilio"
    }
  ]
}
```

### 2. Ver Detalle de un Pedido

**Endpoint:**
```http
GET /api/pedidos/{id}/
```

**Ejemplo:**
```javascript
axios.get('/api/pedidos/1/')
```

### 3. Crear Pedido (SOLO ADMIN via Django Admin)

⚠️ **IMPORTANTE:** Los socios NO crean pedidos desde React.  
El admin los crea desde Django Admin en `/admin/cooperativa/pedido/add/`

**Si necesitas API para crear pedidos:**
```http
POST /api/pedidos/
Content-Type: application/json
```

**Body:**
```json
{
  "socio": 5,
  "cliente_nombre": "María González",
  "cliente_email": "maria@example.com",
  "cliente_telefono": "+591 70123456",
  "cliente_direccion": "Av. Principal #123",
  "fecha_entrega_estimada": "2025-11-05",
  "descuento": "0.00",
  "observaciones": "Entrega en la mañana",
  "items": [
    {
      "producto_cosechado": 10,
      "producto_nombre": "Tomate",
      "producto_descripcion": "Tomate fresco",
      "cantidad": "50.00",
      "unidad_medida": "kg",
      "precio_unitario": "15.00"
    }
  ]
}
```

---

## 💰 PAGOS

### 1. Listar Pagos

**Endpoint:**
```http
GET /api/pagos/
```

**Parámetros:**
| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `pedido_id` | integer | Filtrar por pedido | `?pedido_id=1` |
| `estado` | string | PENDIENTE, COMPLETADO, FALLIDO, etc | `?estado=COMPLETADO` |
| `metodo_pago` | string | EFECTIVO, TRANSFERENCIA, STRIPE, QR | `?metodo_pago=EFECTIVO` |
| `fecha_desde` | date | Desde fecha | `?fecha_desde=2025-11-01` |
| `fecha_hasta` | date | Hasta fecha | `?fecha_hasta=2025-11-30` |

**Ejemplo para ADMIN:**
```javascript
// Ver todos los pagos
axios.get('/api/pagos/')

// Pagos de un pedido específico
axios.get('/api/pagos/?pedido_id=1')
```

**Ejemplo para SOCIO:**
```javascript
// Ver pagos relacionados con mis productos
const miSocioId = 5;
axios.get(`/api/pagos/?pedido__socio=${miSocioId}`)
```

**Respuesta:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "numero_recibo": "PAG-20251103150230",
      "pedido": 1,
      "pedido_numero": "PED-20251103143052",
      "fecha_pago": "2025-11-03T11:00:00-04:00",
      "monto": "500.00",
      "metodo_pago": "EFECTIVO",
      "metodo_pago_display": "Efectivo",
      "estado": "COMPLETADO",
      "estado_display": "Completado",
      "observaciones": "Pago inicial",
      "procesado_por": 1,
      "procesado_por_nombre": "Admin Usuario"
    }
  ]
}
```

### 2. Registrar Pago (SOLO ADMIN via Django Admin)

⚠️ Los socios NO registran pagos. Solo el admin desde `/admin/cooperativa/pago/add/`

---

## 📊 HISTORIAL Y REPORTES

### 1. Historial de Ventas

**Endpoint:**
```http
GET /api/historial-ventas/
```

**Parámetros:**
Todos los mismos de pedidos + estadísticas agregadas

**Ejemplo:**
```javascript
axios.get('/api/historial-ventas/', {
  params: {
    fecha_desde: '2025-11-01',
    fecha_hasta: '2025-11-30',
    socio_id: 5  // Solo para socios
  }
})
```

**Respuesta:**
```json
{
  "estadisticas": {
    "total_ventas": 5,
    "total_monto": "4237.50",
    "total_pagado": "3500.00",
    "total_pendiente": "737.50"
  },
  "ventas": [
    {
      "id": 1,
      "numero_pedido": "PED-20251103143052",
      "fecha_pedido": "2025-11-03T10:30:00-04:00",
      "cliente_nombre": "María González",
      "total": "847.50",
      "total_pagado": "500.00",
      "saldo_pendiente": "347.50",
      "estado": "CONFIRMADO",
      "estado_pago": "PARCIAL"
    }
  ]
}
```

### 2. Exportar a CSV (SOLO ADMIN)

**Endpoint:**
```http
GET /api/exportar-ventas-csv/
```

**Parámetros:** Los mismos que historial

**Ejemplo:**
```javascript
// Descargar CSV
window.location.href = '/api/exportar-ventas-csv/?fecha_desde=2025-11-01&fecha_hasta=2025-11-30';
```

---

## 🎨 COMPONENTES REACT - Ejemplos Completos

### Setup Inicial

**Instalar dependencias:**
```bash
npm install axios
```

**Configurar Axios:**
```javascript
// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
```

---

### 📦 Componente: Lista de Ventas (Para Socios)

```jsx
// src/components/MisVentas.jsx
import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const MisVentas = () => {
  const [ventas, setVentas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtros, setFiltros] = useState({
    fecha_desde: '',
    fecha_hasta: '',
    estado: ''
  });

  // Obtener ID del socio del contexto/localStorage
  const socioId = localStorage.getItem('socio_id'); // Asume que guardaste el ID al login

  useEffect(() => {
    cargarVentas();
  }, [filtros]);

  const cargarVentas = async () => {
    try {
      setLoading(true);
      const params = {
        socio_id: socioId,  // ✅ Filtrar solo MIS ventas
        ...filtros
      };
      
      const response = await api.get('/pedidos/', { params });
      setVentas(response.data.results);
    } catch (error) {
      console.error('Error al cargar ventas:', error);
      alert('Error al cargar las ventas');
    } finally {
      setLoading(false);
    }
  };

  const obtenerColorEstado = (estadoPago) => {
    const colores = {
      'PENDIENTE': 'bg-red-100 text-red-800',
      'PARCIAL': 'bg-yellow-100 text-yellow-800',
      'PAGADO': 'bg-green-100 text-green-800'
    };
    return colores[estadoPago] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="text-center py-4">Cargando...</div>;

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-bold mb-6">Mis Ventas</h1>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Desde</label>
            <input
              type="date"
              value={filtros.fecha_desde}
              onChange={(e) => setFiltros({...filtros, fecha_desde: e.target.value})}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Hasta</label>
            <input
              type="date"
              value={filtros.fecha_hasta}
              onChange={(e) => setFiltros({...filtros, fecha_hasta: e.target.value})}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Estado</label>
            <select
              value={filtros.estado}
              onChange={(e) => setFiltros({...filtros, estado: e.target.value})}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Todos</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="CONFIRMADO">Confirmado</option>
              <option value="EN_PROCESO">En Proceso</option>
              <option value="COMPLETADO">Completado</option>
              <option value="CANCELADO">Cancelado</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabla de ventas */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                N° Pedido
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Cliente
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Fecha
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Total
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Pagado
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Pendiente
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                Estado Pago
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {ventas.map((venta) => (
              <tr key={venta.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {venta.numero_pedido}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {venta.cliente_nombre}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {new Date(venta.fecha_pedido).toLocaleDateString('es-BO')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                  Bs. {parseFloat(venta.total).toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-green-600">
                  Bs. {parseFloat(venta.total_pagado).toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-600">
                  Bs. {parseFloat(venta.saldo_pendiente).toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${obtenerColorEstado(venta.estado_pago)}`}>
                    {venta.estado_pago}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm">
                  <button
                    onClick={() => window.location.href = `/ventas/${venta.id}`}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Ver Detalle
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {ventas.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No se encontraron ventas
          </div>
        )}
      </div>
    </div>
  );
};

export default MisVentas;
```

---

### 📋 Componente: Detalle de Venta

```jsx
// src/components/DetalleVenta.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api/axios';

const DetalleVenta = () => {
  const { id } = useParams();
  const [venta, setVenta] = useState(null);
  const [pagos, setPagos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDatos();
  }, [id]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      
      // Cargar venta
      const ventaRes = await api.get(`/pedidos/${id}/`);
      setVenta(ventaRes.data);
      
      // Cargar pagos de esta venta
      const pagosRes = await api.get(`/pagos/?pedido_id=${id}`);
      setPagos(pagosRes.data.results);
    } catch (error) {
      console.error('Error al cargar datos:', error);
      alert('Error al cargar el detalle');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-4">Cargando...</div>;
  if (!venta) return <div className="text-center py-4">Venta no encontrada</div>;

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold">Pedido {venta.numero_pedido}</h1>
            <p className="text-gray-500">
              {new Date(venta.fecha_pedido).toLocaleDateString('es-BO', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Estado</div>
            <div className="text-xl font-bold">{venta.estado}</div>
          </div>
        </div>

        {/* Información del Cliente */}
        <div className="border-t pt-4">
          <h3 className="font-semibold mb-2">Información del Cliente</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Nombre:</span>
              <span className="ml-2 font-medium">{venta.cliente_nombre}</span>
            </div>
            <div>
              <span className="text-gray-500">Email:</span>
              <span className="ml-2 font-medium">{venta.cliente_email}</span>
            </div>
            <div>
              <span className="text-gray-500">Teléfono:</span>
              <span className="ml-2 font-medium">{venta.cliente_telefono}</span>
            </div>
            {venta.cliente_direccion && (
              <div>
                <span className="text-gray-500">Dirección:</span>
                <span className="ml-2 font-medium">{venta.cliente_direccion}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Items del Pedido */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Productos</h3>
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">
                Producto
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">
                Cantidad
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">
                Precio Unit.
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">
                Subtotal
              </th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {venta.items.map((item) => (
              <tr key={item.id}>
                <td className="px-4 py-3">
                  <div className="font-medium">{item.producto_nombre}</div>
                  {item.producto_descripcion && (
                    <div className="text-sm text-gray-500">{item.producto_descripcion}</div>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  {parseFloat(item.cantidad).toFixed(2)} {item.unidad_medida}
                </td>
                <td className="px-4 py-3 text-right">
                  Bs. {parseFloat(item.precio_unitario).toFixed(2)}
                </td>
                <td className="px-4 py-3 text-right font-medium">
                  Bs. {parseFloat(item.subtotal).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Totales */}
        <div className="border-t mt-4 pt-4">
          <div className="flex justify-end">
            <div className="w-64 space-y-2">
              <div className="flex justify-between text-sm">
                <span>Subtotal:</span>
                <span>Bs. {parseFloat(venta.subtotal).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Impuestos (13%):</span>
                <span>Bs. {parseFloat(venta.impuestos).toFixed(2)}</span>
              </div>
              {parseFloat(venta.descuento) > 0 && (
                <div className="flex justify-between text-sm text-red-600">
                  <span>Descuento:</span>
                  <span>- Bs. {parseFloat(venta.descuento).toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-lg font-bold border-t pt-2">
                <span>TOTAL:</span>
                <span>Bs. {parseFloat(venta.total).toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Estado de Pagos */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Estado de Pago</h3>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 rounded p-4">
            <div className="text-sm text-blue-600">Total Venta</div>
            <div className="text-2xl font-bold text-blue-900">
              Bs. {parseFloat(venta.total).toFixed(2)}
            </div>
          </div>
          <div className="bg-green-50 rounded p-4">
            <div className="text-sm text-green-600">Total Pagado</div>
            <div className="text-2xl font-bold text-green-900">
              Bs. {parseFloat(venta.total_pagado).toFixed(2)}
            </div>
          </div>
          <div className="bg-red-50 rounded p-4">
            <div className="text-sm text-red-600">Saldo Pendiente</div>
            <div className="text-2xl font-bold text-red-900">
              Bs. {parseFloat(venta.saldo_pendiente).toFixed(2)}
            </div>
          </div>
        </div>

        {/* Historial de Pagos */}
        <h4 className="font-semibold mb-3">Historial de Pagos</h4>
        {pagos.length > 0 ? (
          <div className="space-y-2">
            {pagos.map((pago) => (
              <div key={pago.id} className="flex justify-between items-center border-l-4 border-green-500 bg-gray-50 p-3 rounded">
                <div>
                  <div className="font-medium">{pago.numero_recibo}</div>
                  <div className="text-sm text-gray-500">
                    {new Date(pago.fecha_pago).toLocaleDateString('es-BO')} • {pago.metodo_pago_display}
                  </div>
                  {pago.observaciones && (
                    <div className="text-sm text-gray-600 mt-1">{pago.observaciones}</div>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600">
                    Bs. {parseFloat(pago.monto).toFixed(2)}
                  </div>
                  <div className="text-sm">
                    <span className={`px-2 py-1 rounded text-xs ${
                      pago.estado === 'COMPLETADO' ? 'bg-green-100 text-green-800' :
                      pago.estado === 'PENDIENTE' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {pago.estado_display}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500 bg-gray-50 rounded">
            No hay pagos registrados
          </div>
        )}
      </div>

      {/* Observaciones */}
      {venta.observaciones && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Observaciones</h3>
          <p className="text-gray-700">{venta.observaciones}</p>
        </div>
      )}
    </div>
  );
};

export default DetalleVenta;
```

---

### 📊 Componente: Estadísticas (Dashboard)

```jsx
// src/components/EstadisticasVentas.jsx
import React, { useState, useEffect } from 'react';
import api from '../api/axios';

const EstadisticasVentas = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [periodo, setPeriodo] = useState('mes'); // mes, semana, año

  const socioId = localStorage.getItem('socio_id');

  useEffect(() => {
    cargarEstadisticas();
  }, [periodo]);

  const cargarEstadisticas = async () => {
    try {
      setLoading(true);
      
      // Calcular fechas según período
      const hoy = new Date();
      let fechaDesde;
      
      if (periodo === 'semana') {
        fechaDesde = new Date(hoy.setDate(hoy.getDate() - 7));
      } else if (periodo === 'mes') {
        fechaDesde = new Date(hoy.setMonth(hoy.getMonth() - 1));
      } else {
        fechaDesde = new Date(hoy.setFullYear(hoy.getFullYear() - 1));
      }
      
      const params = {
        socio_id: socioId,
        fecha_desde: fechaDesde.toISOString().split('T')[0],
        fecha_hasta: new Date().toISOString().split('T')[0]
      };
      
      const response = await api.get('/historial-ventas/', { params });
      setStats(response.data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-4">Cargando estadísticas...</div>;
  if (!stats) return null;

  const { estadisticas } = stats;

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Mis Estadísticas de Ventas</h1>
        
        <select
          value={periodo}
          onChange={(e) => setPeriodo(e.target.value)}
          className="border rounded px-4 py-2"
        >
          <option value="semana">Última Semana</option>
          <option value="mes">Último Mes</option>
          <option value="año">Último Año</option>
        </select>
      </div>

      {/* Cards de Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
          <div className="text-sm opacity-90 mb-2">Total Ventas</div>
          <div className="text-4xl font-bold mb-1">{estadisticas.total_ventas}</div>
          <div className="text-sm opacity-75">pedidos</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
          <div className="text-sm opacity-90 mb-2">Monto Total</div>
          <div className="text-4xl font-bold mb-1">
            {parseFloat(estadisticas.total_monto).toFixed(0)}
          </div>
          <div className="text-sm opacity-75">Bs.</div>
        </div>

        <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg shadow-lg p-6 text-white">
          <div className="text-sm opacity-90 mb-2">Total Pagado</div>
          <div className="text-4xl font-bold mb-1">
            {parseFloat(estadisticas.total_pagado).toFixed(0)}
          </div>
          <div className="text-sm opacity-75">Bs.</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg shadow-lg p-6 text-white">
          <div className="text-sm opacity-90 mb-2">Pendiente</div>
          <div className="text-4xl font-bold mb-1">
            {parseFloat(estadisticas.total_pendiente).toFixed(0)}
          </div>
          <div className="text-sm opacity-75">Bs.</div>
        </div>
      </div>

      {/* Gráfico de Progreso */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold mb-4">Progreso de Cobro</h3>
        <div className="relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block text-green-600">
                Pagado: Bs. {parseFloat(estadisticas.total_pagado).toFixed(2)}
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs font-semibold inline-block text-gray-600">
                {((parseFloat(estadisticas.total_pagado) / parseFloat(estadisticas.total_monto)) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
            <div
              style={{
                width: `${(parseFloat(estadisticas.total_pagado) / parseFloat(estadisticas.total_monto)) * 100}%`
              }}
              className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500"
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EstadisticasVentas;
```

---

## 🔐 Autenticación y Permisos

### Login y obtener Token

```javascript
// src/services/auth.js
import api from '../api/axios';

export const login = async (username, password) => {
  try {
    const response = await api.post('/login/', {
      usuario: username,
      password: password
    });
    
    const { token, user } = response.data;
    
    // Guardar en localStorage
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    // Si es socio, guardar su ID
    if (user.socio_id) {
      localStorage.setItem('socio_id', user.socio_id);
    }
    
    return { success: true, user };
  } catch (error) {
    console.error('Error en login:', error);
    return { 
      success: false, 
      error: error.response?.data?.error || 'Error al iniciar sesión' 
    };
  }
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('socio_id');
  window.location.href = '/login';
};

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

export const isSocio = () => {
  const user = getCurrentUser();
  return user && !!user.socio_id;
};
```

### Componente de Login

```jsx
// src/components/Login.jsx
import React, { useState } from 'react';
import { login } from '../services/auth';

const Login = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    const result = await login(credentials.username, credentials.password);
    
    if (result.success) {
      // Redirigir según el rol
      if (result.user.is_staff) {
        window.location.href = '/admin/';
      } else {
        window.location.href = '/dashboard';
      }
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6 text-center">
          Cooperativa Agrícola
        </h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Usuario</label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full border rounded px-3 py-2"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Contraseña</label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full border rounded px-3 py-2"
              required
            />
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
```

---

## 🗂️ Estructura del Proyecto React

```
src/
├── api/
│   └── axios.js                 # Configuración de Axios
├── components/
│   ├── Login.jsx                # Login
│   ├── MisVentas.jsx            # Lista de ventas del socio
│   ├── DetalleVenta.jsx         # Detalle de una venta
│   ├── EstadisticasVentas.jsx   # Dashboard con estadísticas
│   └── Layout.jsx               # Layout general
├── services/
│   └── auth.js                  # Servicios de autenticación
├── App.jsx                      # Rutas principales
└── main.jsx                     # Punto de entrada
```

### Rutas Principales (App.jsx)

```jsx
// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated, isSocio } from './services/auth';
import Login from './components/Login';
import MisVentas from './components/MisVentas';
import DetalleVenta from './components/DetalleVenta';
import EstadisticasVentas from './components/EstadisticasVentas';
import Layout from './components/Layout';

// Componente para proteger rutas
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  
  // Si no es socio, redirigir al admin de Django
  if (!isSocio()) {
    window.location.href = '/admin/';
    return null;
  }
  
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<EstadisticasVentas />} />
          <Route path="ventas" element={<MisVentas />} />
          <Route path="ventas/:id" element={<DetalleVenta />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 📝 Resumen de Campos - Referencia Rápida

### Pedido (Venta)
```javascript
{
  id: integer,
  numero_pedido: "PED-YYYYMMDDHHmmss",  // Auto-generado
  fecha_pedido: "2025-11-03T10:30:00-04:00",
  socio: integer,                        // ID del socio
  socio_nombre: "Juan Pérez",           // Read-only
  cliente_nombre: "María González",
  cliente_email: "maria@example.com",
  cliente_telefono: "+591 70123456",
  cliente_direccion: "Dirección...",
  items: [...],                          // Array de DetallePedido
  subtotal: "750.00",                    // Suma de items
  impuestos: "97.50",                    // 13% del subtotal
  descuento: "0.00",
  total: "847.50",                       // subtotal + impuestos - descuento
  total_pagado: "500.00",                // Calculado (read-only)
  saldo_pendiente: "347.50",             // Calculado (read-only)
  estado: "CONFIRMADO",                  // PENDIENTE|CONFIRMADO|EN_PROCESO|COMPLETADO|CANCELADO
  estado_pago: "PARCIAL",                // PENDIENTE|PARCIAL|PAGADO (read-only)
  observaciones: "Notas..."
}
```

### DetallePedido (Item)
```javascript
{
  id: integer,
  pedido: integer,
  producto_cosechado: integer,           // FK al ProductoCosechado
  producto_nombre: "Tomate",             // Nombre del producto
  producto_descripcion: "Fresco...",     // Opcional
  cantidad: "50.00",
  unidad_medida: "kg",                   // kg, unidad, litro, etc
  precio_unitario: "15.00",
  subtotal: "750.00"                     // Calculado automáticamente
}
```

### Pago
```javascript
{
  id: integer,
  numero_recibo: "PAG-YYYYMMDDHHmmss",  // Auto-generado
  pedido: integer,
  pedido_numero: "PED-...",              // Read-only
  fecha_pago: "2025-11-03T11:00:00-04:00",
  monto: "500.00",
  metodo_pago: "EFECTIVO",               // EFECTIVO|TRANSFERENCIA|STRIPE|QR|OTRO
  metodo_pago_display: "Efectivo",       // Read-only
  estado: "COMPLETADO",                  // PENDIENTE|PROCESANDO|COMPLETADO|FALLIDO|REEMBOLSADO|CANCELADO
  estado_display: "Completado",          // Read-only
  referencia_bancaria: "REF-123",        // Para transferencias
  banco: "Banco Nacional",
  comprobante_archivo: "/path/file.pdf",
  observaciones: "Notas...",
  procesado_por: integer,
  procesado_por_nombre: "Admin"          // Read-only
}
```

---

## ✅ Checklist de Implementación

### Para Administradores (Django Admin):
- [ ] Acceder a `/admin/cooperativa/pedido/` para crear ventas
- [ ] Acceder a `/admin/cooperativa/pago/` para registrar pagos
- [ ] Usar filtros para buscar ventas por fecha/cliente
- [ ] Exportar reportes en CSV
- [ ] Verificar estado de pagos de cada venta

### Para Socios (React App):
- [ ] Implementar login y guardar token
- [ ] Mostrar lista de ventas filtrando por `socio_id`
- [ ] Mostrar detalle de cada venta con items y pagos
- [ ] Mostrar dashboard con estadísticas
- [ ] Implementar filtros por fecha y estado
- [ ] Mostrar estado de pago de cada venta
- [ ] NO permitir crear/editar pedidos o pagos

---

## 🆘 Solución de Problemas

### Error 401 Unauthorized
```javascript
// Verificar que el token esté en el header
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}
```

### No se muestran las ventas del socio
```javascript
// Asegurarse de filtrar por socio_id
const socioId = localStorage.getItem('socio_id');
axios.get(`/api/pedidos/?socio_id=${socioId}`)
```

### Error al crear pedido
⚠️ Recuerda: Los socios NO crean pedidos desde React.  
Solo el administrador lo hace desde Django Admin.

---

## 📞 Contacto

- **Backend API:** `http://localhost:8000/api/`
- **Django Admin:** `http://localhost:8000/admin/`
- **Documentación adicional:** Ver carpeta `docs/`

---

**Última actualización:** 3 de Noviembre 2025  
**Versión:** 1.0
