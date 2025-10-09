# 🌱 CU7: Gestión de Semillas - Inventario Agrícola

## 📋 Descripción General

El **Caso de Uso CU7** implementa el sistema completo de gestión de semillas para el inventario agrícola de la Cooperativa. Este CU proporciona funcionalidades avanzadas para el control de inventario de semillas, incluyendo catálogo de especies, seguimiento de lotes, control de vencimiento, y gestión completa del ciclo de vida de las semillas.

## 🎯 Objetivos del Caso de Uso

- ✅ **Catálogo de Inventario:** Sistema completo para gestión de semillas
- ✅ **Control de Vencimiento:** Alertas automáticas y seguimiento de fechas
- ✅ **Gestión de Lotes:** Trazabilidad completa por lote y proveedor
- ✅ **CRUD Completo:** Operaciones completas de creación, lectura, actualización y eliminación
- ✅ **Reportes Avanzados:** Análisis y estadísticas del inventario
- ✅ **Interfaz Administrativa:** Django Admin integrado y optimizado

## 📊 Alcance y Funcionalidades

### **Funcionalidades Principales**
1. **Catálogo de Semillas** - Inventario completo con especies y variedades
2. **Control de Lotes** - Trazabilidad por lote, proveedor y fecha de ingreso
3. **Gestión de Vencimiento** - Alertas automáticas y control de caducidad
4. **CRUD de Semillas** - Operaciones completas con validaciones
5. **Reportes de Inventario** - Estadísticas y análisis del stock
6. **Interfaz de Administración** - Django Admin personalizado

### **Características Técnicas**
- **Backend:** Django REST Framework + PostgreSQL
- **Modelo:** Semilla con campos completos y métodos calculados
- **Validaciones:** Reglas de negocio específicas para semillas
- **Auditoría:** Registro automático de todas las operaciones
- **API REST:** Endpoints completos con filtros y búsqueda

## 🏗️ Arquitectura del Sistema

### **Componentes Principales**

```
CU7_CRUD_Semillas/
├── Backend (Django)
│   ├── Model: Semilla con métodos calculados
│   ├── ViewSet: SemillaViewSet con acciones personalizadas
│   ├── Serializer: SemillaSerializer con validaciones
│   ├── Admin: SemillaAdmin con filtros y exportación
│   └── URLs: Rutas REST completas
├── Base de Datos
│   ├── Tabla: cooperativa_semilla
│   ├── Índices: Optimizados para búsquedas
│   └── Constraints: Validaciones a nivel BD
└── API Endpoints
    ├── CRUD: /api/semillas/
    ├── Filtros: Búsqueda avanzada
    ├── Acciones: Inventario, alertas, reportes
    └── Estadísticas: Métricas calculadas
```

### **Modelo de Datos Semilla**

```python
class Semilla(models.Model):
    # Identificación
    especie = models.CharField(max_length=100)
    variedad = models.CharField(max_length=100)

    # Inventario
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=20)

    # Control de calidad
    fecha_vencimiento = models.DateField()
    porcentaje_germinacion = models.DecimalField(max_digits=5, decimal_places=2)

    # Trazabilidad
    lote = models.CharField(max_length=50)
    proveedor = models.CharField(max_length=100)

    # Valor económico
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    # Ubicación y estado
    ubicacion_almacen = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS)
    observaciones = models.TextField(blank=True)
```

## 📋 Tareas Implementadas

### **T-40: Catálogo de Inventario de Semillas**
- ✅ **Modelo Semilla Completo** con todos los campos requeridos
- ✅ **Validaciones de Negocio** específicas para semillas
- ✅ **Métodos Calculados** (valor_total, días_para_vencer, etc.)
- ✅ **Estados de Semilla** (DISPONIBLE, AGOTADA, VENCIDA, etc.)
- ✅ **Relaciones y Constraints** apropiadas
- ✅ **Índices de Base de Datos** optimizados

