"""
Tests para la API de Semillas - CU7 Gestión de Semillas
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from cooperativa.models import Semilla, Usuario


class SemillaAPITest(APITestCase):
    """Tests de la API REST de Semillas"""

    def setUp(self):
        """Configuración inicial para cada test"""
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

        # Datos de prueba
        self.semilla_data = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": "500.00",
            "unidad_medida": "kg",
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "porcentaje_germinacion": "95.50",
            "lote": "MZ2025001",
            "proveedor": "AgroSemillas S.A.",
            "precio_unitario": "25.00",
            "ubicacion_almacen": "Sector A-15",
            "observaciones": "Lote premium"
        }

        # Crear semilla de prueba
        self.semilla = Semilla.objects.create(**{
            **self.semilla_data,
            'fecha_vencimiento': date.today() + timedelta(days=365)
        })

        # URLs
        self.url_list = reverse('semilla-list')

    def test_list_semillas_sin_autenticacion(self):
        """Test: Acceso denegado sin autenticación"""
        self.client.logout()
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_semillas_autenticado(self):
        """Test: Listar semillas con autenticación"""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn('count', data)
        self.assertIn('results', data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['results']), 1)

        # Verificar campos calculados
        semilla_data = data['results'][0]
        self.assertIn('valor_total', semilla_data)
        self.assertIn('dias_para_vencer', semilla_data)
        self.assertIn('esta_proxima_vencer', semilla_data)
        self.assertIn('esta_vencida', semilla_data)

    def test_create_semilla_exitosa(self):
        """Test: Crear semilla exitosamente"""
        data = self.semilla_data.copy()
        data['lote'] = 'MZ2025002'  # Lote diferente

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que se creó en BD
        self.assertEqual(Semilla.objects.count(), 2)

        # Verificar respuesta
        semilla_creada = Semilla.objects.get(lote='MZ2025002')
        self.assertEqual(semilla_creada.especie, "Maíz")
        self.assertEqual(semilla_creada.estado, "DISPONIBLE")

    def test_create_semilla_datos_invalidos(self):
        """Test: Crear semilla con datos inválidos"""
        data = self.semilla_data.copy()
        data['porcentaje_germinacion'] = '150.00'  # Inválido

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('porcentaje_germinacion', response.data)

    def test_create_semilla_lote_duplicado(self):
        """Test: Error al crear semilla con lote duplicado"""
        data = self.semilla_data.copy()
        # Mismo lote que la semilla existente

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_retrieve_semilla_existente(self):
        """Test: Obtener semilla específica"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['especie'], "Maíz")
        self.assertEqual(data['lote'], "MZ2025001")

    def test_retrieve_semilla_inexistente(self):
        """Test: Obtener semilla inexistente"""
        url = reverse('semilla-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_semilla_patch(self):
        """Test: Actualizar semilla parcialmente"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})
        data = {'cantidad': '400.00', 'observaciones': 'Actualizado'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar actualización
        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.cantidad, Decimal('400.00'))
        self.assertEqual(self.semilla.observaciones, 'Actualizado')

    def test_update_semilla_put(self):
        """Test: Actualizar semilla completamente"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})

        # PUT requiere todos los campos requeridos
        data = self.semilla_data.copy()
        data['cantidad'] = '300.00'
        data['observaciones'] = 'Actualizado completamente'

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar actualización
        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.cantidad, Decimal('300.00'))
        self.assertEqual(self.semilla.observaciones, 'Actualizado completamente')

    def test_update_semilla_estado_automatico(self):
        """Test: Actualización automática de estado"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})
        data = {'cantidad': '0.00'}  # Esto debería cambiar estado a AGOTADA

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.estado, 'AGOTADA')

    def test_delete_semilla(self):
        """Test: Eliminar semilla"""
        url = reverse('semilla-detail', kwargs={'pk': self.semilla.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verificar eliminación
        self.assertEqual(Semilla.objects.count(), 0)

    # ===== FILTROS Y BÚSQUEDA =====

    def test_filtros_por_especie(self):
        """Test: Filtrar semillas por especie"""
        # Crear otra semilla de diferente especie
        Semilla.objects.create(**{
            **self.semilla_data,
            'especie': 'Trigo',
            'lote': 'TR2025001',
            'fecha_vencimiento': date.today() + timedelta(days=365)
        })

        # Filtrar por Maíz
        response = self.client.get(self.url_list, {'especie': 'Maíz'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        # Filtrar por Trigo
        response = self.client.get(self.url_list, {'especie': 'Trigo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filtros_por_estado(self):
        """Test: Filtrar semillas por estado"""
        # Crear semilla agotada
        Semilla.objects.create(**{
            **self.semilla_data,
            'lote': 'MZ2025002',
            'cantidad': Decimal('0.00'),
            'fecha_vencimiento': date.today() + timedelta(days=365)
        })

        # Filtrar disponibles
        response = self.client.get(self.url_list, {'estado': 'DISPONIBLE'})
        self.assertEqual(response.data['count'], 1)

        # Filtrar agotadas
        response = self.client.get(self.url_list, {'estado': 'AGOTADA'})
        self.assertEqual(response.data['count'], 1)

    def test_filtros_por_fecha_vencimiento(self):
        """Test: Filtrar por rango de fechas de vencimiento"""
        fecha_desde = (date.today() + timedelta(days=300)).isoformat()
        fecha_hasta = (date.today() + timedelta(days=400)).isoformat()

        response = self.client.get(self.url_list, {
            'fecha_vencimiento_desde': fecha_desde,
            'fecha_vencimiento_hasta': fecha_hasta
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filtros_porcentaje_germinacion(self):
        """Test: Filtrar por rango de porcentaje de germinación"""
        response = self.client.get(self.url_list, {
            'pg_min': '90',
            'pg_max': '100'
        })
        self.assertEqual(response.data['count'], 1)

        # Fuera de rango
        response = self.client.get(self.url_list, {
            'pg_min': '50',
            'pg_max': '80'
        })
        self.assertEqual(response.data['count'], 0)

    def test_busqueda_general(self):
        """Test: Búsqueda general en múltiples campos"""
        # Buscar por especie
        response = self.client.get(self.url_list, {'search': 'Maíz'})
        self.assertEqual(response.data['count'], 1)

        # Buscar por variedad
        response = self.client.get(self.url_list, {'search': 'Criollo'})
        self.assertEqual(response.data['count'], 1)

        # Buscar por lote
        response = self.client.get(self.url_list, {'search': 'MZ2025001'})
        self.assertEqual(response.data['count'], 1)

        # Buscar por proveedor
        response = self.client.get(self.url_list, {'search': 'AgroSemillas'})
        self.assertEqual(response.data['count'], 1)

    def test_ordenamiento(self):
        """Test: Ordenamiento de resultados"""
        # Crear semillas con diferentes especies
        Semilla.objects.create(**{
            **self.semilla_data,
            'especie': 'Trigo',
            'lote': 'TR2025001',
            'fecha_vencimiento': date.today() + timedelta(days=365)
        })

        Semilla.objects.create(**{
            **self.semilla_data,
            'especie': 'Soya',
            'lote': 'SO2025001',
            'fecha_vencimiento': date.today() + timedelta(days=365)
        })

        # Ordenar por especie ascendente
        response = self.client.get(self.url_list, {'ordering': 'especie'})
        especies = [s['especie'] for s in response.data['results']]
        self.assertEqual(especies, ['Maíz', 'Soya', 'Trigo'])

        # Ordenar por especie descendente
        response = self.client.get(self.url_list, {'ordering': '-especie'})
        especies = [s['especie'] for s in response.data['results']]
        self.assertEqual(especies, ['Trigo', 'Soya', 'Maíz'])

    def test_paginacion(self):
        """Test: Paginación de resultados"""
        # Crear varias semillas
        for i in range(5):
            Semilla.objects.create(**{
                **self.semilla_data,
                'lote': f'MZ20250{i+2:02d}',
                'fecha_vencimiento': date.today() + timedelta(days=365)
            })

        # Página 1 (default page_size=25)
        response = self.client.get(self.url_list)
        self.assertEqual(response.data['count'], 6)
        self.assertIsNone(response.data['previous'])
        self.assertIsNone(response.data['next'])  # Todas caben en una página

        # Página con tamaño personalizado
        response = self.client.get(self.url_list, {'page_size': '3'})
        self.assertEqual(len(response.data['results']), 3)
        self.assertIn('next', response.data)
        self.assertIsNotNone(response.data['next'])

    # ===== ACCIONES PERSONALIZADAS =====

    def test_actualizar_cantidad_accion(self):
        """Test: Acción personalizada actualizar_cantidad"""
        url = reverse('semilla-actualizar-cantidad', kwargs={'pk': self.semilla.pk})
        data = {
            'cantidad_cambio': '100.00',  # Cambio positivo (entrada)
            'motivo': 'Ajuste de inventario'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar respuesta
        self.assertIn('mensaje', response.data)
        self.assertIn('tipo_movimiento', response.data)
        self.assertIn('cantidad_cambio', response.data)
        self.assertIn('semilla', response.data)

        # Verificar actualización en BD
        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.cantidad, Decimal('600.00'))  # 500 + 100

    def test_marcar_vencida_accion(self):
        """Test: Acción personalizada marcar_vencida"""
        url = reverse('semilla-marcar-vencida', kwargs={'pk': self.semilla.pk})
        data = {'motivo': 'Vencimiento detectado'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar respuesta
        self.assertIn('mensaje', response.data)
        self.assertIn('semilla', response.data)

        # Verificar actualización en BD
        self.semilla.refresh_from_db()
        self.assertEqual(self.semilla.estado, 'VENCIDA')

    def test_inventario_bajo_endpoint(self):
        """Test: Endpoint inventario_bajo"""
        # Crear semilla con poco stock
        Semilla.objects.create(**{
            **self.semilla_data,
            'lote': 'LOW2025001',
            'cantidad': Decimal('10.00'),  # Stock bajo
            'fecha_vencimiento': date.today() + timedelta(days=365)
        })

        url = reverse('semilla-inventario-bajo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Debería incluir la semilla de bajo stock
        self.assertGreaterEqual(len(response.data), 1)

    def test_proximas_vencer_endpoint(self):
        """Test: Endpoint próximas a vencer"""
        # Crear semilla próxima a vencer
        Semilla.objects.create(**{
            **self.semilla_data,
            'lote': 'EXP2025001',
            'fecha_vencimiento': date.today() + timedelta(days=15),  # Próxima a vencer
        })

        url = reverse('semilla-proximas-vencer')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Debería incluir la semilla próxima a vencer
        self.assertGreaterEqual(len(response.data), 1)

    def test_vencidas_endpoint(self):
        """Test: Endpoint semillas vencidas"""
        # Crear semilla vencida
        Semilla.objects.create(**{
            **self.semilla_data,
            'lote': 'VEN2025001',
            'fecha_vencimiento': date.today() - timedelta(days=1),  # Ya vencida
        })

        # No hay endpoint específico para vencidas, verificar que aparecen en proximas_vencer con días=0
        url = reverse('semilla-proximas-vencer')
        response = self.client.get(url, {'dias': '0'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Debería incluir la semilla vencida
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_reporte_inventario_endpoint(self):
        """Test: Endpoint reporte de inventario"""
        # Crear varias semillas para el reporte
        Semilla.objects.create(**{
            **self.semilla_data,
            'especie': 'Trigo',
            'lote': 'TR2025001',
            'cantidad': Decimal('200.00'),
            'precio_unitario': Decimal('15.00'),
            'fecha_vencimiento': date.today() + timedelta(days=365)
        })

        url = reverse('semilla-reporte-inventario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        # Verificar estructura del reporte
        self.assertIn('resumen', data)
        self.assertIn('cantidad_por_especie', data)
        self.assertIn('semillas_por_proveedor', data)

        # Verificar estadísticas generales
        estadisticas = data['resumen']
        self.assertIn('total_semillas', estadisticas)
        self.assertIn('semillas_disponibles', estadisticas)
        self.assertIn('valor_total_inventario', estadisticas)
        self.assertEqual(estadisticas['total_semillas'], 2)

    # ===== VALIDACIONES EN API =====

    def test_api_validacion_campos_requeridos(self):
        """Test: Validación de campos requeridos en API"""
        data = {}  # Datos vacíos

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verificar que se reportan los campos requeridos
        errores = response.data
        campos_requeridos = [
            'especie', 'variedad', 'cantidad', 'fecha_vencimiento', 'porcentaje_germinacion'
        ]

        for campo in campos_requeridos:
            self.assertIn(campo, errores)

    def test_api_validacion_porcentaje_germinacion(self):
        """Test: Validación de porcentaje de germinación en API"""
        data = self.semilla_data.copy()
        data['lote'] = 'TEST001'
        data['porcentaje_germinacion'] = '150.00'  # Inválido

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('porcentaje_germinacion', response.data)

    def test_api_validacion_fecha_vencimiento_pasada(self):
        """Test: Validación de fecha de vencimiento pasada en API"""
        data = self.semilla_data.copy()
        data['lote'] = 'TEST002'
        data['fecha_vencimiento'] = (date.today() - timedelta(days=1)).isoformat()

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_vencimiento', response.data)

    def test_api_validacion_precio_cero(self):
        """Test: Validación de precio unitario negativo en API"""
        data = self.semilla_data.copy()
        data['lote'] = 'TEST003'
        data['precio_unitario'] = '-10.00'  # Negativo (inválido)

        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('precio_unitario', response.data)