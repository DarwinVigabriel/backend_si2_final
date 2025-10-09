# 🧪 Tests CU7 - Gestión de Semillas

## 📋 Información General

Suite completa de pruebas para el **Caso de Uso CU7: Gestión de Semillas**. Las pruebas cubren todas las funcionalidades del sistema de inventario de semillas, incluyendo modelo, API, validaciones y administración.

**Framework:** Django TestCase + Django REST Framework  
**Cobertura:** Modelo, Serializer, ViewSet, Admin, API  
**Base de Datos:** SQLite en memoria para tests

## 🏗️ Estructura de Tests

### **Archivos de Test**
```
test/CU7/
├── __init__.py
├── test_modelo_semilla.py      # Tests del modelo Semilla
├── test_serializer_semilla.py  # Tests del serializer
├── test_api_semilla.py         # Tests de la API REST
├── test_admin_semilla.py       # Tests de Django Admin
├── test_validaciones.py        # Tests de validaciones
└── test_integracion_semilla.py # Tests de integración
```

### **Configuración Base**
```python
# test_base.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
import json

class SemillaTestBase(TestCase):
    """Base class para tests de semillas"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='admin',
            password='clave123',
            is_staff=True,
            is_superuser=True
        )

        # Datos de prueba
        self.semilla_data = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "500.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": date.today() + timedelta(days=365),
            "porcentaje_germinacion": "95.50",
            "lote": "MZ2025001",
            "proveedor": "AgroSemillas S.A.",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Sector A-15",
            "observaciones": "Lote premium"
        }

    def crear_semilla(self, **kwargs):
        """Helper para crear semillas de prueba"""
        data = self.semilla_data.copy()
        data.update(kwargs)
        from cooperativa.models import Semilla
        return Semilla.objects.create(**data)
```

## 🧪 Tests del Modelo

### **test_modelo_semilla.py**
```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from cooperativa.models import Semilla

class SemillaModelTest(SemillaTestBase):

    def test_creacion_semilla_valida(self):
        """Test: Crear semilla con datos válidos"""
        semilla = self.crear_semilla()
        self.assertEqual(semilla.especie, "Maíz")
        self.assertEqual(semilla.estado, "DISPONIBLE")
        self.assertEqual(semilla.valor_total(), Decimal('12500.00'))

    def test_calculo_valor_total(self):
        """Test: Cálculo correcto del valor total"""
        semilla = self.crear_semilla(cantidad="100.00", precio_unitario="50.00")
        self.assertEqual(semilla.valor_total(), Decimal('5000.00'))

    def test_dias_para_vencer(self):
        """Test: Cálculo de días para vencer"""
        fecha_futura = date.today() + timedelta(days=30)
        semilla = self.crear_semilla(fecha_vencimiento=fecha_futura)
        self.assertEqual(semilla.dias_para_vencer(), 30)

    def test_esta_proxima_vencer(self):
        """Test: Detección de semillas próximas a vencer"""
        # Dentro de 30 días
        fecha_proxima = date.today() + timedelta(days=15)
        semilla = self.crear_semilla(fecha_vencimiento=fecha_proxima)
        self.assertTrue(semilla.esta_proxima_vencer())

        # Fuera de 30 días
        fecha_lejana = date.today() + timedelta(days=60)
        semilla2 = self.crear_semilla(fecha_vencimiento=fecha_lejana, lote="MZ2025002")
        self.assertFalse(semilla2.esta_proxima_vencer())

    def test_esta_vencida(self):
        """Test: Detección de semillas vencidas"""
        fecha_pasada = date.today() - timedelta(days=1)
        semilla = self.crear_semilla(fecha_vencimiento=fecha_pasada)
        self.assertTrue(semilla.esta_vencida())

    def test_estado_agotada_cantidad_cero(self):
        """Test: Estado AGOTADA cuando cantidad es 0"""
        semilla = self.crear_semilla(cantidad="0.00")
        semilla.save()
        self.assertEqual(semilla.estado, "AGOTADA")

    def test_validacion_cantidad_negativa(self):
        """Test: Error con cantidad negativa"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.cantidad = Decimal('-10.00')
            semilla.full_clean()

    def test_validacion_porcentaje_germinacion_invalido(self):
        """Test: Error con porcentaje de germinación inválido"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.porcentaje_germinacion = Decimal('150.00')
            semilla.full_clean()

    def test_validacion_fecha_vencimiento_pasada(self):
        """Test: Error con fecha de vencimiento en el pasado"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.fecha_vencimiento = date.today() - timedelta(days=1)
            semilla.full_clean()

    def test_lote_unico(self):
        """Test: Lote debe ser único"""
        self.crear_semilla()
        with self.assertRaises(ValidationError):
            self.crear_semilla(lote="MZ2025001")  # Mismo lote

    def test_str_representation(self):
        """Test: Representación string del modelo"""
        semilla = self.crear_semilla()
        expected = "Maíz Criollo - Lote MZ2025001"
        self.assertEqual(str(semilla), expected)
```

