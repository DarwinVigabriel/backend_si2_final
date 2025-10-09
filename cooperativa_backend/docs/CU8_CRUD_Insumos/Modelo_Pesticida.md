# 🐛 Modelo de Datos - Pesticida

## 📋 Descripción General

El modelo **Pesticida** representa los productos fitosanitarios utilizados en la agricultura para el control de plagas, enfermedades y malezas. Implementa un sistema completo de inventario con control de calidad, trazabilidad y gestión económica.

## 🏗️ Estructura del Modelo

### **Definición de Clase**
```python
class Pesticida(models.Model):
    # Identificación y clasificación
    nombre_comercial = models.CharField(max_length=100)
    ingrediente_activo = models.CharField(max_length=100)
    tipo_pesticida = models.CharField(max_length=20, choices=TIPOS_PESTICIDA)

    # Composición y registro
    concentracion = models.CharField(max_length=50)
    registro_sanitario = models.CharField(max_length=50, blank=True)

    # Inventario y control
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=20)

    # Control de calidad
    fecha_vencimiento = models.DateField()
    dosis_recomendada = models.CharField(max_length=50, blank=True)

    # Trazabilidad
    lote = models.CharField(max_length=50, unique=True)
    proveedor = models.CharField(max_length=100)

    # Valor económico
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    # Ubicación y estado
    ubicacion_almacen = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS)
    observaciones = models.TextField(blank=True)

    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pesticida"
        verbose_name_plural = "Pesticidas"
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['estado', 'tipo_pesticida']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['proveedor']),
            models.Index(fields=['lote']),
        ]

    def __str__(self):
        return f"{self.nombre_comercial} - {self.lote}"

    # Métodos calculados
    def valor_total(self):
        """Calcula el valor total del inventario"""
        return self.cantidad * self.precio_unitario

    def dias_para_vencer(self):
        """Calcula días restantes para vencimiento"""
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - timezone.now().date()).days
        return None

    def esta_proximo_vencer(self, dias=30):
        """Verifica si vence en menos de X días"""
        dias_restantes = self.dias_para_vencer()
        return dias_restantes is not None and 0 <= dias_restantes <= dias

    def esta_vencido(self):
        """Verifica si ya venció"""
        dias_restantes = self.dias_para_vencer()
        return dias_restantes is not None and dias_restantes < 0
```

## 📊 Campos del Modelo

### **Campos de Identificación**

#### **nombre_comercial**
- **Tipo:** CharField (max_length=100)
- **Obligatorio:** Sí
- **Descripción:** Nombre comercial del producto fitosanitario
- **Ejemplos:** "Roundup", "Mancozeb 80%", "Chlorpyrifos 48%"
- **Validación:** No vacío, máximo 100 caracteres

#### **ingrediente_activo**
- **Tipo:** CharField (max_length=100)
- **Obligatorio:** Sí
- **Descripción:** Principio activo del pesticida
- **Ejemplos:** "Glifosato", "Mancozeb", "Clorpirifos"
- **Validación:** No vacío, máximo 100 caracteres

#### **tipo_pesticida**
- **Tipo:** CharField (max_length=20, choices=TIPOS_PESTICIDA)
- **Obligatorio:** Sí
- **Descripción:** Clasificación del tipo de pesticida
- **Opciones disponibles:**
  - `INSECTICIDA`: Control de insectos
  - `FUNGICIDA`: Control de hongos
  - `HERBICIDA`: Control de malezas
  - `ACARICIDA`: Control de ácaros
  - `NEMATICIDA`: Control de nematodos
  - `BACTERICIDA`: Control de bacterias
  - `VIRICIDA`: Control de virus
  - `RODENTICIDA`: Control de roedores
  - `MOLUSQUICIDA`: Control de moluscos
- **Validación:** Debe ser una de las opciones válidas

### **Campos de Composición**

#### **concentracion**
- **Tipo:** CharField (max_length=50)
- **Obligatorio:** Sí
- **Descripción:** Concentración del ingrediente activo
- **Ejemplos:** "48% EC", "80% WP", "200 g/L", "500 SC"
- **Formatos válidos:**
  - Porcentaje: "48% EC" (Emulsifiable Concentrate)
  - Peso/Peso: "80% WP" (Wettable Powder)
  - Peso/Volumen: "200 g/L" (gramos por litro)
  - Suspensión: "500 SC" (Suspension Concentrate)
