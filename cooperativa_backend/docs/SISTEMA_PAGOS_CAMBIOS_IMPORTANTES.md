# ⚠️ CAMBIOS IMPORTANTES - Sistema de Pagos

**Fecha de actualización:** 3 de Noviembre 2025  
**Versión:** 1.0 (Actualizada)

---

## 🔴 CAMPOS CORREGIDOS - LEER ANTES DE INTEGRAR

### 📦 Modelo PEDIDO

#### ✅ Campos CORRECTOS:
```json
{
  "numero_pedido": "PED-20251103143052",  // ✅ Formato: PED-YYYYMMDDHHmmss
  "subtotal": "750.00",                    // ✅ Suma de items
  "impuestos": "97.50",                    // ✅ 13% IVA por defecto
  "descuento": "0.00",                     // ✅ Descuento aplicado
  "total": "847.50",                       // ✅ subtotal + impuestos - descuento
  "observaciones": "Notas del pedido",     // ✅ (antes era "notas")
  "fecha_entrega_estimada": "2025-11-05",  // ✅ Solo fecha (YYYY-MM-DD)
  "fecha_entrega_real": null               // ✅ Solo fecha o null
}
```

#### ❌ Campos que NO EXISTEN (no usar):
```json
{
  "monto_subtotal": "...",   // ❌ NO EXISTE - usar "subtotal"
  "monto_impuestos": "...",  // ❌ NO EXISTE - usar "impuestos"
  "monto_descuento": "...",  // ❌ NO EXISTE - usar "descuento"
  "monto_total": "...",      // ❌ NO EXISTE - usar "total"
  "notas": "..."             // ❌ NO EXISTE - usar "observaciones"
}
```

### 📋 Modelo DETALLE_PEDIDO

#### ✅ Campos CORRECTOS:
```json
{
  "producto_cosechado": 10,                    // ✅ FK al ProductoCosechado (opcional)
  "producto_nombre": "Tomate",                 // ✅ Nombre del producto (requerido)
  "producto_descripcion": "Descripción...",    // ✅ Descripción opcional
  "cantidad": "50.00",                         // ✅ Decimal
  "unidad_medida": "kg",                       // ✅ String (kg, unidad, litro, etc)
  "precio_unitario": "15.00",                  // ✅ Decimal
  "subtotal": "750.00"                         // ✅ Calculado automáticamente
}
```

#### ❌ Campos que NO EXISTEN (no usar):
```json
{
  "producto": 10,            // ❌ NO EXISTE - usar "producto_cosechado"
  "producto_id": 10          // ❌ NO EXISTE - usar "producto_cosechado"
}
```

### 💰 Modelo PAGO

#### ✅ Campos CORRECTOS:
```json
{
  "numero_recibo": "PAG-20251103150230",       // ✅ Auto-generado
  "pedido": 1,                                 // ✅ ID del pedido
  "monto": "500.00",                           // ✅ Monto del pago
  "metodo_pago": "EFECTIVO",                   // ✅ EFECTIVO|TRANSFERENCIA|STRIPE|QR|OTRO
  "estado": "COMPLETADO",                      // ✅ Ver estados abajo
  "referencia_bancaria": "REF123",             // ✅ Para transferencias
  "banco": "Banco Nacional",                   // ✅ Nombre del banco
  "comprobante_archivo": "/media/comp.pdf",    // ✅ URL/path del archivo
  "observaciones": "Notas del pago",           // ✅ (antes era "notas")
  "stripe_payment_intent_id": "pi_...",        // ✅ Solo para Stripe
  "stripe_charge_id": "ch_...",                // ✅ Solo para Stripe
  "stripe_customer_id": "cus_..."              // ✅ Solo para Stripe
}
```

#### ❌ Campos que NO EXISTEN (no usar):
```json
{
  "comprobante": "...",           // ❌ NO EXISTE - usar "comprobante_archivo"
  "comprobante_pago": "...",      // ❌ NO EXISTE - usar "comprobante_archivo"
  "referencia_externa": "...",    // ❌ NO EXISTE - usar "referencia_bancaria"
  "notas": "...",                 // ❌ NO EXISTE - usar "observaciones"
  "registrado_por": 1             // ❌ NO EXISTE - usar "procesado_por"
}
```

---

## 🔄 ESTADOS

