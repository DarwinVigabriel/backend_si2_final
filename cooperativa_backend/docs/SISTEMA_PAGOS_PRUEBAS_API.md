# 🧪 Sistema de Pagos - Colección de Pruebas API

Ejemplos de peticiones HTTP para probar todos los endpoints del sistema de pagos.

---

## 🔑 Configuración Inicial

### Variables a usar
```bash
# Reemplazar con tus valores reales
BASE_URL=http://localhost:8000/api
TOKEN=tu_token_de_autenticacion_aqui
```

### Obtener Token (Login)
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "tu_password"
  }'
```

**Respuesta:**
```json
{
  "mensaje": "Login exitoso",
  "usuario": {
    "id": 1,
    "usuario": "admin",
    "nombres": "Admin",
    "apellidos": "Sistema"
  },
  "csrf_token": "..."
}
```

---

## 📦 PEDIDOS

### 1. Listar Todos los Pedidos

```bash
curl -X GET "http://localhost:8000/api/pedidos/" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Respuesta:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
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

---

### 2. Listar Pedidos con Filtros

```bash
# Por estado
curl -X GET "http://localhost:8000/api/pedidos/?estado=CONFIRMADO" \
  -H "Authorization: Bearer ${TOKEN}"

# Por rango de fechas
curl -X GET "http://localhost:8000/api/pedidos/?fecha_desde=2025-11-01&fecha_hasta=2025-11-03" \
  -H "Authorization: Bearer ${TOKEN}"

# Por cliente
curl -X GET "http://localhost:8000/api/pedidos/?cliente_nombre=Maria" \
  -H "Authorization: Bearer ${TOKEN}"

# Por socio
curl -X GET "http://localhost:8000/api/pedidos/?socio_id=5" \
  -H "Authorization: Bearer ${TOKEN}"

# Combinado con paginación
curl -X GET "http://localhost:8000/api/pedidos/?estado=CONFIRMADO&page=1&page_size=10" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

### 3. Obtener Detalle de Pedido

```bash
curl -X GET "http://localhost:8000/api/pedidos/1/" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Respuesta:**
```json
{
  "id": 1,
  "numero_pedido": "ORD-20251103-0001",
  "fecha_pedido": "2025-11-03T10:30:00Z",
  "socio": {
    "id": 5,
    "codigo_interno": "SOC-001",
    "usuario": {
      "id": 10,
      "nombres": "Juan",
      "apellidos": "Pérez",
      "ci_nit": "12345678"
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
        "lote": "LOTE-001",
        "cultivo": {
          "especie": "Tomate"
        }
      },
      "cantidad": "50.00",
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
  "notas": "Entrega a domicilio"
}
```

---

### 4. Crear Pedido

```bash
curl -X POST "http://localhost:8000/api/pedidos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "socio_id": 5,
    "cliente_nombre": "María González",
    "cliente_email": "maria@example.com",
    "cliente_telefono": "+591 70123456",
    "items": [
      {
        "producto_id": 10,
        "cantidad": 50,
        "precio_unitario": "15.00"
      },
      {
        "producto_id": 11,
        "cantidad": 30,
        "precio_unitario": "20.00"
      }
    ],
    "impuestos": "97.50",
    "descuento": "0.00",
    "notas": "Entrega a domicilio"
  }'
```

**Respuesta (201 CREATED):**
```json
{
  "id": 2,
  "numero_pedido": "ORD-20251103-0002",
  "fecha_pedido": "2025-11-03T14:30:00Z",
  "socio": {
    "id": 5,
    "codigo_interno": "SOC-001"
  },
  "cliente_nombre": "María González",
  "cliente_email": "maria@example.com",
  "cliente_telefono": "+591 70123456",
  "items": [
    {
      "id": 2,
      "producto": {
        "id": 10,
        "lote": "LOTE-001"
      },
      "cantidad": "50.00",
      "precio_unitario": "15.00",
      "subtotal": "750.00"
    },
    {
      "id": 3,
      "producto": {
        "id": 11,
        "lote": "LOTE-002"
      },
      "cantidad": "30.00",
      "precio_unitario": "20.00",
      "subtotal": "600.00"
    }
  ],
  "subtotal": "1350.00",
  "impuestos": "97.50",
  "descuento": "0.00",
  "total": "1447.50",
  "total_pagado": "0.00",
  "saldo_pendiente": "1447.50",
  "estado": "PENDIENTE",
  "estado_pago": "PENDIENTE"
}
```