- **Validación:** Formato específico con regex

#### **registro_sanitario**
- **Tipo:** CharField (max_length=50)
- **Obligatorio:** No (blank=True)
- **Descripción:** Número de registro sanitario del producto
- **Ejemplos:** "REG-001-2025", "SENASA-12345"
- **Validación:** Opcional, máximo 50 caracteres

### **Campos de Inventario**

#### **cantidad**
- **Tipo:** DecimalField (max_digits=10, decimal_places=2)
- **Obligatorio:** Sí
- **Descripción:** Cantidad disponible en inventario
- **Rango válido:** 0.01 - 99999999.99
- **Unidades:** Según unidad_medida
- **Validación:** Mayor que 0, máximo 2 decimales

#### **unidad_medida**
- **Tipo:** CharField (max_length=20)
- **Obligatorio:** Sí
- **Descripción:** Unidad de medida del producto
- **Opciones comunes:**
  - "Litros" (L)
  - "Kilogramos" (kg)
  - "Gramos" (g)
  - "Mililitros" (ml)
  - "Toneladas" (t)
- **Validación:** No vacío, máximo 20 caracteres

### **Campos de Control de Calidad**

#### **fecha_vencimiento**
- **Tipo:** DateField
- **Obligatorio:** Sí
- **Descripción:** Fecha límite de uso del producto
- **Formato:** YYYY-MM-DD
- **Validación:** No puede ser fecha pasada, debe ser futura
- **Importancia:** Crítica para seguridad agrícola

#### **dosis_recomendada**
- **Tipo:** CharField (max_length=50)
- **Obligatorio:** No (blank=True)
- **Descripción:** Dosis recomendada de aplicación
- **Ejemplos:** "2-3 L/ha", "1-2 kg/ha", "100-200 ml/hL"
- **Validación:** Opcional, máximo 50 caracteres

### **Campos de Trazabilidad**

#### **lote**
- **Tipo:** CharField (max_length=50, unique=True)
- **Obligatorio:** Sí
- **Descripción:** Número de lote del fabricante
- **Ejemplos:** "LOT-2025-001", "LOTE-A-2025", "BATCH-12345"
- **Validación:** Único en el sistema, no vacío
- **Importancia:** Trazabilidad completa del producto

#### **proveedor**
- **Tipo:** CharField (max_length=100)
- **Obligatorio:** Sí
- **Descripción:** Nombre del proveedor o fabricante
- **Ejemplos:** "AgroQuímica SA", "Bayer CropScience", "Syngenta"
- **Validación:** No vacío, máximo 100 caracteres

### **Campos Económicos**

#### **precio_unitario**
- **Tipo:** DecimalField (max_digits=10, decimal_places=2)
- **Obligatorio:** Sí
- **Descripción:** Precio por unidad del producto
- **Rango válido:** 0.01 - 99999999.99
- **Moneda:** Pesos argentinos (ARS)
- **Validación:** Mayor que 0, máximo 2 decimales

### **Campos Operativos**

#### **ubicacion_almacen**
- **Tipo:** CharField (max_length=100)
- **Obligatorio:** Sí
- **Descripción:** Ubicación física en el almacén
- **Ejemplos:** "Sector A-15", "Estante 3-F", "Depósito Principal"
- **Validación:** No vacío, máximo 100 caracteres

#### **estado**
- **Tipo:** CharField (max_length=20, choices=ESTADOS)
- **Obligatorio:** Sí
- **Descripción:** Estado actual del producto en inventario
- **Opciones disponibles:**
  - `DISPONIBLE`: Producto disponible para uso
  - `AGOTADO`: Producto sin stock disponible
  - `VENCIDO`: Producto fuera de fecha de vencimiento
  - `EN_TRANSITO`: Producto en camino desde proveedor
  - `EN_USO`: Producto actualmente en uso en parcelas
  - `RESERVADO`: Producto reservado para uso específico
  - `RETIRADO`: Producto retirado del mercado
  - `EN_REVISION`: Producto en proceso de revisión
- **Validación:** Debe ser una de las opciones válidas

#### **observaciones**
- **Tipo:** TextField
- **Obligatorio:** No (blank=True)
- **Descripción:** Notas adicionales sobre el producto
- **Ejemplos:** "Producto nuevo", "Revisar caducidad", "Daño en empaque"
- **Validación:** Campo opcional, texto libre

