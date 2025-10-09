# ✅ Validaciones de Insumos Agrícolas

## 📋 Descripción General

El sistema de validaciones de insumos agrícolas implementa reglas de negocio específicas para garantizar la integridad de los datos de pesticidas y fertilizantes. Las validaciones se aplican tanto a nivel de modelo como de serializer, asegurando consistencia y calidad de la información.

## 🏗️ Arquitectura de Validaciones

### **Niveles de Validación**
1. **Validación de Campo:** Constraints básicos (requerido, tipo, longitud)
2. **Validación de Modelo:** Reglas de negocio específicas
3. **Validación de Serializer:** Validaciones complejas y cross-field
4. **Validación de Base de Datos:** Constraints a nivel BD

### **Estrategia de Validación**
- **Defensiva:** Validar en múltiples niveles
- **Específica:** Mensajes de error claros y útiles
- **Consistente:** Patrones uniformes en toda la aplicación

## 🔍 Validaciones de Pesticidas

### **Validaciones de Campo**

#### **Nombre Comercial**
```python
# models.py - Campo
nombre_comercial = models.CharField(max_length=100)

# Validación implícita
- Requerido: True
- Tipo: String
- Longitud máxima: 100 caracteres
- Mensaje de error: "Este campo es obligatorio."
```

#### **Ingrediente Activo**
```python
# models.py - Campo
ingrediente_activo = models.CharField(max_length=100)

# Validación implícita
- Requerido: True
- Tipo: String
- Longitud máxima: 100 caracteres
```

#### **Tipo de Pesticida**
```python
# models.py - Campo
tipo_pesticida = models.CharField(max_length=20, choices=TIPOS_PESTICIDA)

# Validación implícita
- Requerido: True
- Valores permitidos: INSECTICIDA, FUNGICIDA, HERBICIDA, etc.
- Mensaje de error: "Seleccione una opción válida."
```

#### **Concentración**
```python
# models.py - Campo
concentracion = models.CharField(max_length=50)

# Validación personalizada
def validate_concentracion(value):
    """Valida el formato de concentración"""
    import re
    patron = r'^[0-9\.\,\s\%\-\(\)\+\a-zA-Z]+$'
    if not re.match(patron, value):
        raise ValidationError(
            'Formato de concentración inválido. '
            'Ejemplos válidos: "48%% EC", "80%% WP", "200 g/L", "2+4 D"'
        )
```

#### **Registro Sanitario**
```python
# models.py - Campo
registro_sanitario = models.CharField(max_length=50, blank=True)

# Validación implícita
- Requerido: False
- Longitud máxima: 50 caracteres
```

#### **Cantidad**
```python
# models.py - Campo
cantidad = models.DecimalField(max_digits=10, decimal_places=2)

# Validaciones
def validate_cantidad(value):
    """Valida la cantidad del producto"""
    if value <= 0:
        raise ValidationError('La cantidad debe ser mayor que cero.')
    if value > 99999999.99:
        raise ValidationError('La cantidad no puede exceder 99,999,999.99')
```

#### **Unidad de Medida**
```python
# models.py - Campo
unidad_medida = models.CharField(max_length=20)

# Validación implícita
- Requerido: True
- Longitud máxima: 20 caracteres
```

#### **Fecha de Vencimiento**
```python
# models.py - Campo
fecha_vencimiento = models.DateField()

# Validación personalizada
def validate_fecha_vencimiento(value):
    """Valida que la fecha de vencimiento sea futura"""
    from django.utils import timezone
    if value <= timezone.now().date():
        raise ValidationError(
            'La fecha de vencimiento debe ser posterior a la fecha actual.'
        )
```

#### **Lote**
```python
# models.py - Campo
lote = models.CharField(max_length=50, unique=True)

# Validaciones
- Requerido: True
- Longitud máxima: 50 caracteres
- Único: True
- Mensaje de error: "Ya existe un insumo con este lote."
```

#### **Proveedor**
```python
# models.py - Campo
proveedor = models.CharField(max_length=100)

# Validación implícita
- Requerido: True
- Longitud máxima: 100 caracteres
```

#### **Precio Unitario**
```python
# models.py - Campo
precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

# Validación personalizada
def validate_precio_unitario(value):
    """Valida el precio unitario"""
    if value <= 0:
        raise ValidationError('El precio unitario debe ser mayor que cero.')
    if value > 99999999.99:
        raise ValidationError('El precio unitario no puede exceder 99,999,999.99')
```

#### **Ubicación de Almacén**
```python
# models.py - Campo
ubicacion_almacen = models.CharField(max_length=100)

# Validación implícita
- Requerido: True
- Longitud máxima: 100 caracteres
```

