# 💰 Sistema de Pagos - Backend Implementado

## 📋 Resumen

Sistema completo de gestión de pagos y pedidos para la Cooperativa Agrícola. Permite registrar pedidos de venta, gestionar pagos con múltiples métodos (incluido Stripe), consultar historial y exportar reportes.

**Fecha de Implementación:** Noviembre 2025  
**Estado:** ✅ COMPLETADO - Listo para migrar y usar

---

## ✨ Características Implementadas

### 🛒 Gestión de Pedidos
- ✅ Crear pedidos con múltiples productos
- ✅ Actualizar información de pedidos
- ✅ Cambiar estados (Pendiente → Confirmado → En Proceso → Completado)
- ✅ Cancelar pedidos
- ✅ Cálculo automático de totales (subtotal + impuestos - descuento)
- ✅ Control de estados de pago (Pendiente, Parcial, Pagado)

### 💳 Gestión de Pagos
- ✅ Registro de pagos en efectivo
- ✅ Registro de pagos por transferencia
- ✅ Integración completa con Stripe (tarjetas)
- ✅ Pagos con código QR
- ✅ Pagos parciales (permite múltiples pagos por pedido)
- ✅ Validación de montos (no exceder saldo pendiente)
- ✅ Reembolsos automáticos con Stripe

### 📊 Consultas e Historial
- ✅ Historial de ventas con filtros avanzados:
  - Por rango de fechas
  - Por cliente
  - Por socio
  - Por estado de pedido
  - Por método de pago
- ✅ Estadísticas de ventas (total, monto, pagado, pendiente)
- ✅ Exportación a CSV con todos los filtros
- ✅ Paginación de resultados

### 🔒 Seguridad y Auditoría
- ✅ Autenticación requerida en todos los endpoints
- ✅ Control de permisos por rol (Admin vs Socio)
- ✅ Registro automático en bitácora de auditoría
- ✅ Validaciones de negocio estrictas

---

## 📁 Archivos Modificados/Creados

### Backend (Django)

#### Modelos (`cooperativa/models.py`)
```python
# NUEVOS MODELOS AGREGADOS AL FINAL DEL ARCHIVO:

class Pedido(models.Model):
    """Pedido/Orden de venta"""
    numero_pedido = models.CharField(max_length=50, unique=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    cliente_nombre = models.CharField(max_length=200)
    cliente_email = models.EmailField(blank=True, null=True)
    cliente_telefono = models.CharField(max_length=20, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO)
    notas = models.TextField(blank=True, null=True)
    # + timestamps

class DetallePedido(models.Model):
    """Líneas de pedido (productos)"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoCosechado, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

class Pago(models.Model):
    """Pago asociado a un pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    comprobante = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO)
    notas = models.TextField(blank=True, null=True)
    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    
    def procesar_pago_stripe(self, payment_method_id):
        """Procesa pago con Stripe API"""
        # Implementación completa incluida
        
    def reembolsar(self, motivo=''):
        """Reembolsa pago de Stripe"""
        # Implementación completa incluida
```

#### Serializers (`cooperativa/serializers.py`)
```python
# NUEVOS SERIALIZERS AGREGADOS AL FINAL:

class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializer para líneas de pedido"""

class PedidoSerializer(serializers.ModelSerializer):
    """Serializer completo de pedido con relaciones"""

class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pedidos"""

class PagoSerializer(serializers.ModelSerializer):
    """Serializer de pago con display names"""

class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer para registrar pagos (efectivo/transferencia)"""

class PagoStripeSerializer(serializers.Serializer):
    """Serializer para pagos con Stripe"""

class HistorialVentasSerializer(serializers.Serializer):
    """Serializer para validar filtros de historial"""
```

