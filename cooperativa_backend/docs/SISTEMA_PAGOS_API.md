# Sistema de Pagos - Documentación API Backend

**Fecha:** Noviembre 2025  
**Versión:** 1.0  
**Autor:** Backend SI2 - Sistema de Pagos

---

## 📋 Tabla de Contenido

1. [Descripción General](#descripción-general)
2. [Modelos de Datos](#modelos-de-datos)
3. [Endpoints API](#endpoints-api)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Códigos de Estado](#códigos-de-estado)
6. [Configuración Stripe](#configuración-stripe)
7. [Permisos y Seguridad](#permisos-y-seguridad)

---

## 🎯 Descripción General

El sistema de pagos permite a los administradores registrar pedidos/órdenes de venta y gestionar los pagos asociados. Incluye:

- ✅ Registro de pedidos con múltiples productos
- ✅ Múltiples métodos de pago (Efectivo, Transferencia, Stripe, QR)
- ✅ Integración con Stripe para pagos en línea
- ✅ Historial de ventas con filtros avanzados
- ✅ Exportación a CSV
- ✅ Control de estados de pedidos y pagos
- ✅ Registro en bitácora de auditoría

**Base URL:** `http://localhost:8000/api/`

---

## 📊 Modelos de Datos

### 1. Pedido (Orden de Venta)

Representa una orden de compra de productos.

```json
{
  "id": 1,
  "numero_pedido": "PED-20251103143052",
  "fecha_pedido": "2025-11-03T10:30:00-04:00",
  "fecha_entrega_estimada": "2025-11-05",
  "fecha_entrega_real": null,
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
      "producto_descripcion": "Tomate fresco de calidad premium",
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
  "observaciones": "Entrega a domicilio",
  "creado_por": 1,
  "creado_por_nombre": "Admin Usuario",
  "creado_en": "2025-11-03T10:30:00-04:00",
  "actualizado_en": "2025-11-03T11:15:00-04:00"
}
```

**Campos importantes:**
- `numero_pedido`: Auto-generado con formato `PED-YYYYMMDDHHmmss`
- `subtotal`: Suma de todos los items
- `impuestos`: Calculado automáticamente (13% IVA por defecto)
- `total`: subtotal + impuestos - descuento
- `total_pagado`: Suma de pagos COMPLETADOS (campo calculado)
- `saldo_pendiente`: total - total_pagado (campo calculado)
- `estado_pago`: PENDIENTE/PARCIAL/PAGADO (campo calculado)

**Estados de Pedido:**
- `PENDIENTE` - Recién creado, sin confirmar
- `CONFIRMADO` - Confirmado por el cliente
- `EN_PROCESO` - En preparación
- `COMPLETADO` - Entregado y finalizado
- `CANCELADO` - Cancelado

**Estados de Pago (calculados automáticamente):**
- `PENDIENTE` - Sin pagos o todos los pagos fallidos/cancelados
- `PARCIAL` - Tiene pagos pero aún queda saldo pendiente
- `PAGADO` - Total pagado >= total del pedido

### 2. DetallePedido (Línea de Pedido)

Representa cada producto en un pedido.

```json
{
  "id": 1,
  "pedido": 1,
  "producto_cosechado": 10,
  "producto_nombre": "Tomate",
  "producto_descripcion": "Tomate fresco de calidad premium",
  "cantidad": "50.00",
  "unidad_medida": "kg",
  "precio_unitario": "15.00",
  "subtotal": "750.00",
  "creado_en": "2025-11-03T10:30:00-04:00"
}
```

**Campos importantes:**
- `producto_cosechado`: FK opcional al producto cosechado real
- `producto_nombre`: Nombre del producto (snapshot histórico)
- `producto_descripcion`: Descripción opcional
- `subtotal`: Calculado automáticamente (cantidad * precio_unitario)

### 3. Pago

Representa un pago asociado a un pedido.

```json
{
  "id": 1,
  "pedido": 1,
  "pedido_numero": "PED-20251103143052",
  "numero_recibo": "PAG-20251103150230",
  "fecha_pago": "2025-11-03T11:00:00-04:00",
  "monto": "500.00",
  "metodo_pago": "EFECTIVO",
  "metodo_pago_display": "Efectivo",
  "estado": "COMPLETADO",
  "estado_display": "Completado",
  "referencia_bancaria": null,
  "banco": null,
  "comprobante_archivo": null,
  "observaciones": "Pago inicial",
  "stripe_payment_intent_id": null,
  "stripe_charge_id": null,
  "stripe_customer_id": null,
  "procesado_por": 1,
  "procesado_por_nombre": "Admin Usuario",
  "creado_en": "2025-11-03T11:00:00-04:00",
  "actualizado_en": "2025-11-03T11:00:00-04:00"
}
```

**Campos importantes:**
- `numero_recibo`: Auto-generado con formato `PAG-YYYYMMDDHHmmss`
- `referencia_bancaria`: Para pagos por transferencia bancaria
- `banco`: Nombre del banco (para transferencias)
- `comprobante_archivo`: URL o path del archivo de comprobante
- Campos Stripe: Solo se llenan para pagos con método `STRIPE`

**Métodos de Pago:**
- `EFECTIVO` - Pago en efectivo
- `TRANSFERENCIA` - Transferencia bancaria
- `STRIPE` - Pago con tarjeta (Stripe)
- `QR` - Código QR
- `OTRO` - Otro método

**Estados de Pago:**
- `PENDIENTE` - Registrado pero no confirmado
- `PROCESANDO` - En proceso (usado para Stripe)
- `COMPLETADO` - Pago exitoso y confirmado
- `FALLIDO` - Pago rechazado
- `REEMBOLSADO` - Pago devuelto al cliente
- `CANCELADO` - Pago cancelado

---

## 🔌 Endpoints API

### 📦 Gestión de Pedidos

#### 1. Listar Pedidos

```http
GET /api/pedidos/
```

**Parámetros de consulta (query params):**
- `socio_id` (integer, opcional) - Filtrar por socio
- `estado` (string, opcional) - Filtrar por estado (PENDIENTE, CONFIRMADO, EN_PROCESO, COMPLETADO, CANCELADO)
- `fecha_desde` (date, opcional) - Filtrar desde fecha (YYYY-MM-DD)
- `fecha_hasta` (date, opcional) - Filtrar hasta fecha (YYYY-MM-DD)
- `cliente_nombre` (string, opcional) - Buscar por nombre de cliente (búsqueda parcial)
- `page` (integer, opcional) - Número de página (default: 1)
- `page_size` (integer, opcional) - Elementos por página (default: 20)

**Respuesta exitosa (200 OK):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/pedidos/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero_pedido": "ORD-20251103-0001",
      "fecha_pedido": "2025-11-03T10:30:00Z",
      "cliente_nombre": "María González",
      "total": "847.50",
      "estado": "CONFIRMADO",
      "estado_pago": "PARCIAL"
    }
  ]
}
```

**Permisos:**
- Administradores: Ven todos los pedidos
- Socios: Solo ven sus propios pedidos

---

#### 2. Obtener Detalle de Pedido

```http
GET /api/pedidos/{id}/
```

**Respuesta exitosa (200 OK):**
```json
{
  "id": 1,
  "numero_pedido": "ORD-20251103-0001",
  "fecha_pedido": "2025-11-03T10:30:00Z",
  "socio": {
    "id": 5,
    "usuario": {
      "nombres": "Juan",
      "apellidos": "Pérez"
    }
  },
  "cliente_nombre": "María González",
  "cliente_email": "maria@example.com",
  "cliente_telefono": "+591 70123456",
  "items": [
    {
      "id": 1,
      "producto": {
        "id": 10,
        "lote": "LOTE-001"
      },
      "cantidad": 50.0,
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
  "estado_pago": "PARCIAL"
}
```

---

#### 3. Crear Pedido

```http
POST /api/pedidos/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "socio": 5,
  "cliente_nombre": "María González",
  "cliente_email": "maria@example.com",
  "cliente_telefono": "+591 70123456",
  "cliente_direccion": "Av. Principal #123, La Paz",
  "fecha_entrega_estimada": "2025-11-05",
  "descuento": "0.00",
  "observaciones": "Entrega a domicilio en horario de mañana",
  "items": [
    {
      "producto_cosechado": 10,
      "producto_nombre": "Tomate",
      "producto_descripcion": "Tomate fresco de calidad premium",
      "cantidad": "50.00",
      "unidad_medida": "kg",
      "precio_unitario": "15.00"
    },
    {
      "producto_cosechado": 11,
      "producto_nombre": "Lechuga",
      "producto_descripcion": "Lechuga orgánica",
      "cantidad": "30.00",
      "unidad_medida": "unidad",
      "precio_unitario": "20.00"
    }
  ],
  "impuestos": "97.50",
  "descuento": "0.00",
  "notas": "Entrega a domicilio"
}
```

**Respuesta exitosa (201 CREATED):**
```json
{
  "id": 1,
  "numero_pedido": "ORD-20251103-0001",
  "fecha_pedido": "2025-11-03T10:30:00Z",
  "cliente_nombre": "María González",
  "subtotal": "1350.00",
  "impuestos": "97.50",
  "descuento": "0.00",
  "total": "1447.50",
  "estado": "PENDIENTE",
  "estado_pago": "PENDIENTE"
}
```

**Validaciones:**
- `socio_id` debe existir
- `cliente_nombre` es requerido
- `items` debe tener al menos 1 elemento
- Cada `producto_id` debe existir y estar disponible
- `cantidad` debe ser mayor a 0
- `precio_unitario` debe ser mayor a 0

---

#### 4. Actualizar Pedido

```http
PUT /api/pedidos/{id}/
Content-Type: application/json
Authorization: Bearer {token}
```

```http
PATCH /api/pedidos/{id}/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body (ejemplo PATCH):**
```json
{
  "cliente_telefono": "+591 70987654",
  "notas": "Cambio de dirección de entrega"
}
```

**Nota:** No se pueden editar pedidos cancelados.

---

#### 5. Cambiar Estado de Pedido

```http
POST /api/pedidos/{id}/cambiar_estado/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "estado": "CONFIRMADO"
}
```

**Estados válidos:**
- `PENDIENTE`
- `CONFIRMADO`
- `EN_PROCESO`
- `COMPLETADO`
- `CANCELADO`

**Respuesta exitosa (200 OK):**
```json
{
  "mensaje": "Estado del pedido actualizado de PENDIENTE a CONFIRMADO",
  "pedido": {
    "id": 1,
    "numero_pedido": "ORD-20251103-0001",
    "estado": "CONFIRMADO"
  }
}
```

**Reglas de negocio:**
- No se puede cambiar el estado de pedidos ya cancelados
- Solo administradores pueden cancelar pedidos

---

### 💰 Gestión de Pagos

#### 6. Listar Pagos

```http
GET /api/pagos/
```

**Parámetros de consulta:**
- `pedido_id` (integer, opcional) - Filtrar por pedido
- `estado` (string, opcional) - Filtrar por estado
- `metodo_pago` (string, opcional) - Filtrar por método
- `fecha_desde` (date, opcional) - Filtrar desde fecha
- `fecha_hasta` (date, opcional) - Filtrar hasta fecha
- `page` (integer, opcional) - Número de página
- `page_size` (integer, opcional) - Elementos por página

**Respuesta exitosa (200 OK):**
```json
{
  "count": 30,
  "next": "http://localhost:8000/api/pagos/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "pedido": {
        "id": 1,
        "numero_pedido": "ORD-20251103-0001"
      },
      "fecha_pago": "2025-11-03T11:00:00Z",
      "monto": "500.00",
      "metodo_pago": "EFECTIVO",
      "estado": "COMPLETADO"
    }
  ]
}
```

---

#### 7. Registrar Pago (Efectivo/Transferencia)

```http
POST /api/pagos/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "pedido_id": 1,
  "monto": "500.00",
  "metodo_pago": "EFECTIVO",
  "comprobante": "REC-001",
  "notas": "Pago inicial"
}
```

**Respuesta exitosa (201 CREATED):**
```json
{
  "id": 1,
  "pedido": {
    "id": 1,
    "numero_pedido": "ORD-20251103-0001"
  },
  "fecha_pago": "2025-11-03T11:00:00Z",
  "monto": "500.00",
  "metodo_pago": "EFECTIVO",
  "metodo_pago_display": "Efectivo",
  "comprobante": "REC-001",
  "estado": "COMPLETADO",
  "estado_display": "Completado"
}
```

**Validaciones:**
- `pedido_id` debe existir
- El pedido no debe estar cancelado
- `monto` debe ser mayor a 0
- `monto` no debe exceder el saldo pendiente
- `metodo_pago` debe ser válido
- Pagos en efectivo/transferencia se marcan automáticamente como COMPLETADO

---

#### 8. Pagar con Stripe

```http
POST /api/pagos/pagar_con_stripe/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "pedido_id": 1,
  "monto": "500.00",
  "payment_method_id": "pm_1K2L3M4N5O6P7Q8R",
  "comprobante": "STRIPE-REC-001"
}
```

**Respuesta exitosa (201 CREATED):**
```json
{
  "mensaje": "Pago procesado exitosamente",
  "pago": {
    "id": 2,
    "pedido": {
      "id": 1,
      "numero_pedido": "ORD-20251103-0001"
    },
    "fecha_pago": "2025-11-03T12:00:00Z",
    "monto": "500.00",
    "metodo_pago": "STRIPE",
    "comprobante": "STRIPE-REC-001",
    "estado": "COMPLETADO",
    "stripe_payment_intent_id": "pi_1K2L3M4N5O6P7Q8R",
    "stripe_charge_id": "ch_1K2L3M4N5O6P7Q8R"
  }
}
```

**Respuesta de error (400 BAD REQUEST):**
```json
{
  "error": "Error al procesar pago: Tarjeta rechazada"
}
```

**Flujo de pago con Stripe:**
1. Frontend obtiene `payment_method_id` usando Stripe.js
2. Frontend envía `payment_method_id` a este endpoint
3. Backend procesa el pago con Stripe API
4. Backend actualiza el estado del pago
5. Si el pago completa el pedido, actualiza estado del pedido

---

#### 9. Reembolsar Pago de Stripe

```http
POST /api/pagos/{id}/reembolsar/
Content-Type: application/json
Authorization: Bearer {token}
```

**Body:**
```json
{
  "motivo": "Producto defectuoso"
}
```

**Respuesta exitosa (200 OK):**
```json
{
  "mensaje": "Reembolso procesado exitosamente",
  "pago": {
    "id": 2,
    "estado": "REEMBOLSADO",
    "notas": "Producto defectuoso"
  }
}
```

**Validaciones:**
- Solo pagos con método `STRIPE`
- Solo pagos con estado `COMPLETADO`
- Requiere permisos de administrador

---

### 📊 Consultas e Historial

#### 10. Historial de Ventas

```http
GET /api/historial-ventas/
```

**Parámetros de consulta:**
- `fecha_desde` (date, opcional) - Filtrar desde fecha (YYYY-MM-DD)
- `fecha_hasta` (date, opcional) - Filtrar hasta fecha (YYYY-MM-DD)
- `cliente_nombre` (string, opcional) - Buscar por cliente
- `socio_id` (integer, opcional) - Filtrar por socio
- `estado_pedido` (string, opcional) - Filtrar por estado de pedido
- `metodo_pago` (string, opcional) - Filtrar por método de pago
- `page` (integer, opcional) - Número de página
- `page_size` (integer, opcional) - Elementos por página

**Respuesta exitosa (200 OK):**
```json
{
  "count": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "estadisticas": {
    "total_ventas": 45,
    "total_monto": "67500.00",
    "total_pagado": "45000.00",
    "total_pendiente": "22500.00"
  },
  "filtros_aplicados": {
    "fecha_desde": "2025-11-01",
    "fecha_hasta": "2025-11-03",
    "cliente_nombre": null,
    "socio_id": null,
    "estado_pedido": null,
    "metodo_pago": null
  },
  "results": [
    {
      "id": 1,
      "numero_pedido": "ORD-20251103-0001",
      "fecha_pedido": "2025-11-03T10:30:00Z",
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

**Permisos:**
- Administradores: Ven todo el historial
- Socios: Solo ven sus propias ventas

---

#### 11. Exportar Ventas a CSV

```http
GET /api/exportar-ventas-csv/
```

**Parámetros de consulta:** (mismos que historial-ventas)

**Respuesta exitosa (200 OK):**
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="ventas_20251103_143000.csv"

Número Pedido,Fecha,Cliente,Email,Teléfono,Socio,Subtotal,Impuestos,Descuento,Total,Total Pagado,Saldo Pendiente,Estado,Estado Pago
ORD-20251103-0001,2025-11-03 10:30,María González,maria@example.com,+591 70123456,Juan Pérez,750.00,97.50,0.00,847.50,500.00,347.50,CONFIRMADO,PARCIAL
```

**Formato CSV:**
- Codificación: UTF-8 con BOM
- Separador: coma (,)
- Incluye encabezados
- Registra exportación en bitácora

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Flujo Completo de Venta con Efectivo

```javascript
// 1. Crear pedido
const pedido = await fetch('http://localhost:8000/api/pedidos/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    socio_id: 5,
    cliente_nombre: 'María González',
    cliente_email: 'maria@example.com',
    cliente_telefono: '+591 70123456',
    items: [
      {
        producto_id: 10,
        cantidad: 50.0,
        precio_unitario: '15.00'
      }
    ],
    impuestos: '97.50',
    descuento: '0.00'
  })
});

const pedidoData = await pedido.json();
console.log('Pedido creado:', pedidoData.numero_pedido);

// 2. Confirmar pedido
await fetch(`http://localhost:8000/api/pedidos/${pedidoData.id}/cambiar_estado/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    estado: 'CONFIRMADO'
  })
});

