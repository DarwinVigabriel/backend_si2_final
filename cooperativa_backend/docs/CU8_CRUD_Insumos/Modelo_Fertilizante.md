# 🌱 Modelo de Datos - Fertilizante

## 📋 Descripción General

El modelo **Fertilizante** representa los productos utilizados para mejorar la fertilidad del suelo y proporcionar nutrientes esenciales a los cultivos. Implementa un sistema completo de inventario con análisis de composición NPK, control de calidad y gestión económica.

## 🏗️ Estructura del Modelo

### **Definición de Clase**
```python
class Fertilizante(models.Model):
    # Identificación y clasificación
    nombre_comercial = models.CharField(max_length=100)
    tipo_fertilizante = models.CharField(max_length=20, choices=TIPOS_FERTILIZANTE)
    composicion_npk = models.CharField(max_length=20)

    # Inventario y control
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=20)

    # Control de calidad
    fecha_vencimiento = models.DateField(blank=True, null=True)
    dosis_recomendada = models.CharField(max_length=50, blank=True)
    materia_orgánica = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

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
        verbose_name = "Fertilizante"
        verbose_name_plural = "Fertilizantes"
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['estado', 'tipo_fertilizante']),
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

    def get_npk_values(self):
        """Extrae valores N, P, K de la composición"""
        try:
            partes = self.composicion_npk.split('-')
            n = int(partes[0]) if partes[0] != '' else 0
            p = int(partes[1]) if partes[1] != '' else 0
            k = int(partes[2].split('+')[0]) if partes[2] != '' else 0
            return {'N': n, 'P': p, 'K': k}
        except (ValueError, IndexError):
            return None
```

## 📊 Campos del Modelo

### **Campos de Identificación**

#### **nombre_comercial**
- **Tipo:** CharField (max_length=100)
- **Obligatorio:** Sí
- **Descripción:** Nombre comercial del fertilizante
- **Ejemplos:** "Urea 46%", "NPK 15-15-15", "Superfosfato Triple"
- **Validación:** No vacío, máximo 100 caracteres

#### **tipo_fertilizante**
- **Tipo:** CharField (max_length=20, choices=TIPOS_FERTILIZANTE)
- **Obligatorio:** Sí
- **Descripción:** Clasificación del tipo de fertilizante
- **Opciones disponibles:**
  - `QUIMICO`: Fertilizantes químicos sintéticos
  - `ORGANICO`: Fertilizantes de origen orgánico
  - `MINERAL`: Fertilizantes minerales naturales
  - `COMPUESTO`: Fertilizantes con múltiples nutrientes
  - `ESPECIALIZADO`: Fertilizantes para cultivos específicos
- **Validación:** Debe ser una de las opciones válidas

#### **composicion_npk**
- **Tipo:** CharField (max_length=20)
- **Obligatorio:** Sí
- **Descripción:** Composición de nutrientes N-P-K
- **Formato:** N-P-K (ej: 15-15-15, 20-10-10, 10-5-20)
- **Ejemplos:** "15-15-15", "20-10-10", "10-5-20+TE"
- **Validación:** Formato específico N-P-K con números separados por guiones

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
  - "Kilogramos" (kg)
  - "Toneladas" (t)
  - "Litros" (L)
  - "Gramos" (g)
  - "Bolsas de 50kg"
- **Validación:** No vacío, máximo 20 caracteres

### **Campos de Control de Calidad**

#### **fecha_vencimiento**
- **Tipo:** DateField
- **Obligatorio:** No (blank=True, null=True)
- **Descripción:** Fecha límite de uso del fertilizante
- **Formato:** YYYY-MM-DD
- **Nota:** Algunos fertilizantes no tienen vencimiento definido
- **Validación:** Si se proporciona, debe ser futura

#### **dosis_recomendada**
- **Tipo:** CharField (max_length=50)
- **Obligatorio:** No (blank=True)
- **Descripción:** Dosis recomendada de aplicación
- **Ejemplos:** "200-300 kg/ha", "100-150 kg/ha", "50-100 L/ha"
- **Validación:** Opcional, máximo 50 caracteres

#### **materia_orgánica**
- **Tipo:** DecimalField (max_digits=5, decimal_places=2)
- **Obligatorio:** No (blank=True, null=True)
- **Descripción:** Porcentaje de materia orgánica
- **Rango válido:** 0.01 - 100.00
- **Unidad:** Porcentaje (%)
- **Nota:** Solo aplicable a fertilizantes orgánicos

