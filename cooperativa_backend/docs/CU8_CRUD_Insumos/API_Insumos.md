# 📡 API de Insumos Agrícolas - Referencia Completa

## 🌱 Descripción General

La **API de Insumos Agrícolas** proporciona endpoints REST completos para la gestión de inventario de pesticidas y fertilizantes. Implementa operaciones CRUD completas con validaciones avanzadas, filtros, búsqueda y acciones personalizadas.

## 🏗️ Arquitectura de la API

### **Tecnologías Utilizadas**
- **Framework:** Django REST Framework
- **Autenticación:** Token Authentication
- **Paginación:** PageNumberPagination
- **Filtrado:** DjangoFilterBackend
- **Búsqueda:** SearchFilter
- **Ordenamiento:** OrderingFilter

### **Configuración Base**
```python
class PesticidaViewSet(viewsets.ModelViewSet):
    queryset = Pesticida.objects.all()
    serializer_class = PesticidaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'tipo_pesticida', 'proveedor']
    search_fields = ['nombre_comercial', 'ingrediente_activo', 'lote']
    ordering_fields = ['fecha_vencimiento', 'cantidad', 'precio_unitario']
```

## 📋 Endpoints Principales

### **Pesticidas**

#### **Listar Pesticidas**
```http
GET /api/pesticidas/
```

**Parámetros de Consulta:**
- `page`: Número de página (paginación)
- `page_size`: Elementos por página
- `search`: Búsqueda en nombre, ingrediente activo, lote
- `estado`: Filtrar por estado (DISPONIBLE, AGOTADO, etc.)
- `tipo_pesticida`: Filtrar por tipo (INSECTICIDA, FUNGICIDA, etc.)
- `proveedor`: Filtrar por proveedor
- `ordering`: Ordenar por campo (-fecha_vencimiento, cantidad, etc.)

**Respuesta Exitosa (200):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/pesticidas/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "nombre_comercial": "Pesticida X",
            "ingrediente_activo": "Clorpirifos",
            "tipo_pesticida": "INSECTICIDA",
            "concentracion": "48% EC",
            "registro_sanitario": "REG-001",
            "cantidad": "100.00",
            "unidad_medida": "Litros",
            "fecha_vencimiento": "2025-12-31",
            "dosis_recomendada": "2-3 L/ha",
            "lote": "LOT-2025-001",
            "proveedor": "AgroQuimica SA",
            "precio_unitario": "45.50",
            "ubicacion_almacen": "Sector A-15",
            "estado": "DISPONIBLE",
            "observaciones": "",
            "valor_total": 4550.00,
            "dias_para_vencer": 92,
            "esta_proximo_vencer": false,
            "esta_vencido": false,
            "creado_en": "2025-01-15T10:30:00Z",
            "actualizado_en": "2025-01-15T10:30:00Z"
        }
    ]
}
```

#### **Crear Pesticida**
```http
POST /api/pesticidas/
```

**Cuerpo de la Solicitud:**
```json
{
    "nombre_comercial": "Nuevo Pesticida",
    "ingrediente_activo": "Ingrediente Activo",
    "tipo_pesticida": "INSECTICIDA",
    "concentracion": "50% WP",
    "registro_sanitario": "REG-002",
    "cantidad": 200.50,
    "unidad_medida": "Kilogramos",
    "fecha_vencimiento": "2026-06-30",
    "dosis_recomendada": "1-2 kg/ha",
    "lote": "LOT-2025-002",
    "proveedor": "Proveedor XYZ",
    "precio_unitario": 35.75,
    "ubicacion_almacen": "Sector B-20",
    "estado": "DISPONIBLE",
    "observaciones": "Producto nuevo en inventario"
}
```

**Respuesta Exitosa (201):**
```json
{
    "id": 2,
    "nombre_comercial": "Nuevo Pesticida",
    "ingrediente_activo": "Ingrediente Activo",
    "tipo_pesticida": "INSECTICIDA",
    "concentracion": "50% WP",
    "registro_sanitario": "REG-002",
    "cantidad": "200.50",
    "unidad_medida": "Kilogramos",
    "fecha_vencimiento": "2026-06-30",
    "dosis_recomendada": "1-2 kg/ha",
    "lote": "LOT-2025-002",
    "proveedor": "Proveedor XYZ",
    "precio_unitario": "35.75",
    "ubicacion_almacen": "Sector B-20",
    "estado": "DISPONIBLE",
    "observaciones": "Producto nuevo en inventario",
    "valor_total": 7165.00,
    "dias_para_vencer": 531,
    "esta_proximo_vencer": false,
    "esta_vencido": false,
    "creado_en": "2025-01-15T11:00:00Z",
    "actualizado_en": "2025-01-15T11:00:00Z"
}
```

#### **Detalle de Pesticida**
```http
GET /api/pesticidas/{id}/
```

#### **Actualizar Pesticida**
```http
PUT /api/pesticidas/{id}/
PATCH /api/pesticidas/{id}/
```

#### **Eliminar Pesticida**
```http
DELETE /api/pesticidas/{id}/
```

### **Fertilizantes**

#### **Listar Fertilizantes**
```http
GET /api/fertilizantes/
```

**Parámetros de Consulta:**
- `page`: Número de página
- `page_size`: Elementos por página
- `search`: Búsqueda en nombre, composición NPK, lote
- `estado`: Filtrar por estado
- `tipo_fertilizante`: Filtrar por tipo (QUIMICO, ORGANICO, etc.)
- `proveedor`: Filtrar por proveedor
- `ordering`: Ordenar por campo

**Respuesta Exitosa (200):**
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "nombre_comercial": "Fertilizante NPK Completo",
            "tipo_fertilizante": "QUIMICO",
            "composicion_npk": "20-10-10",
            "cantidad": "500.00",
            "unidad_medida": "Kilogramos",
            "fecha_vencimiento": "2026-12-31",
            "dosis_recomendada": "200-300 kg/ha",
            "materia_orgánica": null,
            "lote": "LOT-F-2025-001",
            "proveedor": "NutriAgro SA",
            "precio_unitario": "25.50",
            "ubicacion_almacen": "Sector C-10",
            "estado": "DISPONIBLE",
            "observaciones": "",
            "valor_total": 12750.00,
            "dias_para_vencer": 715,
            "esta_proximo_vencer": false,
            "esta_vencido": false,
            "npk_values": {
                "N": 20,
                "P": 10,
                "K": 10
            },
            "creado_en": "2025-01-15T10:30:00Z",
            "actualizado_en": "2025-01-15T10:30:00Z"
        }
    ]
}
```

