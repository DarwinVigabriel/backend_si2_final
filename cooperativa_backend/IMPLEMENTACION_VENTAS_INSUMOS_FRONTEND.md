# 🌾 Implementación Frontend - Sistema de Ventas de Insumos

**Fecha:** 3 de Noviembre 2025  
**Desarrollador:** Frontend Team  
**Estado:** ✅ COMPLETADO Y LISTO PARA INTEGRACIÓN

---

## 📋 RESUMEN EJECUTIVO

Se implementó completamente el módulo frontend de **Ventas de Insumos** (CU13) siguiendo la arquitectura del sistema existente y la documentación del backend (`VENTAS_INSUMOS_QUICK_START.md`).

### ✅ LO QUE SE IMPLEMENTÓ:
- **1 Servicio API** completo con 4 sub-servicios
- **3 Páginas React** con diseño glassmorphism consistente
- **Integración completa** de rutas y navegación
- **Sincronización exacta** con endpoints del backend

---

## 🎯 ARQUITECTURA IMPLEMENTADA

### Base URL del Backend
```
http://localhost:8000/api/ventas/insumos/
```

### Estructura de Archivos Creados

```
src/
├── api/
│   └── insumosVentaService.js           ✅ NUEVO - Servicio completo
│
├── pages/
│   └── CU13_VentasInsumos/              ✅ NUEVO - Directorio del módulo
│       ├── PedidosInsumosPage.jsx       ✅ NUEVO - Listado principal
│       ├── PedidoInsumoFormPage.jsx     ✅ NUEVO - Formulario de solicitud
│       └── PedidoInsumoDetailPage.jsx   ✅ NUEVO - Detalle y pagos
│
├── components/
│   └── Layout/
│       └── Sidebar.jsx                   ✅ MODIFICADO - Menú agregado
│
└── App.jsx                               ✅ MODIFICADO - Rutas agregadas
```

---

## 🔌 SERVICIO API IMPLEMENTADO

### Archivo: `src/api/insumosVentaService.js`

Este servicio maneja **TODAS** las llamadas al backend del sistema de ventas de insumos.

#### 📦 4 Sub-Servicios Implementados:

#### 1️⃣ `preciosTemporadaService`
Maneja los precios por temporada de insumos.

```javascript
// Endpoints implementados:
GET /api/ventas/insumos/precios-temporada/      // Listar precios
GET /api/ventas/insumos/precios-temporada/{id}/ // Ver detalle

// Filtros soportados:
- tipo_insumo: 'SEMILLA' | 'PESTICIDA' | 'FERTILIZANTE'
- temporada: 'VERANO' | 'INVIERNO' | 'PRIMAVERA' | 'OTOÑO'
- activo: boolean
- vigente: boolean
```

**Uso:**
```javascript
import { preciosTemporadaService } from '@/api/insumosVentaService';

// Ver precios vigentes de semillas
const precios = await preciosTemporadaService.listar({
  tipo_insumo: 'SEMILLA',
  vigente: true,
  activo: true
});
```

---

#### 2️⃣ `pedidosInsumosService`
Maneja las solicitudes y pedidos de insumos.

```javascript
// Endpoints implementados:
GET  /api/ventas/insumos/pedidos/              // Listar pedidos
GET  /api/ventas/insumos/pedidos/{id}/         // Ver detalle
POST /api/ventas/insumos/pedidos/              // Crear solicitud
POST /api/ventas/insumos/pedidos/{id}/aprobar/ // Aprobar (ADMIN)
POST /api/ventas/insumos/pedidos/{id}/entregar/// Marcar entregado (ADMIN)

// Filtros soportados:
- socio: integer (ID del socio)
- estado: 'SOLICITADO' | 'APROBADO' | 'EN_PREPARACION' | 'LISTO_ENTREGA' | 'ENTREGADO' | 'CANCELADO'
- fecha_desde: 'YYYY-MM-DD'
- fecha_hasta: 'YYYY-MM-DD'
- page: integer
- page_size: integer
```