#### **Estado**
```python
# models.py - Campo
estado = models.CharField(max_length=20, choices=ESTADOS)

# Validación implícita
- Requerido: True
- Valores permitidos: DISPONIBLE, AGOTADO, VENCIDO, EN_TRANSITO, EN_USO, RESERVADO
```

### **Validaciones de Serializer (PesticidaSerializer)**

#### **Validaciones Cross-Field**
```python
def validate(self, data):
    """Validaciones que involucran múltiples campos"""
    # Validar que si el estado es VENCIDO, la fecha de vencimiento debe ser pasada
    if data.get('estado') == 'VENCIDO':
        fecha_venc = data.get('fecha_vencimiento')
        if fecha_venc and fecha_venc > timezone.now().date():
            raise ValidationError({
                'estado': 'Un producto marcado como vencido debe tener fecha de vencimiento pasada.'
            })

    # Validar dosis recomendada según tipo de pesticida
    tipo = data.get('tipo_pesticida')
    dosis = data.get('dosis_recomendada')
    if tipo and dosis:
        self._validate_dosis_por_tipo(tipo, dosis)

    return data
```

#### **Validación de Dosis por Tipo**
```python
def _validate_dosis_por_tipo(self, tipo, dosis):
    """Valida dosis recomendada según tipo de pesticida"""
    patrones_dosis = {
        'INSECTICIDA': r'^[0-9\-\.\s]+(ml|L|kg|g)/ha$',
        'FUNGICIDA': r'^[0-9\-\.\s]+(kg|g|ml|L)/ha$',
        'HERBICIDA': r'^[0-9\-\.\s]+(ml|L|kg|g)/ha$',
    }

    if tipo in patrones_dosis:
        import re
        if not re.match(patrones_dosis[tipo], dosis, re.IGNORECASE):
            raise ValidationError({
                'dosis_recomendada': f'Formato de dosis inválido para {tipo.lower()}. '
                                   f'Use formato como "2-3 L/ha" o "1-2 kg/ha".'
            })
```

## 🌱 Validaciones de Fertilizantes

### **Validaciones de Campo**

#### **Nombre Comercial**
```python
# models.py - Campo
nombre_comercial = models.CharField(max_length=100)

# Validación implícita
- Requerido: True
- Longitud máxima: 100 caracteres
```

#### **Tipo de Fertilizante**
```python
# models.py - Campo
tipo_fertilizante = models.CharField(max_length=20, choices=TIPOS_FERTILIZANTE)

# Validación implícita
- Requerido: True
- Valores permitidos: QUIMICO, ORGANICO, MINERAL, UREA, NPK_COMPLEJO,
  FOSFATO, POTASIO, CALCIO, MAGNESIO, MICRONUTRIENTES
```

#### **Composición NPK**
```python
# models.py - Campo
composicion_npk = models.CharField(max_length=20)

# Validación personalizada
def validate_composicion_npk(value):
    """Valida el formato N-P-K"""
    import re
    patron = r'^[0-9]{1,2}-[0-9]{1,2}-[0-9]{1,2}(\+[A-Za-z]+)?$'
    if not re.match(patron, value):
        raise ValidationError(
            'Formato NPK inválido. Use formato N-P-K (ej: 10-10-10). '
            'Los valores deben estar entre 0-99.'
        )

    # Validar rangos individuales
    try:
        partes = value.split('-')
        n = int(partes[0])
        p = int(partes[1])
        k_part = partes[2].split('+')[0]
        k = int(k_part)

        if not all(0 <= val <= 99 for val in [n, p, k]):
            raise ValidationError('Los valores NPK deben estar entre 0 y 99.')
    except (ValueError, IndexError):
        raise ValidationError('Formato NPK inválido.')
```

#### **Cantidad**
```python
# models.py - Campo
cantidad = models.DecimalField(max_digits=10, decimal_places=2)

# Validación personalizada (igual que pesticidas)
def validate_cantidad(value):
    if value <= 0:
        raise ValidationError('La cantidad debe ser mayor que cero.')
    if value > 99999999.99:
        raise ValidationError('La cantidad no puede exceder 99,999,999.99')
```

#### **Fecha de Vencimiento**
```python
# models.py - Campo
fecha_vencimiento = models.DateField(blank=True, null=True)

# Validación personalizada
def validate_fecha_vencimiento_opcional(value):
    """Valida fecha de vencimiento si se proporciona"""
    if value and value <= timezone.now().date():
        raise ValidationError(
            'La fecha de vencimiento debe ser posterior a la fecha actual.'
        )
```