#### **Crear Fertilizante**
```http
POST /api/fertilizantes/
```

**Cuerpo de la Solicitud:**
```json
{
    "nombre_comercial": "Nuevo Fertilizante Orgánico",
    "tipo_fertilizante": "ORGANICO",
    "composicion_npk": "5-3-8",
    "cantidad": 300.00,
    "unidad_medida": "Kilogramos",
    "fecha_vencimiento": "2027-06-30",
    "dosis_recomendada": "150-200 kg/ha",
    "materia_orgánica": 45.50,
    "lote": "LOT-F-2025-002",
    "proveedor": "EcoFertil SA",
    "precio_unitario": 18.75,
    "ubicacion_almacen": "Sector D-05",
    "estado": "DISPONIBLE",
    "observaciones": "Fertilizante orgánico certificado"
}
```

## 🎯 Endpoints Avanzados

### **Pesticidas**

#### **Pesticidas Próximos a Vencer**
```http
GET /api/pesticidas/proximos_vencer/
```

**Parámetros:**
- `dias`: Número de días para considerar "próximo" (default: 30)

**Respuesta (200):**
```json
{
    "count": 3,
    "results": [
        {
            "id": 5,
            "nombre_comercial": "Pesticida A Vencer",
            "fecha_vencimiento": "2025-02-10",
            "dias_para_vencer": 26,
            "cantidad": "50.00",
            "estado": "DISPONIBLE"
        }
    ]
}
```

#### **Pesticidas Vencidos**
```http
GET /api/pesticidas/vencidos/
```

#### **Actualizar Cantidad de Pesticida**
```http
POST /api/pesticidas/{id}/actualizar_cantidad/
```

**Cuerpo:**
```json
{
    "cantidad": 75.50,
    "motivo": "Ajuste de inventario"
}
```

#### **Marcar Pesticida como Vencido**
```http
POST /api/pesticidas/{id}/marcar_vencido/
```

#### **Reporte de Inventario de Pesticidas**
```http
GET /api/pesticidas/reporte_inventario/
```