**Estructura de Datos para Crear:**
```javascript
{
  socio_id: 5,                              // ID del socio
  fecha_entrega_solicitada: "2025-11-15",  // Fecha requerida
  motivo_solicitud: "Texto...",             // Motivo de la solicitud
  observaciones: "Texto...",                // Opcional
  items: [                                  // Array de items
    {
      tipo_insumo: "SEMILLA",               // Tipo de insumo
      semilla: 10,                          // ID (solo uno de: semilla, pesticida, fertilizante)
      cantidad: 50.00,                      // Cantidad solicitada
      precio_unitario: 25.00                // Precio al momento de crear
    }
  ]
}
```

**Mapeo de Campos (Frontend → Backend):**
```javascript
// El servicio convierte automáticamente:
socio_id   → socio         // Integer directo
semilla    → semilla       // Integer directo (sin cambios)
pesticida  → pesticida     // Integer directo (sin cambios)
fertilizante → fertilizante // Integer directo (sin cambios)
```

---

#### 3️⃣ `pagosInsumosService`
Maneja los pagos de los pedidos de insumos.

```javascript
// Endpoints implementados:
GET  /api/ventas/insumos/pagos/  // Listar pagos
POST /api/ventas/insumos/pagos/  // Registrar pago

// Filtros soportados:
- pedido_insumo: integer (ID del pedido)
- metodo_pago: 'EFECTIVO' | 'TRANSFERENCIA' | 'DESCUENTO_PRODUCCION' | 'CREDITO' | 'OTRO'
- estado: 'PENDIENTE' | 'COMPLETADO' | 'PARCIAL' | 'CANCELADO'
- fecha_desde: 'YYYY-MM-DD'
- fecha_hasta: 'YYYY-MM-DD'
```

**Estructura de Datos para Registrar Pago:**
```javascript
// Caso 1: Pago en EFECTIVO
{
  pedido_insumo_id: 1,      // ID del pedido
  monto: 500.00,            // Monto a pagar
  metodo_pago: "EFECTIVO",  // Método
  observaciones: "..."      // Opcional
}

// Caso 2: Pago por TRANSFERENCIA
{
  pedido_insumo_id: 1,
  monto: 750.00,
  metodo_pago: "TRANSFERENCIA",
  referencia_bancaria: "REF-123456",  // ⚠️ REQUERIDO para transferencias
  banco: "Banco Nacional de Bolivia", // ⚠️ REQUERIDO para transferencias
  observaciones: "..."
}
```

**Mapeo de Campos (Frontend → Backend):**
```javascript
// El servicio convierte automáticamente:
pedido_insumo_id → pedido_insumo  // Integer directo

// Validación condicional:
if (metodo_pago === 'TRANSFERENCIA') {
  // Campos REQUERIDOS:
  - referencia_bancaria
  - banco
}
```

---

#### 4️⃣ `historialInsumosService`
Maneja el historial y exportación de datos.

```javascript
// Endpoints implementados:
GET /api/ventas/insumos/historial/      // Estadísticas
GET /api/ventas/insumos/exportar-csv/   // Exportar CSV

// Filtros soportados (para ambos):
- socio: integer
- fecha_desde: 'YYYY-MM-DD'
- fecha_hasta: 'YYYY-MM-DD'
- estado: string
```

**Respuesta de Historial:**
```javascript
{
  estadisticas: {
    total_pedidos: 12,
    total_gastado: "15350.00",
    total_pagado: "12000.00",
    saldo_pendiente: "3350.00"
  },
  pedidos: [...]  // Array de pedidos
}
```

---

## 🎨 PÁGINAS IMPLEMENTADAS

### 1️⃣ PedidosInsumosPage.jsx (Listado Principal)

**Ruta:** `/pedidos-insumos`  
**Propósito:** Vista principal con todos los pedidos del socio