## 📋 Tests del Serializer

### **test_serializer_semilla.py**
```python
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.serializers import SemillaSerializer
from cooperativa.models import Semilla

class SemillaSerializerTest(SemillaTestBase, APITestCase):

    def test_serializer_campos_requeridos(self):
        """Test: Serializer valida campos requeridos"""
        serializer = SemillaSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('especie', serializer.errors)
        self.assertIn('variedad', serializer.errors)
        self.assertIn('cantidad', serializer.errors)

    def test_serializer_datos_validos(self):
        """Test: Serializer acepta datos válidos"""
        serializer = SemillaSerializer(data=self.semilla_data)
        self.assertTrue(serializer.is_valid())
        semilla = serializer.save()
        self.assertEqual(semilla.especie, "Maíz")

    def test_serializer_campos_calculados(self):
        """Test: Campos calculados en serializer"""
        semilla = self.crear_semilla()
        serializer = SemillaSerializer(semilla)
        data = serializer.data

        self.assertIn('valor_total', data)
        self.assertIn('dias_para_vencer', data)
        self.assertIn('esta_proxima_vencer', data)
        self.assertIn('esta_vencida', data)

        self.assertEqual(data['valor_total'], '12500.00')

    def test_validacion_porcentaje_germinacion_serializer(self):
        """Test: Validación de porcentaje en serializer"""
        data = self.semilla_data.copy()
        data['porcentaje_germinacion'] = '150.00'

        serializer = SemillaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('porcentaje_germinacion', serializer.errors)

    def test_validacion_fecha_vencimiento_serializer(self):
        """Test: Validación de fecha vencimiento en serializer"""
        data = self.semilla_data.copy()
        data['fecha_vencimiento'] = date.today() - timedelta(days=1)

        serializer = SemillaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_vencimiento', serializer.errors)

    def test_validacion_estado_cantidad_serializer(self):
        """Test: Validación cruzada estado vs cantidad"""
        data = self.semilla_data.copy()
        data['estado'] = 'AGOTADA'
        data['cantidad'] = '100.00'

        serializer = SemillaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cantidad', serializer.errors)
```

## 🌐 Tests de la API

