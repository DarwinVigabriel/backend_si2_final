# 🌱 API de Semillas - Referencia Completa

## 📋 Información General

La **API de Semillas** proporciona endpoints RESTful completos para la gestión del inventario de semillas de la Cooperativa. Implementa operaciones CRUD completas con validaciones avanzadas, filtros, búsqueda y acciones personalizadas para el control de inventario.

**Base URL:** `/api/semillas/`  
**Autenticación:** Token Authentication  
**Formato:** JSON  
**Encoding:** UTF-8

## 🔐 Autenticación

Todos los endpoints requieren autenticación mediante token:

```bash
Authorization: Token <your-token>
```

**Credenciales de prueba:**
- Usuario: `admin`
- Contraseña: `clave123`

## 📊 Endpoints Principales

### **1. Listar Semillas**
```http
GET /api/semillas/
```

**Parámetros de Consulta:**
- `especie`: Filtrar por especie (string)
- `variedad`: Filtrar por variedad (string)
- `estado`: Filtrar por estado (string)
- `proveedor`: Filtrar por proveedor (string)
- `lote`: Filtrar por lote (string)
- `fecha_vencimiento_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_vencimiento_hasta`: Fecha hasta (YYYY-MM-DD)
- `pg_min`: Porcentaje germinación mínimo (decimal)
- `pg_max`: Porcentaje germinación máximo (decimal)
- `search`: Búsqueda general (string)
- `ordering`: Ordenamiento (string)
- `page`: Página (integer)
- `page_size`: Tamaño de página (integer)

**Ejemplo de Request:**
```bash
GET /api/semillas/?especie=Maíz&estado=DISPONIBLE&ordering=-fecha_vencimiento
```