#### Características:
✅ **4 Tarjetas de Estadísticas:**
- Total de Pedidos
- Total Gastado
- Total Pagado
- Saldo Pendiente

✅ **Filtros Avanzados:**
- Por estado del pedido
- Por rango de fechas (desde/hasta)
- Paginación con control de tamaño

✅ **Tabla de Pedidos con:**
- Número de pedido
- Fecha de solicitud
- Monto total
- Monto pagado
- Saldo pendiente
- Estado del pedido (badge con color)
- Estado de pago (badge con color)
- Botón "Ver Detalle"

✅ **Funcionalidades:**
- Exportar a CSV
- Navegación a detalle
- Crear nuevo pedido
- **Filtrado automático por socio** (socios solo ven sus propios pedidos)
- **Vista completa para admin** (admin ve todos los pedidos)

#### Colores de Estados Implementados:
```javascript
// Estados de Pedido:
SOLICITADO      → Azul    (bg-blue-500/20)
APROBADO        → Verde   (bg-green-500/20)
EN_PREPARACION  → Amarillo (bg-yellow-500/20)
LISTO_ENTREGA   → Púrpura (bg-purple-500/20)
ENTREGADO       → Esmeralda (bg-emerald-500/20)
RECHAZADO       → Rojo    (bg-red-500/20)
CANCELADO       → Gris    (bg-gray-500/20)

// Estados de Pago:
PENDIENTE → Rojo    (bg-red-500/20)
PARCIAL   → Amarillo (bg-yellow-500/20)
PAGADO    → Verde   (bg-green-500/20)
```

---

### 2️⃣ PedidoInsumoFormPage.jsx (Formulario de Solicitud)

**Ruta:** `/pedidos-insumos/nuevo`  
**Propósito:** Crear nueva solicitud de insumos

#### Características:
✅ **Sección 1: Información de la Solicitud**
- Fecha de entrega solicitada (date picker)
- Motivo de la solicitud (textarea)
- Observaciones adicionales (textarea opcional)

✅ **Sección 2: Insumos Solicitados**
- Lista dinámica de items
- Botón "Agregar Insumo"
- Cada item incluye:
  - Selector de tipo (SEMILLA/PESTICIDA/FERTILIZANTE)
  - Selector de insumo específico (carga precios disponibles)
  - Cantidad
  - Precio unitario (auto-completado desde precios)
  - Subtotal (calculado automáticamente)
  - Botón eliminar item

✅ **Sección 3: Totales**
- Subtotal general
- Total final
- Contador de items

#### Funcionalidades Especiales:
- **Auto-población de precios:** Al seleccionar un insumo, se carga automáticamente el precio
- **Precio mayoreo automático:** Si la cantidad supera el mínimo, aplica precio mayoreo
- **Cálculo en tiempo real:** Los totales se actualizan al cambiar cantidades
- **Validaciones:**
  - Fecha de entrega no puede ser anterior a hoy
  - Motivo de solicitud es requerido
  - Al menos 1 item es requerido
  - Todos los campos de cada item son requeridos

---

### 3️⃣ PedidoInsumoDetailPage.jsx (Detalle y Pagos)

**Ruta:** `/pedidos-insumos/:id`  
**Propósito:** Ver detalle completo y registrar pagos

#### Características:
✅ **Header con:**
- Número de pedido
- Fecha de solicitud
- Badge de estado del pedido
- Badge de estado de pago

✅ **Sección: Información del Socio**
- Nombre completo
- CI
- Teléfono
- Email

✅ **Sección: Detalles de la Solicitud**
- Fecha de solicitud
- Fecha de entrega solicitada
- Fecha de entrega real (si aplica)
- Motivo de la solicitud
- Observaciones

✅ **Sección: Insumos Solicitados (Tabla)**
- Tipo de insumo
- Nombre del insumo
- Cantidad
- Precio unitario
- Subtotal

