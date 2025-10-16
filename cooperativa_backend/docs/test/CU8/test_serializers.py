# 🧪 Tests de Serializers de Insumos Agrícolas

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

from cooperativa.models import Pesticida, Fertilizante
from cooperativa.serializers import PesticidaSerializer, FertilizanteSerializer


class PesticidaSerializerTest(TestCase):
    """Tests para el serializer de Pesticida"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)
        self.fecha_pasada = date.today() - timedelta(days=30)

        # Datos válidos para pesticida
        self.pesticida_data = {
            'nombre_comercial': 'Roundup Test',
            'ingrediente_activo': 'Glifosato',
            'tipo_pesticida': 'HERBICIDA',
            'concentracion': '48% EC',
            'registro_sanitario': 'REG-TEST-001',
            'cantidad': Decimal('100.00'),
            'unidad_medida': 'Litros',
            'fecha_vencimiento': self.fecha_futura,
            'dosis_recomendada': '2-3 L/ha',
            'lote': 'LOT-SERIALIZER-001',
            'proveedor': 'Test Provider',
            'precio_unitario': Decimal('45.50'),
            'ubicacion_almacen': 'Sector Test',
            'estado': 'DISPONIBLE',
            'observaciones': 'Test serializer'
        }

    def test_serializer_valido(self):
        """Test serialización de datos válidos"""
        serializer = PesticidaSerializer(data=self.pesticida_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['nombre_comercial'], 'Roundup Test')

    def test_serializer_campos_readonly(self):
        """Test campos de solo lectura"""
        # Crear instancia
        pesticida = Pesticida.objects.create(**self.pesticida_data)

        # Serializar
        serializer = PesticidaSerializer(pesticida)
        data = serializer.data

        # Verificar campos calculados
        self.assertIn('valor_total', data)
        self.assertIn('dias_para_vencer', data)
        self.assertIn('esta_proximo_vencer', data)
        self.assertIn('esta_vencido', data)
        self.assertIn('creado_en', data)
        self.assertIn('actualizado_en', data)

        # Verificar valores calculados
        self.assertEqual(data['valor_total'], '4550.00')
        self.assertIsInstance(data['dias_para_vencer'], int)
        self.assertGreaterEqual(data['dias_para_vencer'], 360)

    def test_serializer_validacion_cantidad_negativa(self):
        """Test validación de cantidad negativa en serializer"""
        data = self.pesticida_data.copy()
        data['cantidad'] = Decimal('-50.00')

        serializer = PesticidaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cantidad', serializer.errors)

    def test_serializer_validacion_precio_negativo(self):
        """Test validación de precio negativo en serializer"""
        data = self.pesticida_data.copy()
        data['precio_unitario'] = Decimal('-10.00')

        serializer = PesticidaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('precio_unitario', serializer.errors)

    def test_serializer_validacion_fecha_vencimiento_pasada(self):
        """Test validación de fecha de vencimiento pasada"""
        data = self.pesticida_data.copy()
        data['fecha_vencimiento'] = self.fecha_pasada

        serializer = PesticidaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_vencimiento', serializer.errors)

    def test_serializer_validacion_concentracion_invalida(self):
        """Test validación de formato de concentración"""
        data = self.pesticida_data.copy()
        data['concentracion'] = 'FORMATO_INVALIDO!!!'

        serializer = PesticidaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('concentracion', serializer.errors)

    def test_serializer_validacion_estado_vencido_sin_fecha_pasada(self):
        """Test validación cross-field: estado VENCIDO requiere fecha pasada"""
        data = self.pesticida_data.copy()
        data['estado'] = 'VENCIDO'
        # fecha_vencimiento sigue siendo futura

        serializer = PesticidaSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('estado', serializer.errors)

    def test_serializer_validacion_dosis_por_tipo(self):
        """Test validación de dosis recomendada según tipo"""
        # Dosis válida para insecticida
        data = self.pesticida_data.copy()
        data['tipo_pesticida'] = 'INSECTICIDA'
        data['dosis_recomendada'] = '1-2 L/ha'
        data['lote'] = 'LOT-DOSIS-001'

        serializer = PesticidaSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_campos_requeridos(self):
        """Test validación de campos requeridos"""
        # Datos vacíos
        serializer = PesticidaSerializer(data={})
        self.assertFalse(serializer.is_valid())

        # Verificar campos requeridos
        required_fields = [
            'nombre_comercial', 'ingrediente_activo', 'tipo_pesticida',
            'concentracion', 'cantidad', 'unidad_medida', 'fecha_vencimiento',
            'lote', 'proveedor', 'precio_unitario', 'ubicacion_almacen', 'estado'
        ]

        for field in required_fields:
            self.assertIn(field, serializer.errors)


class FertilizanteSerializerTest(TestCase):
    """Tests para el serializer de Fertilizante"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)

        # Datos válidos para fertilizante
        self.fertilizante_data = {
            'nombre_comercial': 'NPK 15-15-15 Test',
            'tipo_fertilizante': 'COMPUESTO',
            'composicion_npk': '15-15-15',
            'cantidad': Decimal('500.00'),
            'unidad_medida': 'Kilogramos',
            'fecha_vencimiento': self.fecha_futura,
            'dosis_recomendada': '200-300 kg/ha',
            'lote': 'LOT-F-SERIALIZER-001',
            'proveedor': 'Test Nutri',
            'precio_unitario': Decimal('25.50'),
            'ubicacion_almacen': 'Sector Fert',
            'estado': 'DISPONIBLE',
            'observaciones': 'Test serializer fertilizante'
        }

    def test_serializer_valido(self):
        """Test serialización de fertilizante válido"""
        serializer = FertilizanteSerializer(data=self.fertilizante_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['nombre_comercial'], 'NPK 15-15-15 Test')

    def test_serializer_organico_con_materia_organica(self):
        """Test fertilizante orgánico con materia orgánica"""
        data = self.fertilizante_data.copy()
        data['tipo_fertilizante'] = 'ORGANICO'
        data['composicion_npk'] = '3-2-1'
        data['materia_orgánica'] = Decimal('85.50')
        data['lote'] = 'LOT-ORG-SERIALIZER-001'

        serializer = FertilizanteSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_campos_readonly_fertilizante(self):
        """Test campos de solo lectura en fertilizante"""
        fertilizante = Fertilizante.objects.create(**self.fertilizante_data)

        serializer = FertilizanteSerializer(fertilizante)
        data = serializer.data

        # Verificar campos calculados
        self.assertIn('valor_total', data)
        self.assertIn('dias_para_vencer', data)
        self.assertIn('esta_proximo_vencer', data)
        self.assertIn('esta_vencido', data)
        self.assertIn('npk_values', data)
        self.assertIn('creado_en', data)
        self.assertIn('actualizado_en', data)

        # Verificar valores calculados
        self.assertEqual(data['valor_total'], '12750.00')
        self.assertIsInstance(data['dias_para_vencer'], int)
        self.assertEqual(data['npk_values'], {'N': 15, 'P': 15, 'K': 15})

    def test_serializer_validacion_npk_invalido(self):
        """Test validación de composición NPK inválida"""
        data = self.fertilizante_data.copy()
        data['composicion_npk'] = 'INVALIDO'

        serializer = FertilizanteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('composicion_npk', serializer.errors)

    def test_serializer_validacion_npk_rango(self):
        """Test validación de valores NPK fuera de rango"""
        data = self.fertilizante_data.copy()
        data['composicion_npk'] = '150-200-300'  # Valores > 99

        serializer = FertilizanteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('composicion_npk', serializer.errors)

    def test_serializer_validacion_materia_organica_requerida(self):
        """Test validación: fertilizante orgánico requiere materia orgánica"""
        data = self.fertilizante_data.copy()
        data['tipo_fertilizante'] = 'ORGANICO'
        data['composicion_npk'] = '3-2-1'
        data['materia_orgánica'] = None  # No especificada
        data['lote'] = 'LOT-ORG-REQ-001'

        serializer = FertilizanteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('materia_orgánica', serializer.errors)

    def test_serializer_validacion_materia_organica_no_organico(self):
        """Test validación: solo orgánicos pueden tener materia orgánica"""
        data = self.fertilizante_data.copy()
        data['tipo_fertilizante'] = 'QUIMICO'
        data['materia_orgánica'] = Decimal('50.00')  # Específica materia orgánica
        data['lote'] = 'LOT-NO-ORG-001'

        serializer = FertilizanteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('materia_orgánica', serializer.errors)

    def test_serializer_validacion_materia_organica_rango(self):
        """Test validación de rango de materia orgánica"""
        data = self.fertilizante_data.copy()
        data['tipo_fertilizante'] = 'ORGANICO'
        data['composicion_npk'] = '3-2-1'
        data['materia_orgánica'] = Decimal('150.00')  # > 100%
        data['lote'] = 'LOT-ORG-RANGE-001'

        serializer = FertilizanteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('materia_orgánica', serializer.errors)

    def test_serializer_npk_con_aditivos(self):
        """Test composición NPK con aditivos (+TE)"""
        data = self.fertilizante_data.copy()
        data['composicion_npk'] = '15-15-15+TE'
        data['lote'] = 'LOT-TE-001'

        serializer = FertilizanteSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Verificar valores NPK
        fertilizante = serializer.save()
        serializer_data = FertilizanteSerializer(fertilizante)
        self.assertEqual(serializer_data.data['npk_values'], {'N': 15, 'P': 15, 'K': 15})

    def test_serializer_sin_fecha_vencimiento(self):
        """Test fertilizante sin fecha de vencimiento (válido)"""
        data = self.fertilizante_data.copy()
        data['fecha_vencimiento'] = None
        data['tipo_fertilizante'] = 'ORGANICO'
        data['composicion_npk'] = '2-1-3'
        data['materia_orgánica'] = Decimal('90.00')
        data['lote'] = 'LOT-SIN-VENC-001'

        serializer = FertilizanteSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Verificar campos calculados
        fertilizante = serializer.save()
        serializer_data = FertilizanteSerializer(fertilizante)
        self.assertIsNone(serializer_data.data['dias_para_vencer'])
        self.assertFalse(serializer_data.data['esta_vencido'])