### **T-41: CRUD de Semillas**
- ✅ **Create:** Creación con validaciones completas
- ✅ **Read:** Consulta con filtros y búsqueda avanzada
- ✅ **Update:** Actualización con control de cambios
- ✅ **Delete:** Eliminación con auditoría
- ✅ **API RESTful** completa con Django REST Framework
- ✅ **Serializers** con validaciones específicas
- ✅ **ViewSet** con acciones personalizadas

## 🔍 Funcionalidades Avanzadas

### **Control de Vencimiento**
```python
def dias_para_vencer(self):
    """Calcula días restantes para vencimiento"""
    if self.fecha_vencimiento:
        return (self.fecha_vencimiento - timezone.now().date()).days
    return None

def esta_proxima_vencer(self):
    """Verifica si vence en menos de 30 días"""
    dias = self.dias_para_vencer()
    return dias is not None and 0 <= dias <= 30

def esta_vencida(self):
    """Verifica si la semilla ya venció"""
    dias = self.dias_para_vencer()
    return dias is not None and dias < 0
```

### **Cálculos Automáticos**
```python
def valor_total(self):
    """Calcula el valor total del inventario"""
    if self.precio_unitario and self.cantidad:
        return self.precio_unitario * self.cantidad
    return 0
```

### **Validaciones de Negocio**
- **Porcentaje de Germinación:** 0-100%
- **Cantidad:** No negativa
- **Precio Unitario:** No negativo
- **Fecha de Vencimiento:** No en el pasado para nuevas semillas
- **Estado vs Cantidad:** Si agotada, cantidad debe ser 0

## 📊 API Endpoints

### **Endpoints Principales**
```
GET    /api/semillas/           # Listar semillas con filtros
POST   /api/semillas/           # Crear nueva semilla
GET    /api/semillas/{id}/      # Detalle de semilla
PUT    /api/semillas/{id}/      # Actualizar semilla
DELETE /api/semillas/{id}/      # Eliminar semilla
```

### **Endpoints Avanzados**
```
GET    /api/semillas/inventario_bajo/     # Semillas con stock bajo
GET    /api/semillas/proximas_vencer/     # Semillas próximas a vencer
GET    /api/semillas/vencidas/            # Semillas vencidas
POST   /api/semillas/{id}/actualizar_cantidad/  # Actualizar stock
POST   /api/semillas/{id}/marcar_vencida/       # Marcar como vencida
GET    /api/semillas/reporte_inventario/        # Reporte completo
```

### **Filtros Disponibles**
- `especie`: Filtrar por especie
- `variedad`: Filtrar por variedad
- `estado`: Filtrar por estado
- `proveedor`: Filtrar por proveedor
- `lote`: Filtrar por lote
- `fecha_vencimiento_desde/hasta`: Rango de fechas
- `pg_min/pg_max`: Rango de porcentaje de germinación

## 🎛️ Interfaz de Administración

### **SemillaAdmin Configurado**
```python
class SemillaAdmin(admin.ModelAdmin):
    list_display = ['especie', 'variedad', 'cantidad', 'estado', 'fecha_vencimiento', 'valor_total']
    list_filter = ['estado', 'especie', 'proveedor', 'fecha_vencimiento']
    search_fields = ['especie', 'variedad', 'lote', 'proveedor']
    readonly_fields = ['creado_en', 'actualizado_en']
    actions = [exportar_csv]
```

### **Características del Admin**
- **Lista Optimizada:** Campos importantes visibles
- **Filtros Avanzados:** Por estado, especie, proveedor, fechas
- **Búsqueda Global:** En especie, variedad, lote, proveedor
- **Campos de Solo Lectura:** Timestamps automáticos
- **Acciones Masivas:** Exportar a CSV
- **Paginación:** 25 registros por página

## 📈 Reportes y Estadísticas

### **Métricas Calculadas**
- **Valor Total del Inventario**
- **Semillas Próximas a Vencer** (< 30 días)
- **Semillas Vencidas**
- **Stock Bajo** (configurable)
- **Distribución por Especie**
- **Distribución por Proveedor**

### **Reportes Disponibles**
- **Inventario Completo:** Estado actual de todas las semillas
- **Alertas de Vencimiento:** Semillas que requieren atención
- **Análisis de Stock:** Tendencias y patrones de consumo
- **Proveedores:** Rendimiento y calidad por proveedor