### Estados de PEDIDO:
```
PENDIENTE    → Recién creado, sin confirmar
CONFIRMADO   → Confirmado por el cliente
EN_PROCESO   → En preparación/empaque
COMPLETADO   → Entregado y finalizado
CANCELADO    → Cancelado (no se pueden registrar pagos)
```

### Estados de PAGO (calculado automáticamente en pedido):
```
PENDIENTE    → Sin pagos o todos fallidos/cancelados
PARCIAL      → Tiene pagos pero queda saldo pendiente
PAGADO       → Total pagado >= total del pedido
```

### Estados de registro de PAGO:
```
PENDIENTE     → Registrado pero no confirmado
PROCESANDO    → En proceso (usado para Stripe)
COMPLETADO    → Pago exitoso y confirmado
FALLIDO       → Pago rechazado
REEMBOLSADO   → Pago devuelto al cliente
CANCELADO     → Pago cancelado
```

---

## 📝 EJEMPLOS DE USO CORRECTOS

### 1️⃣ Crear un Pedido

```javascript
// ✅ CORRECTO
const pedido = {
  socio: 5,                               // ID del socio
  cliente_nombre: "María González",
  cliente_email: "maria@example.com",
  cliente_telefono: "+591 70123456",
  cliente_direccion: "Av. Principal #123",
  fecha_entrega_estimada: "2025-11-05",   // Solo fecha
  descuento: "0.00",                      // Decimal como string
  observaciones: "Entrega a domicilio",   // ✅ NO "notas"
  items: [
    {
      producto_cosechado: 10,             // ✅ NO "producto" ni "producto_id"
      producto_nombre: "Tomate",          // ✅ Requerido
      producto_descripcion: "Premium",    // Opcional
      cantidad: "50.00",                  // ✅ String decimal
      unidad_medida: "kg",                // ✅ Requerido
      precio_unitario: "15.00"            // ✅ String decimal
    }
  ]
};

// ❌ INCORRECTO - NO USAR
const pedidoMal = {
  socio_id: 5,                    // ❌ Es "socio", no "socio_id"
  notas: "...",                   // ❌ Es "observaciones"
  items: [{
    producto_id: 10,              // ❌ Es "producto_cosechado"
    producto: 10,                 // ❌ Es "producto_cosechado"
  }]
};
```

### 2️⃣ Registrar un Pago

```javascript
// ✅ CORRECTO - Pago en Efectivo
const pagoEfectivo = {
  pedido: 1,
  monto: "500.00",
  metodo_pago: "EFECTIVO",
  observaciones: "Pago inicial"    // ✅ NO "notas"
};

// ✅ CORRECTO - Pago con Transferencia
const pagoTransferencia = {
  pedido: 1,
  monto: "347.50",
  metodo_pago: "TRANSFERENCIA",
  referencia_bancaria: "REF-123456",  // ✅ NO "referencia_externa"
  banco: "Banco Nacional de Bolivia",
  comprobante_archivo: "/uploads/comprobante.pdf",  // ✅ NO "comprobante_pago"
  observaciones: "Pago final"
};

// ❌ INCORRECTO - NO USAR
const pagoMal = {
  pedido: 1,
  monto: "500.00",
  metodo_pago: "EFECTIVO",
  comprobante: "...",              // ❌ Es "comprobante_archivo"
  referencia_externa: "...",       // ❌ Es "referencia_bancaria"
  notas: "..."                     // ❌ Es "observaciones"
};
```

### 3️⃣ Obtener datos de un Pedido

```javascript
// ✅ CORRECTO - Acceder a campos
const pedido = response.data;

console.log(pedido.numero_pedido);      // ✅ "PED-20251103143052"
console.log(pedido.total);              // ✅ "847.50"
console.log(pedido.subtotal);           // ✅ "750.00"
console.log(pedido.impuestos);          // ✅ "97.50"
console.log(pedido.observaciones);      // ✅ "Entrega a domicilio"
console.log(pedido.total_pagado);       // ✅ "500.00" (calculado)
console.log(pedido.saldo_pendiente);    // ✅ "347.50" (calculado)
console.log(pedido.estado_pago);        // ✅ "PARCIAL" (calculado)

// Items del pedido
pedido.items.forEach(item => {
  console.log(item.producto_nombre);    // ✅ "Tomate"
  console.log(item.cantidad);           // ✅ "50.00"
  console.log(item.unidad_medida);      // ✅ "kg"
  console.log(item.subtotal);           // ✅ "750.00"
});

// ❌ INCORRECTO - Estos campos NO EXISTEN
console.log(pedido.monto_total);        // ❌ undefined
console.log(pedido.notas);              // ❌ undefined
item.producto                           // ❌ undefined
item.producto_id                        // ❌ undefined
```

