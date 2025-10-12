"""
CU9: TESTS FUNCIONALES DEL MÓDULO DE CAMPAÑAS
T053: Pruebas funcionales del módulo de Campañas

Tests unitarios y de integración para:
- Modelo Campaign (validaciones)
- API para todos los endpoints CRUD
- Relaciones con socios/parcelas
- Cobertura mínima: 80%
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, date, timedelta
from decimal import Decimal

from cooperativa.models import (
    Campaign, CampaignPartner, CampaignPlot,
    Socio, Parcela, Comunidad, Rol, UsuarioRol,
    Tratamiento, Cosecha, CicloCultivo, Cultivo
)

Usuario = get_user_model()


class CampaignModelTest(TestCase):
    """
    T053: Tests unitarios para modelo Campaign (validaciones)
    """

    def setUp(self):
        """Configurar datos de prueba"""
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

    def test_create_campaign_valido(self):
        """Test crear campaña con datos válidos"""
        campaign = Campaign.objects.create(
            nombre='Campaña 2024',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00'),
            unidad_meta='kg',
            estado='PLANIFICADA',
            descripcion='Campaña de prueba',
            responsable=self.admin_user
        )

        self.assertIsNotNone(campaign.id)
        self.assertEqual(campaign.nombre, 'Campaña 2024')
        self.assertEqual(campaign.estado, 'PLANIFICADA')
        self.assertEqual(campaign.duracion_dias(), 365)

    def test_validacion_fecha_fin_mayor_que_inicio(self):
        """Test validación: fecha_fin > fecha_inicio"""
        from django.core.exceptions import ValidationError

        campaign = Campaign(
            nombre='Campaña Inválida',
            fecha_inicio=date(2024, 12, 31),
            fecha_fin=date(2024, 1, 1),  # Fecha fin anterior a inicio
            meta_produccion=Decimal('10000.00')
        )

        with self.assertRaises(ValidationError) as context:
            campaign.full_clean()

        self.assertIn('fecha_fin', str(context.exception))

    def test_validacion_nombre_unico(self):
        """Test validación: nombre de campaña único"""
        Campaign.objects.create(
            nombre='Campaña Única',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 6, 30),
            meta_produccion=Decimal('5000.00')
        )

        # Intentar crear otra con el mismo nombre
        # El modelo tiene unique=True, por lo que lanza ValidationError al hacer full_clean()
        campaign2 = Campaign(
            nombre='Campaña Única',
            fecha_inicio=date(2024, 7, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('5000.00')
        )
        
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError) as context:
            campaign2.full_clean()
        
        self.assertIn('nombre', str(context.exception))

    def test_validacion_no_solape_fechas(self):
        """Test validación: no solape de fechas entre campañas"""
        from django.core.exceptions import ValidationError

        # Crear primera campaña
        Campaign.objects.create(
            nombre='Campaña 1',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 6, 30),
            meta_produccion=Decimal('5000.00'),
            estado='PLANIFICADA'
        )

        # Intentar crear segunda campaña que se solapa
        campaign2 = Campaign(
            nombre='Campaña 2',
            fecha_inicio=date(2024, 5, 1),  # Se solapa con campaña 1
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('5000.00'),
            estado='PLANIFICADA'
        )

        with self.assertRaises(ValidationError) as context:
            campaign2.full_clean()

        self.assertIn('fecha_inicio', str(context.exception))
        self.assertIn('solap', str(context.exception).lower())

    def test_puede_eliminar_sin_labores_ni_cosechas(self):
        """Test: campaña puede eliminarse si no tiene labores ni cosechas"""
        campaign = Campaign.objects.create(
            nombre='Campaña Sin Datos',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        self.assertTrue(campaign.puede_eliminar())

    def test_calcular_progreso_temporal(self):
        """Test: cálculo de progreso temporal de campaña"""
        hoy = date.today()
        campaign = Campaign.objects.create(
            nombre='Campaña Actual',
            fecha_inicio=hoy - timedelta(days=10),
            fecha_fin=hoy + timedelta(days=20),
            meta_produccion=Decimal('10000.00'),
            estado='EN_CURSO'
        )

        progreso = campaign.progreso_temporal()
        self.assertGreater(progreso, 0)
        self.assertLessEqual(progreso, 100)


class CampaignAPITest(APITestCase):
    """
    T053: Tests de API para todos los endpoints CRUD de Campaign
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

        # Limpiar cualquier campaña existente para tests aislados
        Campaign.objects.all().delete()

        # Autenticar cliente
        self.client.force_authenticate(user=self.admin_user)

    def test_list_campaigns(self):
        """Test GET /api/campaigns/ - Listar campañas"""
        # Crear campañas de prueba
        Campaign.objects.create(
            nombre='Campaña 1',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 6, 30),
            meta_produccion=Decimal('5000.00')
        )
        Campaign.objects.create(
            nombre='Campaña 2',
            fecha_inicio=date(2024, 7, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('5000.00')
        )

        response = self.client.get('/api/campaigns/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_campaign(self):
        """Test POST /api/campaigns/ - Crear campaña"""
        data = {
            'nombre': 'Nueva Campaña',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-12-31',
            'meta_produccion': '15000.00',
            'unidad_meta': 'kg',
            'estado': 'PLANIFICADA',
            'descripcion': 'Campaña de prueba'
        }

        response = self.client.post('/api/campaigns/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Nueva Campaña')
        self.assertIn('duracion_dias', response.data)

    def test_retrieve_campaign(self):
        """Test GET /api/campaigns/{id}/ - Obtener detalle de campaña"""
        campaign = Campaign.objects.create(
            nombre='Campaña Detalle',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        response = self.client.get(f'/api/campaigns/{campaign.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Campaña Detalle')
        self.assertIn('socios_asignados', response.data)
        self.assertIn('parcelas', response.data)

    def test_update_campaign(self):
        """Test PUT /api/campaigns/{id}/ - Actualizar campaña"""
        campaign = Campaign.objects.create(
            nombre='Campaña Original',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        data = {
            'nombre': 'Campaña Actualizada',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-12-31',
            'meta_produccion': '15000.00',
            'unidad_meta': 'kg',
            'estado': 'EN_CURSO'
        }

        response = self.client.put(f'/api/campaigns/{campaign.id}/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Campaña Actualizada')
        self.assertEqual(response.data['estado'], 'EN_CURSO')

    def test_delete_campaign_sin_datos(self):
        """Test DELETE /api/campaigns/{id}/ - Eliminar campaña sin datos"""
        campaign = Campaign.objects.create(
            nombre='Campaña a Eliminar',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        response = self.client.delete(f'/api/campaigns/{campaign.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Campaign.objects.filter(id=campaign.id).exists())

    def test_delete_campaign_con_labores_falla(self):
        """Test: no se puede eliminar campaña con labores asociadas"""
        # Este test requiere configuración más compleja con parcelas y labores
        # Lo marco como pendiente de implementación completa
        pass

    def test_filtro_campañas_por_estado(self):
        """Test filtro de campañas por estado"""
        Campaign.objects.create(
            nombre='Campaña Planificada',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 6, 30),
            meta_produccion=Decimal('5000.00'),
            estado='PLANIFICADA'
        )
        Campaign.objects.create(
            nombre='Campaña En Curso',
            fecha_inicio=date(2024, 7, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('5000.00'),
            estado='EN_CURSO'
        )

        response = self.client.get('/api/campaigns/?estado=PLANIFICADA')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['estado'], 'PLANIFICADA')


class CampaignPartnerIntegrationTest(APITestCase):
    """
    T053: Tests de integración para relaciones Campaign-Socio
    """

    def setUp(self):
        """Configurar datos de prueba"""
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

        # Crear comunidad
        self.comunidad = Comunidad.objects.create(
            nombre='Comunidad Test'
        )

        # Crear socio
        self.socio_user = Usuario.objects.create_user(
            ci_nit='7654321',
            nombres='Socio',
            apellidos='Test',
            email='socio@test.com',
            usuario='socio',
            password='testpass123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad,
            estado='ACTIVO'
        )

        # Crear campaña
        self.campaign = Campaign.objects.create(
            nombre='Campaña Test',
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2024, 12, 31),
            meta_produccion=Decimal('10000.00')
        )

        # Autenticar cliente
        self.client.force_authenticate(user=self.admin_user)

    def test_asignar_socio_a_campaña(self):
        """Test asignar socio a campaña"""
        data = {
            'socio_id': self.socio.id,
            'rol': 'PRODUCTOR',
            'fecha_asignacion': '2024-01-01'
        }

        response = self.client.post(
            f'/api/campaigns/{self.campaign.id}/assign_partner/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rol'], 'PRODUCTOR')
        self.assertTrue(
            CampaignPartner.objects.filter(
                campaign=self.campaign,
                socio=self.socio
            ).exists()
        )

    def test_desasignar_socio_de_campaña(self):
        """Test desasignar socio de campaña"""
        # Primero asignar
        CampaignPartner.objects.create(
            campaign=self.campaign,
            socio=self.socio,
            rol='PRODUCTOR'
        )

        data = {
            'socio_id': self.socio.id
        }

        response = self.client.post(
            f'/api/campaigns/{self.campaign.id}/remove_partner/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            CampaignPartner.objects.filter(
                campaign=self.campaign,
                socio=self.socio
            ).exists()
        )

    def test_listar_socios_de_campaña(self):
        """Test listar socios asignados a campaña"""
        # Asignar socios
        CampaignPartner.objects.create(
            campaign=self.campaign,
            socio=self.socio,
            rol='PRODUCTOR'
        )

        response = self.client.get(f'/api/campaigns/{self.campaign.id}/partners/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['socio'], self.socio.id)


class CampaignPlotIntegrationTest(APITestCase):
    """
    T053: Tests de integración para relaciones Campaign-Parcela
    """

    def setUp(self):
        """Configurar datos de prueba"""
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

        # Crear socio y parcela
        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio_user = Usuario.objects.create_user(
            ci_nit='7654321',
            nombres='Socio',
            apellidos='Test',
            email='socio@test.com',
            usuario='socio',
            password='testpass123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad,
            estado='ACTIVO'
        )
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

        # Autenticar cliente
        self.client.force_authenticate(user=self.admin_user)

    def test_asignar_parcela_a_campaña(self):
        """Test asignar parcela a campaña"""
        data = {
            'parcela_id': self.parcela.id,
            'fecha_asignacion': '2024-01-01',
            'superficie_comprometida': '8.00',
            'cultivo_planificado': 'Maíz'
        }

        response = self.client.post(
            f'/api/campaigns/{self.campaign.id}/assign_plot/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['cultivo_planificado'], 'Maíz')
        self.assertTrue(
            CampaignPlot.objects.filter(
                campaign=self.campaign,
                parcela=self.parcela
            ).exists()
        )

    def test_desasignar_parcela_de_campaña(self):
        """Test desasignar parcela de campaña"""
        # Primero asignar
        CampaignPlot.objects.create(
            campaign=self.campaign,
            parcela=self.parcela
        )

        data = {
            'parcela_id': self.parcela.id
        }

        response = self.client.post(
            f'/api/campaigns/{self.campaign.id}/remove_plot/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            CampaignPlot.objects.filter(
                campaign=self.campaign,
                parcela=self.parcela
            ).exists()
        )

    def test_listar_parcelas_de_campaña(self):
        """Test listar parcelas asignadas a campaña"""
        # Asignar parcela
        CampaignPlot.objects.create(
            campaign=self.campaign,
            parcela=self.parcela,
            superficie_comprometida=Decimal('8.00')
        )

        response = self.client.get(f'/api/campaigns/{self.campaign.id}/plots/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['parcela'], self.parcela.id)

    def test_validacion_superficie_comprometida(self):
        """Test validación: superficie comprometida no puede exceder superficie parcela"""
        data = {
            'parcela_id': self.parcela.id,
            'fecha_asignacion': '2024-01-01',
            'superficie_comprometida': '15.00',  # Excede 10 ha de la parcela
            'cultivo_planificado': 'Maíz'
        }

        response = self.client.post(
            f'/api/campaigns/{self.campaign.id}/assign_plot/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