### **Campos de Trazabilidad**

#### **lote**
- **Tipo:** CharField (max_length=50, unique=True)
- **Obligatorio:** Sí
- **Descripción:** Número de lote del fabricante
- **Ejemplos:** "LOT-F-2025-001", "LOTE-NPK-2025", "BATCH-FERT-12345"
- **Validación:** Único en el sistema, no vacío
- **Importancia:** Trazabilidad completa del producto

#### **proveedor**
- **Tipo:** CharField (max_length=100)
- **Obligatorio:** Sí
- **Descripción:** Nombre del proveedor o fabricante
- **Ejemplos:** "NutriAgro SA", "Fertilizantes del Sur", "Yara International"
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
- **Ejemplos:** "Sector B-10", "Área Fertilizantes", "Depósito Norte"
- **Validación:** No vacío, máximo 100 caracteres

#### **estado**
- **Tipo:** CharField (max_length=20, choices=ESTADOS)
- **Obligatorio:** Sí
- **Descripción:** Estado actual del producto en inventario
- **Opciones disponibles:**
  - `DISPONIBLE`: Producto disponible para uso
  - `AGOTADO`: Producto sin stock disponible
  - `VENCIDO`: Producto fuera de fecha de vencimiento
  - `RETIRADO`: Producto retirado del mercado
  - `EN_REVISION`: Producto en proceso de revisión
- **Validación:** Debe ser una de las opciones válidas

#### **observaciones**
- **Tipo:** TextField
- **Obligatorio:** No (blank=True)
- **Descripción:** Notas adicionales sobre el producto
- **Ejemplos:** "Alta calidad", "Buen rendimiento", "Problemas de humedad"
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
- **Ejemplo:** cantidad=500, precio_unitario=25.50 → 12750.00

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
- **Nota:** Puede retornar None si no tiene fecha de vencimiento

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

#### **get_npk_values()**
```python
def get_npk_values(self):
    """Extrae valores N, P, K de la composición"""
    try:
        partes = self.composicion_npk.split('-')
        n = int(partes[0]) if partes[0] != '' else 0
        p = int(partes[1]) if partes[1] != '' else 0
        k = int(partes[2].split('+')[0]) if partes[2] != '' else 0
        return {'N': n, 'P': p, 'K': k}
    except (ValueError, IndexError):
        return None
```
- **Retorno:** Dict o None - Valores N, P, K
- **Uso:** Análisis de composición nutricional
- **Ejemplo:** "15-15-15" → {'N': 15, 'P': 15, 'K': 15}

### **Método de Representación**

#### **__str__()**
```python
def __str__(self):
    return f"{self.nombre_comercial} - {self.lote}"
```
- **Retorno:** String - Representación legible del objeto
- **Uso:** Display en admin, logs, etc.
- **Ejemplo:** "NPK 15-15-15 - LOT-F-2025-001"

## 🎯 Constantes y Choices

### **TIPOS_FERTILIZANTE**
```python
TIPOS_FERTILIZANTE = [
    ('QUIMICO', 'Químico'),
    ('ORGANICO', 'Orgánico'),
    ('MINERAL', 'Mineral'),
    ('UREA', 'Urea'),
    ('NPK_COMPLEJO', 'NPK Complejo'),
    ('FOSFATO', 'Fosfato'),
    ('POTASIO', 'Potasio'),
    ('CALCIO', 'Calcio'),
    ('MAGNESIO', 'Magnesio'),
    ('MICRONUTRIENTES', 'Micronutrientes'),
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
    models.Index(fields=['estado', 'tipo_fertilizante']),
    models.Index(fields=['fecha_vencimiento']),
    models.Index(fields=['proveedor']),
    models.Index(fields=['lote']),
]
```

### **Justificación de Índices**
- **estado + tipo_fertilizante:** Consultas por estado y tipo
- **fecha_vencimiento:** Ordenamiento y filtros por fecha
- **proveedor:** Agrupación por proveedor
- **lote:** Búsqueda rápida por lote (único)

## 🔍 Validaciones Personalizadas

### **Validación de Composición NPK**
```python
def validate_composicion_npk(value):
    """Valida el formato N-P-K"""
    import re
    if not re.match(r'^[0-9\-]+(\+[A-Za-z]+)?$', value):
        raise ValidationError('Formato NPK inválido. Use formato N-P-K (ej: 10-10-10)')
```

