# 🧪 Tests de Views de Insumos Agrícolas

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal

from cooperativa.models import Pesticida, Fertilizante


class PesticidaAPITest(APITestCase):
    """Tests para la API de Pesticidas"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)
        self.fecha_cerca = date.today() + timedelta(days=15)
        self.fecha_pasada = date.today() - timedelta(days=30)

        # Crear usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Datos de prueba para pesticida
        self.pesticida_data = {
            'nombre_comercial': 'Roundup API',
            'ingrediente_activo': 'Glifosato',
            'tipo_pesticida': 'HERBICIDA',
            'concentracion': '48% EC',
            'registro_sanitario': 'REG-API-001',
            'cantidad': '100.00',
            'unidad_medida': 'Litros',
            'fecha_vencimiento': str(self.fecha_futura),
            'dosis_recomendada': '2-3 L/ha',
            'lote': 'LOT-API-001',
            'proveedor': 'API Provider',
            'precio_unitario': '45.50',
            'ubicacion_almacen': 'Sector API',
            'estado': 'DISPONIBLE',
            'observaciones': 'Test API'
        }

    def test_list_pesticidas_sin_autenticacion(self):
        """Test acceso no autorizado a lista de pesticidas"""
        url = reverse('pesticida-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_pesticidas_con_autenticacion(self):
        """Test lista de pesticidas con autenticación"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pesticida-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)  # Sin datos inicialmente

    def test_create_pesticida(self):
        """Test creación de pesticida vía API"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pesticida-list')
        response = self.client.post(url, self.pesticida_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre_comercial'], 'Roundup API')

    def test_create_pesticida_datos_invalidos(self):
        """Test creación con datos inválidos"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('pesticida-list')

        # Datos inválidos
        invalid_data = self.pesticida_data.copy()
        invalid_data['cantidad'] = '-50.00'  # Cantidad negativa

        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cantidad', response.data)

    def test_retrieve_pesticida(self):
        """Test obtener detalle de pesticida"""
        self.client.login(username='testuser', password='testpass123')

        # Crear pesticida
        pesticida = Pesticida.objects.create(**{
            k: v for k, v in self.pesticida_data.items()
            if k not in ['fecha_vencimiento']  # Excluir fecha para conversión
        })
        pesticida.fecha_vencimiento = self.fecha_futura
        pesticida.save()

        url = reverse('pesticida-detail', kwargs={'pk': pesticida.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], pesticida.pk)

    def test_update_pesticida(self):
        """Test actualización de pesticida"""
        self.client.login(username='testuser', password='testpass123')

        # Crear pesticida
        pesticida = Pesticida.objects.create(**{
            k: v for k, v in self.pesticida_data.items()
            if k not in ['fecha_vencimiento']
        })
        pesticida.fecha_vencimiento = self.fecha_futura
        pesticida.save()

        url = reverse('pesticida-detail', kwargs={'pk': pesticida.pk})

        # Datos de actualización
        update_data = {
            'cantidad': '150.00',
            'observaciones': 'Actualizado vía API'
        }

        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cantidad'], '150.00')

    def test_delete_pesticida(self):
        """Test eliminación de pesticida"""
        self.client.login(username='testuser', password='testpass123')

        # Crear pesticida
        pesticida = Pesticida.objects.create(**{
            k: v for k, v in self.pesticida_data.items()
            if k not in ['fecha_vencimiento']
        })
        pesticida.fecha_vencimiento = self.fecha_futura
        pesticida.save()

        url = reverse('pesticida-detail', kwargs={'pk': pesticida.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verificar eliminación
        self.assertFalse(Pesticida.objects.filter(pk=pesticida.pk).exists())

    def test_filtros_pesticidas(self):
        """Test filtros de búsqueda"""
        self.client.login(username='testuser', password='testpass123')

        # Crear pesticidas con diferentes características
        Pesticida.objects.create(
            nombre_comercial='Insecticida Test',
            ingrediente_activo='Test Activo',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-FILTER-001',
            proveedor='Filter Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Filter',
            estado='DISPONIBLE'
        )

        Pesticida.objects.create(
            nombre_comercial='Herbicida Test',
            ingrediente_activo='Herb Activo',
            tipo_pesticida='HERBICIDA',
            concentracion='50% WP',
            cantidad=Decimal('200.00'),
            unidad_medida='Kilogramos',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-FILTER-002',
            proveedor='Filter Provider',
            precio_unitario=Decimal('50.00'),
            ubicacion_almacen='Sector Filter',
            estado='AGOTADO'
        )

        url = reverse('pesticida-list')

        # Filtrar por estado
        response = self.client.get(url, {'estado': 'DISPONIBLE'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        # Filtrar por tipo
        response = self.client.get(url, {'tipo_pesticida': 'INSECTICIDA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        # Búsqueda por nombre
        response = self.client.get(url, {'search': 'Insecticida'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_acciones_personalizadas_pesticida(self):
        """Test acciones personalizadas del ViewSet"""
        self.client.login(username='testuser', password='testpass123')

        # Crear pesticida
        pesticida = Pesticida.objects.create(
            nombre_comercial='Test Acciones',
            ingrediente_activo='Test',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-ACTION-001',
            proveedor='Action Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Action',
            estado='DISPONIBLE'
        )

        # Acción: actualizar cantidad
        url = reverse('pesticida-actualizar-cantidad', kwargs={'pk': pesticida.pk})
        response = self.client.post(url, {'cantidad': '75.00', 'motivo': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pesticida.refresh_from_db()
        self.assertEqual(pesticida.cantidad, Decimal('75.00'))

        # Acción: marcar como vencido
        url = reverse('pesticida-marcar-vencido', kwargs={'pk': pesticida.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pesticida.refresh_from_db()
        self.assertEqual(pesticida.estado, 'VENCIDO')

    def test_proximos_vencer_pesticidas(self):
        """Test endpoint de pesticidas próximos a vencer"""
        self.client.login(username='testuser', password='testpass123')

        # Crear pesticida próximo a vencer
        Pesticida.objects.create(
            nombre_comercial='Próximo Vencer',
            ingrediente_activo='Test',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('50.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_cerca,
            lote='LOT-VENCER-001',
            proveedor='Vencer Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Vencer',
            estado='DISPONIBLE'
        )

        url = reverse('pesticida-proximos-vencer')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_reporte_inventario_pesticidas(self):
        """Test reporte de inventario de pesticidas"""
        self.client.login(username='testuser', password='testpass123')

        # Crear algunos pesticidas
        for i in range(3):
            Pesticida.objects.create(
                nombre_comercial=f'Pesticida Report {i}',
                ingrediente_activo=f'Activo {i}',
                tipo_pesticida='INSECTICIDA' if i % 2 == 0 else 'FUNGICIDA',
                concentracion='40% EC',
                cantidad=Decimal('100.00'),
                unidad_medida='Litros',
                fecha_vencimiento=self.fecha_futura,
                lote=f'LOT-REPORT-{i}',
                proveedor='Report Provider',
                precio_unitario=Decimal('40.00'),
                ubicacion_almacen='Sector Report',
                estado='DISPONIBLE'
            )

        url = reverse('pesticida-reporte-inventario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar estructura del reporte
        self.assertIn('total_pesticidas', response.data)
        self.assertIn('valor_total_inventario', response.data)
        self.assertIn('distribucion_por_tipo', response.data)
        self.assertEqual(response.data['total_pesticidas'], 3)


class FertilizanteAPITest(APITestCase):
    """Tests para la API de Fertilizantes"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)

        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Datos de prueba para fertilizante
        self.fertilizante_data = {
            'nombre_comercial': 'NPK 15-15-15 API',
            'tipo_fertilizante': 'COMPUESTO',
            'composicion_npk': '15-15-15',
            'cantidad': '500.00',
            'unidad_medida': 'Kilogramos',
            'fecha_vencimiento': str(self.fecha_futura),
            'dosis_recomendada': '200-300 kg/ha',
            'lote': 'LOT-F-API-001',
            'proveedor': 'API Nutri',
            'precio_unitario': '25.50',
            'ubicacion_almacen': 'Sector Fert API',
            'estado': 'DISPONIBLE',
            'observaciones': 'Test API Fertilizante'
        }

    def test_create_fertilizante(self):
        """Test creación de fertilizante vía API"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('fertilizante-list')
        response = self.client.post(url, self.fertilizante_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre_comercial'], 'NPK 15-15-15 API')

    def test_create_fertilizante_organico(self):
        """Test creación de fertilizante orgánico"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('fertilizante-list')

        data = self.fertilizante_data.copy()
        data['tipo_fertilizante'] = 'ORGANICO'
        data['composicion_npk'] = '3-2-1'
        data['materia_orgánica'] = '85.50'
        data['lote'] = 'LOT-ORG-API-001'

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_acciones_fertilizante(self):
        """Test acciones personalizadas de fertilizante"""
        self.client.login(username='testuser', password='testpass123')

        # Crear fertilizante
        fertilizante = Fertilizante.objects.create(
            nombre_comercial='Test Fertilizante',
            tipo_fertilizante='QUIMICO',
            composicion_npk='10-10-10',
            cantidad=Decimal('200.00'),
            unidad_medida='Kilogramos',
            lote='LOT-F-ACTION-001',
            proveedor='Action Provider',
            precio_unitario=Decimal('20.00'),
            ubicacion_almacen='Sector Action',
            estado='DISPONIBLE'
        )

        # Actualizar cantidad
        url = reverse('fertilizante-actualizar-cantidad', kwargs={'pk': fertilizante.pk})
        response = self.client.post(url, {'cantidad': '150.00', 'motivo': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fertilizante.refresh_from_db()
        self.assertEqual(fertilizante.cantidad, Decimal('150.00'))

    def test_reporte_inventario_fertilizantes(self):
        """Test reporte de inventario de fertilizantes"""
        self.client.login(username='testuser', password='testpass123')

        # Crear fertilizantes
        for i in range(2):
            Fertilizante.objects.create(
                nombre_comercial=f'Fertilizante Report {i}',
                tipo_fertilizante='QUIMICO',
                composicion_npk='15-15-15',
                cantidad=Decimal('300.00'),
                unidad_medida='Kilogramos',
                lote=f'LOT-F-REPORT-{i}',
                proveedor='Report Nutri',
                precio_unitario=Decimal('25.00'),
                ubicacion_almacen='Sector Report',
                estado='DISPONIBLE'
            )

        url = reverse('fertilizante-reporte-inventario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_fertilizantes', response.data)
        self.assertEqual(response.data['total_fertilizantes'], 2)


class InsumosAPIIntegrationTest(APITestCase):
    """Tests de integración de la API de insumos"""

    def setUp(self):
        self.fecha_futura = date.today() + timedelta(days=365)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_api_completa_insumos(self):
        """Test flujo completo de la API de insumos"""
        self.client.login(username='testuser', password='testpass123')

        # 1. Crear pesticidas
        pesticida_data = {
            'nombre_comercial': 'Integration Test',
            'ingrediente_activo': 'Test Activo',
            'tipo_pesticida': 'INSECTICIDA',
            'concentracion': '40% EC',
            'cantidad': '100.00',
            'unidad_medida': 'Litros',
            'fecha_vencimiento': str(self.fecha_futura),
            'lote': 'LOT-INTEGRATION-001',
            'proveedor': 'Integration Provider',
            'precio_unitario': '40.00',
            'ubicacion_almacen': 'Sector Integration',
            'estado': 'DISPONIBLE'
        }

        url = reverse('pesticida-list')
        response = self.client.post(url, pesticida_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pesticida_id = response.data['id']

        # 2. Crear fertilizantes
        fertilizante_data = {
            'nombre_comercial': 'NPK Integration',
            'tipo_fertilizante': 'COMPUESTO',
            'composicion_npk': '15-15-15',
            'cantidad': '200.00',
            'unidad_medida': 'Kilogramos',
            'lote': 'LOT-F-INTEGRATION-001',
            'proveedor': 'Integration Nutri',
            'precio_unitario': '25.00',
            'ubicacion_almacen': 'Sector Integration',
            'estado': 'DISPONIBLE'
        }

        url = reverse('fertilizante-list')
        response = self.client.post(url, fertilizante_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        fertilizante_id = response.data['id']

        # 3. Listar todos los insumos
        url = reverse('pesticida-list')
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)

        url = reverse('fertilizante-list')
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)

        # 4. Actualizar insumos
        url = reverse('pesticida-detail', kwargs={'pk': pesticida_id})
        response = self.client.patch(url, {'cantidad': '80.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5. Verificar reportes
        url = reverse('pesticida-reporte-inventario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('fertilizante-reporte-inventario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6. Eliminar insumos
        url = reverse('pesticida-detail', kwargs={'pk': pesticida_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('fertilizante-detail', kwargs={'pk': fertilizante_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)