✅ **Sección: Historial de Pagos**
- Número de recibo
- Fecha del pago
- Monto
- Método de pago
- Referencia (si aplica)
- Observaciones

✅ **Sidebar: Resumen Financiero**
- Total del pedido
- Monto pagado
- Saldo pendiente
- **Botón "Registrar Pago"** (si hay saldo pendiente)

#### Modal de Pago Implementado:
✅ **Campos:**
- Monto a pagar (pre-llenado con saldo pendiente)
- Método de pago (select)
- Referencia bancaria (solo si es TRANSFERENCIA)
- Banco (solo si es TRANSFERENCIA)
- Observaciones (opcional)

✅ **Validaciones:**
- Monto debe ser mayor a 0
- Monto no puede exceder saldo pendiente
- Si es TRANSFERENCIA, referencia y banco son obligatorios
- No se puede pagar pedidos CANCELADOS

✅ **Métodos de Pago Soportados:**
```javascript
EFECTIVO              → Auto-completado
TRANSFERENCIA         → Requiere referencia + banco
DESCUENTO_PRODUCCION  → Descuenta de ventas del socio
CREDITO               → Pago a crédito
OTRO                  → Otro método
```

#### Acciones Administrativas (Solo Admin):
✅ **Botón "Aprobar Solicitud"** (si estado = SOLICITADO)
- Cambia el estado a APROBADO
- Registra quién aprobó y cuándo

✅ **Botón "Marcar como Entregado"** (si estado = LISTO_ENTREGA)
- Cambia el estado a ENTREGADO
- Registra fecha de entrega real

---

## 🔗 INTEGRACIÓN DE RUTAS

### Archivo: `App.jsx`

Se agregaron 3 nuevas rutas protegidas:

```javascript
// ===== CU13: Ventas de Insumos =====
<Route
  path="/pedidos-insumos"
  element={
    <ProtectedLayout>
      <PedidosInsumosPage />
    </ProtectedLayout>
  }
/>
<Route
  path="/pedidos-insumos/nuevo"
  element={
    <ProtectedLayout>
      <PedidoInsumoFormPage />
    </ProtectedLayout>
  }
/>
<Route
  path="/pedidos-insumos/:id"
  element={
    <ProtectedLayout>
      <PedidoInsumoDetailPage />
    </ProtectedLayout>
  }
/>
```

**Protección:** Todas las rutas requieren autenticación (token válido).

---

## 🧭 INTEGRACIÓN DE NAVEGACIÓN

### Archivo: `Sidebar.jsx`

Se agregó un nuevo menú principal con submenú:

```javascript
{
  path: '/pedidos-insumos',
  label: 'Ventas de Insumos',
  icon: ShoppingBag,                      // Icono principal
  always: true,
  subMenu: [
    { 
      path: '/pedidos-insumos', 
      label: 'Mis Pedidos de Insumos', 
      icon: Package 
    },
    { 
      path: '/pedidos-insumos/nuevo', 
      label: 'Solicitar Insumos', 
      icon: ShoppingBag 
    }
  ]
}
```

**Iconos usados:**
- `ShoppingBag` (de lucide-react) - Menú principal y solicitar
- `Package` (de lucide-react) - Mis pedidos

---

## 🎨 DISEÑO Y ESTILO

### Consistencia con el Sistema Existente

Se mantuvo el **mismo diseño glassmorphism** del resto del sistema:

#### Paleta de Colores:
```css
/* Fondos principales */
bg-gradient-to-br from-emerald-950 via-emerald-900 to-emerald-800

/* Tarjetas glassmorphism */
bg-white/10 backdrop-blur-lg border border-white/20

/* Tarjetas de estadísticas con gradiente */
bg-gradient-to-br from-emerald-500/20 to-teal-500/20

/* Botones principales */
bg-gradient-to-r from-emerald-500 to-teal-500

/* Texto */
text-white           /* Títulos */
text-white/80        /* Subtítulos */
text-emerald-100/80  /* Descripciones */
```