### **Validación de Materia Orgánica**
```python
def validate_materia_organica(value):
    """Valida el porcentaje de materia orgánica"""
    if value is not None and (value < 0 or value > 100):
        raise ValidationError('La materia orgánica debe estar entre 0 y 100')
```

## 📋 Meta Configuración

### **Configuración de Modelo**
```python
class Meta:
    verbose_name = "Fertilizante"
    verbose_name_plural = "Fertilizantes"
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
fertilizante = Fertilizante.objects.create(
    nombre_comercial="NPK 15-15-15",
    tipo_fertilizante="COMPUESTO",
    composicion_npk="15-15-15",
    cantidad=500.00,
    unidad_medida="Kilogramos",
    fecha_vencimiento=date(2026, 12, 31),
    dosis_recomendada="200-300 kg/ha",
    materia_orgánica=None,
    lote="LOT-F-2025-001",
    proveedor="NutriAgro SA",
    precio_unitario=25.50,
    ubicacion_almacen="Sector B-10",
    estado="DISPONIBLE",
    observaciones="Fertilizante balanceado de alta calidad"
)
```

### **Consultas Comunes**
```python
# Fertilizantes disponibles
disponibles = Fertilizante.objects.filter(estado='DISPONIBLE')

# Fertilizantes orgánicos
organicos = Fertilizante.objects.filter(tipo_fertilizante='ORGANICO')

# Fertilizantes con alto contenido de nitrógeno
alto_n = Fertilizante.objects.filter(
    composicion_npk__startswith='20-'
)

# Valor total del inventario
valor_total = sum(f.valor_total() for f in Fertilizante.objects.all())

# Fertilizantes por tipo con NPK promedio
por_tipo = Fertilizante.objects.values('tipo_fertilizante').annotate(
    total=models.Count('id'),
    valor=models.Sum(models.F('cantidad') * models.F('precio_unitario'))
)
```

## 🚨 Consideraciones Especiales

### **Campos Críticos**
- **composicion_npk:** Formato estricto para análisis nutricional
- **lote:** Garantiza unicidad para trazabilidad
- **fecha_vencimiento:** Opcional para algunos fertilizantes

### **Reglas de Negocio**
- Fertilizantes orgánicos pueden no tener fecha de vencimiento
- Composición NPK debe seguir formato estándar
- Materia orgánica solo para fertilizantes orgánicos

### **Seguridad**
- Validar permisos para modificación
- Auditar cambios en composición NPK
- Backup regular de datos de inventario

## 📈 Métricas y KPIs

### **Métricas del Modelo**
- **Total de Fertilizantes:** Conteo total de registros
- **Valor del Inventario:** Suma de valor_total()
- **Productos Vencidos:** Conteo de esta_vencido() = True
- **Distribución por Tipo:** Agrupación por tipo_fertilizante
- **Análisis NPK:** Promedios de composición por tipo

### **Alertas Automáticas**
- Productos vencidos (diariamente)
- Productos próximos a vencer (semanalmente)
- Stock bajo por tipo de fertilizante

## 🔧 Mantenimiento

### **Tareas de Mantenimiento**
- **Diario:** Verificar productos vencidos
- **Semanal:** Revisar próximos a vencer
- **Mensual:** Actualizar precios y proveedores
- **Trimestral:** Análisis de composición NPK promedio

### **Backup y Recuperación**
- Backup diario de tabla
- Logs de cambios para auditoría
- Procedimientos de recuperación de datos

---

**📅 Última actualización:** Diciembre 2024  
**🔍 Modelo:** Fertilizante  
**📊 Versión:** 1.1.0  
**✅ Estado:** Actualizado con tipos expandidos y nuevos estados

### **📝 Cambios Recientes (v1.1.0)**
- **Tipos expandidos:** Agregados UREA, NPK_COMPLEJO, FOSFATO, POTASIO, CALCIO, MAGNESIO, MICRONUTRIENTES
- **Estados expandidos:** Agregados EN_TRANSITO, EN_USO, RESERVADO para mejor control operativo
- **Validaciones:** Mejoradas para mayor precisión en clasificación de fertilizantes</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU8_CRUD_Insumos\Modelo_Fertilizante.md