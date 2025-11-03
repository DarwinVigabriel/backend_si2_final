# ⚡ Sistema Ventas de Insumos - Quick Start

## 🎯 ¿Qué es?
Sistema para que **SOCIOS** compren **INSUMOS** (semillas, pesticidas, fertilizantes) a la **COOPERATIVA** con:
- Precios por temporada
- Aprobación administrativa
- Seguimiento de pagos

---

## 🚀 ENDPOINTS PRINCIPALES

### Base URL: `http://localhost:8000/api/ventas/insumos/`

| Método | Endpoint | Descripción | Quién |
|--------|----------|-------------|-------|
| GET | `/precios-temporada/` | Ver precios vigentes | Todos |
| POST | `/pedidos/` | Crear solicitud | Socio |
| GET | `/pedidos/` | Listar pedidos | Todos* |
| GET | `/pedidos/{id}/` | Ver detalle | Todos* |
| POST | `/pedidos/{id}/aprobar/` | Aprobar | Admin |
| POST | `/pedidos/{id}/entregar/` | Marcar entregado | Admin |
| POST | `/pagos/` | Registrar pago | Todos |
| GET | `/pagos/` | Listar pagos | Todos* |
| GET | `/historial/` | Estadísticas | Todos* |

*Socios solo ven sus propios datos

---

## 📊 FLUJO RÁPIDO

```
1. SOCIO ve precios    → GET /precios-temporada/?vigente=true
2. SOCIO crea pedido   → POST /pedidos/ (estado: SOLICITADO)
3. ADMIN aprueba       → POST /pedidos/{id}/aprobar/ (estado: APROBADO)
4. ADMIN entrega       → POST /pedidos/{id}/entregar/ (estado: ENTREGADO)
5. SOCIO paga          → POST /pagos/
6. Sistema calcula     → total_pagado, saldo_pendiente, estado_pago
```

---

## 🔑 CAMPOS CLAVE

### Al CREAR pedido:
```json
{
  "socio": 5,                              // ✅ Requerido
  "fecha_entrega_solicitada": "2025-11-15", // ✅ Requerido
  "motivo_solicitud": "...",                // ✅ Requerido
  "items": [                                // ✅ Requerido (mínimo 1)
    {
      "tipo_insumo": "SEMILLA",             // ✅ Requerido
      "semilla": 10,                        // ✅ Requerido (o pesticida o fertilizante)
      "cantidad": 50.00,                    // ✅ Requerido
      "precio_unitario": 25.00              // ✅ Requerido
    }
  ]
}
```

### Al REGISTRAR pago:
```json
{
  "pedido_insumo": 1,                       // ✅ Requerido
  "monto": 500.00,                          // ✅ Requerido
  "metodo_pago": "EFECTIVO",                // ✅ Requerido
  "referencia_bancaria": "...",             // ⚠️ Si es TRANSFERENCIA
  "banco": "...",                           // ⚠️ Si es TRANSFERENCIA
  "observaciones": "..."                    // ❌ Opcional
}
```

---

## ⚠️ VALIDACIONES IMPORTANTES

### ❌ NO puedes:
- Pagar más del `saldo_pendiente`
- Pagar pedidos `CANCELADO`
- Aprobar pedidos que no estén en `SOLICITADO`
- Especificar múltiples insumos en un item

### ✅ SÍ puedes:
- Crear múltiples items en un pedido
- Hacer pagos parciales
- Ver solo tus propios pedidos (socios)
- Filtrar por fecha, estado, tipo de insumo

---

## 🎨 ESTADOS

### Pedido:
```
SOLICITADO → APROBADO → EN_PREPARACION → LISTO_ENTREGA → ENTREGADO
                                                              ↓
                                                          CANCELADO
```

### Pago (calculado automáticamente):
```
PENDIENTE (sin pagos) → PARCIAL (pagos < total) → PAGADO (pagos >= total)
```

---

## 💻 EJEMPLO COMPLETO

```javascript
// 1. Ver precios
const precios = await axios.get('/api/ventas/insumos/precios-temporada/', {
  params: { vigente: true, activo: true }
});

// 2. Crear pedido
const pedido = await axios.post('/api/ventas/insumos/pedidos/', {
  socio: 5,
  fecha_entrega_solicitada: '2025-11-15',
  motivo_solicitud: 'Semillas para siembra',
  items: [{
    tipo_insumo: 'SEMILLA',
    semilla: 10,
    cantidad: 50.00,
    precio_unitario: 25.00
  }]
});
// → numero_pedido: "INS-20251103143052"
// → total: 1250.00, saldo_pendiente: 1250.00, estado: SOLICITADO

// 3. Admin aprueba (desde otra sesión)
await axios.post(`/api/ventas/insumos/pedidos/${pedido.data.id}/aprobar/`);
// → estado: APROBADO

// 4. Socio paga
const pago = await axios.post('/api/ventas/insumos/pagos/', {
  pedido_insumo: pedido.data.id,
  monto: 500.00,
  metodo_pago: 'EFECTIVO'
});
// → numero_recibo: "PGINS-20251103150230"

// 5. Ver saldo actualizado
const pedidoActualizado = await axios.get(`/api/ventas/insumos/pedidos/${pedido.data.id}/`);
// → total_pagado: 500.00
// → saldo_pendiente: 750.00
// → estado_pago: PARCIAL
```

---

## 🛠️ SETUP AXIOS

```javascript
// api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
```

---

## 🐛 ERRORES COMUNES

### 400 Bad Request
```json
{ "monto": ["El monto excede el saldo pendiente (Bs. 750.00)"] }
```
**Solución:** Verificar `saldo_pendiente` antes de pagar

### 403 Forbidden
```json
{ "error": "No tiene permisos para aprobar pedidos" }
```
**Solución:** Solo admin puede aprobar

### 404 Not Found
```
Not Found: /api/ventas/insumos/pedidos/
```
**Solución:** Verificar que el servidor esté corriendo y las URLs registradas

---

## 📝 CHECKLIST RÁPIDO

- [ ] Backend corriendo (`python manage.py runserver`)
- [ ] Token de autenticación obtenido
- [ ] Precios creados en Django Admin
- [ ] Socio creado en sistema
- [ ] Insumos (semillas/pesticidas/fertilizantes) creados
- [ ] Frontend configurado con Axios
- [ ] CORS configurado si frontend está en otro puerto

---

## 📚 DOCUMENTACIÓN COMPLETA

Ver `VENTAS_INSUMOS_GUIA_FRONTEND.md` para:
- Modelos de datos detallados
- Todos los endpoints con ejemplos
- Componentes React completos
- Casos de uso avanzados
- Solución de problemas
- Referencias técnicas

---

**¿Listo para empezar? Sigue el ejemplo completo arriba. ¡Está todo implementado y funcionando!** 🚀