#### **Materia Orgánica**
```python
# models.py - Campo
materia_orgánica = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

# Validación personalizada
def validate_materia_organica(value):
    """Valida el porcentaje de materia orgánica"""
    if value is not None:
        if value < 0 or value > 100:
            raise ValidationError('La materia orgánica debe estar entre 0% y 100%.')
```

#### **Lote**
```python
# models.py - Campo
lote = models.CharField(max_length=50, unique=True)

# Validaciones (igual que pesticidas)
- Requerido: True
- Longitud máxima: 50 caracteres
- Único: True
```

### **Validaciones de Serializer (FertilizanteSerializer)**

#### **Validaciones Cross-Field**
```python
def validate(self, data):
    """Validaciones que involucran múltiples campos"""
    # Validar materia orgánica solo para fertilizantes orgánicos
    tipo = data.get('tipo_fertilizante')
    materia_org = data.get('materia_orgánica')

    if tipo == 'ORGANICO' and materia_org is None:
        raise ValidationError({
            'materia_orgánica': 'Los fertilizantes orgánicos deben especificar el porcentaje de materia orgánica.'
        })

    if tipo != 'ORGANICO' and materia_org is not None:
        raise ValidationError({
            'materia_orgánica': 'Solo los fertilizantes orgánicos pueden tener materia orgánica.'
        })

    # Validar composición NPK según tipo
    composicion = data.get('composicion_npk')
    if composicion:
        self._validate_npk_por_tipo(tipo, composicion)

    return data
```

#### **Validación NPK por Tipo**
```python
def _validate_npk_por_tipo(self, tipo, composicion):
    """Valida composición NPK según tipo de fertilizante"""
    try:
        npk = self._parse_npk(composicion)
        n, p, k = npk['N'], npk['P'], npk['K']

        # Validaciones específicas por tipo
        if tipo == 'QUIMICO':
            if n + p + k < 10:
                raise ValidationError({
                    'composicion_npk': 'Los fertilizantes químicos deben tener al menos 10% de nutrientes totales.'
                })

        elif tipo == 'ORGANICO':
            if n + p + k > 15:
                raise ValidationError({
                    'composicion_npk': 'Los fertilizantes orgánicos normalmente tienen menos del 15% de nutrientes totales.'
                })

    except (ValueError, KeyError):
        raise ValidationError({
            'composicion_npk': 'Error al procesar la composición NPK.'
        })
```

## 🔒 Validaciones de Seguridad

### **Validaciones de Autenticación**
```python
# En ViewSets
authentication_classes = [TokenAuthentication]
permission_classes = [IsAuthenticated]

# Validar permisos específicos
def perform_create(self, serializer):
    """Solo usuarios autorizados pueden crear insumos"""
    if not self.request.user.has_perm('cooperativa.add_pesticida'):
        raise PermissionDenied("No tiene permisos para crear pesticidas.")
    serializer.save()
```

### **Validaciones de Integridad**
```python
# Evitar modificación de campos críticos
def perform_update(self, serializer):
    """Validar cambios en campos críticos"""
    instance = self.get_object()

    # No permitir cambiar lote una vez creado
    if 'lote' in serializer.validated_data:
        if serializer.validated_data['lote'] != instance.lote:
            raise ValidationError({
                'lote': 'No se puede modificar el número de lote.'
            })

    serializer.save()
```

## 📊 Validaciones de Base de Datos

### **Constraints a Nivel BD**
```sql
-- Constraints para Pesticida
ALTER TABLE cooperativa_pesticida
ADD CONSTRAINT chk_pesticida_cantidad CHECK (cantidad > 0),
ADD CONSTRAINT chk_pesticida_precio CHECK (precio_unitario > 0),
ADD CONSTRAINT chk_pesticida_fecha_venc CHECK (fecha_vencimiento > CURRENT_DATE);

-- Constraints para Fertilizante
ALTER TABLE cooperativa_fertilizante
ADD CONSTRAINT chk_fertilizante_cantidad CHECK (cantidad > 0),
ADD CONSTRAINT chk_fertilizante_precio CHECK (precio_unitario > 0),
ADD CONSTRAINT chk_fertilizante_fecha_venc CHECK (fecha_vencimiento > CURRENT_DATE OR fecha_vencimiento IS NULL);
```

### **Índices Únicos**
```sql
-- Índices únicos para garantizar integridad
CREATE UNIQUE INDEX idx_pesticida_lote ON cooperativa_pesticida (lote);
CREATE UNIQUE INDEX idx_fertilizante_lote ON cooperativa_fertilizante (lote);
```

## ⚠️ Manejo de Errores

### **Tipos de Errores de Validación**

