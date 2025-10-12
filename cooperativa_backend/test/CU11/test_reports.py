"""
CU11: TESTS PARA REPORTES DE CAMPAÑAS
T053: Pruebas funcionales de reportes

Tests para verificar cálculos correctos en:
- T039: Reporte de labores por campaña
- T050: Reporte de producción por campaña
- T052: Reporte de producción por parcela
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, date, timedelta
from decimal import Decimal

from cooperativa.models import (
    Campaign, CampaignPlot, Socio, Parcela, Comunidad,
    CicloCultivo, Cultivo, Tratamiento, Cosecha
)
from cooperativa.reports import CampaignReports

Usuario = get_user_model()


class LaborsByCampaignReportTest(TestCase):
    """
    T039: Tests para reporte de labores por campaña
    """

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario
        self.user = Usuario.objects.create_user(
            ci_nit='1234567',
            nombres='Test',
            apellidos='User',
            email='test@test.com',
            usuario='test',
            password='testpass123'
        )

        # Crear comunidad y socio
        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio = Socio.objects.create(
            usuario=self.user,
            comunidad=self.comunidad,
            estado='ACTIVO'
        )

        # Crear parcela
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=Decimal('10.00'),
            estado='ACTIVA'
        )

        # Crear campaña
        self.campaign = Campaign.objects.create(
            nombre='Campaña Test',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        # Asociar parcela a campaña
        CampaignPlot.objects.create(
            campaign=self.campaign,
            parcela=self.parcela
        )

        # Crear cultivo y ciclo
        self.cultivo = Cultivo.objects.create(
            parcela=self.parcela,
            especie='Maíz',
            estado='ACTIVO'
        )

        self.ciclo = CicloCultivo.objects.create(
            cultivo=self.cultivo,
            fecha_inicio=date(2024, 1, 15),
            fecha_estimada_fin=date(2024, 6, 15),
            estado='EN_CRECIMIENTO'
        )

        # Crear tratamientos (labores)
        Tratamiento.objects.create(
            ciclo_cultivo=self.ciclo,
            tipo_tratamiento='FERTILIZANTE',
            nombre_producto='Urea',
            dosis=Decimal('100.00'),
            unidad_dosis='kg/ha',
            fecha_aplicacion=date(2024, 2, 1),
            costo=Decimal('500.00')
        )

        Tratamiento.objects.create(
            ciclo_cultivo=self.ciclo,
            tipo_tratamiento='PESTICIDA',
            nombre_producto='Insecticida X',
            dosis=Decimal('2.00'),
            unidad_dosis='L/ha',
            fecha_aplicacion=date(2024, 3, 1),
            costo=Decimal('300.00')
        )

    def test_reporte_labores_basico(self):
        """Test reporte básico de labores"""
        report = CampaignReports.get_labors_by_campaign(
            campaign_id=self.campaign.id
        )

        self.assertIn('campaign', report)
        self.assertIn('estadisticas', report)
        self.assertEqual(report['estadisticas']['total_labors'], 2)
        self.assertEqual(float(report['estadisticas']['costo_total_labores']), 800.00)

    def test_reporte_labores_filtro_tipo(self):
        """Test reporte de labores filtrado por tipo"""
        report = CampaignReports.get_labors_by_campaign(
            campaign_id=self.campaign.id,
            tipo_tratamiento='FERTILIZANTE'
        )

        self.assertEqual(report['estadisticas']['total_labors'], 1)
        self.assertEqual(
            report['labors_detail'][0]['tipo_tratamiento'],
            'FERTILIZANTE'
        )

    def test_reporte_labores_filtro_fechas(self):
        """Test reporte de labores filtrado por rango de fechas"""
        report = CampaignReports.get_labors_by_campaign(
            campaign_id=self.campaign.id,
            start_date=date(2024, 2, 15),
            end_date=date(2024, 3, 31)
        )

        self.assertEqual(report['estadisticas']['total_labors'], 1)
        self.assertEqual(
            report['labors_detail'][0]['tipo_tratamiento'],
            'PESTICIDA'
        )

    def test_reporte_labores_area_trabajada(self):
        """Test cálculo de área trabajada"""
        report = CampaignReports.get_labors_by_campaign(
            campaign_id=self.campaign.id
        )

        self.assertEqual(
            float(report['estadisticas']['total_area_worked']),
            10.00
        )

    def test_reporte_labores_campaign_no_existe(self):
        """Test reporte con campaña inexistente"""
        report = CampaignReports.get_labors_by_campaign(
            campaign_id=99999
        )

        self.assertIn('error', report)


class ProductionByCampaignReportTest(TestCase):
    """
    T050: Tests para reporte de producción por campaña
    """

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario
        self.user = Usuario.objects.create_user(
            ci_nit='1234567',
            nombres='Test',
            apellidos='User',
            email='test@test.com',
            usuario='test',
            password='testpass123'
        )

        # Crear comunidad y socio
        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio = Socio.objects.create(
            usuario=self.user,
            comunidad=self.comunidad,
            estado='ACTIVO'
        )

        # Crear parcela
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=Decimal('10.00'),
            estado='ACTIVA'
        )

        # Crear campaña
        self.campaign = Campaign.objects.create(
            nombre='Campaña Test',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00'),
            unidad_meta='kg'
        )

        # Asociar parcela a campaña
        CampaignPlot.objects.create(
            campaign=self.campaign,
            parcela=self.parcela
        )

        # Crear cultivo y ciclo
        self.cultivo = Cultivo.objects.create(
            parcela=self.parcela,
            especie='Maíz',
            estado='ACTIVO'
        )

        self.ciclo = CicloCultivo.objects.create(
            cultivo=self.cultivo,
            fecha_inicio=date(2024, 1, 15),
            fecha_estimada_fin=date(2024, 6, 15),
            estado='FINALIZADO'
        )

        # Crear cosechas
        Cosecha.objects.create(
            ciclo_cultivo=self.ciclo,
            fecha_cosecha=date(2024, 6, 10),
            cantidad_cosechada=Decimal('8000.00'),
            unidad_medida='kg',
            calidad='BUENA',
            estado='COMPLETADA',
            precio_venta=Decimal('2.50')
        )

        Cosecha.objects.create(
            ciclo_cultivo=self.ciclo,
            fecha_cosecha=date(2024, 6, 15),
            cantidad_cosechada=Decimal('3000.00'),
            unidad_medida='kg',
            calidad='EXCELENTE',
            estado='COMPLETADA',
            precio_venta=Decimal('3.00')
        )

    def test_reporte_produccion_basico(self):
        """Test reporte básico de producción"""
        report = CampaignReports.get_production_by_campaign(
            campaign_id=self.campaign.id
        )

        self.assertIn('campaign', report)
        self.assertIn('estadisticas', report)
        self.assertEqual(
            float(report['estadisticas']['total_production']),
            11000.00
        )

    def test_reporte_rendimiento_por_hectarea(self):
        """Test cálculo de rendimiento promedio por hectárea"""
        report = CampaignReports.get_production_by_campaign(
            campaign_id=self.campaign.id
        )

        # 11000 kg / 10 ha = 1100 kg/ha
        self.assertEqual(
            float(report['estadisticas']['avg_yield_per_hectare']),
            1100.00
        )

    def test_reporte_comparativa_con_meta(self):
        """Test comparativa con meta de producción"""
        report = CampaignReports.get_production_by_campaign(
            campaign_id=self.campaign.id
        )

        self.assertIn('comparativa_meta', report)
        # Meta: 10000, Producción: 11000
        self.assertEqual(
            float(report['comparativa_meta']['meta_produccion']),
            10000.00
        )
        self.assertEqual(
            float(report['comparativa_meta']['produccion_real']),
            11000.00
        )
        self.assertEqual(
            float(report['comparativa_meta']['diferencia']),
            1000.00
        )
        self.assertTrue(report['comparativa_meta']['cumplida'])
        self.assertEqual(
            float(report['comparativa_meta']['porcentaje_cumplimiento']),
            110.00
        )

    def test_reporte_produccion_por_producto(self):
        """Test agrupación de producción por producto"""
        report = CampaignReports.get_production_by_campaign(
            campaign_id=self.campaign.id
        )

        self.assertIn('production_by_product', report)
        productos = report['production_by_product']
        self.assertEqual(len(productos), 1)
        self.assertEqual(productos[0]['cultivo_especie'], 'Maíz')
        self.assertEqual(
            float(productos[0]['cantidad_total']),
            11000.00
        )

    def test_reporte_valor_economico(self):
        """Test cálculo de valor económico total"""
        report = CampaignReports.get_production_by_campaign(
            campaign_id=self.campaign.id
        )

        # (8000 * 2.50) + (3000 * 3.00) = 20000 + 9000 = 29000
        self.assertEqual(
            float(report['estadisticas']['valor_economico_total']),
            29000.00
        )


class ProductionByPlotReportTest(TestCase):
    """
    T052: Tests para reporte de producción por parcela
    """

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario
        self.user = Usuario.objects.create_user(
            ci_nit='1234567',
            nombres='Test',
            apellidos='User',
            email='test@test.com',
            usuario='test',
            password='testpass123'
        )

        # Crear comunidad y socio
        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio = Socio.objects.create(
            usuario=self.user,
            comunidad=self.comunidad,
            estado='ACTIVO'
        )

        # Crear parcela
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=Decimal('10.00'),
            estado='ACTIVA'
        )

        # Crear campaña
        self.campaign = Campaign.objects.create(
            nombre='Campaña Test',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        # Asociar parcela a campaña
        CampaignPlot.objects.create(
            campaign=self.campaign,
            parcela=self.parcela,
            meta_produccion_parcela=Decimal('5000.00')
        )

        # Crear cultivo y ciclo
        self.cultivo = Cultivo.objects.create(
            parcela=self.parcela,
            especie='Maíz',
            variedad='Híbrido X',
            estado='ACTIVO'
        )

        self.ciclo = CicloCultivo.objects.create(
            cultivo=self.cultivo,
            fecha_inicio=date(2024, 1, 15),
            fecha_estimada_fin=date(2024, 6, 15),
            estado='FINALIZADO'
        )

        # Crear cosecha
        Cosecha.objects.create(
            ciclo_cultivo=self.ciclo,
            fecha_cosecha=date(2024, 6, 10),
            cantidad_cosechada=Decimal('6000.00'),
            unidad_medida='kg',
            calidad='BUENA',
            estado='COMPLETADA',
            precio_venta=Decimal('2.50')
        )

    def test_reporte_produccion_parcela_basico(self):
        """Test reporte básico de producción por parcela"""
        report = CampaignReports.get_production_by_plot(
            plot_id=self.parcela.id
        )

        self.assertIn('parcela', report)
        self.assertIn('estadisticas', report)
        self.assertEqual(
            float(report['estadisticas']['total_production']),
            6000.00
        )

    def test_reporte_rendimiento_parcela(self):
        """Test cálculo de rendimiento por hectárea de la parcela"""
        report = CampaignReports.get_production_by_plot(
            plot_id=self.parcela.id
        )

        # 6000 kg / 10 ha = 600 kg/ha
        self.assertEqual(
            float(report['estadisticas']['yield_per_hectare']),
            600.00
        )

    def test_reporte_productos_cosechados(self):
        """Test listado de productos cosechados"""
        report = CampaignReports.get_production_by_plot(
            plot_id=self.parcela.id
        )

        self.assertIn('productos_cosechados', report)
        productos = report['productos_cosechados']
        self.assertEqual(len(productos), 1)
        self.assertEqual(productos[0]['cultivo_especie'], 'Maíz')
        self.assertEqual(productos[0]['cultivo_variedad'], 'Híbrido X')

    def test_reporte_historico_campañas(self):
        """Test histórico de producción por campañas"""
        report = CampaignReports.get_production_by_plot(
            plot_id=self.parcela.id
        )

        self.assertIn('historico_campañas', report)
        historico = report['historico_campañas']
        self.assertEqual(len(historico), 1)
        self.assertEqual(historico[0]['campaign_nombre'], 'Campaña Test')
        self.assertEqual(
            float(historico[0]['produccion_total']),
            6000.00
        )

    def test_reporte_filtro_por_campaña(self):
        """Test reporte filtrado por campaña específica"""
        report = CampaignReports.get_production_by_plot(
            plot_id=self.parcela.id,
            campaign_id=self.campaign.id
        )

        self.assertIn('filtros_aplicados', report)
        self.assertEqual(report['filtros_aplicados']['campaign_id'], self.campaign.id)

    def test_reporte_filtro_por_fechas(self):
        """Test reporte filtrado por rango de fechas"""
        report = CampaignReports.get_production_by_plot(
            plot_id=self.parcela.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 30)
        )

        self.assertEqual(
            float(report['estadisticas']['total_production']),
            6000.00
        )

    def test_reporte_parcela_no_existe(self):
        """Test reporte con parcela inexistente"""
        report = CampaignReports.get_production_by_plot(
            plot_id=99999
        )

        self.assertIn('error', report)


class ReportsAPITest(APITestCase):
    """
    Tests de endpoints API para reportes
    """

    def setUp(self):
        """Configurar cliente API y datos de prueba"""
        self.client = APIClient()

        # Crear usuario administrador
        self.admin_user = Usuario.objects.create_user(
            ci_nit='1234567',
            nombres='Admin',
            apellidos='Test',
            email='admin@test.com',
            usuario='admin',
            password='testpass123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        # Crear campaña
        self.campaign = Campaign.objects.create(
            nombre='Campaña API Test',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        # Autenticar cliente
        self.client.force_authenticate(user=self.admin_user)

    def test_api_reporte_labores(self):
        """Test endpoint de reporte de labores"""
        response = self.client.get(
            f'/api/reports/labors-by-campaign/?campaign_id={self.campaign.id}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('campaign', response.data)
        self.assertIn('estadisticas', response.data)

    def test_api_reporte_produccion_campaña(self):
        """Test endpoint de reporte de producción por campaña"""
        response = self.client.get(
            f'/api/reports/production-by-campaign/?campaign_id={self.campaign.id}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('campaign', response.data)
        self.assertIn('estadisticas', response.data)
        self.assertIn('comparativa_meta', response.data)

    def test_api_reporte_sin_campaign_id(self):
        """Test endpoint sin campaign_id requerido"""
        response = self.client.get('/api/reports/labors-by-campaign/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_api_autenticacion_requerida(self):
        """Test que los reportes requieren autenticación"""
        self.client.force_authenticate(user=None)

        response = self.client.get(
            f'/api/reports/labors-by-campaign/?campaign_id={self.campaign.id}'
        )

        # Django REST Framework con SessionAuthentication devuelve 403 cuando no hay autenticación
        # 401 es para credenciales inválidas, 403 es para sin credenciales con IsAuthenticated
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