**Respuesta Exitosa (200):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/semillas/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "500.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": "2025-12-31",
            "porcentaje_germinacion": "95.50",
            "lote": "MZ2025001",
            "proveedor": "AgroSemillas S.A.",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Sector A-15",
            "estado": "DISPONIBLE",
            "observaciones": "Lote premium de alta germinación",
            "creado_en": "2025-01-15T10:30:00Z",
            "actualizado_en": "2025-01-15T10:30:00Z",
            "valor_total": "12500.00",
            "dias_para_vencer": 350,
            "esta_proxima_vencer": false,
            "esta_vencida": false
        }
    ]
}
```

### **2. Crear Semilla**
```http
POST /api/semillas/
```

**Campos Requeridos:**
- `especie`: Especie de la semilla (string, max 100)
- `variedad`: Variedad específica (string, max 100)
- `cantidad`: Cantidad disponible (decimal, positivo)
- `unidad_medida`: Unidad de medida (string, max 20)
- `fecha_vencimiento`: Fecha de vencimiento (date)
- `porcentaje_germinacion`: % de germinación (decimal, 0-100)
- `lote`: Número de lote (string, max 50)
- `proveedor`: Nombre del proveedor (string, max 100)
- `precio_unitario`: Precio por unidad (decimal, positivo)
- `ubicacion_almacen`: Ubicación en almacén (string, max 100)

**Campos Opcionales:**
- `observaciones`: Notas adicionales (text)

**Ejemplo de Request:**
```json
{
    "especie": "Trigo",
    "variedad": "Cenizo",
    "cantidad": "200.50",
    "unidad_medida": "kg",
    "fecha_vencimiento": "2026-06-30",
    "porcentaje_germinacion": "92.30",
    "lote": "TR2025002",
    "proveedor": "Semillas del Sur",
    "precio_unitario": "18.50",
    "ubicacion_almacen": "Sector B-08",
    "observaciones": "Variedad resistente a sequía"
}
```

**Respuesta Exitosa (201):**
```json
{
    "id": 2,
    "especie": "Trigo",
    "variedad": "Cenizo",
    "cantidad": "200.50",
    "unidad_medida": "kg",
    "fecha_vencimiento": "2026-06-30",
    "porcentaje_germinacion": "92.30",
    "lote": "TR2025002",
    "proveedor": "Semillas del Sur",
    "precio_unitario": "18.50",
    "ubicacion_almacen": "Sector B-08",
    "estado": "DISPONIBLE",
    "observaciones": "Variedad resistente a sequía",
    "creado_en": "2025-01-15T11:45:00Z",
    "actualizado_en": "2025-01-15T11:45:00Z",
    "valor_total": "3719.25",
    "dias_para_vencer": 531,
    "esta_proxima_vencer": false,
    "esta_vencida": false
}
```

### **3. Obtener Semilla Específica**
```http
GET /api/semillas/{id}/
```

**Parámetros de URL:**
- `id`: ID de la semilla (integer)

**Respuesta Exitosa (200):** Similar al objeto individual del listado

### **4. Actualizar Semilla**
```http
PUT /api/semillas/{id}/
PATCH /api/semillas/{id}/
```

**PUT:** Actualización completa (todos los campos requeridos)  
**PATCH:** Actualización parcial (solo campos especificados)

**Ejemplo PATCH:**
```json
{
    "cantidad": "150.00",
    "observaciones": "Stock actualizado después de venta"
}
```

### **5. Eliminar Semilla**
```http
DELETE /api/semillas/{id}/
```

**Respuesta Exitosa (204):** Sin contenido

## 🎯 Endpoints Avanzados

### **6. Actualizar Cantidad**
```http
POST /api/semillas/{id}/actualizar_cantidad/
```

**Body:**
```json
{
    "nueva_cantidad": "300.00",
    "motivo": "Reabastecimiento de inventario"
}
```

**Respuesta (200):**
```json
{
    "mensaje": "Cantidad actualizada exitosamente",
    "cantidad_anterior": "200.50",
    "cantidad_nueva": "300.00",
    "diferencia": "99.50"
}
```

### **7. Marcar como Vencida**
```http
POST /api/semillas/{id}/marcar_vencida/
```

**Body:**
```json
{
    "motivo": "Vencimiento natural del lote"
}
```

**Respuesta (200):**
```json
{
    "mensaje": "Semilla marcada como vencida",
    "estado_anterior": "DISPONIBLE",
    "estado_nuevo": "VENCIDA"
}
```

### **8. Inventario Bajo**
```http
GET /api/semillas/inventario_bajo/
```

**Parámetros:**
- `umbral`: Cantidad mínima (decimal, default: 50)

**Respuesta (200):** Lista de semillas con stock bajo

### **9. Próximas a Vencer**
```http
GET /api/semillas/proximas_vencer/
```

**Parámetros:**
- `dias`: Días límite (integer, default: 30)

**Respuesta (200):** Lista de semillas que vencen pronto

### **10. Semillas Vencidas**
```http
GET /api/semillas/vencidas/
```

**Respuesta (200):** Lista de semillas ya vencidas

### **11. Reporte de Inventario**
```http
GET /api/semillas/reporte_inventario/
```

**Respuesta (200):**
```json
{
    "resumen": {
        "total_semillas": 25,
        "semillas_disponibles": 22,
        "semillas_agotadas": 1,
        "semillas_vencidas": 2,
        "semillas_reservadas": 0,
        "valor_total_inventario": 45250.75,
        "promedio_porcentaje_germinacion": 92.5
    },
    "cantidad_por_especie": [
        {
            "especie": "Maíz",
            "total_cantidad": 150.50,
            "num_variedades": 2
        },
        {
            "especie": "Trigo",
            "total_cantidad": 200.25,
            "num_variedades": 1
        }
    ],
    "semillas_por_proveedor": [
        {
            "proveedor": "AgroSemillas S.A.",
            "num_semillas": 15,
            "total_cantidad": 350.75
        },
        {
            "proveedor": "Semillas del Sur",
            "num_semillas": 10,
            "total_cantidad": 125.50
        }
    ]
}
```

## 📋 Estados de Semilla

| Estado | Descripción |
|--------|-------------|
| `DISPONIBLE` | Semilla disponible para uso |
| `AGOTADA` | Sin stock disponible |
| `VENCIDA` | Fecha de vencimiento pasada |
| `EN_CUARENTENA` | Pendiente de análisis de calidad |
| `RECHAZADA` | No cumple estándares de calidad |

## ⚠️ Códigos de Error

### **Errores de Validación (400)**
```json
{
    "especie": ["Este campo es requerido."],
    "porcentaje_germinacion": ["El porcentaje debe estar entre 0 y 100."],
    "fecha_vencimiento": ["La fecha no puede ser en el pasado."],
    "cantidad": ["La cantidad no puede ser negativa."]
}
```

### **No Encontrado (404)**
```json
{
    "detail": "No encontrado."
}
```

### **No Autorizado (401)**
```json
{
    "detail": "Credenciales de autenticación no proporcionadas."
}
```

### **Prohibido (403)**
```json
{
    "detail": "No tiene permiso para realizar esta acción."
}
```

### **Error del Servidor (500)**
```json
{
    "detail": "Error interno del servidor."
}
```

## 🔍 Filtros y Búsqueda

### **Filtros Disponibles**
- **Por especie:** `?especie=Maíz`
- **Por variedad:** `?variedad=Criollo`
- **Por estado:** `?estado=DISPONIBLE`
- **Por proveedor:** `?proveedor=AgroSemillas`
- **Por lote:** `?lote=MZ2025001`
- **Rango de fechas:** `?fecha_vencimiento_desde=2025-01-01&fecha_vencimiento_hasta=2025-12-31`
- **Rango de germinación:** `?pg_min=90&pg_max=100`

### **Búsqueda General**
```bash
GET /api/semillas/?search=maiz
```
Busca en: especie, variedad, lote, proveedor, observaciones

### **Ordenamiento**
```bash
GET /api/semillas/?ordering=especie,-fecha_vencimiento
```
Campos disponibles: especie, variedad, fecha_vencimiento, porcentaje_germinacion, cantidad, precio_unitario, creado_en, actualizado_en

## 📄 Paginación

La API utiliza paginación automática:

```json
{
    "count": 125,
    "next": "http://localhost:8000/api/semillas/?page=2",
    "previous": null,
    "results": [...]
}
```

**Parámetros:**
- `page`: Número de página (default: 1)
- `page_size`: Registros por página (default: 25, max: 100)

## 🧪 Ejemplos de Uso

### **Python - Requests**
```python
import requests