### **test_api_semilla.py**
```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from cooperativa.models import Semilla

class SemillaAPITest(SemillaTestBase, APITestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username='admin', password='clave123')
        self.url_list = reverse('semilla-list')
        self.semilla = self.crear_semilla()

    def test_list_semillas(self):
        """Test: Listar semillas"""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_semilla(self):
        """Test: Crear semilla vía API"""
        data = self.semilla_data.copy()
        data['lote'] = 'MZ2025002'  # Lote diferente

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Semilla.objects.count(), 2)

    def test_retrieve_semilla(self):
        """Test: Obtener semilla específica"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['especie'], "Maíz")

    def test_update_semilla(self):
        """Test: Actualizar semilla"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})
        data = {'cantidad': '400.00'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.cantidad, Decimal('400.00'))

    def test_delete_semilla(self):
        """Test: Eliminar semilla"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Semilla.objects.count(), 0)

    def test_filtros_busqueda(self):
        """Test: Filtros y búsqueda"""
        # Crear semillas adicionales
        self.crear_semilla(especie="Trigo", lote="TR2025001")
        self.crear_semilla(variedad="Híbrido", lote="MZ2025003")

        # Filtrar por especie
        response = self.client.get(self.url_list, {'especie': 'Maíz'})
        self.assertEqual(len(response.data['results']), 2)

        # Buscar por lote
        response = self.client.get(self.url_list, {'search': 'TR2025001'})
        self.assertEqual(len(response.data['results']), 1)

    def test_inventario_bajo(self):
        """Test: Endpoint inventario bajo"""
        url = reverse('semilla-inventario-bajo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_proximas_vencer(self):
        """Test: Endpoint próximas a vencer"""
        url = reverse('semilla-proximas-vencer')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reporte_inventario(self):
        """Test: Endpoint reporte de inventario"""
        url = reverse('semilla-reporte-inventario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn('resumen', data)
        self.assertIn('total_semillas', data['resumen'])
        self.assertIn('valor_total_inventario', data['resumen'])

    def test_actualizar_cantidad(self):
        """Test: Acción actualizar cantidad"""
        url = reverse('semilla-actualizar-cantidad', kwargs={'pk': self.semilla.pk})
        data = {
            'nueva_cantidad': '300.00',
            'motivo': 'Ajuste de inventario'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.cantidad, Decimal('300.00'))

    def test_marcar_vencida(self):
        """Test: Acción marcar como vencida"""
        url = reverse('semilla-marcar-vencida', kwargs={'pk': self.semilla.pk})
        data = {'motivo': 'Vencimiento detectado'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.estado, 'VENCIDA')
```

## 🎛️ Tests de Django Admin

### **test_admin_semilla.py**
```python
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from cooperativa.admin import SemillaAdmin
from cooperativa.models import Semilla

class SemillaAdminTest(SemillaTestBase):

    def setUp(self):
        super().setUp()
        self.site = AdminSite()
        self.admin = SemillaAdmin(Semilla, self.site)

    def test_list_display(self):
        """Test: Campos mostrados en lista"""
        semilla = self.crear_semilla()
        displayed = self.admin.list_display

        # Verificar que los campos importantes están en list_display
        self.assertIn('especie', displayed)
        self.assertIn('variedad', displayed)
        self.assertIn('cantidad', displayed)
        self.assertIn('estado', displayed)
        self.assertIn('fecha_vencimiento', displayed)

    def test_list_filter(self):
        """Test: Filtros disponibles"""
        filtros = self.admin.list_filter

        self.assertIn('estado', filtros)
        self.assertIn('especie', filtros)
        self.assertIn('proveedor', filtros)
        self.assertIn('fecha_vencimiento', filtros)

    def test_search_fields(self):
        """Test: Campos de búsqueda"""
        search_fields = self.admin.search_fields

        self.assertIn('especie', search_fields)
        self.assertIn('variedad', search_fields)
        self.assertIn('lote', search_fields)
        self.assertIn('proveedor', search_fields)

    def test_readonly_fields(self):
        """Test: Campos de solo lectura"""
        readonly = self.admin.readonly_fields

        self.assertIn('creado_en', readonly)
        self.assertIn('actualizado_en', readonly)

    def test_admin_permissions(self):
        """Test: Permisos de admin"""
        # Verificar que el usuario admin puede acceder
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)
```

## ✅ Tests de Validaciones