### **Campos de Auditoría**

#### **creado_en**
- **Tipo:** DateTimeField (auto_now_add=True)
- **Obligatorio:** Automático
- **Descripción:** Fecha y hora de creación del registro

#### **actualizado_en**
- **Tipo:** DateTimeField (auto_now=True)
- **Obligatorio:** Automático
- **Descripción:** Fecha y hora de última actualización

## 🔧 Métodos del Modelo

### **Métodos Calculados**

#### **valor_total()**
```python
def valor_total(self):
    """Calcula el valor total del inventario"""
    return self.cantidad * self.precio_unitario
```
- **Retorno:** Decimal - Valor total en pesos
- **Uso:** Cálculo automático del valor económico
- **Ejemplo:** cantidad=100, precio_unitario=45.50 → 4550.00

#### **dias_para_vencer()**
```python
def dias_para_vencer(self):
    """Calcula días restantes para vencimiento"""
    if self.fecha_vencimiento:
        return (self.fecha_vencimiento - timezone.now().date()).days
    return None
```
- **Retorno:** Integer o None - Días restantes
- **Uso:** Control de proximidad al vencimiento
- **Ejemplo:** fecha_vencimiento=2025-12-31, hoy=2025-10-01 → 91 días

#### **esta_proximo_vencer(dias=30)**
```python
def esta_proximo_vencer(self, dias=30):
    """Verifica si vence en menos de X días"""
    dias_restantes = self.dias_para_vencer()
    return dias_restantes is not None and 0 <= dias_restantes <= dias
```
- **Parámetros:** dias (int, default=30) - Umbral en días
- **Retorno:** Boolean - True si vence pronto
- **Uso:** Alertas de vencimiento próximo

#### **esta_vencido()**
```python
def esta_vencido(self):
    """Verifica si ya venció"""
    dias_restantes = self.dias_para_vencer()
    return dias_restantes is not None and dias_restantes < 0
```
- **Retorno:** Boolean - True si ya venció
- **Uso:** Identificación de productos caducados

### **Método de Representación**

#### **__str__()**
```python
def __str__(self):
    return f"{self.nombre_comercial} - {self.lote}"
```
- **Retorno:** String - Representación legible del objeto
- **Uso:** Display en admin, logs, etc.
- **Ejemplo:** "Roundup - LOT-2025-001"

## 🎯 Constantes y Choices

### **TIPOS_PESTICIDA**
```python
TIPOS_PESTICIDA = [
    ('INSECTICIDA', 'Insecticida'),
    ('FUNGICIDA', 'Fungicida'),
    ('HERBICIDA', 'Herbicida'),
    ('ACARICIDA', 'Acaricida'),
    ('NEMATICIDA', 'Nematicida'),
    ('BACTERICIDA', 'Bactericida'),
    ('VIRICIDA', 'Vírícida'),
    ('RODENTICIDA', 'Rodenticida'),
    ('MOLUSQUICIDA', 'Molusquicida'),
]
```

### **ESTADOS**
```python
ESTADOS = [
    ('DISPONIBLE', 'Disponible'),
    ('AGOTADO', 'Agotado'),
    ('VENCIDO', 'Vencido'),
    ('EN_TRANSITO', 'En Tránsito'),
    ('EN_USO', 'En Uso'),
    ('RESERVADO', 'Reservado'),
    ('RETIRADO', 'Retirado'),
    ('EN_REVISION', 'En Revisión'),
]
```

## 📊 Índices de Base de Datos

### **Índices Optimizados**
```python
indexes = [
    models.Index(fields=['estado', 'tipo_pesticida']),
    models.Index(fields=['fecha_vencimiento']),
    models.Index(fields=['proveedor']),
    models.Index(fields=['lote']),
]
```

### **Justificación de Índices**
- **estado + tipo_pesticida:** Consultas por estado y tipo
- **fecha_vencimiento:** Ordenamiento y filtros por fecha
- **proveedor:** Agrupación por proveedor
- **lote:** Búsqueda rápida por lote (único)

## 🔍 Validaciones Personalizadas

### **Validación de Concentración**
```python
def validate_concentracion(value):
    """Valida el formato de concentración"""
    import re
    if not re.match(r'^[0-9\.\,\s\%\-\(\)a-zA-Z]+$', value):
        raise ValidationError('Formato de concentración inválido')
```