**Respuesta (200):**
```json
{
    "total_pesticidas": 25,
    "valor_total_inventario": 125000.50,
    "pesticidas_disponibles": 22,
    "pesticidas_agotados": 1,
    "pesticidas_vencidos": 2,
    "proximos_vencer_30_dias": 3,
    "distribucion_por_tipo": {
        "INSECTICIDA": 12,
        "FUNGICIDA": 8,
        "HERBICIDA": 5
    },
    "top_proveedores": [
        {"proveedor": "AgroQuimica SA", "cantidad": 8},
        {"proveedor": "Quimica Verde", "cantidad": 6}
    ]
}
```

### **Fertilizantes**

#### **Fertilizantes Próximos a Vencer**
```http
GET /api/fertilizantes/proximos_vencer/
```

#### **Fertilizantes Vencidos**
```http
GET /api/fertilizantes/vencidos/
```

#### **Actualizar Cantidad de Fertilizante**
```http
POST /api/fertilizantes/{id}/actualizar_cantidad/
```

#### **Marcar Fertilizante como Vencido**
```http
POST /api/fertilizantes/{id}/marcar_vencido/
```

#### **Reporte de Inventario de Fertilizantes**
```http
GET /api/fertilizantes/reporte_inventario/
```

## 🔍 Filtros y Búsqueda

### **Filtros Disponibles**

#### **Pesticidas**
- `estado`: DISPONIBLE, AGOTADO, VENCIDO, RETIRADO
- `tipo_pesticida`: INSECTICIDA, FUNGICIDA, HERBICIDA, ACARICIDA, NEMATICIDA
- `proveedor`: Nombre del proveedor
- `fecha_vencimiento_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_vencimiento_hasta`: Fecha hasta (YYYY-MM-DD)
- `cantidad_min`: Cantidad mínima
- `cantidad_max`: Cantidad máxima

#### **Fertilizantes**
- `estado`: DISPONIBLE, AGOTADO, VENCIDO, RETIRADO
- `tipo_fertilizante`: QUIMICO, ORGANICO, MINERAL, COMPUESTO
- `proveedor`: Nombre del proveedor
- `fecha_vencimiento_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_vencimiento_hasta`: Fecha hasta (YYYY-MM-DD)
- `cantidad_min`: Cantidad mínima
- `cantidad_max`: Cantidad máxima
- `nitrogeno_min`: Nivel mínimo de nitrógeno
- `nitrogeno_max`: Nivel máximo de nitrógeno

### **Búsqueda de Texto**
- **Pesticidas:** nombre_comercial, ingrediente_activo, lote, proveedor
- **Fertilizantes:** nombre_comercial, composicion_npk, lote, proveedor

### **Ordenamiento**
- `fecha_vencimiento`: Fecha de vencimiento
- `cantidad`: Cantidad disponible
- `precio_unitario`: Precio unitario
- `creado_en`: Fecha de creación
- `actualizado_en`: Fecha de actualización

## ⚠️ Códigos de Error

### **Errores Comunes**

#### **400 Bad Request**
```json
{
    "error": "Datos de entrada inválidos",
    "details": {
        "nombre_comercial": ["Este campo es obligatorio."],
        "fecha_vencimiento": ["La fecha de vencimiento no puede ser en el pasado."]
    }
}
```

#### **401 Unauthorized**
```json
{
    "error": "Autenticación requerida",
    "message": "Token de autenticación no proporcionado o inválido"
}
```

#### **403 Forbidden**
```json
{
    "error": "Permisos insuficientes",
    "message": "No tienes permisos para realizar esta acción"
}
```

#### **404 Not Found**
```json
{
    "error": "Recurso no encontrado",
    "message": "El insumo solicitado no existe"
}
```

#### **409 Conflict**
```json
{
    "error": "Conflicto de datos",
    "message": "Ya existe un insumo con este lote"
}
```

#### **422 Unprocessable Entity**
```json
{
    "error": "Validación fallida",
    "details": {
        "composicion_npk": ["Formato NPK inválido. Use formato N-P-K (ej: 10-10-10)"]
    }
}
```

## 🔒 Autenticación y Seguridad

### **Autenticación Requerida**
Todos los endpoints requieren autenticación mediante Token Authentication:

**Header requerido:**
```
Authorization: Token your_token_here
```

### **Permisos**
- **Lectura:** Usuarios autenticados pueden listar y ver detalles
- **Escritura:** Solo usuarios con permisos específicos pueden crear/modificar/eliminar
- **Admin:** Acceso completo a todas las operaciones