---

### 5. Actualizar Pedido (Parcial)

```bash
curl -X PATCH "http://localhost:8000/api/pedidos/1/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_telefono": "+591 70987654",
    "notas": "Cambio de dirección de entrega"
  }'
```

---

### 6. Cambiar Estado de Pedido

```bash
# Confirmar pedido
curl -X POST "http://localhost:8000/api/pedidos/1/cambiar_estado/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "CONFIRMADO"
  }'

# Pasar a en proceso
curl -X POST "http://localhost:8000/api/pedidos/1/cambiar_estado/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "EN_PROCESO"
  }'

# Completar pedido
curl -X POST "http://localhost:8000/api/pedidos/1/cambiar_estado/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "COMPLETADO"
  }'

# Cancelar pedido
curl -X POST "http://localhost:8000/api/pedidos/1/cambiar_estado/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "CANCELADO"
  }'
```

**Respuesta:**
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

---

## 💰 PAGOS

### 7. Listar Todos los Pagos

```bash
curl -X GET "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Respuesta:**
```json
{
  "count": 5,
  "next": null,
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
      "metodo_pago_display": "Efectivo",
      "comprobante": "REC-001",
      "estado": "COMPLETADO",
      "estado_display": "Completado"
    }
  ]
}
```

---

### 8. Listar Pagos con Filtros

```bash
# Por pedido
curl -X GET "http://localhost:8000/api/pagos/?pedido_id=1" \
  -H "Authorization: Bearer ${TOKEN}"

# Por método de pago
curl -X GET "http://localhost:8000/api/pagos/?metodo_pago=EFECTIVO" \
  -H "Authorization: Bearer ${TOKEN}"

# Por estado
curl -X GET "http://localhost:8000/api/pagos/?estado=COMPLETADO" \
  -H "Authorization: Bearer ${TOKEN}"

# Por rango de fechas
curl -X GET "http://localhost:8000/api/pagos/?fecha_desde=2025-11-01&fecha_hasta=2025-11-03" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

### 9. Registrar Pago en Efectivo

```bash
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "pedido_id": 1,
    "monto": "500.00",
    "metodo_pago": "EFECTIVO",
    "comprobante": "REC-001",
    "notas": "Pago inicial"
  }'
```

**Respuesta (201 CREATED):**
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
  "estado_display": "Completado",
  "notas": "Pago inicial",
  "registrado_por": {
    "id": 1,
    "usuario": "admin"
  }
}
```

---

### 10. Registrar Pago por Transferencia

```bash
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "pedido_id": 1,
    "monto": "347.50",
    "metodo_pago": "TRANSFERENCIA",
    "comprobante": "TRANS-20251103-001",
    "notas": "Transferencia Banco XYZ"
  }'
```

---

### 11. Pagar con Stripe

```bash
curl -X POST "http://localhost:8000/api/pagos/pagar_con_stripe/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "pedido_id": 1,
    "monto": "500.00",
    "payment_method_id": "pm_1K2L3M4N5O6P7Q8R",
    "comprobante": "STRIPE-REC-001"
  }'
```

**Respuesta Exitosa (201 CREATED):**
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
    "metodo_pago_display": "Stripe",
    "comprobante": "STRIPE-REC-001",
    "estado": "COMPLETADO",
    "estado_display": "Completado",
    "stripe_payment_intent_id": "pi_1K2L3M4N5O6P7Q8R",
    "stripe_charge_id": "ch_1K2L3M4N5O6P7Q8R"
  }
}
```

**Respuesta de Error (400 BAD REQUEST):**
```json
{
  "error": "Error al procesar pago: Tu tarjeta ha sido rechazada"
}
```

---

### 12. Reembolsar Pago de Stripe

```bash
curl -X POST "http://localhost:8000/api/pagos/2/reembolsar/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "motivo": "Producto defectuoso"
  }'
```

**Respuesta:**
```json
{
  "mensaje": "Reembolso procesado exitosamente",
  "pago": {
    "id": 2,
    "estado": "REEMBOLSADO",
    "estado_display": "Reembolsado",
    "notas": "Producto defectuoso"
  }
}
```