// 3. Registrar pago en efectivo
const pago = await fetch('http://localhost:8000/api/pagos/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    pedido_id: pedidoData.id,
    monto: '847.50',
    metodo_pago: 'EFECTIVO',
    comprobante: 'REC-001'
  })
});

const pagoData = await pago.json();
console.log('Pago registrado:', pagoData.id);
```

---

### Ejemplo 2: Pago con Stripe

```javascript
// Frontend con Stripe.js
import { loadStripe } from '@stripe/stripe-js';

const stripe = await loadStripe('pk_test_...');

// 1. Crear PaymentMethod con datos de tarjeta
const {paymentMethod, error} = await stripe.createPaymentMethod({
  type: 'card',
  card: cardElement, // elemento de Stripe Elements
  billing_details: {
    name: 'María González',
    email: 'maria@example.com'
  }
});

if (error) {
  console.error('Error al crear PaymentMethod:', error);
  return;
}

// 2. Enviar PaymentMethod al backend
const response = await fetch('http://localhost:8000/api/pagos/pagar_con_stripe/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    pedido_id: 1,
    monto: '500.00',
    payment_method_id: paymentMethod.id,
    comprobante: 'STRIPE-REC-001'
  })
});

const result = await response.json();

if (response.ok) {
  console.log('Pago exitoso:', result.pago);
  alert('¡Pago procesado exitosamente!');
} else {
  console.error('Error en pago:', result.error);
  alert('Error: ' + result.error);
}
```

---

### Ejemplo 3: Consultar Historial de Ventas

```javascript
// Consultar ventas del último mes
const hoy = new Date();
const hace30Dias = new Date(hoy.getTime() - 30 * 24 * 60 * 60 * 1000);