#### Componentes Reutilizados:
- Badges con colores temáticos
- Inputs con estilo glassmorphism
- Botones con gradientes emerald/teal
- Tablas responsive
- Cards con backdrop-blur
- Modals con overlay oscuro

---

## 🔐 AUTENTICACIÓN Y PERMISOS

### Manejo de Roles:

#### SOCIO:
```javascript
// Se obtiene del localStorage:
const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
const socioId = userData.socio_id;
const isAdmin = userData.rol === 'ADMIN';

// Los socios solo ven sus propios pedidos:
if (!isAdmin) {
  filtros.socio = socioId;  // Auto-filtra por su ID
}
```

#### ADMIN:
```javascript
// Admin ve todos los pedidos sin filtro de socio
// Admin tiene botones adicionales:
- Aprobar solicitud
- Marcar como entregado
- Ver todos los pedidos del sistema
```

### CSRF Token:
```javascript
// El servicio incluye interceptor para CSRF:
api.interceptors.request.use((config) => {
  let csrfToken = localStorage.getItem('csrf_token');
  if (!csrfToken) {
    // Intenta obtener de cookies
    const cookies = document.cookie.split('; ');
    const csrfCookie = cookies.find(row => row.startsWith('csrftoken='));
    if (csrfCookie) {
      csrfToken = csrfCookie.split('=')[1];
    }
  }
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});
```

---

## 📊 FLUJO DE DATOS

### Flujo Completo del Sistema:

```
┌──────────────────────────────────────────────────────────────┐
│  1. SOCIO: Ver Precios                                       │
│     GET /api/ventas/insumos/precios-temporada/               │
│     Filtros: vigente=true, activo=true                       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  2. SOCIO: Crear Solicitud                                   │
│     POST /api/ventas/insumos/pedidos/                        │
│     Body: { socio, fecha_entrega, items[] }                  │
│     → Estado: SOLICITADO                                     │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  3. ADMIN: Aprobar                                           │
│     POST /api/ventas/insumos/pedidos/{id}/aprobar/           │
│     → Estado: APROBADO                                       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  4. ADMIN: Cambiar estados manualmente (Django Admin)       │
│     APROBADO → EN_PREPARACION → LISTO_ENTREGA               │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  5. ADMIN: Marcar Entregado                                  │
│     POST /api/ventas/insumos/pedidos/{id}/entregar/          │
│     → Estado: ENTREGADO                                      │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  6. SOCIO: Registrar Pago(s)                                 │
│     POST /api/ventas/insumos/pagos/                          │
│     Body: { pedido_insumo, monto, metodo_pago }              │
│     → Puede hacer múltiples pagos parciales                  │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  7. BACKEND: Calcular Automáticamente                        │
│     total_pagado = sum(pagos COMPLETADOS)                    │
│     saldo_pendiente = total - total_pagado                   │
│     estado_pago = PENDIENTE | PARCIAL | PAGADO               │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚠️ VALIDACIONES IMPLEMENTADAS

### En el Frontend:

#### Formulario de Solicitud:
```javascript
✅ Fecha de entrega no puede ser anterior a hoy
✅ Motivo de solicitud es requerido (no vacío)
✅ Al menos 1 item debe existir
✅ Todos los campos de cada item son requeridos
✅ Cantidad debe ser > 0
✅ Precio unitario debe ser > 0
✅ Solo se puede especificar UN tipo de insumo por item
```

#### Modal de Pago:
```javascript
✅ Monto debe ser > 0
✅ Monto no puede exceder saldo_pendiente
✅ No se puede pagar pedidos CANCELADOS
✅ Si metodo_pago = TRANSFERENCIA:
   - referencia_bancaria es REQUERIDA
   - banco es REQUERIDO