### **test_validaciones.py**
```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.models import Semilla
from cooperativa.serializers import SemillaSerializer

class SemillaValidacionesTest(SemillaTestBase):

    def test_validacion_especie_invalida(self):
        """Test: Especie con caracteres inválidos"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.especie = "Maíz@2025"  # Carácter inválido
            semilla.full_clean()

    def test_validacion_variedad_invalida(self):
        """Test: Variedad con caracteres inválidos"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.variedad = "Criollo#1"  # Carácter inválido
            semilla.full_clean()

    def test_validacion_lote_invalido(self):
        """Test: Lote con caracteres inválidos"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.lote = "mz-2025-001"  # Minúsculas no permitidas
            semilla.full_clean()

    def test_validacion_precio_cero(self):
        """Test: Precio unitario cero"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.precio_unitario = Decimal('0.00')
            semilla.full_clean()

    def test_validacion_estado_agotada_cantidad_no_cero(self):
        """Test: Estado AGOTADA con cantidad > 0"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.estado = 'AGOTADA'
            semilla.cantidad = Decimal('100.00')
            semilla.full_clean()

    def test_validacion_semilla_vencida_estado_incorrecto(self):
        """Test: Semilla vencida con estado incorrecto"""
        fecha_pasada = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.fecha_vencimiento = fecha_pasada
            semilla.estado = 'DISPONIBLE'  # Debería ser VENCIDA
            semilla.full_clean()

    def test_validacion_semilla_rechazada_germinacion_alta(self):
        """Test: Semilla rechazada con germinación alta"""
        with self.assertRaises(ValidationError):
            semilla = Semilla(**self.semilla_data)
            semilla.estado = 'RECHAZADA'
            semilla.porcentaje_germinacion = Decimal('75.00')  # > 50%
            semilla.full_clean()
```

## 🔗 Tests de Integración

### **test_integracion_semilla.py**
```python
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.db import transaction
from cooperativa.models import Semilla, BitacoraAuditoria

class SemillaIntegracionTest(SemillaTestBase, APITestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username='admin', password='clave123')

    def test_flujo_completo_semilla(self):
        """Test: Flujo completo CRUD de semilla"""
        # 1. Crear semilla
        data = self.semilla_data.copy()
        response = self.client.post(reverse('semilla-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        semilla_id = response.data['id']

        # 2. Leer semilla
        response = self.client.get(reverse('semilla-detail', kwargs={'pk': semilla_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['especie'], "Maíz")

        # 3. Actualizar semilla
        update_data = {'cantidad': '400.00'}
        response = self.client.patch(
            reverse('semilla-detail', kwargs={'pk': semilla_id}),
            update_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. Verificar actualización
        response = self.client.get(reverse('semilla-detail', kwargs={'pk': semilla_id}))
        self.assertEqual(response.data['cantidad'], '400.00')

        # 5. Eliminar semilla
        response = self.client.delete(reverse('semilla-detail', kwargs={'pk': semilla_id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 6. Verificar eliminación
        response = self.client.get(reverse('semilla-detail', kwargs={'pk': semilla_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_concurrencia_actualizacion_cantidad(self):
        """Test: Actualización concurrente de cantidad"""
        semilla = self.crear_semilla()

        # Simular actualización concurrente
        with transaction.atomic():
            semilla.cantidad = Decimal('300.00')
            semilla.save()

        # Verificar que la cantidad se actualizó
        semilla.refresh_from_db()
        self.assertEqual(semilla.cantidad, Decimal('300.00'))

    def test_auditoria_automatica(self):
        """Test: Auditoría automática de operaciones"""
        # Crear semilla
        semilla = self.crear_semilla()

        # Verificar que se creó registro de auditoría
        auditoria_count = BitacoraAuditoria.objects.filter(
            tabla_afectada='Semilla',
            tipo_operacion='CREATE'
        ).count()
        self.assertGreater(auditoria_count, 0)

    def test_reportes_integrados(self):
        """Test: Reportes con múltiples semillas"""
        # Crear varias semillas
        semillas_data = [
            {"especie": "Maíz", "lote": "MZ001", "cantidad": "100.00"},
            {"especie": "Trigo", "lote": "TR001", "cantidad": "200.00"},
            {"especie": "Maíz", "lote": "MZ002", "cantidad": "150.00"},
        ]

        for data in semillas_data:
            full_data = self.semilla_data.copy()
            full_data.update(data)
            self.crear_semilla(**full_data)

        # Obtener reporte
        response = self.client.get(reverse('semilla-reporte-inventario'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['resumen']['total_semillas'], 3)

        # Verificar agrupación por especie
        especies = data['por_especie']
        self.assertEqual(len(especies), 2)  # Maíz y Trigo

        maiz_data = next(e for e in especies if e['especie'] == 'Maíz')
        self.assertEqual(maiz_data['cantidad_total'], '250.00')
```

