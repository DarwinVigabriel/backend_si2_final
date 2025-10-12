# 🧪 Tests de Admin de Insumos Agrícolas

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal

from cooperativa.models import Pesticida, Fertilizante
from cooperativa.admin import PesticidaAdmin, FertilizanteAdmin


class PesticidaAdminTest(TestCase):
    """Tests para la administración de Pesticidas"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)
        self.fecha_pasada = date.today() - timedelta(days=30)

        # Crear usuario admin
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

        # Crear sitio admin
        self.site = AdminSite()

        # Instancia del admin
        self.pesticida_admin = PesticidaAdmin(Pesticida, self.site)

    def test_list_display(self):
        """Test campos mostrados en la lista"""
        # Crear pesticida
        pesticida = Pesticida.objects.create(
            nombre_comercial='Test Admin',
            ingrediente_activo='Test Activo',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-ADMIN-001',
            proveedor='Admin Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Admin',
            estado='DISPONIBLE'
        )

        # Verificar campos en list_display
        self.assertIn('nombre_comercial', self.pesticida_admin.list_display)
        self.assertIn('tipo_pesticida', self.pesticida_admin.list_display)
        self.assertIn('cantidad', self.pesticida_admin.list_display)
        self.assertIn('estado', self.pesticida_admin.list_display)
        self.assertIn('fecha_vencimiento', self.pesticida_admin.list_display)
        self.assertIn('valor_total', self.pesticida_admin.list_display)

    def test_list_filter(self):
        """Test filtros disponibles"""
        # Verificar filtros configurados
        expected_filters = ['estado', 'tipo_pesticida', 'proveedor', 'fecha_vencimiento']
        for filter_field in expected_filters:
            self.assertIn(filter_field, self.pesticida_admin.list_filter)

    def test_search_fields(self):
        """Test campos de búsqueda"""
        # Verificar campos de búsqueda
        expected_search = ['nombre_comercial', 'ingrediente_activo', 'lote', 'proveedor']
        for search_field in expected_search:
            self.assertIn(search_field, self.pesticida_admin.search_fields)

    def test_readonly_fields(self):
        """Test campos de solo lectura"""
        # Verificar campos readonly
        self.assertIn('creado_en', self.pesticida_admin.readonly_fields)
        self.assertIn('actualizado_en', self.pesticida_admin.readonly_fields)

    def test_valor_total_readonly(self):
        """Test que valor_total se muestra como readonly"""
        # Crear pesticida
        pesticida = Pesticida.objects.create(
            nombre_comercial='Test Valor',
            ingrediente_activo='Test',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('50.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-VALOR-001',
            proveedor='Valor Provider',
            precio_unitario=Decimal('20.00'),
            ubicacion_almacen='Sector Valor',
            estado='DISPONIBLE'
        )

        # Verificar que valor_total se calcula correctamente
        self.assertEqual(pesticida.valor_total(), Decimal('1000.00'))

    def test_admin_changelist_view(self):
        """Test vista de lista en admin"""
        self.client.login(username='admin', password='admin123')

        # Crear algunos pesticidas
        for i in range(3):
            Pesticida.objects.create(
                nombre_comercial=f'Pesticida Admin {i}',
                ingrediente_activo=f'Activo {i}',
                tipo_pesticida='INSECTICIDA',
                concentracion='40% EC',
                cantidad=Decimal('100.00'),
                unidad_medida='Litros',
                fecha_vencimiento=self.fecha_futura,
                lote=f'LOT-ADMIN-LIST-{i}',
                proveedor='Admin List Provider',
                precio_unitario=Decimal('40.00'),
                ubicacion_almacen='Sector Admin',
                estado='DISPONIBLE' if i % 2 == 0 else 'AGOTADO'
            )

        url = reverse('admin:cooperativa_pesticida_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que se muestran los pesticidas
        self.assertContains(response, 'Pesticida Admin 0')
        self.assertContains(response, 'Pesticida Admin 1')
        self.assertContains(response, 'Pesticida Admin 2')

    def test_admin_change_view(self):
        """Test vista de detalle/edición en admin"""
        self.client.login(username='admin', password='admin123')

        # Crear pesticida
        pesticida = Pesticida.objects.create(
            nombre_comercial='Test Change',
            ingrediente_activo='Test',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-CHANGE-001',
            proveedor='Change Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Change',
            estado='DISPONIBLE'
        )

        url = reverse('admin:cooperativa_pesticida_change', args=(pesticida.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar campos en el formulario
        self.assertContains(response, 'Test Change')
        self.assertContains(response, 'LOT-CHANGE-001')

    def test_admin_add_view(self):
        """Test vista de agregar en admin"""
        self.client.login(username='admin', password='admin123')

        url = reverse('admin:cooperativa_pesticida_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el formulario está vacío
        self.assertContains(response, 'Agregar pesticida')

    def test_admin_delete_view(self):
        """Test vista de eliminar en admin"""
        self.client.login(username='admin', password='admin123')

        # Crear pesticida
        pesticida = Pesticida.objects.create(
            nombre_comercial='Test Delete',
            ingrediente_activo='Test',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-DELETE-001',
            proveedor='Delete Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Delete',
            estado='DISPONIBLE'
        )

        url = reverse('admin:cooperativa_pesticida_delete', args=(pesticida.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Delete')


class FertilizanteAdminTest(TestCase):
    """Tests para la administración de Fertilizantes"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)

        # Crear usuario admin
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

        # Crear sitio admin
        self.site = AdminSite()

        # Instancia del admin
        self.fertilizante_admin = FertilizanteAdmin(Fertilizante, self.site)

    def test_list_display_fertilizante(self):
        """Test campos mostrados en la lista de fertilizantes"""
        # Crear fertilizante
        fertilizante = Fertilizante.objects.create(
            nombre_comercial='NPK 15-15-15 Admin',
            tipo_fertilizante='COMPUESTO',
            composicion_npk='15-15-15',
            cantidad=Decimal('500.00'),
            unidad_medida='Kilogramos',
            lote='LOT-F-ADMIN-001',
            proveedor='Admin Nutri',
            precio_unitario=Decimal('25.00'),
            ubicacion_almacen='Sector Fert Admin',
            estado='DISPONIBLE'
        )

        # Verificar campos en list_display
        self.assertIn('nombre_comercial', self.fertilizante_admin.list_display)
        self.assertIn('composicion_npk', self.fertilizante_admin.list_display)
        self.assertIn('cantidad', self.fertilizante_admin.list_display)
        self.assertIn('estado', self.fertilizante_admin.list_display)
        self.assertIn('fecha_vencimiento', self.fertilizante_admin.list_display)
        self.assertIn('valor_total', self.fertilizante_admin.list_display)

    def test_list_filter_fertilizante(self):
        """Test filtros disponibles para fertilizantes"""
        expected_filters = ['estado', 'tipo_fertilizante', 'proveedor', 'fecha_vencimiento']
        for filter_field in expected_filters:
            self.assertIn(filter_field, self.fertilizante_admin.list_filter)

    def test_search_fields_fertilizante(self):
        """Test campos de búsqueda para fertilizantes"""
        expected_search = ['nombre_comercial', 'composicion_npk', 'lote', 'proveedor']
        for search_field in expected_search:
            self.assertIn(search_field, self.fertilizante_admin.search_fields)

    def test_npk_values_display(self):
        """Test display de valores NPK"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial='Test NPK',
            tipo_fertilizante='QUIMICO',
            composicion_npk='20-10-5',
            cantidad=Decimal('100.00'),
            unidad_medida='Kilogramos',
            lote='LOT-NPK-001',
            proveedor='NPK Provider',
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen='Sector NPK',
            estado='DISPONIBLE'
        )

        # Verificar cálculo de NPK
        npk_values = fertilizante.get_npk_values()
        self.assertEqual(npk_values['N'], 20)
        self.assertEqual(npk_values['P'], 10)
        self.assertEqual(npk_values['K'], 5)

    def test_admin_fertilizante_views(self):
        """Test vistas admin de fertilizantes"""
        self.client.login(username='admin', password='admin123')

        # Crear fertilizante
        fertilizante = Fertilizante.objects.create(
            nombre_comercial='Test Fert Admin',
            tipo_fertilizante='ORGANICO',
            composicion_npk='3-2-1',
            cantidad=Decimal('200.00'),
            unidad_medida='Kilogramos',
            materia_orgánica=Decimal('80.00'),
            lote='LOT-FERT-ADMIN-001',
            proveedor='Fert Admin Provider',
            precio_unitario=Decimal('15.00'),
            ubicacion_almacen='Sector Fert Admin',
            estado='DISPONIBLE'
        )

        # Test changelist
        url = reverse('admin:cooperativa_fertilizante_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Fert Admin')

        # Test change view
        url = reverse('admin:cooperativa_fertilizante_change', args=(fertilizante.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test add view
        url = reverse('admin:cooperativa_fertilizante_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AdminIntegrationTest(TestCase):
    """Tests de integración del admin"""

    def setUp(self):
        self.fecha_futura = date.today() + timedelta(days=365)

        # Crear usuario admin
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

    def test_admin_insumos_section(self):
        """Test que la sección 'insumos' existe en el admin"""
        self.client.login(username='admin', password='admin123')

        # Acceder al index del admin
        url = reverse('admin:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que aparecen las apps de insumos
        self.assertContains(response, 'Pesticidas')
        self.assertContains(response, 'Fertilizantes')

    def test_admin_bulk_actions(self):
        """Test acciones masivas en admin"""
        self.client.login(username='admin', password='admin123')

        # Crear múltiples pesticidas
        pesticidas = []
        for i in range(3):
            pesticida = Pesticida.objects.create(
                nombre_comercial=f'Pesticida Bulk {i}',
                ingrediente_activo=f'Activo {i}',
                tipo_pesticida='INSECTICIDA',
                concentracion='40% EC',
                cantidad=Decimal('100.00'),
                unidad_medida='Litros',
                fecha_vencimiento=self.fecha_futura,
                lote=f'LOT-BULK-{i}',
                proveedor='Bulk Provider',
                precio_unitario=Decimal('40.00'),
                ubicacion_almacen='Sector Bulk',
                estado='DISPONIBLE'
            )
            pesticidas.append(pesticida)

        # Verificar que se crearon
        self.assertEqual(Pesticida.objects.count(), 3)

        # Acceder a changelist
        url = reverse('admin:cooperativa_pesticida_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que todos aparecen
        for pesticida in pesticidas:
            self.assertContains(response, pesticida.nombre_comercial)

    def test_admin_filtering(self):
        """Test filtrado en admin"""
        self.client.login(username='admin', password='admin123')

        # Crear pesticidas con diferentes estados
        Pesticida.objects.create(
            nombre_comercial='Disponible',
            ingrediente_activo='Test',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-FILTER-DISP',
            proveedor='Filter Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Filter',
            estado='DISPONIBLE'
        )

        Pesticida.objects.create(
            nombre_comercial='Agotado',
            ingrediente_activo='Test',
            tipo_pesticida='FUNGICIDA',
            concentracion='50% WP',
            cantidad=Decimal('0.00'),
            unidad_medida='Kilogramos',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-FILTER-AGOT',
            proveedor='Filter Provider',
            precio_unitario=Decimal('50.00'),
            ubicacion_almacen='Sector Filter',
            estado='AGOTADO'
        )

        # Test filtro por estado
        url = reverse('admin:cooperativa_pesticida_changelist')
        response = self.client.get(url, {'estado': 'DISPONIBLE'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Disponible')
        self.assertNotContains(response, 'Agotado')

    def test_admin_search(self):
        """Test búsqueda en admin"""
        self.client.login(username='admin', password='admin123')

        # Crear pesticidas
        Pesticida.objects.create(
            nombre_comercial='Buscar Insecticida',
            ingrediente_activo='Test',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-SEARCH-INS',
            proveedor='Search Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Sector Search',
            estado='DISPONIBLE'
        )

        Pesticida.objects.create(
            nombre_comercial='Otro Producto',
            ingrediente_activo='Test',
            tipo_pesticida='FUNGICIDA',
            concentracion='50% WP',
            cantidad=Decimal('50.00'),
            unidad_medida='Kilogramos',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-SEARCH-OTHER',
            proveedor='Other Provider',
            precio_unitario=Decimal('50.00'),
            ubicacion_almacen='Sector Other',
            estado='DISPONIBLE'
        )

        # Test búsqueda
        url = reverse('admin:cooperativa_pesticida_changelist')
        response = self.client.get(url, {'q': 'Insecticida'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buscar Insecticida')
        self.assertNotContains(response, 'Otro Producto')