```

### Mensajes de Error:
Todos los errores del backend se muestran al usuario:
```javascript
try {
  await pedidosInsumosService.crear(datos);
} catch (error) {
  setError(error.response?.data?.error || 'Error al crear la solicitud');
}
```

---

## 🧪 TESTING RECOMENDADO

### Casos de Prueba para el Backend:

#### Test 1: Crear Solicitud Exitosa
```javascript
// Socio ID: 5
// Datos: fecha_entrega válida, 2 items de semillas
// Esperado: Pedido creado con estado SOLICITADO
```

#### Test 2: Aprobar Solicitud
```javascript
// Admin aprueba pedido ID 1
// Esperado: Estado cambia a APROBADO, se registra admin y fecha
```

#### Test 3: Pago Parcial
```javascript
// Pedido total: 1250.00
// Pago: 500.00 EFECTIVO
// Esperado: 
//   - total_pagado = 500.00
//   - saldo_pendiente = 750.00
//   - estado_pago = PARCIAL
```

#### Test 4: Pago Completo
```javascript
// Pedido total: 1250.00
// Pago anterior: 500.00
// Nuevo pago: 750.00 TRANSFERENCIA
// Esperado:
//   - total_pagado = 1250.00
//   - saldo_pendiente = 0.00
//   - estado_pago = PAGADO
```

#### Test 5: Validación de Exceso
```javascript
// Pedido total: 1250.00
// Pago anterior: 500.00
// Intento pagar: 800.00 (excede saldo de 750.00)
// Esperado: Error 400 "El monto excede el saldo pendiente"
```

#### Test 6: Transferencia sin Datos
```javascript
// metodo_pago: TRANSFERENCIA
// Sin referencia_bancaria o banco
// Esperado: Error 400 con campos requeridos
```

---

## 📡 ENDPOINTS CONSUMIDOS

### Resumen de Todas las Llamadas al Backend:

| Método | Endpoint | Página que lo usa | Propósito |
|--------|----------|-------------------|-----------|
| GET | `/api/ventas/insumos/precios-temporada/` | FormPage | Listar precios disponibles |
| GET | `/api/ventas/insumos/pedidos/` | ListPage | Listar pedidos del socio |
| GET | `/api/ventas/insumos/pedidos/{id}/` | DetailPage | Ver detalle completo |
| POST | `/api/ventas/insumos/pedidos/` | FormPage | Crear nueva solicitud |
| POST | `/api/ventas/insumos/pedidos/{id}/aprobar/` | DetailPage | Aprobar (solo admin) |
| POST | `/api/ventas/insumos/pedidos/{id}/entregar/` | DetailPage | Entregar (solo admin) |
| POST | `/api/ventas/insumos/pagos/` | DetailPage | Registrar pago |
| GET | `/api/ventas/insumos/pagos/` | DetailPage | Listar pagos del pedido |
| GET | `/api/ventas/insumos/historial/` | ListPage | Estadísticas (stats cards) |
| GET | `/api/ventas/insumos/exportar-csv/` | ListPage | Exportar a CSV |

---

## 🔧 CONFIGURACIÓN NECESARIA

### Variables de Entorno:
```javascript
// src/config/api.config.js
export const API_BASE_URL = 'http://localhost:8000/api';
```

### Dependencias Usadas:
```json
{
  "axios": "^1.12.2",          // HTTP client
  "react": "^19.1.1",          // Framework
  "react-router-dom": "latest", // Routing
  "lucide-react": "^0.544.0"   // Iconos
}
```

### LocalStorage Requerido:
```javascript
// Datos del usuario autenticado:
localStorage.setItem('user_data', JSON.stringify({
  id: 1,
  username: "juanperez",
  rol: "SOCIO",        // o "ADMIN"
  socio_id: 5,         // ID del socio (si rol=SOCIO)
  nombre: "Juan",
  apellido: "Pérez"
}));