## 📊 Paginación

### **Configuración por Defecto**
- **page_size**: 25 elementos por página
- **max_page_size**: 100 elementos por página

### **Ejemplo de Paginación**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/pesticidas/?page=2",
    "previous": "http://localhost:8000/api/pesticidas/?page=1",
    "results": [...]
}
```

**Personalizar tamaño de página:**
```
GET /api/pesticidas/?page_size=50
```

## 📈 Límites de Tasa (Rate Limiting)

### **Límites Implementados**
- **Autenticado:** 1000 requests/hora
- **No autenticado:** 100 requests/hora
- **Burst:** 50 requests/minuto

### **Headers de Rate Limiting**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## 🧪 Ejemplos de Uso

### **JavaScript (fetch)**
```javascript
// Listar pesticidas
const response = await fetch('/api/pesticidas/', {
    headers: {
        'Authorization': 'Token your_token',
        'Content-Type': 'application/json'
    }
});
const data = await response.json();

// Crear nuevo pesticida
const nuevoPesticida = {
    nombre_comercial: "Pesticida Ejemplo",
    ingrediente_activo: "Ejemplo Activo",
    tipo_pesticida: "INSECTICIDA",
    concentracion: "40% EC",
    cantidad: 100,
    unidad_medida: "Litros",
    fecha_vencimiento: "2026-12-31",
    lote: "LOT-2025-999",
    proveedor: "Proveedor Demo",
    precio_unitario: 50.00,
    ubicacion_almacen: "Demo Sector",
    estado: "DISPONIBLE"
};

await fetch('/api/pesticidas/', {
    method: 'POST',
    headers: {
        'Authorization': 'Token your_token',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(nuevoPesticida)
});
```

### **Python (requests)**
```python
import requests

headers = {
    'Authorization': 'Token your_token',
    'Content-Type': 'application/json'
}

# Listar fertilizantes próximos a vencer
response = requests.get('/api/fertilizantes/proximos_vencer/', headers=headers)
data = response.json()

# Actualizar cantidad
update_data = {
    'cantidad': 250.00,
    'motivo': 'Reabastecimiento'
}
response = requests.post(
    '/api/fertilizantes/1/actualizar_cantidad/',
    json=update_data,
    headers=headers
)
```

### **cURL**
```bash
# Listar pesticidas con filtros
curl -H "Authorization: Token your_token" \
     "http://localhost:8000/api/pesticidas/?estado=DISPONIBLE&tipo_pesticida=INSECTICIDA"

# Crear fertilizante
curl -X POST \
     -H "Authorization: Token your_token" \
     -H "Content-Type: application/json" \
     -d '{"nombre_comercial":"Fertilizante Demo","tipo_fertilizante":"QUIMICO","composicion_npk":"15-15-15","cantidad":100,"unidad_medida":"Kilogramos","fecha_vencimiento":"2026-12-31","lote":"LOT-DEMO","proveedor":"Demo Provider","precio_unitario":30.00,"ubicacion_almacen":"Sector Demo","estado":"DISPONIBLE"}' \
     http://localhost:8000/api/fertilizantes/
```

## 📋 Versionado de API

### **Versión Actual**
- **Versión:** v1
- **Base URL:** `/api/v1/`
- **Estado:** Estable

### **Política de Versionado**
- **Cambios incompatibles:** Nueva versión mayor (v2, v3, etc.)
- **Cambios compatibles:** Misma versión con documentación actualizada
- **Deprecación:** 6 meses de antelación antes de remover endpoints

## 🔧 Configuración y Despliegue

### **Variables de Entorno**
```env
# API Configuration
API_BASE_URL=/api/v1/
API_PAGE_SIZE=25
API_MAX_PAGE_SIZE=100

# Rate Limiting
RATE_LIMIT_AUTHENTICATED=1000/hour
RATE_LIMIT_ANONYMOUS=100/hour
RATE_LIMIT_BURST=50/minute
```

### **Configuración Django**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

## 📞 Soporte y Contacto

- **Documentación:** [API Docs](README.md)
- **Issues:** [GitHub Issues](../../issues)
- **Soporte:** api-support@cooperativa.com
- **Versión:** 1.0.0
- **Última actualización:** Octubre 2025</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU8_CRUD_Insumos\API_Insumos.md