const response = await fetch(
  `http://localhost:8000/api/historial-ventas/?` +
  `fecha_desde=${hace30Dias.toISOString().split('T')[0]}&` +
  `fecha_hasta=${hoy.toISOString().split('T')[0]}&` +
  `page=1&page_size=20`,
  {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  }
);

const data = await response.json();

console.log('Total de ventas:', data.estadisticas.total_ventas);
console.log('Monto total:', data.estadisticas.total_monto);
console.log('Pedidos:', data.results);
```

---

### Ejemplo 4: Exportar a CSV

```javascript
// Descargar CSV de ventas
const params = new URLSearchParams({
  fecha_desde: '2025-11-01',
  fecha_hasta: '2025-11-03',
  estado_pedido: 'COMPLETADO'
});

const response = await fetch(
  `http://localhost:8000/api/exportar-ventas-csv/?${params}`,
  {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  }
);

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'ventas.csv';
a.click();
```

---

## 🔐 Códigos de Estado HTTP

### Códigos de Éxito
- **200 OK** - Solicitud exitosa
- **201 CREATED** - Recurso creado exitosamente
- **204 NO CONTENT** - Solicitud exitosa sin contenido

### Códigos de Error del Cliente
- **400 BAD REQUEST** - Datos inválidos o falta información requerida
- **401 UNAUTHORIZED** - No autenticado
- **403 FORBIDDEN** - Sin permisos suficientes
- **404 NOT FOUND** - Recurso no encontrado

### Códigos de Error del Servidor
- **500 INTERNAL SERVER ERROR** - Error interno del servidor

---

## 💳 Configuración Stripe

### Variables de Entorno Requeridas

Crear archivo `.env` en la raíz del proyecto backend:

```env
# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_51xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### Obtener Claves de Stripe

