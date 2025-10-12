"""
Tests de Integración para CU7 - Gestión de Semillas
"""
from django.test import TestCase, TransactionTestCase
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
from cooperativa.models import Semilla, BitacoraAuditoria, Usuario


class SemillaIntegracionTest(TestCase):
    """Tests de integración completa del sistema de semillas"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        
        # Limpiar completamente la base de datos usando flush de Django
        from django.core.management import call_command
        call_command('flush', '--no-input', verbosity=0)
        
        # Generar un sufijo único para este test basado en timestamp y nombre del test
        import time
        import random
        test_name = self._testMethodName
        # Usar solo las últimas 4-6 letras del nombre del test + timestamp corto para mantener < 50 chars
        short_test_name = test_name[-6:] if len(test_name) > 6 else test_name
        self.unique_suffix = f"{short_test_name}_{int(time.time() * 1000) % 10000}_{random.randint(10, 99)}"
        
        # Crear usuario admin
        self.user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='clave123'
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='admin', password='clave123')

        # Datos base para pruebas con sufijo único
        self.semilla_data = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "500.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "porcentaje_germinacion": "95.50",
            "lote": f"BASE{self.unique_suffix}",
            "proveedor": "AgroSemillas S.A.",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Sector A-15",
            "observaciones": "Lote premium"
        }

    def tearDown(self):
        """Limpieza mínima - TestCase hace rollback automático"""
        pass

    def test_flujo_completo_crud_semilla(self):
        """Test: Flujo completo CRUD de una semilla desde API"""
        # === 1. CREAR ===
        data = self.semilla_data.copy()
        response = self.client.post('/api/semillas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        semilla_id = response.data['id']
        self.assertEqual(Semilla.objects.count(), 1)

        # Verificar campos calculados en respuesta
        self.assertIn('valor_total', response.data)
        self.assertEqual(float(response.data['valor_total']), 12500.00)

        # === 2. LEER ===
        response = self.client.get(f'/api/semillas/{semilla_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['especie'], "Maíz")
        self.assertEqual(response.data['estado'], "DISPONIBLE")

        # === 3. ACTUALIZAR ===
        update_data = {
            'cantidad': '400.00',
            'observaciones': 'Stock actualizado'
        }
        response = self.client.patch(f'/api/semillas/{semilla_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar actualización
        semilla = Semilla.objects.get(pk=semilla_id)
        self.assertEqual(semilla.cantidad, Decimal('400.00'))
        self.assertEqual(semilla.observaciones, 'Stock actualizado')

        # === 4. ELIMINAR ===
        response = self.client.delete(f'/api/semillas/{semilla_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verificar eliminación
        self.assertEqual(Semilla.objects.count(), 0)

        # Verificar que ya no existe
        response = self.client.get(f'/api/semillas/{semilla_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_gestion_inventario_completo(self):
        """Test: Gestión completa de inventario con múltiples operaciones"""
        # Crear inventario inicial
        semillas_data = [
            {
                "especie": "Maíz", "variedad": "Criollo", "cantidad": "1000.00",
                "lote": f"INV001{self.unique_suffix}", "precio_unitario": "25.00"
            },
            {
                "especie": "Trigo", "variedad": "Cenizo", "cantidad": "800.00",
                "lote": f"INV002{self.unique_suffix}", "precio_unitario": "18.00"
            },
            {
                "especie": "Soya", "variedad": "INTA", "cantidad": "500.00",
                "lote": f"INV003{self.unique_suffix}", "precio_unitario": "35.00"
            }
        ]

        # Crear semillas
        for semilla_info in semillas_data:
            data = {
                "especie": semilla_info["especie"],
                "variedad": semilla_info["variedad"],
                "cantidad": semilla_info["cantidad"],
                "unidad_medida": "kg",
                "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
                "porcentaje_germinacion": "95.50",
                "lote": semilla_info["lote"],
                "proveedor": "Proveedor Test",
                "precio_unitario": semilla_info["precio_unitario"],
                "ubicacion_almacen": "Almacen Test",
                "observaciones": "Test inventario"
            }
            response = self.client.post('/api/semillas/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Semilla.objects.count(), 3)

        # === OPERACIONES DE INVENTARIO ===

        # 1. Actualizar cantidad de Maíz
        maiz = Semilla.objects.get(lote=f'INV001{self.unique_suffix}')
        response = self.client.post(
            f'/api/semillas/{maiz.pk}/actualizar_cantidad/',
            {'cantidad_cambio': '-200.00', 'motivo': 'Venta parcial'},  # Cambio negativo para reducir stock
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Agotar stock de Trigo
        trigo = Semilla.objects.get(lote=f'INV002{self.unique_suffix}')
        response = self.client.post(
            f'/api/semillas/{trigo.pk}/actualizar_cantidad/',
            {'cantidad_cambio': '-800.00', 'motivo': 'Venta total'},  # Cambio negativo para agotar stock
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar estado automático
        trigo.refresh_from_db()
        self.assertEqual(trigo.estado, 'AGOTADA')

        # === REPORTES ===

        # Reporte de inventario
        response = self.client.get('/api/semillas/reporte_inventario/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        reporte = response.data
        self.assertEqual(reporte['resumen']['total_semillas'], 3)
        self.assertEqual(reporte['resumen']['semillas_disponibles'], 2)
        self.assertEqual(reporte['resumen']['semillas_agotadas'], 1)

        # Verificar valor total - corregir cálculo para incluir todas las semillas
        # Maíz: 800kg * 25 = 20000, Trigo: 0kg * 18 = 0, Soya: 500kg * 35 = 17500
        valor_esperado = Decimal('20000.00') + Decimal('0.00') + Decimal('17500.00')
        self.assertEqual(Decimal(reporte['resumen']['valor_total_inventario']), valor_esperado)

        # Limpiar semillas creadas en este test
        for lote in [f'INV001{self.unique_suffix}', f'INV002{self.unique_suffix}', f'INV003{self.unique_suffix}']:
            try:
                semilla = Semilla.objects.get(lote=lote)
                semilla.delete()
            except Semilla.DoesNotExist:
                pass

    def test_control_vencimientos_integrado(self):
        """Test: Control integrado de vencimientos"""
        # Crear semillas con diferentes fechas de vencimiento
        fechas_vencimiento = [
            date.today() + timedelta(days=400),  # Lejana
            date.today() + timedelta(days=15),   # Próxima
            date.today() - timedelta(days=5),    # Vencida
        ]

        lotes = [f'VEN{i+1:03d}{self.unique_suffix}' for i in range(3)]

        for i, (fecha, lote) in enumerate(zip(fechas_vencimiento, lotes)):
            # Determinar estado basado en la fecha
            estado = 'VENCIDA' if fecha < date.today() else 'DISPONIBLE'
            
            data = {
                "especie": f"Maíz Tipo {['Uno', 'Dos', 'Tres'][i]}",
                "variedad": f"Variedad {['A', 'B', 'C'][i]}",
                "cantidad": "100.00",
                "unidad_medida": "kg",
                "fecha_vencimiento": fecha.isoformat(),
                "porcentaje_germinacion": "95.50",
                "lote": lote,
                "proveedor": "Proveedor Test",
                "precio_unitario": "25.00",
                "ubicacion_almacen": "Almacen Test",
                "estado": estado,
                "observaciones": f"Test vencimiento {i}"
            }
            response = self.client.post('/api/semillas/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # === VERIFICAR ESTADOS ===
        semilla_futura = Semilla.objects.get(lote=f'VEN001{self.unique_suffix}')
        semilla_proxima = Semilla.objects.get(lote=f'VEN002{self.unique_suffix}')
        semilla_vencida = Semilla.objects.get(lote=f'VEN003{self.unique_suffix}')

        # La vencida debería estar marcada automáticamente
        self.assertEqual(semilla_vencida.estado, 'VENCIDA')

        # === ENDPOINTS DE VENCIMIENTO ===

        # Próximas a vencer
        response = self.client.get('/api/semillas/proximas_vencer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería incluir al menos la semilla próxima
        self.assertGreaterEqual(len(response.data), 1)

        # Vencidas
        response = self.client.get('/api/semillas/vencidas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debería incluir la semilla vencida
        self.assertGreaterEqual(len(response.data), 1)

        # === MARCAR MANUALMENTE ===
        response = self.client.post(
            f'/api/semillas/{semilla_proxima.pk}/marcar_vencida/',
            {'motivo': 'Vencimiento anticipado'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        semilla_proxima.refresh_from_db()
        self.assertEqual(semilla_proxima.estado, 'VENCIDA')

    def test_concurrencia_operaciones_inventario(self):
        """Test: Operaciones concurrentes en inventario"""
        # Crear semilla con stock inicial usando la API para consistencia
        data = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "1000.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "porcentaje_germinacion": "95.50",
            "lote": f"CONC001{self.unique_suffix}",
            "proveedor": "Proveedor Test",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Almacen Test",
            "observaciones": "Test concurrencia"
        }
        response = self.client.post('/api/semillas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        semilla_id = response.data['id']
        semilla = Semilla.objects.get(pk=semilla_id)

        # Simular operaciones "concurrentes" usando transacciones manuales
        resultados = []

        # Primera "operación concurrente"
        with transaction.atomic():
            semilla.refresh_from_db()
            nueva_cantidad = semilla.cantidad - Decimal('200.00')
            if nueva_cantidad >= 0:
                semilla.cantidad = nueva_cantidad
                semilla.save()
                resultados.append("Venta de 200kg exitosa")
            else:
                resultados.append("Venta de 200kg fallida - stock insuficiente")

        # Segunda "operación concurrente"
        with transaction.atomic():
            semilla.refresh_from_db()
            nueva_cantidad = semilla.cantidad - Decimal('300.00')
            if nueva_cantidad >= 0:
                semilla.cantidad = nueva_cantidad
                semilla.save()
                resultados.append("Venta de 300kg exitosa")
            else:
                resultados.append("Venta de 300kg fallida - stock insuficiente")

        # Tercera "operación concurrente" (debería fallar)
        with transaction.atomic():
            semilla.refresh_from_db()
            nueva_cantidad = semilla.cantidad - Decimal('600.00')
            if nueva_cantidad >= 0:
                semilla.cantidad = nueva_cantidad
                semilla.save()
                resultados.append("Venta de 600kg exitosa")
            else:
                resultados.append("Venta de 600kg fallida - stock insuficiente")

        # Verificar resultados
        semilla.refresh_from_db()

        # Deberían haber 2 ventas exitosas (200+300=500) y 1 fallida (600)
        ventas_exitosas = [r for r in resultados if "exitosa" in r]
        ventas_fallidas = [r for r in resultados if "fallida" in r]

        self.assertEqual(len(ventas_exitosas), 2)
        self.assertEqual(len(ventas_fallidas), 1)
        self.assertEqual(semilla.cantidad, Decimal('500.00'))  # 1000 - 200 - 300

    def test_auditoria_automatica_operaciones(self):
        """Test: Auditoría automática de todas las operaciones"""
        # Contar registros iniciales de auditoría
        auditoria_inicial = BitacoraAuditoria.objects.count()

        # Crear semilla
        data = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "500.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "porcentaje_germinacion": "95.50",
            "lote": f"AUD001{self.unique_suffix}",
            "proveedor": "Proveedor Test",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Almacen Test",
            "observaciones": "Test auditoria"
        }
        response = self.client.post('/api/semillas/', data, format='json')
        semilla_id = response.data['id']

        # Actualizar semilla
        self.client.patch(f'/api/semillas/{semilla_id}/', {'cantidad': '400.00'}, format='json')

        # Actualizar cantidad (acción personalizada)
        self.client.post(
            f'/api/semillas/{semilla_id}/actualizar_cantidad/',
            {'cantidad_cambio': '-200.00', 'motivo': 'Test'},  # Cambio negativo
            format='json'
        )

        # Eliminar semilla
        self.client.delete(f'/api/semillas/{semilla_id}/')

        # Verificar que se crearon registros de auditoría
        auditoria_final = BitacoraAuditoria.objects.count()
        registros_nuevos = auditoria_final - auditoria_inicial

        # Deberían haber al menos 3 operaciones auditadas (CREATE, UPDATE, DELETE)
        # La actualización personalizada puede o no crear un registro separado
        self.assertGreaterEqual(registros_nuevos, 3)

        # Verificar tipos de operaciones
        operaciones = BitacoraAuditoria.objects.filter(
            tabla_afectada='Semilla'
        ).values_list('accion', flat=True)

        self.assertIn('CREAR_SEMILLA', operaciones)
        self.assertIn('ACTUALIZAR_SEMILLA', operaciones)
        self.assertIn('ELIMINAR_SEMILLA', operaciones)

    def test_filtros_busqueda_avanzada_integrada(self):
        """Test: Sistema completo de filtros y búsqueda"""
        # Crear conjunto diverso de semillas
        semillas_data = [
            {"especie": "Maíz", "variedad": "Criollo", "lote": f"FLT001{self.unique_suffix}", "proveedor": "AgroA", "estado": "DISPONIBLE"},
            {"especie": "Maíz", "variedad": "Híbrido", "lote": f"FLT002{self.unique_suffix}", "proveedor": "AgroB", "estado": "DISPONIBLE"},
            {"especie": "Trigo", "variedad": "Cenizo", "lote": f"FLT003{self.unique_suffix}", "proveedor": "AgroA", "estado": "AGOTADA"},
            {"especie": "Soya", "variedad": "INTA", "lote": f"FLT004{self.unique_suffix}", "proveedor": "AgroC", "estado": "VENCIDA"},
            {"especie": "Girasol", "variedad": "Alto Oleico", "lote": f"FLT005{self.unique_suffix}", "proveedor": "AgroB", "estado": "DISPONIBLE"},
        ]

        for semilla_info in semillas_data:
            # Determinar fecha de vencimiento basada en el estado
            if semilla_info['estado'] == 'VENCIDA':
                fecha_venc = (date.today() - timedelta(days=30)).isoformat()  # Vencida hace 30 días
            else:
                fecha_venc = (date.today() + timedelta(days=365)).isoformat()  # Futura
            
            data = {
                "especie": semilla_info["especie"],
                "variedad": semilla_info["variedad"],
                "cantidad": "100.00" if semilla_info['estado'] != 'AGOTADA' else "0.00",
                "unidad_medida": "kg",
                "fecha_vencimiento": fecha_venc,
                "porcentaje_germinacion": "95.50",
                "lote": semilla_info["lote"],
                "proveedor": semilla_info["proveedor"],
                "precio_unitario": "25.00",
                "ubicacion_almacen": "Almacen Test",
                "estado": semilla_info["estado"],
                "observaciones": "Test filtros"
            }
            self.client.post('/api/semillas/', data, format='json')

        # === PRUEBAS DE FILTROS ===

        # 1. Filtro por especie - verificar que incluye las semillas de Maíz creadas en este test
        response = self.client.get('/api/semillas/', {'especie': 'Maíz'})
        self.assertGreaterEqual(response.data['count'], 2)  # Al menos las 2 semillas de Maíz creadas
        # Verificar que las semillas específicas existen en los resultados
        lotes_maiz = [s['lote'] for s in response.data['results']]
        self.assertIn(f'FLT001{self.unique_suffix}', lotes_maiz)
        self.assertIn(f'FLT002{self.unique_suffix}', lotes_maiz)

        # 2. Filtro por proveedor - verificar que incluye las semillas de AgroB creadas en este test
        response = self.client.get('/api/semillas/', {'proveedor': 'AgroB'})
        self.assertGreaterEqual(response.data['count'], 2)  # Al menos las 2 semillas de AgroB creadas
        # Verificar que las semillas específicas existen en los resultados
        lotes_agrob = [s['lote'] for s in response.data['results']]
        self.assertIn(f'FLT002{self.unique_suffix}', lotes_agrob)
        self.assertIn(f'FLT005{self.unique_suffix}', lotes_agrob)

        # 3. Filtro por estado - verificar que incluye las semillas DISPONIBLE creadas en este test
        response = self.client.get('/api/semillas/', {'estado': 'DISPONIBLE'})
        self.assertGreaterEqual(response.data['count'], 3)  # Al menos las 3 semillas DISPONIBLE creadas
        # Verificar que las semillas específicas existen en los resultados
        lotes_disponible = [s['lote'] for s in response.data['results']]
        self.assertIn(f'FLT001{self.unique_suffix}', lotes_disponible)
        self.assertIn(f'FLT002{self.unique_suffix}', lotes_disponible)
        self.assertIn(f'FLT005{self.unique_suffix}', lotes_disponible)

        # 4. Filtros combinados - verificar la semilla específica de Maíz y AgroA
        response = self.client.get('/api/semillas/', {
            'especie': 'Maíz',
            'proveedor': 'AgroA'
        })
        self.assertGreaterEqual(response.data['count'], 1)  # Al menos 1 semilla que cumple ambos criterios
        # Verificar que la semilla específica existe en los resultados
        lotes_maiz_agroa = [s['lote'] for s in response.data['results']]
        self.assertIn(f'FLT001{self.unique_suffix}', lotes_maiz_agroa)

        # 5. Búsqueda general - verificar la semilla específica con 'Criollo'
        response = self.client.get('/api/semillas/', {'search': 'Criollo'})
        self.assertGreaterEqual(response.data['count'], 1)  # Al menos 1 semilla que contiene 'Criollo'
        # Verificar que la semilla específica existe en los resultados
        lotes_criollo = [s['lote'] for s in response.data['results']]
        self.assertIn(f'FLT001{self.unique_suffix}', lotes_criollo)

        # 6. Rango de germinación - verificar que incluye las semillas creadas en este test
        response = self.client.get('/api/semillas/', {'pg_min': '90', 'pg_max': '100'})
        self.assertGreaterEqual(response.data['count'], 5)  # Al menos las 5 semillas creadas tienen 95.50%

        # 7. Ordenamiento múltiple - verificar orden correcto
        response = self.client.get('/api/semillas/', {'ordering': 'especie,-cantidad'})
        especies = [s['especie'] for s in response.data['results']]
        # Verificar que Girasol aparece antes que Maíz en orden alfabético
        girasol_index = next((i for i, e in enumerate(especies) if e == 'Girasol'), -1)
        maiz_index = next((i for i, e in enumerate(especies) if e == 'Maíz'), -1)
        if girasol_index >= 0 and maiz_index >= 0:
            self.assertLess(girasol_index, maiz_index)

        # Limpiar semillas creadas en este test
        for semilla_info in semillas_data:
            lote = semilla_info["lote"]
            try:
                semilla = Semilla.objects.get(lote=lote)
                semilla.delete()
            except Semilla.DoesNotExist:
                pass

    def test_recuperacion_errores_sistema(self):
        """Test: Recuperación de errores del sistema"""
        # Contar semillas existentes antes de este test
        semillas_antes = Semilla.objects.count()
        
        # Crear semilla válida
        data = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "500.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "porcentaje_germinacion": "95.50",
            "lote": f"ERR001{self.unique_suffix}",
            "proveedor": "Proveedor Test",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Almacen Test",
            "observaciones": "Test errores"
        }
        response = self.client.post('/api/semillas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        semilla_id = response.data['id']

        # Intentar operaciones inválidas y verificar recuperación

        # 1. Actualizar con cantidad negativa (debería fallar)
        response = self.client.post(
            f'/api/semillas/{semilla_id}/actualizar_cantidad/',
            {'cantidad_cambio': '-600.00', 'motivo': 'Test'},  # Cambio que resultaría en cantidad negativa
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar que la cantidad original se mantiene
        semilla = Semilla.objects.get(pk=semilla_id)
        self.assertEqual(semilla.cantidad, Decimal('500.00'))

        # 2. Intentar eliminar semilla inexistente
        response = self.client.delete('/api/semillas/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verificar que la semilla original sigue existiendo
        self.assertTrue(Semilla.objects.filter(pk=semilla_id).exists())

        # 3. Crear semilla con lote duplicado
        data_duplicada = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "500.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "porcentaje_germinacion": "95.50",
            "lote": f"DUP001{self.unique_suffix}",
            "proveedor": "Proveedor Test",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Almacen Test",
            "observaciones": "Test duplicado"
        }
        response = self.client.post('/api/semillas/', data_duplicada, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Crear primera vez

        # Intentar crear la misma semilla nuevamente (debería fallar)
        response = self.client.post('/api/semillas/', data_duplicada, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar que no se creó semilla adicional (debe haber 2 semillas nuevas en total)
        semillas_despues = Semilla.objects.count()
        self.assertEqual(semillas_despues, semillas_antes + 2)

        # Limpiar semillas creadas en este test
        for lote in [f"ERR001{self.unique_suffix}", f"DUP001{self.unique_suffix}"]:
            try:
                semilla = Semilla.objects.get(lote=lote)
                semilla.delete()
            except Semilla.DoesNotExist:
                pass

    def test_performance_consultas_complejas(self):
        """Test: Performance de consultas complejas"""
        # Crear muchas semillas para testing de performance
        import time

        semillas_creadas = []
        for i in range(50):  # Crear 50 semillas
            data = {
                "especie": f"Especie {['Uno', 'Dos', 'Tres', 'Cuatro', 'Cinco'][i%5]}",
                "variedad": f"Variedad {['A', 'B', 'C'][i%3]}",
                "cantidad": "100.00",
                "unidad_medida": "kg",
                "fecha_vencimiento": (date.today() + timedelta(days=365 - i)).isoformat(),
                "porcentaje_germinacion": "95.50",
                "lote": f"PERF{i:03d}{self.unique_suffix}",
                "proveedor": f"Proveedor {['A', 'B', 'C', 'D'][i%4]}",
                "precio_unitario": "25.00",
                "ubicacion_almacen": "Almacen Test",
                "observaciones": f"Test performance {i}"
            }
            response = self.client.post('/api/semillas/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            semillas_creadas.append(response.data['id'])

        # Medir tiempo de consultas complejas
        start_time = time.time()

        # Consulta con múltiples filtros
        response = self.client.get('/api/semillas/', {
            'especie': 'Especie Uno',
            'estado': 'DISPONIBLE',
            'pg_min': '90',
            'ordering': '-fecha_vencimiento'
        })

        end_time = time.time()
        query_time = end_time - start_time

        # Verificar que la consulta fue exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que el tiempo de respuesta es razonable (< 1 segundo)
        self.assertLess(query_time, 1.0, f"Consulta demasiado lenta: {query_time} segundos")

        # Verificar resultados
        self.assertGreater(response.data['count'], 0)

        # Limpiar semillas de performance
        for semilla_id in semillas_creadas:
            self.client.delete(f'/api/semillas/{semilla_id}/')