---

## 📊 HISTORIAL Y REPORTES

### 13. Consultar Historial de Ventas

```bash
# Sin filtros
curl -X GET "http://localhost:8000/api/historial-ventas/" \
  -H "Authorization: Bearer ${TOKEN}"

# Con todos los filtros
curl -X GET "http://localhost:8000/api/historial-ventas/?fecha_desde=2025-11-01&fecha_hasta=2025-11-03&cliente_nombre=Maria&estado_pedido=COMPLETADO&metodo_pago=EFECTIVO&page=1&page_size=20" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Respuesta:**
```json
{
  "count": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "estadisticas": {
    "total_ventas": 15,
    "total_monto": "22500.00",
    "total_pagado": "18000.00",
    "total_pendiente": "4500.00"
  },
  "filtros_aplicados": {
    "fecha_desde": "2025-11-01",
    "fecha_hasta": "2025-11-03",
    "cliente_nombre": "Maria",
    "socio_id": null,
    "estado_pedido": "COMPLETADO",
    "metodo_pago": "EFECTIVO"
  },
  "results": [
    {
      "id": 1,
      "numero_pedido": "ORD-20251103-0001",
      "fecha_pedido": "2025-11-03T10:30:00Z",
      "cliente_nombre": "María González",
      "total": "847.50",
      "total_pagado": "847.50",
      "saldo_pendiente": "0.00",
      "estado": "COMPLETADO",
      "estado_pago": "PAGADO"
    }
  ]
}
```

---

### 14. Exportar Historial a CSV

```bash
# Descargar archivo CSV
curl -X GET "http://localhost:8000/api/exportar-ventas-csv/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -o ventas.csv

# Con filtros
curl -X GET "http://localhost:8000/api/exportar-ventas-csv/?fecha_desde=2025-11-01&fecha_hasta=2025-11-03&estado_pedido=COMPLETADO" \
  -H "Authorization: Bearer ${TOKEN}" \
  -o ventas_completadas.csv
```

**Contenido del CSV:**
```csv
Número Pedido,Fecha,Cliente,Email,Teléfono,Socio,Subtotal,Impuestos,Descuento,Total,Total Pagado,Saldo Pendiente,Estado,Estado Pago
ORD-20251103-0001,2025-11-03 10:30,María González,maria@example.com,+591 70123456,Juan Pérez,750.00,97.50,0.00,847.50,847.50,0.00,COMPLETADO,PAGADO
```

---

## 📋 CONSULTAS ADICIONALES

### 15. Ver Bitácora de Auditoría

```bash
# Bitácora de pedidos
curl -X GET "http://localhost:8000/api/bitacora/?tabla_afectada=Pedido" \
  -H "Authorization: Bearer ${TOKEN}"

# Bitácora de pagos
curl -X GET "http://localhost:8000/api/bitacora/?tabla_afectada=Pago" \
  -H "Authorization: Bearer ${TOKEN}"

# Por usuario
curl -X GET "http://localhost:8000/api/bitacora/?usuario_id=1" \
  -H "Authorization: Bearer ${TOKEN}"

# Por acción
curl -X GET "http://localhost:8000/api/bitacora/?accion=REGISTRAR_PAGO" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## 🧪 CASOS DE PRUEBA COMPLETOS

### Test 1: Flujo Completo de Venta con Efectivo

```bash
# 1. Crear pedido
PEDIDO_ID=$(curl -X POST "http://localhost:8000/api/pedidos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "socio_id": 5,
    "cliente_nombre": "Test Cliente",
    "items": [{"producto_id": 10, "cantidad": 10, "precio_unitario": "50.00"}],
    "impuestos": "65.00",
    "descuento": "0.00"
  }' | jq -r '.id')

echo "Pedido creado con ID: $PEDIDO_ID"

# 2. Confirmar pedido
curl -X POST "http://localhost:8000/api/pedidos/${PEDIDO_ID}/cambiar_estado/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"estado": "CONFIRMADO"}'

# 3. Registrar pago completo en efectivo
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"pedido_id\": ${PEDIDO_ID},
    \"monto\": \"565.00\",
    \"metodo_pago\": \"EFECTIVO\",
    \"comprobante\": \"REC-TEST-001\"
  }"

# 4. Verificar que el pedido se completó automáticamente
curl -X GET "http://localhost:8000/api/pedidos/${PEDIDO_ID}/" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

### Test 2: Pagos Parciales

```bash
# 1. Crear pedido de 1000 Bs
PEDIDO_ID=$(curl -X POST "http://localhost:8000/api/pedidos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "socio_id": 5,
    "cliente_nombre": "Test Pagos Parciales",
    "items": [{"producto_id": 10, "cantidad": 20, "precio_unitario": "50.00"}],
    "impuestos": "0.00",
    "descuento": "0.00"
  }' | jq -r '.id')