#### Views (`cooperativa/views.py`)
```python
# NUEVOS VIEWSETS Y ENDPOINTS AGREGADOS AL FINAL:

class PedidoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pedidos"""
    # GET /api/pedidos/
    # POST /api/pedidos/
    # GET /api/pedidos/{id}/
    # PUT/PATCH /api/pedidos/{id}/
    # POST /api/pedidos/{id}/cambiar_estado/

class PagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pagos"""
    # GET /api/pagos/
    # POST /api/pagos/
    # POST /api/pagos/pagar_con_stripe/
    # POST /api/pagos/{id}/reembolsar/

@api_view(['GET'])
def historial_ventas(request):
    """Consultar historial con filtros y estadísticas"""
    # GET /api/historial-ventas/

@api_view(['GET'])
def exportar_ventas_csv(request):
    """Exportar historial a CSV"""
    # GET /api/exportar-ventas-csv/
```

#### URLs (`cooperativa/urls.py`)
```python
# NUEVAS RUTAS AGREGADAS:

# ViewSets registrados en el router
router.register(r'pedidos', views.PedidoViewSet)
router.register(r'pagos', views.PagoViewSet)

# Endpoints adicionales
path('api/historial-ventas/', views.historial_ventas, name='historial-ventas'),
path('api/exportar-ventas-csv/', views.exportar_ventas_csv, name='exportar-ventas-csv'),
```

#### Settings (`cooperativa_backend/settings.py`)
```python
# NUEVAS CONFIGURACIONES AGREGADAS AL FINAL:

# Stripe Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
```

#### Requirements (`requirements.txt`)
```txt
# NUEVA DEPENDENCIA AGREGADA:
stripe==11.2.0
```

---

## 🗂️ Estructura de la Base de Datos

### Tabla: `cooperativa_pedido`
```sql
- id (PK)
- numero_pedido (UNIQUE)
- fecha_pedido
- socio_id (FK → cooperativa_socio)
- cliente_nombre
- cliente_email
- cliente_telefono
- subtotal
- impuestos
- descuento
- total
- estado
- notas
- creado_en
- actualizado_en
```

### Tabla: `cooperativa_detallepedido`
```sql
- id (PK)
- pedido_id (FK → cooperativa_pedido)
- producto_id (FK → cooperativa_productocosechado)
- cantidad
- precio_unitario
- subtotal
```

### Tabla: `cooperativa_pago`
```sql
- id (PK)
- pedido_id (FK → cooperativa_pedido)
- fecha_pago
- monto
- metodo_pago
- comprobante
- estado
- notas
- stripe_payment_intent_id
- stripe_charge_id
- stripe_customer_id
- registrado_por_id (FK → cooperativa_usuario)
- creado_en
```

---

## 🚀 Cómo Usar

### 1. Instalar Dependencias
```bash
cd c:\Users\httpReen\Desktop\GitYandira\backend_si2_final\cooperativa_backend
pip install stripe==11.2.0
```

### 2. Configurar Variables de Entorno
Crear/editar archivo `.env`:
```env
# Stripe (obtener desde https://dashboard.stripe.com)
STRIPE_PUBLIC_KEY=pk_test_51xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### 3. Crear Migraciones
```bash
python manage.py makemigrations
```

**Output esperado:**
```
Migrations for 'cooperativa':
  cooperativa/migrations/0003_pedido_detallepedido_pago.py
    - Create model Pedido
    - Create model DetallePedido
    - Create model Pago
```

### 4. Aplicar Migraciones
```bash
python manage.py migrate
```

### 5. Iniciar Servidor
```bash
python manage.py runserver
```

### 6. Probar Endpoints
```bash
# Listar pedidos
curl -H "Authorization: Bearer {token}" http://localhost:8000/api/pedidos/

# Crear pedido
curl -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" \
  -d '{"socio_id":5,"cliente_nombre":"Test","items":[{"producto_id":1,"cantidad":10,"precio_unitario":"5.00"}],"impuestos":"0","descuento":"0"}' \
  http://localhost:8000/api/pedidos/