class SerializersIntegrationTest(TestCase):
    """Tests de integración entre serializers"""

    def setUp(self):
        self.fecha_futura = date.today() + timedelta(days=365)

    def test_serializers_multiples_insumos(self):
        """Test serialización de múltiples insumos"""
        # Crear varios pesticidas
        for i in range(3):
            Pesticida.objects.create(
                nombre_comercial=f'Pesticida {i}',
                ingrediente_activo=f'Activo {i}',
                tipo_pesticida='INSECTICIDA',
                concentracion='40% EC',
                cantidad=Decimal('100.00'),
                unidad_medida='Litros',
                fecha_vencimiento=self.fecha_futura,
                lote=f'LOT-MULTI-P-{i}',
                proveedor='Multi Provider',
                precio_unitario=Decimal('40.00'),
                ubicacion_almacen=f'Sector {i}',
                estado='DISPONIBLE'
            )

        # Crear varios fertilizantes
        for i in range(2):
            Fertilizante.objects.create(
                nombre_comercial=f'Fertilizante {i}',
                tipo_fertilizante='QUIMICO',
                composicion_npk='10-10-10',
                cantidad=Decimal('200.00'),
                unidad_medida='Kilogramos',
                lote=f'LOT-MULTI-F-{i}',
                proveedor='Multi Nutri',
                precio_unitario=Decimal('20.00'),
                ubicacion_almacen=f'Sector F-{i}',
                estado='DISPONIBLE'
            )

        # Serializar todos
        pesticidas = Pesticida.objects.all()
        fertilizantes = Fertilizante.objects.all()

        pesticidas_data = PesticidaSerializer(pesticidas, many=True).data
        fertilizantes_data = FertilizanteSerializer(fertilizantes, many=True).data

        # Verificaciones
        self.assertEqual(len(pesticidas_data), 3)
        self.assertEqual(len(fertilizantes_data), 2)

        # Verificar cálculos
        total_valor_pesticidas = sum(float(p['valor_total']) for p in pesticidas_data)
        total_valor_fertilizantes = sum(float(f['valor_total']) for f in fertilizantes_data)

        self.assertEqual(total_valor_pesticidas, 12000.00)  # 3 * 100 * 40
        self.assertEqual(total_valor_fertilizantes, 8000.00)  # 2 * 200 * 20

    def test_serializer_update_parcial(self):
        """Test actualización parcial con serializer"""
        # Crear pesticida
        pesticida = Pesticida.objects.create(
            nombre_comercial='Original',
            ingrediente_activo='Original',
            tipo_pesticida='INSECTICIDA',
            concentracion='40% EC',
            cantidad=Decimal('100.00'),
            unidad_medida='Litros',
            fecha_vencimiento=self.fecha_futura,
            lote='LOT-UPDATE-001',
            proveedor='Original Provider',
            precio_unitario=Decimal('40.00'),
            ubicacion_almacen='Original',
            estado='DISPONIBLE'
        )

        # Actualizar parcialmente
        update_data = {
            'cantidad': Decimal('150.00'),
            'observaciones': 'Actualizado'
        }

        serializer = PesticidaSerializer(pesticida, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()

        # Verificaciones
        self.assertEqual(updated.cantidad, Decimal('150.00'))
        self.assertEqual(updated.observaciones, 'Actualizado')
        self.assertEqual(updated.nombre_comercial, 'Original')  # Sin cambios</content>