// Token CSRF:
localStorage.setItem('csrf_token', 'token_aqui');
```

---

## 🚀 CÓMO PROBAR LA IMPLEMENTACIÓN

### 1. Verificar que el Backend esté corriendo:
```bash
python manage.py runserver
```

### 2. Iniciar el Frontend:
```bash
npm run dev
# o
npm start
```

### 3. Login con un usuario SOCIO:
```
- Ir a /login
- Ingresar credenciales de socio
- Verificar que localStorage tenga user_data con socio_id
```

### 4. Probar flujo completo:
```
✅ Ir a sidebar → "Ventas de Insumos" → "Solicitar Insumos"
✅ Llenar formulario y crear solicitud
✅ Ver que aparece en "Mis Pedidos de Insumos"
✅ Click en "Ver Detalle"
✅ Verificar que muestra toda la info correctamente
```

### 5. Login con usuario ADMIN:
```
✅ Ir a "Mis Pedidos de Insumos" (admin ve todos)
✅ Entrar al pedido creado
✅ Ver botón "Aprobar Solicitud"
✅ Aprobar
✅ Verificar cambio de estado
```

### 6. Registrar pago:
```
✅ Volver a entrar al pedido (como socio o admin)
✅ Click en "Registrar Pago"
✅ Llenar datos del pago
✅ Enviar
✅ Verificar que se actualiza saldo_pendiente
```

---

## 🐛 TROUBLESHOOTING

### Error: "404 Not Found"
**Causa:** El backend no tiene las rutas registradas  
**Solución:** Verificar que en `urls.py` estén registrados los ViewSets:
```python
router.register(r'ventas/insumos/precios-temporada', PrecioTemporadaViewSet)
router.register(r'ventas/insumos/pedidos', PedidoInsumoViewSet)
router.register(r'ventas/insumos/pagos', PagoInsumoViewSet)
```

### Error: "CSRF token missing"
**Causa:** No se está enviando el token CSRF  
**Solución:** Verificar que el interceptor de axios esté configurado y que el token esté en localStorage o cookies.

### Error: "No se cargan los precios"
**Causa:** No hay precios activos y vigentes en la BD  
**Solución:** Crear precios en Django Admin con:
- `activo = true`
- `fecha_inicio <= HOY <= fecha_fin`

### Error: "No puedo ver mis pedidos"
**Causa:** El `socio_id` no está en localStorage  
**Solución:** Verificar que al hacer login se guarde correctamente el `socio_id` en `user_data`.

---

## 📈 MÉTRICAS DE IMPLEMENTACIÓN

### Líneas de Código:
- **insumosVentaService.js**: ~280 líneas
- **PedidosInsumosPage.jsx**: ~470 líneas
- **PedidoInsumoFormPage.jsx**: ~530 líneas
- **PedidoInsumoDetailPage.jsx**: ~640 líneas
- **Total**: ~1,920 líneas de código nuevo

### Tiempo Estimado de Desarrollo:
- Servicio API: 2 horas
- Página de listado: 3 horas
- Formulario: 4 horas
- Página de detalle + modal: 5 horas
- Integración y testing: 2 horas
- **Total**: ~16 horas

---

## ✅ CHECKLIST DE ENTREGA

### Archivos Nuevos:
- [x] `src/api/insumosVentaService.js`
- [x] `src/pages/CU13_VentasInsumos/PedidosInsumosPage.jsx`
- [x] `src/pages/CU13_VentasInsumos/PedidoInsumoFormPage.jsx`
- [x] `src/pages/CU13_VentasInsumos/PedidoInsumoDetailPage.jsx`

### Archivos Modificados:
- [x] `src/App.jsx` (3 rutas agregadas)
- [x] `src/components/Layout/Sidebar.jsx` (menú agregado)

### Funcionalidades:
- [x] Listar precios de insumos
- [x] Crear solicitud de insumos
- [x] Ver mis pedidos
- [x] Ver detalle de pedido
- [x] Registrar pagos
- [x] Aprobar solicitud (admin)
- [x] Marcar entregado (admin)
- [x] Exportar a CSV
- [x] Filtros por estado y fecha
- [x] Paginación
- [x] Cálculo automático de totales
- [x] Validaciones de negocio

### Testing:
- [x] Flujo completo probado localmente
- [x] Validaciones funcionando
- [x] Responsive design
- [x] Manejo de errores
- [x] Loading states

---

## 📞 CONTACTO Y SOPORTE

**Desarrollado por:** Frontend Team  
**Fecha:** 3 de Noviembre 2025  
**Stack:** React 19.1.1 + Vite + Tailwind CSS + Axios

### Documentación de Referencia:
- `VENTAS_INSUMOS_QUICK_START.md` - Guía rápida del backend
- `VENTAS_INSUMOS_GUIA_FRONTEND.md` - Guía completa con ejemplos

---

## 🎯 PRÓXIMOS PASOS RECOMENDADOS

### Para el Backend:
1. ✅ Verificar que todos los endpoints estén expuestos
2. ✅ Verificar permisos de roles (SOCIO vs ADMIN)
3. ✅ Probar validaciones con datos del frontend
4. ✅ Verificar cálculos automáticos (total_pagado, saldo_pendiente)
5. ⚠️ Implementar notificaciones cuando cambia estado

### Para el Frontend:
1. ⏳ Testing end-to-end
2. ⏳ Implementar notificaciones en tiempo real
3. ⏳ Agregar gráficos de estadísticas
4. ⏳ Mejorar responsive en móviles
5. ⏳ Agregar tooltips y ayudas contextuales

---

**¡IMPLEMENTACIÓN COMPLETADA Y LISTA PARA INTEGRACIÓN! 🚀**

---

## 📋 APÉNDICE: EJEMPLO DE PAYLOAD COMPLETO

### Crear Solicitud:
```json
POST /api/ventas/insumos/pedidos/
Content-Type: application/json
Authorization: Bearer {token}

