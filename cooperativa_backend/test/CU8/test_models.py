# 🧪 Tests del Modelo de Insumos Agrícolas

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from cooperativa.models import Pesticida, Fertilizante


class PesticidaModelTest(TestCase):
    """Tests para el modelo Pesticida"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)
        self.fecha_pasada = date.today() - timedelta(days=30)

    def test_creacion_pesticida_valido(self):
        """Test creación de pesticida con datos válidos"""
        pesticida = Pesticida.objects.create(
            nombre_comercial="Roundup",
            ingrediente_activo="Glifosato",
            tipo_pesticida="HERBICIDA",
            concentracion="48% EC",
            registro_sanitario="REG-001-2025",
            cantidad=Decimal('100.00'),
            unidad_medida="Litros",
            fecha_vencimiento=self.fecha_futura,
            dosis_recomendada="2-3 L/ha",
            lote="LOT-2025-001",
            proveedor="Monsanto",
            precio_unitario=Decimal('45.50'),
            ubicacion_almacen="Sector A-15",
            estado="DISPONIBLE",
            observaciones="Herbicida sistémico"
        )

        self.assertEqual(pesticida.nombre_comercial, "Roundup")
        self.assertEqual(pesticida.tipo_pesticida, "HERBICIDA")
        self.assertEqual(pesticida.estado, "DISPONIBLE")
        self.assertEqual(str(pesticida), "Roundup - Glifosato (Lote: LOT-2025-001)")

    def test_valor_total_calculado(self):
        """Test cálculo automático del valor total"""
        pesticida = Pesticida.objects.create(
            nombre_comercial="Test",
            ingrediente_activo="Test Activo",
            tipo_pesticida="INSECTICIDA",
            concentracion="50% WP",
            cantidad=Decimal('200.00'),
            unidad_medida="Kilogramos",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-TEST-001",
            proveedor="Test Provider",
            precio_unitario=Decimal('25.00'),
            ubicacion_almacen="Test Sector",
            estado="DISPONIBLE"
        )

        self.assertEqual(pesticida.valor_total(), Decimal('5000.00'))

    def test_dias_para_vencer(self):
        """Test cálculo de días para vencer"""
        # Fecha futura
        pesticida = Pesticida.objects.create(
            nombre_comercial="Test",
            ingrediente_activo="Test",
            tipo_pesticida="INSECTICIDA",
            concentracion="40% EC",
            cantidad=Decimal('50.00'),
            unidad_medida="Litros",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-TEST-002",
            proveedor="Test Provider",
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        dias = pesticida.dias_para_vencer()
        self.assertIsInstance(dias, int)
        self.assertGreaterEqual(dias, 360)  # Al menos 360 días

    def test_esta_proximo_vencer(self):
        """Test verificación de proximidad al vencimiento"""
        # Pesticida que vence en 15 días
        fecha_cerca = date.today() + timedelta(days=15)
        pesticida = Pesticida.objects.create(
            nombre_comercial="Test",
            ingrediente_activo="Test",
            tipo_pesticida="INSECTICIDA",
            concentracion="40% EC",
            cantidad=Decimal('50.00'),
            unidad_medida="Litros",
            fecha_vencimiento=fecha_cerca,
            lote="LOT-TEST-003",
            proveedor="Test Provider",
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        self.assertTrue(pesticida.esta_proximo_vencer(30))
        self.assertFalse(pesticida.esta_proximo_vencer(10))

    def test_esta_vencido(self):
        """Test verificación de producto vencido"""
        # Crear pesticida con fecha futura
        pesticida = Pesticida.objects.create(
            nombre_comercial="Test",
            ingrediente_activo="Test",
            tipo_pesticida="INSECTICIDA",
            concentracion="40% EC",
            cantidad=Decimal('50.00'),
            unidad_medida="Litros",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-TEST-004",
            proveedor="Test Provider",
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        # Cambiar fecha a pasada para probar el método
        from datetime import date
        fecha_pasada = date.today() - timedelta(days=30)
        pesticida.fecha_vencimiento = fecha_pasada
        pesticida.save()

        self.assertTrue(pesticida.esta_vencido())

    def test_validacion_cantidad_negativa(self):
        """Test validación de cantidad negativa"""
        with self.assertRaises(ValidationError):
            pesticida = Pesticida(
                nombre_comercial="Test",
                ingrediente_activo="Test",
                tipo_pesticida="INSECTICIDA",
                concentracion="40% EC",
                cantidad=Decimal('-10.00'),
                unidad_medida="Litros",
                fecha_vencimiento=self.fecha_futura,
                lote="LOT-TEST-005",
                proveedor="Test Provider",
                precio_unitario=Decimal('30.00'),
                ubicacion_almacen="Test",
                estado="DISPONIBLE"
            )
            pesticida.full_clean()

    def test_validacion_precio_unitario_negativo(self):
        """Test validación de precio unitario negativo"""
        with self.assertRaises(ValidationError):
            pesticida = Pesticida(
                nombre_comercial="Test",
                ingrediente_activo="Test",
                tipo_pesticida="INSECTICIDA",
                concentracion="40% EC",
                cantidad=Decimal('50.00'),
                unidad_medida="Litros",
                fecha_vencimiento=self.fecha_futura,
                lote="LOT-TEST-006",
                proveedor="Test Provider",
                precio_unitario=Decimal('-5.00'),
                ubicacion_almacen="Test",
                estado="DISPONIBLE"
            )
            pesticida.full_clean()

    def test_validacion_fecha_vencimiento_pasada(self):
        """Test validación de fecha de vencimiento pasada"""
        with self.assertRaises(ValidationError):
            pesticida = Pesticida(
                nombre_comercial="Test",
                ingrediente_activo="Test",
                tipo_pesticida="INSECTICIDA",
                concentracion="40% EC",
                cantidad=Decimal('50.00'),
                unidad_medida="Litros",
                fecha_vencimiento=self.fecha_pasada,
                lote="LOT-TEST-007",
                proveedor="Test Provider",
                precio_unitario=Decimal('30.00'),
                ubicacion_almacen="Test",
                estado="DISPONIBLE"
            )
            pesticida.full_clean()

    def test_lote_unico(self):
        """Test unicidad del lote"""
        # Crear primer pesticida
        Pesticida.objects.create(
            nombre_comercial="Test 1",
            ingrediente_activo="Test",
            tipo_pesticida="INSECTICIDA",
            concentracion="40% EC",
            cantidad=Decimal('50.00'),
            unidad_medida="Litros",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-DUPLICADO",
            proveedor="Test Provider",
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        # Intentar crear segundo con mismo lote
        with self.assertRaises(Exception):  # IntegrityError
            Pesticida.objects.create(
                nombre_comercial="Test 2",
                ingrediente_activo="Test",
                tipo_pesticida="INSECTICIDA",
                concentracion="40% EC",
                cantidad=Decimal('30.00'),
                unidad_medida="Litros",
                fecha_vencimiento=self.fecha_futura,
                lote="LOT-DUPLICADO",  # Mismo lote
                proveedor="Test Provider 2",
                precio_unitario=Decimal('25.00'),
                ubicacion_almacen="Test 2",
                estado="DISPONIBLE"
            )

    def test_campos_requeridos(self):
        """Test validación de campos requeridos"""
        with self.assertRaises(ValidationError):
            pesticida = Pesticida()  # Sin campos requeridos
            pesticida.full_clean()


class FertilizanteModelTest(TestCase):
    """Tests para el modelo Fertilizante"""

    def setUp(self):
        """Configuración inicial para tests"""
        self.fecha_futura = date.today() + timedelta(days=365)

    def test_creacion_fertilizante_valido(self):
        """Test creación de fertilizante con datos válidos"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial="NPK 15-15-15",
            tipo_fertilizante="QUIMICO",
            composicion_npk="15-15-15",
            cantidad=Decimal('500.00'),
            unidad_medida="Kilogramos",
            fecha_vencimiento=self.fecha_futura,
            dosis_recomendada="200-300 kg/ha",
            lote="LOT-F-2025-001",
            proveedor="NutriAgro SA",
            precio_unitario=Decimal('25.50'),
            ubicacion_almacen="Sector B-10",
            estado="DISPONIBLE",
            observaciones="Fertilizante balanceado"
        )

        self.assertEqual(fertilizante.nombre_comercial, "NPK 15-15-15")
        self.assertEqual(fertilizante.tipo_fertilizante, "QUIMICO")
        self.assertEqual(fertilizante.estado, "DISPONIBLE")
        self.assertEqual(str(fertilizante), "NPK 15-15-15 - 15-15-15 (Lote: LOT-F-2025-001)")

    def test_creacion_fertilizante_organico(self):
        """Test creación de fertilizante orgánico"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial="Humus de Lombriz",
            tipo_fertilizante="ORGANICO",
            composicion_npk="3-2-1",
            cantidad=Decimal('200.00'),
            unidad_medida="Kilogramos",
            dosis_recomendada="500-1000 kg/ha",
            materia_orgánica=Decimal('85.50'),
            lote="LOT-ORG-2025-001",
            proveedor="EcoFertil SA",
            precio_unitario=Decimal('15.00'),
            ubicacion_almacen="Sector Orgánico",
            estado="DISPONIBLE"
        )

        self.assertEqual(fertilizante.tipo_fertilizante, "ORGANICO")
        self.assertEqual(fertilizante.materia_orgánica, Decimal('85.50'))

    def test_valor_total_fertilizante(self):
        """Test cálculo del valor total de fertilizante"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial="Test",
            tipo_fertilizante="QUIMICO",
            composicion_npk="10-10-10",
            cantidad=Decimal('300.00'),
            unidad_medida="Kilogramos",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-F-TEST-001",
            proveedor="Test Provider",
            precio_unitario=Decimal('20.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        self.assertEqual(fertilizante.valor_total(), Decimal('6000.00'))

    def test_get_npk_values(self):
        """Test extracción de valores NPK"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial="Test",
            tipo_fertilizante="QUIMICO",
            composicion_npk="20-10-5",
            cantidad=Decimal('100.00'),
            unidad_medida="Kilogramos",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-F-TEST-002",
            proveedor="Test Provider",
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        npk_values = fertilizante.get_npk_values()
        self.assertEqual(npk_values['N'], 20)
        self.assertEqual(npk_values['P'], 10)
        self.assertEqual(npk_values['K'], 5)

    def test_get_npk_values_con_aditivos(self):
        """Test extracción NPK con aditivos (+TE)"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial="Test",
            tipo_fertilizante="QUIMICO",
            composicion_npk="15-15-15+5",
            cantidad=Decimal('100.00'),
            unidad_medida="Kilogramos",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-F-TEST-003",
            proveedor="Test Provider",
            precio_unitario=Decimal('35.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        npk_values = fertilizante.get_npk_values()
        self.assertEqual(npk_values['N'], 15)
        self.assertEqual(npk_values['P'], 15)
        self.assertEqual(npk_values['K'], 15)

    def test_get_npk_values_invalido(self):
        """Test manejo de composición NPK inválida"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial="Test",
            tipo_fertilizante="QUIMICO",
            composicion_npk="10-10-10",  # Composición válida
            cantidad=Decimal('100.00'),
            unidad_medida="Kilogramos",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-F-TEST-004",
            proveedor="Test Provider",
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        # Cambiar manualmente la composición para probar el método
        fertilizante.composicion_npk = "INVALIDO"
        npk_values = fertilizante.get_npk_values()
        self.assertIsNone(npk_values)

    def test_validacion_composicion_npk_invalida(self):
        """Test validación de composición NPK inválida"""
        with self.assertRaises(ValidationError):
            fertilizante = Fertilizante(
                nombre_comercial="Test",
                tipo_fertilizante="QUIMICO",
                composicion_npk="INVALIDO",
                cantidad=Decimal('100.00'),
                unidad_medida="Kilogramos",
                lote="LOT-F-TEST-005",
                proveedor="Test Provider",
                precio_unitario=Decimal('30.00'),
                ubicacion_almacen="Test",
                estado="DISPONIBLE"
            )
            fertilizante.full_clean()

    def test_validacion_materia_organica_rango(self):
        """Test validación de materia orgánica fuera de rango"""
        with self.assertRaises(ValidationError):
            fertilizante = Fertilizante(
                nombre_comercial="Test",
                tipo_fertilizante="ORGANICO",
                composicion_npk="5-3-2",
                cantidad=Decimal('100.00'),
                unidad_medida="Kilogramos",
                materia_orgánica=Decimal('150.00'),  # > 100%
                lote="LOT-F-TEST-006",
                proveedor="Test Provider",
                precio_unitario=Decimal('30.00'),
                ubicacion_almacen="Test",
                estado="DISPONIBLE"
            )
            fertilizante.full_clean()

    def test_lote_unico_fertilizante(self):
        """Test unicidad del lote en fertilizantes"""
        # Crear primer fertilizante
        Fertilizante.objects.create(
            nombre_comercial="Test 1",
            tipo_fertilizante="QUIMICO",
            composicion_npk="10-10-10",
            cantidad=Decimal('100.00'),
            unidad_medida="Kilogramos",
            fecha_vencimiento=self.fecha_futura,
            lote="LOT-F-DUPLICADO",
            proveedor="Test Provider",
            precio_unitario=Decimal('30.00'),
            ubicacion_almacen="Test",
            estado="DISPONIBLE"
        )

        # Intentar crear segundo con mismo lote
        with self.assertRaises(Exception):  # IntegrityError
            Fertilizante.objects.create(
                nombre_comercial="Test 2",
                tipo_fertilizante="QUIMICO",
                composicion_npk="15-15-15",
                cantidad=Decimal('200.00'),
                unidad_medida="Kilogramos",
                fecha_vencimiento=self.fecha_futura,
                lote="LOT-F-DUPLICADO",  # Mismo lote
                proveedor="Test Provider 2",
                precio_unitario=Decimal('25.00'),
                ubicacion_almacen="Test 2",
                estado="DISPONIBLE"
            )

    def test_fertilizante_sin_fecha_vencimiento(self):
        """Test fertilizante sin fecha de vencimiento (válido)"""
        fertilizante = Fertilizante.objects.create(
            nombre_comercial="Fertilizante Orgánico",
            tipo_fertilizante="ORGANICO",
            composicion_npk="2-1-3",
            cantidad=Decimal('1000.00'),
            unidad_medida="Kilogramos",
            materia_orgánica=Decimal('75.00'),
            lote="LOT-F-SIN-VENC",
            proveedor="Eco Provider",
            precio_unitario=Decimal('12.00'),
            ubicacion_almacen="Sector Orgánico",
            estado="DISPONIBLE"
        )

        self.assertIsNone(fertilizante.fecha_vencimiento)
        self.assertIsNone(fertilizante.dias_para_vencer())
        self.assertFalse(fertilizante.esta_vencido())


class InsumosIntegrationTest(TestCase):
    """Tests de integración entre modelos de insumos"""

    def setUp(self):
        self.fecha_futura = date.today() + timedelta(days=365)

    def test_calculos_masivos(self):
        """Test cálculos masivos de valor total"""
        # Crear múltiples insumos
        for i in range(5):
            Pesticida.objects.create(
                nombre_comercial=f"Pesticida {i}",
                ingrediente_activo=f"Activo {i}",
                tipo_pesticida="INSECTICIDA",
                concentracion="40% EC",
                cantidad=Decimal('100.00'),
                unidad_medida="Litros",
                fecha_vencimiento=self.fecha_futura,
                lote=f"LOT-MASS-{i}",
                proveedor="Mass Provider",
                precio_unitario=Decimal('50.00'),
                ubicacion_almacen=f"Sector {i}",
                estado="DISPONIBLE"
            )

        valor_total_pesticidas = sum(p.valor_total() for p in Pesticida.objects.all())
        self.assertEqual(valor_total_pesticidas, Decimal('25000.00'))  # 5 * 100 * 50

    def test_filtros_por_estado(self):
        """Test filtros por estado"""
        # Crear insumos con diferentes estados
        estados = ['DISPONIBLE', 'AGOTADO', 'VENCIDO']
        for i, estado in enumerate(estados):
            cantidad = Decimal('50.00') if estado != 'AGOTADO' else Decimal('0.00')
            Pesticida.objects.create(
                nombre_comercial=f"Test {estado}",
                ingrediente_activo="Test",
                tipo_pesticida="INSECTICIDA",
                concentracion="40% EC",
                cantidad=cantidad,
                unidad_medida="Litros",
                fecha_vencimiento=self.fecha_futura,
                lote=f"LOT-STATE-{i}",
                proveedor="Test Provider",
                precio_unitario=Decimal('30.00'),
                ubicacion_almacen="Test",
                estado=estado
            )

        disponibles = Pesticida.objects.filter(estado='DISPONIBLE').count()
        agotados = Pesticida.objects.filter(estado='AGOTADO').count()
        vencidos = Pesticida.objects.filter(estado='VENCIDO').count()

        self.assertEqual(disponibles, 1)
        self.assertEqual(agotados, 1)
        self.assertEqual(vencidos, 1)