---

## 🔍 FILTROS Y BÚSQUEDA

### Listar Pedidos con Filtros
```javascript
// ✅ CORRECTO
const params = {
  socio_id: 5,                    // Filtrar por socio
  estado: 'CONFIRMADO',           // Filtrar por estado
  fecha_desde: '2025-11-01',      // Desde fecha
  fecha_hasta: '2025-11-30',      // Hasta fecha
  cliente_nombre: 'María',        // Búsqueda parcial
  page: 1,
  page_size: 20
};

axios.get('/api/pedidos/', { params });
```

### Listar Pagos con Filtros
```javascript
// ✅ CORRECTO
const params = {
  pedido_id: 1,                   // Filtrar por pedido
  estado: 'COMPLETADO',           // Filtrar por estado
  metodo_pago: 'EFECTIVO',        // Filtrar por método
  fecha_desde: '2025-11-01',      // Desde fecha
  fecha_hasta: '2025-11-30',      // Hasta fecha
  page: 1
};

axios.get('/api/pagos/', { params });
```

---

## 🎨 COMPONENTES REACT - EJEMPLOS ACTUALIZADOS

### Crear Pedido (Formulario)
```jsx
const CrearPedido = () => {
  const [pedido, setPedido] = useState({
    socio: null,                        // ✅ No "socio_id"
    cliente_nombre: '',
    cliente_email: '',
    cliente_telefono: '',
    cliente_direccion: '',
    fecha_entrega_estimada: '',
    descuento: '0.00',
    observaciones: '',                  // ✅ No "notas"
    items: []
  });

  const agregarItem = () => {
    setPedido({
      ...pedido,
      items: [...pedido.items, {
        producto_cosechado: null,       // ✅ No "producto_id"
        producto_nombre: '',            // ✅ Requerido
        producto_descripcion: '',
        cantidad: '0.00',
        unidad_medida: 'kg',
        precio_unitario: '0.00'
      }]
    });
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post('/api/pedidos/', pedido);
      console.log('Pedido creado:', response.data);
    } catch (error) {
      console.error('Error:', error.response?.data);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Formulario aquí */}
    </form>
  );
};
```

### Mostrar Pedido (Detalle)
```jsx
const DetallePedido = ({ pedidoId }) => {
  const [pedido, setPedido] = useState(null);

  useEffect(() => {
    axios.get(`/api/pedidos/${pedidoId}/`)
      .then(res => setPedido(res.data));
  }, [pedidoId]);

  if (!pedido) return <div>Cargando...</div>;

  return (
    <div>
      <h2>Pedido {pedido.numero_pedido}</h2>
      
      <div>
        <strong>Cliente:</strong> {pedido.cliente_nombre}
      </div>
      
      <div>
        <strong>Subtotal:</strong> Bs. {pedido.subtotal}
      </div>
      <div>
        <strong>Impuestos:</strong> Bs. {pedido.impuestos}
      </div>
      <div>
        <strong>Descuento:</strong> Bs. {pedido.descuento}
      </div>
      <div>
        <strong>Total:</strong> Bs. {pedido.total}
      </div>
      
      <div>
        <strong>Total Pagado:</strong> Bs. {pedido.total_pagado}
      </div>
      <div>
        <strong>Saldo Pendiente:</strong> Bs. {pedido.saldo_pendiente}
      </div>
      <div>
        <strong>Estado Pago:</strong> 
        <span className={`badge badge-${pedido.estado_pago.toLowerCase()}`}>
          {pedido.estado_pago}
        </span>
      </div>

      <h3>Items</h3>
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Precio Unit.</th>
            <th>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {pedido.items.map(item => (
            <tr key={item.id}>
              <td>{item.producto_nombre}</td>
              <td>{item.cantidad} {item.unidad_medida}</td>
              <td>Bs. {item.precio_unitario}</td>
              <td>Bs. {item.subtotal}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {pedido.observaciones && (
        <div>
          <strong>Observaciones:</strong> {pedido.observaciones}
        </div>
      )}
    </div>
  );
};
```

