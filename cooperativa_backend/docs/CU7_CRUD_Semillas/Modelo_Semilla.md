# 🌱 Modelo de Datos - Semilla

## 📋 Información General

El modelo **Semilla** representa una entidad completa para la gestión del inventario de semillas en el sistema de la Cooperativa. Incluye campos para identificación, control de inventario, trazabilidad, control de calidad y gestión económica.

**Tabla:** `cooperativa_semilla`  
**Aplicación:** `cooperativa`  
**Herencia:** `models.Model` (Django estándar)

## 🏗️ Estructura del Modelo

### **Campos del Modelo**

```python
class Semilla(models.Model):
    # === IDENTIFICACIÓN ===
    especie = models.CharField(
        max_length=100,
        verbose_name="Especie",
        help_text="Especie de la semilla (ej: Maíz, Trigo, Soya)"
    )

    variedad = models.CharField(
        max_length=100,
        verbose_name="Variedad",
        help_text="Variedad específica dentro de la especie"
    )

    # === INVENTARIO ===
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Cantidad",
        help_text="Cantidad disponible en inventario"
    )

    unidad_medida = models.CharField(
        max_length=20,
        verbose_name="Unidad de Medida",
        help_text="Unidad de medida (kg, toneladas, etc.)"
    )

    # === CONTROL DE CALIDAD ===
    fecha_vencimiento = models.DateField(
        verbose_name="Fecha de Vencimiento",
        help_text="Fecha límite de uso de la semilla"
    )

    porcentaje_germinacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Porcentaje de Germinación",
        help_text="Porcentaje de germinación esperado (0-100%)"
    )

    # === TRAZABILIDAD ===
    lote = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Lote",
        help_text="Número único del lote de semillas"
    )

    proveedor = models.CharField(
        max_length=100,
        verbose_name="Proveedor",
        help_text="Nombre del proveedor o empresa proveedora"
    )

    # === VALOR ECONÓMICO ===
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio Unitario",
        help_text="Precio por unidad de medida"
    )

    # === UBICACIÓN Y ESTADO ===
    ubicacion_almacen = models.CharField(
        max_length=100,
        verbose_name="Ubicación en Almacén",
        help_text="Sector y posición en el almacén"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='DISPONIBLE',
        verbose_name="Estado",
        help_text="Estado actual de la semilla"
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
        help_text="Notas adicionales sobre la semilla"
    )

    # === TIMESTAMPS ===
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado en"
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado en"
    )

    # === CONSTANTES ===
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('AGOTADA', 'Agotada'),
        ('VENCIDA', 'Vencida'),
        ('EN_CUARENTENA', 'En Cuarentena'),
        ('RECHAZADA', 'Rechazada'),
    ]
```

## 🔑 Campos y Validaciones

### **Campos Requeridos**
| Campo | Tipo | Validación | Descripción |
|-------|------|------------|-------------|
| `especie` | CharField(100) | Requerido | Especie de la semilla |
| `variedad` | CharField(100) | Requerido | Variedad específica |
| `cantidad` | DecimalField | ≥ 0 | Cantidad en inventario |
| `unidad_medida` | CharField(20) | Requerido | Unidad de medida |
| `fecha_vencimiento` | DateField | Requerido | Fecha límite de uso |
| `porcentaje_germinacion` | DecimalField | 0-100 | % de germinación |
| `lote` | CharField(50) | Único | Número de lote |
| `proveedor` | CharField(100) | Requerido | Nombre del proveedor |
| `precio_unitario` | DecimalField | ≥ 0 | Precio por unidad |
| `ubicacion_almacen` | CharField(100) | Requerido | Ubicación física |

### **Campos Opcionales**
| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `estado` | CharField | 'DISPONIBLE' | Estado de la semilla |
| `observaciones` | TextField | '' | Notas adicionales |

### **Campos Automáticos**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `creado_en` | DateTimeField | Timestamp de creación |
| `actualizado_en` | DateTimeField | Timestamp de última modificación |

## 🎯 Estados de Semilla

### **Estados Disponibles**
```python
ESTADOS = [
    ('DISPONIBLE', 'Disponible'),           # Semilla lista para uso
    ('AGOTADA', 'Agotada'),                 # Sin stock disponible
    ('VENCIDA', 'Vencida'),                 # Fecha de vencimiento pasada
    ('EN_CUARENTENA', 'En Cuarentena'),     # Pendiente de análisis
    ('RECHAZADA', 'Rechazada'),             # No cumple estándares
]
```

### **Transiciones de Estado**
- **DISPONIBLE** → AGOTADA (cuando cantidad = 0)
- **DISPONIBLE** → VENCIDA (cuando fecha_vencimiento < hoy)
- **DISPONIBLE** → EN_CUARENTENA (por análisis de calidad)
- **EN_CUARENTENA** → DISPONIBLE (aprobada)
- **EN_CUARENTENA** → RECHAZADA (rechazada)

## ⚙️ Métodos del Modelo

### **Métodos de Cálculo**