{
  "socio": 5,
  "fecha_entrega_solicitada": "2025-11-15",
  "motivo_solicitud": "Necesito insumos para la campaña de verano",
  "observaciones": "Entregar en parcela #3",
  "items": [
    {
      "tipo_insumo": "SEMILLA",
      "semilla": 10,
      "cantidad": 50.00,
      "precio_unitario": 25.00
    },
    {
      "tipo_insumo": "FERTILIZANTE",
      "fertilizante": 3,
      "cantidad": 30.00,
      "precio_unitario": 35.00
    }
  ]
}

// Respuesta esperada:
{
  "id": 1,
  "numero_pedido": "INS-20251103143052",
  "socio": 5,
  "estado": "SOLICITADO",
  "subtotal": "2300.00",
  "descuento": "0.00",
  "total": "2300.00",
  "total_pagado": "0.00",
  "saldo_pendiente": "2300.00",
  "estado_pago": "PENDIENTE",
  "items": [...]
}
```

### Registrar Pago:
```json
POST /api/ventas/insumos/pagos/
Content-Type: application/json
Authorization: Bearer {token}

{
  "pedido_insumo": 1,
  "monto": 500.00,
  "metodo_pago": "EFECTIVO",
  "observaciones": "Pago inicial del 21.7%"
}

// Respuesta esperada:
{
  "id": 1,
  "numero_recibo": "PGINS-20251103150230",
  "pedido_insumo": 1,
  "monto": "500.00",
  "metodo_pago": "EFECTIVO",
  "estado": "COMPLETADO",
  "fecha_pago": "2025-11-03T15:02:30-04:00"
}

// Luego hacer GET del pedido para ver totales actualizados:
GET /api/ventas/insumos/pedidos/1/

{
  "id": 1,
  "total": "2300.00",
  "total_pagado": "500.00",      // ← Actualizado
  "saldo_pendiente": "1800.00",  // ← Actualizado
  "estado_pago": "PARCIAL"       // ← Actualizado
}
```

---

**FIN DEL DOCUMENTO**