## 📊 Ejecutar Tests

### **Comandos de Ejecución**
```bash
# Ejecutar todos los tests de CU7
python manage.py test test.CU7

# Ejecutar tests específicos
python manage.py test test.CU7.test_modelo_semilla
python manage.py test test.CU7.test_api_semilla
python manage.py test test.CU7.test_validaciones

# Ejecutar con cobertura
coverage run --source='cooperativa' manage.py test test.CU7
coverage report
```

### **Configuración de Coverage**
```ini
# .coveragerc
[run]
source = cooperativa
omit =
    */migrations/*
    */tests/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 📈 Resultados Esperados

### **Cobertura de Tests**
- ✅ **Modelo Semilla:** 100% (métodos, validaciones, estados)
- ✅ **Serializer:** 100% (validaciones, campos calculados)
- ✅ **API Endpoints:** 100% (CRUD + acciones personalizadas)
- ✅ **Admin Interface:** 95% (listado, filtros, búsqueda)
- ✅ **Validaciones:** 100% (todos los niveles)
- ✅ **Integración:** 100% (flujos completos)

### **Métricas de Calidad**
- **Líneas de Código Testeado:** > 95%
- **Ramas de Código:** > 90%
- **Complejidad Ciclomática:** < 10 por método
- **Tiempo de Ejecución:** < 30 segundos
- **Tests por Clase:** 10-15 tests promedio

## 🚨 Manejo de Errores en Tests

### **Patrones de Error Comunes**
```python
# E1: AssertionError en cálculos
# Causa: Error en lógica de cálculo
# Solución: Verificar fórmulas matemáticas

# E2: ValidationError no esperado
# Causa: Validación demasiado estricta o datos de prueba inválidos
# Solución: Revisar reglas de validación

# E3: IntegrityError en BD
# Causa: Constraints violadas
# Solución: Verificar datos únicos y referencias

# E4: Timeouts en tests de API
# Causa: Consultas ineficientes
# Solución: Optimizar queries con select_related/prefetch_related
```

### **Debugging de Tests**
```python
# Agregar prints para debugging
def test_debug_semilla(self):
    semilla = self.crear_semilla()
    print(f"Semilla creada: {semilla}")
    print(f"Valor total: {semilla.valor_total()}")
    print(f"Estado: {semilla.estado}")
    # ... resto del test

# Usar pdb para debugging interactivo
import pdb; pdb.set_trace()

# Verificar estado de BD durante test
from django.db import connection
print(connection.queries)  # Ver queries ejecutadas
```

## 📋 Checklist de Tests

### **Modelo**
- [ ] Creación con datos válidos
- [ ] Validaciones de campos
- [ ] Cálculos automáticos (valor_total, vencimiento)
- [ ] Estados y transiciones
- [ ] Unicidad de lote
- [ ] Constraints de BD

### **Serializer**
- [ ] Campos requeridos
- [ ] Validaciones específicas
- [ ] Campos calculados
- [ ] Validaciones cruzadas
- [ ] Manejo de errores

### **API**
- [ ] CRUD completo
- [ ] Filtros y búsqueda
- [ ] Paginación
- [ ] Acciones personalizadas
- [ ] Autenticación
- [ ] Manejo de errores

### **Admin**
- [ ] List display
- [ ] Filtros
- [ ] Búsqueda
- [ ] Permisos
- [ ] Acciones masivas

### **Integración**
- [ ] Flujos completos
- [ ] Concurrencia
- [ ] Auditoría
- [ ] Reportes
- [ ] Performance

---

**📅 Fecha de creación:** Octubre 2025  
**🔗 Versión:** 1.0.0  
**📧 Contacto:** desarrollo@cooperativa.com</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\test\CU7\README.md