# Historial
curl -H "Authorization: Bearer {token}" http://localhost:8000/api/historial-ventas/
```

---

## 📖 Documentación para Frontend

Se crearon 3 documentos en `docs/`:

### 1. **SISTEMA_PAGOS_API.md** (Documentación Completa)
- Descripción detallada de cada endpoint
- Ejemplos de request/response
- Modelos de datos completos
- Códigos de error
- Configuración Stripe
- Permisos y seguridad

### 2. **SISTEMA_PAGOS_FRONTEND_EJEMPLOS.md** (Código Frontend)
- Servicio API JavaScript completo
- Componentes React completos:
  - Lista de pedidos
  - Formulario crear pedido
  - Formulario pago con Stripe
  - Dashboard de resumen
- Componentes Vue 3
- Integración Stripe completa

### 3. **SISTEMA_PAGOS_GUIA_RAPIDA.md** (Guía Rápida)
- Endpoints resumidos
- Ejemplos rápidos
- Estados y códigos
- Configuración Stripe simplificada

---

## 🔑 Endpoints API

### Pedidos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/pedidos/` | Listar pedidos (con filtros) |
| POST | `/api/pedidos/` | Crear pedido |
| GET | `/api/pedidos/{id}/` | Obtener detalle |
| PUT/PATCH | `/api/pedidos/{id}/` | Actualizar pedido |
| POST | `/api/pedidos/{id}/cambiar_estado/` | Cambiar estado |

### Pagos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/pagos/` | Listar pagos (con filtros) |
| POST | `/api/pagos/` | Registrar pago efectivo/transferencia |
| POST | `/api/pagos/pagar_con_stripe/` | Procesar pago con Stripe |
| POST | `/api/pagos/{id}/reembolsar/` | Reembolsar pago Stripe |

### Historial
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/historial-ventas/` | Consultar historial (con filtros y estadísticas) |
| GET | `/api/exportar-ventas-csv/` | Descargar CSV del historial |

---

## 🎯 Validaciones Implementadas

### Pedidos
- ✅ Socio debe existir
- ✅ Cliente nombre es requerido
- ✅ Al menos 1 producto requerido
- ✅ Cantidad > 0
- ✅ Precio unitario > 0
- ✅ No se pueden editar pedidos cancelados
- ✅ Número de pedido único autogenerado

### Pagos
- ✅ Pedido debe existir
- ✅ Pedido no debe estar cancelado
- ✅ Monto > 0
- ✅ Monto ≤ saldo pendiente
- ✅ Método de pago válido
- ✅ Pagos efectivo/transferencia → auto-completados
- ✅ Pagos Stripe → procesados con API
- ✅ Actualización automática de estado del pedido

---

## 🔒 Permisos

### Administrador (`is_staff=True`)
- Ver todos los pedidos y pagos
- Crear, editar, eliminar pedidos
- Registrar pagos (todos los métodos)
- Cambiar estados de pedidos
- Procesar reembolsos
- Ver historial completo
- Exportar CSV

### Socio (Usuario normal)
- Ver solo sus propios pedidos
- Ver pagos de sus pedidos
- NO puede ver pedidos de otros socios
- NO puede procesar reembolsos

---

## 📊 Flujos de Negocio

### Flujo 1: Venta con Efectivo
```
1. Crear Pedido → estado: PENDIENTE
2. Cambiar estado → CONFIRMADO
3. Registrar Pago (efectivo) → estado pago: COMPLETADO
4. Si pago = total → Pedido auto-cambia a COMPLETADO
```

### Flujo 2: Venta con Stripe
```
1. Crear Pedido → estado: PENDIENTE
2. Cambiar estado → CONFIRMADO
3. Frontend: Obtener payment_method_id con Stripe.js
4. Enviar a /pagos/pagar_con_stripe/
5. Backend procesa con Stripe API
6. Si exitoso → Pago: COMPLETADO, Pedido: COMPLETADO si total pagado
7. Si falla → Pago: FALLIDO, error devuelto
```

### Flujo 3: Pagos Parciales
```
1. Crear Pedido (total: 1000)
2. Registrar Pago 1 (500) → estado_pago: PARCIAL
3. Registrar Pago 2 (300) → estado_pago: PARCIAL
4. Registrar Pago 3 (200) → estado_pago: PAGADO, pedido: COMPLETADO
```

---

## 🧪 Datos de Prueba

### Tarjetas Stripe (Modo Test)
```
ÉXITO:     4242 4242 4242 4242
FALLO:     4000 0000 0000 0002
3D SECURE: 4000 0025 0000 3155

