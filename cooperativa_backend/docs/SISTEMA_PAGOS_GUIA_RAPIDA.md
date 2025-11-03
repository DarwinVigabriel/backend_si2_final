# 🚀 Sistema de Pagos - Guía Rápida para Frontend

## ✅ Lo que ya está listo en el Backend

1. ✅ Modelos de datos (Pedido, DetallePedido, Pago)
2. ✅ Integración con Stripe
3. ✅ Endpoints REST API completos
4. ✅ Validaciones de negocio
5. ✅ Registro en bitácora
6. ✅ Exportación CSV

---

## 📍 Endpoints Principales

### Base URL
```
http://localhost:8000/api
```

### 1. Listar Pedidos
```
GET /pedidos/
GET /pedidos/?estado=CONFIRMADO
GET /pedidos/?fecha_desde=2025-11-01&fecha_hasta=2025-11-03
```

### 2. Crear Pedido
```
POST /pedidos/
Content-Type: application/json

{
  "socio_id": 5,
  "cliente_nombre": "María González",
  "cliente_email": "maria@example.com",
  "items": [
    {
      "producto_id": 10,
      "cantidad": 50,
      "precio_unitario": "15.00"
    }
  ],
  "impuestos": "97.50",
  "descuento": "0.00"
}
```

### 3. Ver Detalle de Pedido
```
GET /pedidos/1/
```

### 4. Cambiar Estado de Pedido
```
POST /pedidos/1/cambiar_estado/
Content-Type: application/json

{
  "estado": "CONFIRMADO"
}
```

### 5. Registrar Pago (Efectivo/Transferencia)
```
POST /pagos/
Content-Type: application/json

{
  "pedido_id": 1,
  "monto": "500.00",
  "metodo_pago": "EFECTIVO",
  "comprobante": "REC-001"
}
```

### 6. Pagar con Stripe
```
POST /pagos/pagar_con_stripe/
Content-Type: application/json

{
  "pedido_id": 1,
  "monto": "500.00",
  "payment_method_id": "pm_1K2L3M4N5O6P7Q8R",
  "comprobante": "STRIPE-REC-001"
}
```

### 7. Historial de Ventas
```
GET /historial-ventas/
GET /historial-ventas/?fecha_desde=2025-11-01&fecha_hasta=2025-11-03
GET /historial-ventas/?cliente_nombre=María
GET /historial-ventas/?estado_pedido=COMPLETADO
```

### 8. Exportar a CSV
```
GET /exportar-ventas-csv/
GET /exportar-ventas-csv/?fecha_desde=2025-11-01&estado_pedido=COMPLETADO
```

---

## 🔑 Autenticación

Todas las peticiones requieren token:

```javascript
headers: {
  'Authorization': 'Bearer TU_TOKEN_AQUI',
  'Content-Type': 'application/json'
}
```

---

## 📊 Estados

### Estados de Pedido
- `PENDIENTE` - Recién creado
- `CONFIRMADO` - Confirmado
- `EN_PROCESO` - En preparación
- `COMPLETADO` - Finalizado
- `CANCELADO` - Cancelado

### Métodos de Pago
- `EFECTIVO` - Efectivo
- `TRANSFERENCIA` - Transferencia bancaria
- `STRIPE` - Tarjeta (Stripe)
- `QR` - Código QR
- `OTRO` - Otro método

### Estados de Pago
- `PENDIENTE` - Sin procesar
- `PROCESANDO` - En proceso (Stripe)
- `COMPLETADO` - Pago exitoso
- `FALLIDO` - Pago rechazado
- `REEMBOLSADO` - Devuelto
- `CANCELADO` - Cancelado

---

## 💡 Ejemplo Rápido (JavaScript)

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
    items: [
      {
        producto_id: 10,
        cantidad: 50,
        precio_unitario: '15.00'
      }
    ],
    impuestos: '0.00',
    descuento: '0.00'
  })
});

const pedidoData = await pedido.json();
console.log('Pedido creado:', pedidoData.numero_pedido);

// 2. Registrar pago en efectivo
const pago = await fetch('http://localhost:8000/api/pagos/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    pedido_id: pedidoData.id,
    monto: pedidoData.total,
    metodo_pago: 'EFECTIVO',
    comprobante: 'REC-001'
  })
});

console.log('Pago registrado');
```

---

## 💳 Stripe - Configuración

### 1. Instalar en Frontend
```bash
npm install @stripe/stripe-js
```

### 2. Configurar
```javascript
import { loadStripe } from '@stripe/stripe-js';

const stripe = await loadStripe('pk_test_51xxxxxxxxxxxxx');
```

### 3. Crear Pago
```javascript
// Crear PaymentMethod
const { paymentMethod } = await stripe.createPaymentMethod({
  type: 'card',
  card: cardElement
});

// Enviar al backend
const response = await fetch('http://localhost:8000/api/pagos/pagar_con_stripe/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    pedido_id: 1,
    monto: '500.00',
    payment_method_id: paymentMethod.id
  })
});
```

### Tarjetas de Prueba
- **Éxito:** 4242 4242 4242 4242
- **Fallo:** 4000 0000 0000 0002
- CVV: 123 | Fecha: 12/30

---

## 🎯 Pasos Siguientes

### 1. Ejecutar Migraciones (Backend)
```bash
cd c:\Users\httpReen\Desktop\GitYandira\backend_si2_final\cooperativa_backend
python manage.py makemigrations
python manage.py migrate
```

### 2. Configurar Variables de Entorno (Backend)
Crear archivo `.env`:
```env
STRIPE_PUBLIC_KEY=pk_test_51xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### 3. Crear Componentes Frontend
- ✅ Lista de pedidos
- ✅ Formulario crear pedido
- ✅ Detalle de pedido
- ✅ Formulario de pago
- ✅ Historial de ventas
- ✅ Botón exportar CSV

---

## 📚 Documentación Completa

Ver archivos en `docs/`:
- **SISTEMA_PAGOS_API.md** - Documentación completa de la API
- **SISTEMA_PAGOS_FRONTEND_EJEMPLOS.md** - Código completo React/Vue

---

## 🔧 Permisos

### Administrador
- ✅ Ver todos los pedidos
- ✅ Crear, editar, eliminar pedidos
- ✅ Registrar pagos
- ✅ Ver historial completo
- ✅ Exportar CSV
- ✅ Procesar reembolsos

### Socio (Usuario normal)
- ✅ Ver sus propios pedidos
- ✅ Ver pagos de sus pedidos
- ❌ No ver pedidos de otros
- ❌ No procesar reembolsos

---

## 🐛 Errores Comunes

### Error: "Pedido no encontrado"
**Solución:** Verificar que el `pedido_id` exista.

### Error: "No se puede pagar un pedido cancelado"
**Solución:** Verificar el estado del pedido antes de pagar.

### Error: "El monto excede el saldo pendiente"
**Solución:** Verificar `saldo_pendiente` antes de registrar pago.

### Error: "Tarjeta rechazada"
**Solución:** Usar tarjeta de prueba 4242 4242 4242 4242.

---

## 📞 Contacto

Para dudas, revisar:
- Documentación completa en `docs/`
- Logs del servidor Django
- Bitácora del sistema: `GET /api/bitacora/`

---

**¡Todo listo para empezar! 🎉**