1. Ir a [https://dashboard.stripe.com/](https://dashboard.stripe.com/)
2. Crear cuenta o iniciar sesión
3. En el dashboard, ir a **Developers > API keys**
4. Copiar:
   - **Publishable key** → `STRIPE_PUBLIC_KEY`
   - **Secret key** → `STRIPE_SECRET_KEY`

### Claves de Prueba vs Producción

**Modo Test (desarrollo):**
```env
STRIPE_PUBLIC_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
```

**Modo Live (producción):**
```env
STRIPE_PUBLIC_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
```

### Tarjetas de Prueba Stripe

Para testing en modo desarrollo:

| Número de Tarjeta | Tipo | Resultado |
|-------------------|------|-----------|
| 4242 4242 4242 4242 | Visa | ✅ Pago exitoso |
| 4000 0000 0000 0002 | Visa | ❌ Tarjeta rechazada |
| 4000 0025 0000 3155 | Visa | ⚠️ Requiere autenticación 3D Secure |

**Datos adicionales para pruebas:**
- CVV: Cualquier 3 dígitos (ej: 123)
- Fecha: Cualquier fecha futura (ej: 12/30)
- ZIP: Cualquier código (ej: 12345)

---

## 🔒 Permisos y Seguridad

### Roles y Permisos

#### Administrador (`is_staff=True`)
- ✅ Crear, ver, editar y eliminar pedidos
- ✅ Registrar pagos (todos los métodos)
- ✅ Ver historial completo de ventas
- ✅ Procesar reembolsos
- ✅ Cambiar estados de pedidos
- ✅ Exportar a CSV

#### Socio (Usuario normal)
- ✅ Ver sus propios pedidos
- ✅ Ver pagos de sus pedidos
- ❌ No puede ver pedidos de otros socios
- ❌ No puede procesar reembolsos
- ❌ No puede cambiar estados de pedidos

### Autenticación

Todas las peticiones (excepto login) requieren token de autenticación:

```javascript
headers: {
  'Authorization': 'Bearer ' + token
}
```

### Registro en Bitácora

Todas las operaciones se registran automáticamente en la bitácora de auditoría:

- Creación de pedidos
- Cambios de estado
- Registro de pagos
- Pagos con Stripe (éxito/fallo)
- Reembolsos
- Exportaciones CSV

Consultar bitácora:
```http
GET /api/bitacora/?tabla_afectada=Pedido
GET /api/bitacora/?tabla_afectada=Pago
```

---

## 🐛 Manejo de Errores

### Formato de Respuesta de Error

```json
{
  "error": "Mensaje de error descriptivo"
}
```

o para errores de validación:

```json
{
  "campo": ["Error en este campo"],
  "otro_campo": ["Otro error"]
}
```

### Errores Comunes

#### Error: "Pedido no encontrado"
```json
{
  "error": "Pedido no encontrado"
}
```
**Solución:** Verificar que el `pedido_id` sea correcto y exista.

#### Error: "No se puede pagar un pedido cancelado"
```json
{
  "error": "No se puede pagar un pedido cancelado"
}
```
**Solución:** Verificar el estado del pedido antes de intentar pagar.

#### Error: "El monto excede el saldo pendiente"
```json
{
  "monto": ["El monto no puede ser mayor al saldo pendiente del pedido"]
}
```
**Solución:** Verificar `saldo_pendiente` del pedido antes de registrar pago.

#### Error: "Error al procesar pago: Tarjeta rechazada"
```json
{
  "error": "Error al procesar pago: Tarjeta rechazada"
}
```
**Solución:** Tarjeta inválida. Solicitar otro método de pago o verificar datos.

---

## 📝 Notas Importantes

### 1. Cálculo Automático de Totales

Al crear un pedido, el backend calcula automáticamente:
- `subtotal` = suma de (cantidad × precio_unitario) de todos los items
- `total` = subtotal + impuestos - descuento

### 2. Actualización Automática de Estado de Pago

Cuando se registra un pago:
- Si `total_pagado = 0` → `estado_pago = PENDIENTE`
- Si `0 < total_pagado < total` → `estado_pago = PARCIAL`
- Si `total_pagado >= total` → `estado_pago = PAGADO` y `estado_pedido = COMPLETADO`

### 3. Validaciones de Negocio

- No se pueden registrar pagos en pedidos cancelados
- No se puede pagar más del saldo pendiente
- Los pagos en efectivo/transferencia se marcan automáticamente como COMPLETADO
- Los pagos con Stripe pasan por estado PROCESANDO antes de COMPLETADO/FALLIDO

### 4. Formato de Fechas

Todas las fechas se devuelven en formato ISO 8601:
```
2025-11-03T10:30:00Z
```

Para filtros, usar formato simple:
```
2025-11-03
```

### 5. Decimales

Todos los montos son strings con 2 decimales:
```json
{
  "monto": "1500.00",
  "total": "847.50"
}
```

---

## 🚀 Próximos Pasos

### Para el Frontend

1. **Instalar Stripe.js:**
   ```bash
   npm install @stripe/stripe-js
   ```

2. **Crear formulario de pago con Stripe Elements**

3. **Implementar tabla de pedidos con filtros**

4. **Implementar formulario de registro de pagos**

5. **Agregar exportación CSV**

### Migraciones Pendientes

Ejecutar en el backend:
```bash
cd c:\Users\httpReen\Desktop\GitYandira\backend_si2_final\cooperativa_backend
python manage.py makemigrations
python manage.py migrate
```

---

## 📧 Soporte

Para dudas o problemas, consultar:
- Bitácora del sistema: `/api/bitacora/`
- Logs del servidor Django
- Documentación de Stripe: [https://stripe.com/docs](https://stripe.com/docs)

---

**Última actualización:** 3 de Noviembre, 2025  
**Versión del API:** 1.0