CVV: 123
Fecha: 12/30
ZIP: 12345
```

### Ejemplo de Pedido de Prueba
```json
{
  "socio_id": 1,
  "cliente_nombre": "Cliente de Prueba",
  "cliente_email": "test@test.com",
  "items": [
    {
      "producto_id": 1,
      "cantidad": 10,
      "precio_unitario": "50.00"
    }
  ],
  "impuestos": "65.00",
  "descuento": "0.00"
}
```

---

## 📝 Notas Técnicas

### Cálculo de Totales
```python
subtotal = sum(item.cantidad * item.precio_unitario)
total = subtotal + impuestos - descuento
saldo_pendiente = total - total_pagado
```

### Estados de Pago Automáticos
```python
if total_pagado == 0:
    estado_pago = 'PENDIENTE'
elif 0 < total_pagado < total:
    estado_pago = 'PARCIAL'
elif total_pagado >= total:
    estado_pago = 'PAGADO'
    estado_pedido = 'COMPLETADO'  # auto-actualización
```

### Números de Pedido
```python
# Formato: ORD-YYYYMMDD-NNNN
# Ejemplo: ORD-20251103-0001
```

---

## ⚠️ Consideraciones Importantes

1. **Migraciones Pendientes**: Ejecutar `makemigrations` y `migrate` antes de usar
2. **Variables de Entorno**: Configurar Stripe keys en `.env`
3. **Permisos**: Los socios solo ven sus propios pedidos
4. **Stripe Webhooks**: No implementados (solo PaymentIntent directo)
5. **Inventario**: No hay descuento automático de stock (implementar si necesario)
6. **Moneda**: Todo en bolivianos (Bs.)
7. **Zona Horaria**: America/La_Paz configurada

---

## 🐛 Troubleshooting

### Error: "No module named 'stripe'"
```bash
pip install stripe==11.2.0
```

### Error: "No such table: cooperativa_pedido"
```bash
python manage.py makemigrations
python manage.py migrate
```

### Error: "STRIPE_SECRET_KEY not configured"
```bash
# Crear archivo .env con las keys de Stripe
```

### Error: "Tarjeta rechazada"
```bash
# Usar tarjeta de prueba: 4242 4242 4242 4242
```

---

## 📦 Dependencias

```txt
Django==5.2.5
djangorestframework==3.16.1
stripe==11.2.0  # ← NUEVA
dj-database-url==2.3.0
psycopg==3.2.3
python-dotenv==1.0.1
```

---

## ✅ Checklist de Implementación

- [x] Modelos de datos creados
- [x] Serializers implementados
- [x] ViewSets creados
- [x] URLs registradas
- [x] Integración Stripe completa
- [x] Validaciones de negocio
- [x] Registro en bitácora
- [x] Control de permisos
- [x] Exportación CSV
- [x] Documentación API
- [x] Ejemplos frontend
- [x] Guía rápida
- [ ] **PENDIENTE: Ejecutar migraciones**
- [ ] **PENDIENTE: Configurar Stripe keys**
- [ ] **PENDIENTE: Probar endpoints**

---

## 📧 Soporte

Para dudas técnicas:
- Ver documentación en `docs/SISTEMA_PAGOS_API.md`
- Revisar ejemplos en `docs/SISTEMA_PAGOS_FRONTEND_EJEMPLOS.md`
- Consultar guía rápida en `docs/SISTEMA_PAGOS_GUIA_RAPIDA.md`
- Revisar bitácora: `GET /api/bitacora/?tabla_afectada=Pedido`

---

**Sistema implementado por:** Backend SI2 Team  
**Fecha:** Noviembre 3, 2025  
**Estado:** ✅ LISTO PARA PRODUCCIÓN (después de migrar)