# Configurar headers
headers = {
    'Authorization': 'Token your-token-here',
    'Content-Type': 'application/json'
}

# Listar semillas
response = requests.get('http://localhost:8000/api/semillas/', headers=headers)
semillas = response.json()

# Crear nueva semilla
nueva_semilla = {
    "especie": "Soya",
    "variedad": "INTA",
    "cantidad": "100.00",
    "unidad_medida": "kg",
    "fecha_vencimiento": "2026-03-15",
    "porcentaje_germinacion": "88.50",
    "lote": "SO2025001",
    "proveedor": "Instituto Nacional",
    "precio_unitario": "35.00",
    "ubicacion_almacen": "Sector C-12"
}

response = requests.post(
    'http://localhost:8000/api/semillas/',
    json=nueva_semilla,
    headers=headers
)
```

### **JavaScript - Fetch**
```javascript
// Obtener token
const token = 'your-token-here';

// Headers comunes
const headers = {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
};

// Listar semillas con filtros
fetch('http://localhost:8000/api/semillas/?especie=Maíz&estado=DISPONIBLE', {
    headers: headers
})
.then(response => response.json())
.then(data => console.log(data));

// Crear semilla
const nuevaSemilla = {
    especie: "Girasol",
    variedad: "Alto Oleico",
    cantidad: "75.50",
    unidad_medida: "kg",
    fecha_vencimiento: "2026-08-20",
    porcentaje_germinacion: "91.20",
    lote: "GI2025003",
    proveedor: "Oleaginosas del Litoral",
    precio_unitario: "42.00",
    ubicacion_almacen": "Sector D-05"
};

fetch('http://localhost:8000/api/semillas/', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(nuevaSemilla)
})
.then(response => response.json())
.then(data => console.log(data));
```

### **cURL**
```bash
# Listar semillas
curl -H "Authorization: Token your-token-here" \
     http://localhost:8000/api/semillas/

# Crear semilla
curl -X POST \
     -H "Authorization: Token your-token-here" \
     -H "Content-Type: application/json" \
     -d '{
       "especie": "Cebada",
       "variedad": "Maltería",
       "cantidad": "300.00",
       "unidad_medida": "kg",
       "fecha_vencimiento": "2026-11-30",
       "porcentaje_germinacion": "89.70",
       "lote": "CE2025004",
       "proveedor": "Cervecería Nacional",
       "precio_unitario": "15.50",
       "ubicacion_almacen": "Sector E-18"
     }' \
     http://localhost:8000/api/semillas/
```

## 📊 Límites y Consideraciones

- **Rate Limiting:** 1000 requests por hora por usuario
- **Tamaño máximo de archivos:** No aplica (solo JSON)
- **Timeout:** 30 segundos por request
- **Encoding:** UTF-8 obligatorio
- **Fechas:** Formato ISO 8601 (YYYY-MM-DD)
- **Decimales:** Hasta 2 decimales para cantidades y precios

## 🔄 Versionado

- **Versión actual:** v1
- **Endpoint base:** `/api/v1/semillas/`
- **Compatibilidad:** Mantenida por 12 meses
- **Deprecaciones:** Anunciadas con 3 meses de antelación

## 📞 Soporte

- **Documentación:** Esta referencia completa
- **Issues:** GitHub del proyecto
- **Email:** api-support@cooperativa.com
- **Slack:** #api-semillas

---

**📅 Última actualización:** Octubre 2025  
**🔗 Versión:** 1.0.0  
**📧 Contacto:** desarrollo@cooperativa.com</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU7_CRUD_Semillas\API_Semillas.md