# 2. Pago 1: 400 Bs
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"pedido_id\": ${PEDIDO_ID},
    \"monto\": \"400.00\",
    \"metodo_pago\": \"EFECTIVO\",
    \"comprobante\": \"REC-PARCIAL-1\"
  }"

# 3. Pago 2: 300 Bs
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"pedido_id\": ${PEDIDO_ID},
    \"monto\": \"300.00\",
    \"metodo_pago\": \"TRANSFERENCIA\",
    \"comprobante\": \"TRANS-PARCIAL-2\"
  }"

# 4. Pago 3: 300 Bs (completa el total)
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"pedido_id\": ${PEDIDO_ID},
    \"monto\": \"300.00\",
    \"metodo_pago\": \"EFECTIVO\",
    \"comprobante\": \"REC-PARCIAL-3\"
  }"

# 5. Ver que el pedido está COMPLETADO
curl -X GET "http://localhost:8000/api/pedidos/${PEDIDO_ID}/" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

### Test 3: Validaciones de Error

```bash
# Error: Monto mayor al saldo pendiente
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "pedido_id": 1,
    "monto": "999999.00",
    "metodo_pago": "EFECTIVO"
  }'

# Error: Pedido no existe
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "pedido_id": 99999,
    "monto": "100.00",
    "metodo_pago": "EFECTIVO"
  }'

# Error: Método de pago inválido
curl -X POST "http://localhost:8000/api/pagos/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "pedido_id": 1,
    "monto": "100.00",
    "metodo_pago": "METODO_INVALIDO"
  }'
```

---

## 📦 Colección Postman

### Importar a Postman

Crear un archivo `Sistema_Pagos.postman_collection.json`:

```json
{
  "info": {
    "name": "Sistema de Pagos - Cooperativa",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api"
    },
    {
      "key": "token",
      "value": "TU_TOKEN_AQUI"
    }
  ],
  "item": [
    {
      "name": "Pedidos",
      "item": [
        {
          "name": "Listar Pedidos",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": "{{base_url}}/pedidos/"
          }
        },
        {
          "name": "Crear Pedido",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"socio_id\": 5,\n  \"cliente_nombre\": \"María González\",\n  \"items\": [\n    {\n      \"producto_id\": 10,\n      \"cantidad\": 50,\n      \"precio_unitario\": \"15.00\"\n    }\n  ],\n  \"impuestos\": \"0.00\",\n  \"descuento\": \"0.00\"\n}"
            },
            "url": "{{base_url}}/pedidos/"
          }
        }
      ]
    },
    {
      "name": "Pagos",
      "item": [
        {
          "name": "Registrar Pago Efectivo",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"pedido_id\": 1,\n  \"monto\": \"500.00\",\n  \"metodo_pago\": \"EFECTIVO\",\n  \"comprobante\": \"REC-001\"\n}"
            },
            "url": "{{base_url}}/pagos/"
          }
        }
      ]
    }
  ]
}
```

---

## 🎯 Respuestas de Validación

### Error 400: Datos Inválidos
```json
{
  "socio_id": ["Este campo es requerido."],
  "items": ["Este campo es requerido."]
}
```

### Error 401: No Autenticado
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Error 403: Sin Permisos
```json
{
  "error": "Permisos insuficientes"
}
```

### Error 404: No Encontrado
```json
{
  "error": "Pedido no encontrado"
}
```

---

**Fin de la Colección de Pruebas**

Usa estos ejemplos para probar todos los endpoints del sistema de pagos.