## 🔒 Seguridad y Validaciones

### **Validaciones Implementadas**
```python
def validate_porcentaje_germinacion(self, value):
    if value < 0 or value > 100:
        raise ValidationError('El porcentaje debe estar entre 0 y 100')

def validate_fecha_vencimiento(self, value):
    if value and value < timezone.now().date():
        raise ValidationError('La fecha no puede ser en el pasado')
```

### **Auditoría Automática**
- **Registro de Creación:** Usuario y timestamp
- **Registro de Actualización:** Usuario y timestamp
- **Registro de Eliminación:** Usuario y detalles
- **Bitácora de Cambios:** Historial completo

## 🧪 Testing y Calidad

### **Casos de Prueba**
- ✅ **Creación de Semillas** con datos válidos
- ✅ **Validaciones de Campos** obligatorios y opcionales
- ✅ **Cálculos Automáticos** (valor_total, vencimiento)
- ✅ **Filtros y Búsqueda** avanzada
- ✅ **Operaciones CRUD** completas
- ✅ **Estados de Semilla** y transiciones
- ✅ **API Endpoints** con diferentes parámetros

### **Cobertura de Tests**
- **Model:** Validaciones y métodos calculados
- **Serializer:** Validaciones de entrada/salida
- **ViewSet:** Endpoints y lógica de negocio
- **Admin:** Interfaz de administración
- **API:** Integración completa

## 📊 Estado de Implementación

| Componente | Estado | Validación |
|------------|--------|------------|
| Modelo Semilla | ✅ Completo | ✅ Probado |
| Serializer | ✅ Completo | ✅ Probado |
| ViewSet | ✅ Completo | ✅ Probado |
| Admin Interface | ✅ Completo | ✅ Probado |
| URLs y Routing | ✅ Completo | ✅ Probado |
| Base de Datos | ✅ Migrado | ✅ Verificado |
| API Endpoints | ✅ Funcional | ✅ Probado |
| Documentación | ✅ Completa | ✅ Revisada |

## 📚 Documentación Técnica

### **Archivos de Documentación**
- **README.md** - Documentación general del CU7
- **API_Semillas.md** - Referencia completa de la API
- **Modelo_Semilla.md** - Especificación del modelo de datos
- **Validaciones_Semilla.md** - Reglas de validación implementadas

### **Referencias de Código**
- **models.py:** Definición del modelo Semilla
- **serializers.py:** SemillaSerializer con validaciones
- **views.py:** SemillaViewSet con acciones personalizadas
- **admin.py:** Configuración del admin para semillas
- **urls.py:** Rutas de la API de semillas

## 🚀 Próximos Pasos

### **Mejoras Planificadas**
- 🔄 **Códigos de Barras:** Integración con lectores
- 🔄 **Alertas Automáticas:** Notificaciones por email/SMS
- 🔄 **Integración con Compras:** Automatización de pedidos
- 🔄 **Análisis Predictivo:** Pronósticos de demanda
- 🔄 **App Móvil:** Gestión móvil del inventario

### **Mantenimiento**
- 📅 **Revisiones de Stock:** Semanales
- 📅 **Verificación de Vencimientos:** Diaria
- 📅 **Backup de Datos:** Diario
- 📅 **Actualización de Precios:** Mensual

## 👥 Equipo Responsable

- **Desarrollo Backend:** Equipo Django
- **Análisis de Negocio:** Equipo Agrícola
- **Testing:** Equipo QA
- **Documentación:** Equipo Técnico

## 📞 Soporte y Contacto

- **Issues:** GitHub Issues del proyecto
- **Documentación:** Wiki del proyecto
- **Soporte:** admin@cooperativa.com

---

**📅 Fecha de implementación:** Octubre 2025  
**🌱 Tipo:** Gestión de Inventario Agrícola  
**📊 Complejidad:** Media-Alta  
**✅ Estado:** Completo y operativo  
**🚀 Readiness:** Production Ready</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU7_CRUD_Semillas\README.md