### **Validación de Fecha de Vencimiento**
```python
def validate_fecha_vencimiento(value):
    """Valida que la fecha de vencimiento no sea pasada"""
    if value <= timezone.now().date():
        raise ValidationError('La fecha de vencimiento debe ser futura')
```

## 📋 Meta Configuración

### **Configuración de Modelo**
```python
class Meta:
    verbose_name = "Pesticida"
    verbose_name_plural = "Pesticidas"
    ordering = ['-creado_en']  # Más recientes primero
    indexes = [...]  # Índices definidos arriba
```

## 🔄 Relaciones y Dependencias

### **Dependencias Externas**
- **Django Core:** models, timezone, ValidationError
- **Python:** datetime, decimal

### **Relaciones Futuras**
- **Usuario:** Quién creó/actualizó el registro
- **Movimientos:** Historial de entradas/salidas
- **Aplicaciones:** Registros de uso en parcelas

## 📊 Ejemplos de Uso

### **Creación de Instancia**
```python
pesticida = Pesticida.objects.create(
    nombre_comercial="Mancozeb 80%",
    ingrediente_activo="Mancozeb",
    tipo_pesticida="FUNGICIDA",
    concentracion="80% WP",
    registro_sanitario="REG-001-2025",
    cantidad=100.00,
    unidad_medida="Kilogramos",
    fecha_vencimiento=date(2026, 12, 31),
    dosis_recomendada="2-3 kg/ha",
    lote="LOT-2025-001",
    proveedor="AgroQuímica SA",
    precio_unitario=35.50,
    ubicacion_almacen="Sector A-15",
    estado="DISPONIBLE",
    observaciones="Producto certificado"
)
```

### **Consultas Comunes**
```python
# Pesticidas disponibles
disponibles = Pesticida.objects.filter(estado='DISPONIBLE')

# Pesticidas próximos a vencer
proximos = Pesticida.objects.filter(
    fecha_vencimiento__lte=date.today() + timedelta(days=30),
    estado='DISPONIBLE'
)

# Valor total del inventario
valor_total = sum(p.valor_total() for p in Pesticida.objects.all())

# Pesticidas por tipo
por_tipo = Pesticida.objects.values('tipo_pesticida').annotate(
    total=models.Count('id'),
    valor=models.Sum(models.F('cantidad') * models.F('precio_unitario'))
)
```

## 🚨 Consideraciones Especiales

### **Campos Críticos**
- **fecha_vencimiento:** Nunca debe ser modificada manualmente sin validación
- **lote:** Garantiza unicidad para trazabilidad
- **cantidad:** Debe actualizarse solo a través de métodos controlados

### **Reglas de Negocio**
- No se puede usar producto vencido
- Lote único por producto
- Precio unitario siempre positivo
- Cantidad nunca negativa

### **Seguridad**
- Validar permisos para modificación
- Auditar cambios en campos críticos
- Backup regular de datos de inventario

## 📈 Métricas y KPIs

### **Métricas del Modelo**
- **Total de Pesticidas:** Conteo total de registros
- **Valor del Inventario:** Suma de valor_total()
- **Productos Vencidos:** Conteo de esta_vencido() = True
- **Próximos a Vencer:** Conteo de esta_proximo_vencer() = True
- **Distribución por Tipo:** Agrupación por tipo_pesticida

### **Alertas Automáticas**
- Productos vencidos (diariamente)
- Productos próximos a vencer (semanalmente)
- Stock bajo (por tipo de producto)

## 🔧 Mantenimiento

### **Tareas de Mantenimiento**
- **Diario:** Verificar productos vencidos
- **Semanal:** Revisar próximos a vencer
- **Mensual:** Actualizar precios y proveedores
- **Anual:** Auditoría completa de inventario

### **Backup y Recuperación**
- Backup diario de tabla
- Logs de cambios para auditoría
- Procedimientos de recuperación de datos

---

**📅 Última actualización:** Diciembre 2024  
**🔍 Modelo:** Pesticida  
**📊 Versión:** 1.1.0  
**✅ Estado:** Actualizado con nuevos estados de inventario

### **📝 Cambios Recientes (v1.1.0)**
- **Estados expandidos:** Agregados EN_TRANSITO, EN_USO, RESERVADO para mejor control de inventario
- **Validaciones:** Mejoradas para mayor flexibilidad operativa</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU8_CRUD_Insumos\Modelo_Pesticida.md