#### **Errores de Campo Requerido**
```json
{
    "nombre_comercial": ["Este campo es obligatorio."]
}
```

#### **Errores de Formato**
```json
{
    "concentracion": ["Formato de concentración inválido. Ejemplos válidos: \"48% EC\", \"80% WP\", \"200 g/L\""]
}
```

#### **Errores de Regla de Negocio**
```json
{
    "estado": ["Un producto marcado como vencido debe tener fecha de vencimiento pasada."]
}
```

#### **Errores de Unicidad**
```json
{
    "lote": ["Ya existe un insumo con este lote."]
}
```

#### **Errores Cross-Field**
```json
{
    "materia_orgánica": ["Solo los fertilizantes orgánicos pueden tener materia orgánica."]
}
```

### **Estrategia de Manejo de Errores**
```python
# En ViewSets
def handle_validation_error(self, exc):
    """Manejar errores de validación de forma consistente"""
    if isinstance(exc, ValidationError):
        return Response({
            'error': 'Datos de entrada inválidos',
            'details': exc.detail
        }, status=status.HTTP_400_BAD_REQUEST)

    return super().handle_exception(exc)
```

## 🧪 Testing de Validaciones

### **Casos de Prueba**

#### **Validaciones de Pesticida**
```python
def test_pesticida_validaciones(self):
    # Campo requerido
    with self.assertRaises(ValidationError):
        Pesticida.objects.create()  # Sin nombre_comercial

    # Concentración inválida
    with self.assertRaises(ValidationError):
        Pesticida.objects.create(
            nombre_comercial="Test",
            concentracion="INVALIDO!!!"
        )

    # Fecha de vencimiento pasada
    with self.assertRaises(ValidationError):
        Pesticida.objects.create(
            nombre_comercial="Test",
            fecha_vencimiento=date(2020, 1, 1)
        )

    # Lote duplicado
    Pesticida.objects.create(
        nombre_comercial="Test 1",
        lote="LOT-001",
        # ... otros campos
    )
    with self.assertRaises(IntegrityError):
        Pesticida.objects.create(
            nombre_comercial="Test 2",
            lote="LOT-001",  # Duplicado
            # ... otros campos
        )
```

#### **Validaciones de Fertilizante**
```python
def test_fertilizante_validaciones(self):
    # NPK inválido
    with self.assertRaises(ValidationError):
        Fertilizante.objects.create(
            nombre_comercial="Test",
            composicion_npk="INVALIDO"
        )

    # Materia orgánica fuera de rango
    with self.assertRaises(ValidationError):
        Fertilizante.objects.create(
            nombre_comercial="Test",
            tipo_fertilizante="ORGANICO",
            materia_orgánica=150.00  # > 100%
        )
```

## 📈 Métricas de Validación

### **Métricas de Calidad**
- **Tasa de Éxito de Validaciones:** Porcentaje de operaciones exitosas
- **Tipos de Errores Más Comunes:** Análisis de frecuencia de errores
- **Tiempo de Validación:** Performance de las validaciones
- **Cobertura de Validaciones:** Campos y reglas cubiertas

### **Monitoreo**
```python
# Logging de validaciones
import logging
logger = logging.getLogger(__name__)

def log_validation_error(field, error):
    """Log errores de validación para análisis"""
    logger.warning(f"Validation error in {field}: {error}")
```

## 🔧 Mantenimiento de Validaciones

### **Actualización de Reglas**
- **Revisión Periódica:** Validaciones cada 6 meses
- **Actualización de Patrones:** Según cambios regulatorios
- **Testing Exhaustivo:** Antes de desplegar cambios

### **Documentación**
- **Catálogo de Validaciones:** Documento actualizado
- **Ejemplos de Uso:** Casos válidos e inválidos
- **Mensajes de Error:** Guía para usuarios

---

**📅 Última actualización:** Diciembre 2024  
**🔍 Sistema:** Validaciones de Insumos  
**📊 Versión:** 1.1.0  
**✅ Estado:** Actualizado con cambios de regex y tipos expandidos

### **📝 Cambios Recientes (v1.1.0)**
- **Regex de concentración:** Actualizado para permitir caracteres '+' y '%' adicionales
- **Tipos de fertilizante:** Expandidos con UREA, NPK_COMPLEJO, FOSFATO, POTASIO, CALCIO, MAGNESIO, MICRONUTRIENTES
- **Estados de inventario:** Agregados EN_TRANSITO, EN_USO, RESERVADO
- **Validaciones:** Mejoradas para mayor flexibilidad en nombres de productos agrícolas</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU8_CRUD_Insumos\Validaciones_Insumos.md