#### **`valor_total()`**
```python
def valor_total(self):
    """
    Calcula el valor total del inventario de esta semilla.

    Returns:
        Decimal: Valor total (precio_unitario * cantidad)
    """
    if self.precio_unitario and self.cantidad:
        return self.precio_unitario * self.cantidad
    return Decimal('0.00')
```

#### **`dias_para_vencer()`**
```python
def dias_para_vencer(self):
    """
    Calcula los días restantes para el vencimiento.

    Returns:
        int or None: Días hasta vencimiento, None si no hay fecha
    """
    if self.fecha_vencimiento:
        return (self.fecha_vencimiento - timezone.now().date()).days
    return None
```

#### **`esta_proxima_vencer()`**
```python
def esta_proxima_vencer(self):
    """
    Verifica si la semilla vence en menos de 30 días.

    Returns:
        bool: True si vence en 30 días o menos
    """
    dias = self.dias_para_vencer()
    return dias is not None and 0 <= dias <= 30
```

#### **`esta_vencida()`**
```python
def esta_vencida(self):
    """
    Verifica si la semilla ya está vencida.

    Returns:
        bool: True si la fecha de vencimiento ya pasó
    """
    dias = self.dias_para_vencer()
    return dias is not None and dias < 0
```

### **Métodos de Validación**

#### **`clean()`**
```python
def clean(self):
    """
    Validaciones de negocio a nivel de modelo.
    """
    # Validar que si está agotada, cantidad debe ser 0
    if self.estado == 'AGOTADA' and self.cantidad != 0:
        raise ValidationError({
            'cantidad': 'Si la semilla está agotada, la cantidad debe ser 0.'
        })

    # Validar que si está vencida, estado debe ser VENCIDA
    if self.esta_vencida() and self.estado != 'VENCIDA':
        raise ValidationError({
            'estado': 'La semilla está vencida. El estado debe ser VENCIDA.'
        })

    # Validar fecha de vencimiento no en el pasado para nuevas semillas
    if not self.pk and self.fecha_vencimiento < timezone.now().date():
        raise ValidationError({
            'fecha_vencimiento': 'La fecha de vencimiento no puede ser en el pasado.'
        })
```

#### **`save()`**
```python
def save(self, *args, **kwargs):
    """
    Override del método save para lógica adicional.
    """
    # Actualizar estado basado en cantidad
    if self.cantidad == 0 and self.estado == 'DISPONIBLE':
        self.estado = 'AGOTADA'

    # Actualizar estado basado en fecha de vencimiento
    if self.esta_vencida() and self.estado not in ['VENCIDA', 'RECHAZADA']:
        self.estado = 'VENCIDA'

    super().save(*args, **kwargs)
```

### **Métodos de Representación**

#### **`__str__()`**
```python
def __str__(self):
    """
    Representación string del objeto.
    """
    return f"{self.especie} {self.variedad} - Lote {self.lote}"
```

#### **`get_absolute_url()`**
```python
def get_absolute_url(self):
    """
    URL absoluta para el detalle de la semilla.
    """
    return reverse('semilla-detail', kwargs={'pk': self.pk})
```

## 🔍 Propiedades Calculadas

### **Propiedades del Serializer**
```python
@property
def valor_total_calculado(self):
    """Propiedad para acceso directo al valor total"""
    return self.valor_total()

@property
def dias_para_vencer_calculado(self):
    """Propiedad para acceso directo a días para vencer"""
    return self.dias_para_vencer()

@property
def esta_proxima_vencer_calculado(self):
    """Propiedad para acceso directo a estado próxima a vencer"""
    return self.esta_proxima_vencer()

@property
def esta_vencida_calculado(self):
    """Propiedad para acceso directo a estado vencida"""
    return self.esta_vencida()
```

## 📊 Índices y Optimizaciones

### **Índices de Base de Datos**
```sql
-- Índice para búsquedas por especie
CREATE INDEX idx_semilla_especie ON cooperativa_semilla (especie);

-- Índice para búsquedas por estado
CREATE INDEX idx_semilla_estado ON cooperativa_semilla (estado);

-- Índice para búsquedas por fecha de vencimiento
CREATE INDEX idx_semilla_fecha_vencimiento ON cooperativa_semilla (fecha_vencimiento);

-- Índice compuesto para filtros comunes
CREATE INDEX idx_semilla_especie_estado ON cooperativa_semilla (especie, estado);

-- Índice único para lote
CREATE UNIQUE INDEX idx_semilla_lote_unique ON cooperativa_semilla (lote);
```

### **Optimizaciones de Consulta**
```python
# Consultas optimizadas con select_related/prefetch_related
semillas = Semilla.objects.select_related().filter(
    estado='DISPONIBLE'
).order_by('fecha_vencimiento')

# Uso de only/defer para campos específicos
semillas = Semilla.objects.only(
    'especie', 'variedad', 'cantidad', 'estado', 'fecha_vencimiento'
).filter(fecha_vencimiento__lte=timezone.now().date() + timedelta(days=30))
```

## 🔒 Constraints y Reglas de Integridad