### Registrar Pago
```jsx
const RegistrarPago = ({ pedidoId }) => {
  const [pago, setPago] = useState({
    pedido: pedidoId,
    monto: '',
    metodo_pago: 'EFECTIVO',
    referencia_bancaria: '',           // ✅ No "referencia_externa"
    banco: '',
    comprobante_archivo: null,         // ✅ No "comprobante_pago"
    observaciones: ''                  // ✅ No "notas"
  });

  const handleFileChange = (e) => {
    setPago({ ...pago, comprobante_archivo: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    Object.keys(pago).forEach(key => {
      if (pago[key] !== null && pago[key] !== '') {
        formData.append(key, pago[key]);
      }
    });

    try {
      const response = await axios.post('/api/pagos/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      console.log('Pago registrado:', response.data);
    } catch (error) {
      console.error('Error:', error.response?.data);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="number"
        step="0.01"
        value={pago.monto}
        onChange={e => setPago({...pago, monto: e.target.value})}
        placeholder="Monto"
        required
      />

      <select
        value={pago.metodo_pago}
        onChange={e => setPago({...pago, metodo_pago: e.target.value})}
      >
        <option value="EFECTIVO">Efectivo</option>
        <option value="TRANSFERENCIA">Transferencia</option>
        <option value="QR">QR</option>
        <option value="STRIPE">Tarjeta (Stripe)</option>
        <option value="OTRO">Otro</option>
      </select>

      {pago.metodo_pago === 'TRANSFERENCIA' && (
        <>
          <input
            type="text"
            value={pago.referencia_bancaria}
            onChange={e => setPago({...pago, referencia_bancaria: e.target.value})}
            placeholder="Referencia bancaria"
          />
          <input
            type="text"
            value={pago.banco}
            onChange={e => setPago({...pago, banco: e.target.value})}
            placeholder="Banco"
          />
        </>
      )}

      <input
        type="file"
        onChange={handleFileChange}
        accept="image/*,application/pdf"
      />

      <textarea
        value={pago.observaciones}
        onChange={e => setPago({...pago, observaciones: e.target.value})}
        placeholder="Observaciones"
      />

      <button type="submit">Registrar Pago</button>
    </form>
  );
};
```

---

## 📊 PROPIEDADES CALCULADAS

Estas propiedades se calculan automáticamente en el backend:

### En Pedido:
```javascript
// ✅ Campos calculados (read-only)
pedido.total_pagado      // Suma de pagos COMPLETADOS
pedido.saldo_pendiente   // total - total_pagado
pedido.estado_pago       // PENDIENTE | PARCIAL | PAGADO
```

### En DetallePedido:
```javascript
// ✅ Campo calculado (read-only)
item.subtotal  // cantidad * precio_unitario
```

**⚠️ IMPORTANTE:** Estos campos NO se deben enviar al crear/actualizar. Son calculados automáticamente por el backend.

---

## ✅ CHECKLIST DE INTEGRACIÓN

### Antes de integrar, verifica:

- [ ] Usar `socio` (no `socio_id`)
- [ ] Usar `producto_cosechado` (no `producto` ni `producto_id`)
- [ ] Usar `producto_nombre` para el nombre del producto
- [ ] Usar `subtotal`, `impuestos`, `descuento`, `total` (no `monto_*`)
- [ ] Usar `observaciones` (no `notas`)
- [ ] Usar `referencia_bancaria` (no `referencia_externa`)
- [ ] Usar `comprobante_archivo` (no `comprobante` ni `comprobante_pago`)
- [ ] Usar `procesado_por` (no `registrado_por`)
- [ ] Incluir `unidad_medida` en items
- [ ] Los montos son strings decimales: `"500.00"`
- [ ] Las fechas son ISO 8601: `"2025-11-03T10:30:00-04:00"`
- [ ] Los campos calculados son read-only

---

## 📞 SOPORTE

Si encuentras algún error o inconsistencia:
1. Verifica esta documentación primero
2. Revisa los ejemplos de código
3. Consulta `SISTEMA_PAGOS_API.md` para detalles de endpoints
4. Revisa `SISTEMA_PAGOS_FRONTEND_EJEMPLOS.md` para más ejemplos

**Última actualización:** 3 de Noviembre 2025