### **Constraints de Base de Datos**
```sql
-- Check constraint para porcentaje de germinación
ALTER TABLE cooperativa_semilla
ADD CONSTRAINT chk_porcentaje_germinacion
CHECK (porcentaje_germinacion >= 0 AND porcentaje_germinacion <= 100);

-- Check constraint para cantidades positivas
ALTER TABLE cooperativa_semilla
ADD CONSTRAINT chk_cantidad_positiva
CHECK (cantidad >= 0);

-- Check constraint para precios positivos
ALTER TABLE cooperativa_semilla
ADD CONSTRAINT chk_precio_positivo
CHECK (precio_unitario >= 0);
```

### **Reglas de Negocio**
1. **Unicidad de Lote:** Cada lote debe ser único en el sistema
2. **Cantidad No Negativa:** La cantidad nunca puede ser negativa
3. **Precio No Negativo:** El precio unitario debe ser positivo
4. **Porcentaje Válido:** Germinación entre 0% y 100%
5. **Estado Consistente:** Estado debe reflejar realidad (agotada, vencida)
6. **Fecha Vencimiento:** No puede ser en el pasado para nuevas semillas

## 📈 Estadísticas y Métricas

### **Métricas del Modelo**
```python
@classmethod
def estadisticas_inventario(cls):
    """
    Estadísticas generales del inventario.
    """
    return {
        'total_semillas': cls.objects.count(),
        'valor_total': cls.objects.aggregate(
            total=Sum(F('precio_unitario') * F('cantidad'))
        )['total'] or 0,
        'semillas_disponibles': cls.objects.filter(estado='DISPONIBLE').count(),
        'semillas_vencidas': cls.objects.filter(estado='VENCIDA').count(),
        'proximas_vencer': cls.objects.filter(
            fecha_vencimiento__lte=timezone.now().date() + timedelta(days=30),
            estado='DISPONIBLE'
        ).count()
    }

@classmethod
def semillas_por_especie(cls):
    """
    Agrupación de semillas por especie.
    """
    return cls.objects.values('especie').annotate(
        cantidad_total=Sum('cantidad'),
        valor_total=Sum(F('precio_unitario') * F('cantidad')),
        count=Count('id')
    ).order_by('-valor_total')
```

## 🔄 Migraciones

### **Migración Inicial**
```python
# 0009_alter_tratamiento_tipo_tratamiento_semilla.py
operations = [
    migrations.CreateModel(
        name='Semilla',
        fields=[
            ('id', models.AutoField(primary_key=True)),
            ('especie', models.CharField(max_length=100, verbose_name='Especie')),
            ('variedad', models.CharField(max_length=100, verbose_name='Variedad')),
            ('cantidad', models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0)], verbose_name='Cantidad')),
            ('unidad_medida', models.CharField(max_length=20, verbose_name='Unidad de Medida')),
            ('fecha_vencimiento', models.DateField(verbose_name='Fecha de Vencimiento')),
            ('porcentaje_germinacion', models.DecimalField(decimal_places=2, max_digits=5, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Porcentaje de Germinación')),
            ('lote', models.CharField(max_length=50, unique=True, verbose_name='Lote')),
            ('proveedor', models.CharField(max_length=100, verbose_name='Proveedor')),
            ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0)], verbose_name='Precio Unitario')),
            ('ubicacion_almacen', models.CharField(max_length=100, verbose_name='Ubicación en Almacén')),
            ('estado', models.CharField(choices=[('DISPONIBLE', 'Disponible'), ('AGOTADA', 'Agotada'), ('VENCIDA', 'Vencida'), ('EN_CUARENTENA', 'En Cuarentena'), ('RECHAZADA', 'Rechazada')], default='DISPONIBLE', max_length=20, verbose_name='Estado')),
            ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
            ('creado_en', models.DateTimeField(auto_now_add=True, verbose_name='Creado en')),
            ('actualizado_en', models.DateTimeField(auto_now=True, verbose_name='Actualizado en')),
        ],
    ),
]
```

## 📋 Consideraciones de Diseño

### **Decisiones Arquitectónicas**
1. **DecimalField vs FloatField:** DecimalField para precisión financiera
2. **CharField vs TextField:** CharField con límites para campos cortos
3. **Unique Constraint en Lote:** Garantiza trazabilidad única
4. **Estados como Choices:** Mejora integridad y UI
5. **Timestamps Automáticos:** Auditoría automática
6. **Validadores Django:** Validación a nivel de campo y modelo

### **Escalabilidad**
- **Índices Optimizados:** Para consultas frecuentes
- **Campos Calculados:** Lógica de negocio en métodos
- **Constraints de BD:** Integridad referencial
- **Separación de Concerns:** Modelo enfocado en datos

### **Mantenibilidad**
- **Documentación Clara:** Campos bien documentados
- **Métodos Consistentes:** Nombres descriptivos
- **Validaciones Centralizadas:** Lógica en clean() y save()
- **Constantes Definidas:** Estados y configuraciones

---

**📅 Fecha de creación:** Octubre 2025  
**🔗 Versión:** 1.0.0  
**📧 Contacto:** desarrollo@cooperativa.com</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU7_CRUD_Semillas\Modelo_Semilla.md