"""
Tests para el Modelo Semilla - CU7 Gestión de Semillas
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta
from cooperativa.models import Semilla


class SemillaModelTest(TestCase):
    """Tests del modelo Semilla"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.semilla_data = {
            "especie": "Maíz",
            "variedad": "Criollo",
            "cantidad": Decimal("500.00"),
            "unidad_medida": "kg",
            "fecha_vencimiento": date.today() + timedelta(days=365),
            "porcentaje_germinacion": Decimal("95.50"),
            "lote": "MZ2025001",
            "proveedor": "AgroSemillas S.A.",
            "precio_unitario": Decimal("25.00"),
            "ubicacion_almacen": "Sector A-15",
            "observaciones": "Lote premium"
        }

    def test_creacion_semilla_valida(self):
        """Test: Crear semilla con datos válidos"""
        semilla = Semilla.objects.create(**self.semilla_data)
        self.assertEqual(semilla.especie, "Maíz")
        self.assertEqual(semilla.estado, "DISPONIBLE")
        self.assertEqual(semilla.valor_total(), Decimal('12500.00'))

    def test_calculo_valor_total(self):
        """Test: Cálculo correcto del valor total"""
        semilla = Semilla.objects.create(**self.semilla_data)
        self.assertEqual(semilla.valor_total(), Decimal('12500.00'))

    def test_dias_para_vencer(self):
        """Test: Cálculo de días para vencer"""
        fecha_futura = date.today() + timedelta(days=30)
        data = self.semilla_data.copy()
        data['fecha_vencimiento'] = fecha_futura
        semilla = Semilla.objects.create(**data)
        self.assertEqual(semilla.dias_para_vencer(), 30)

    def test_esta_proxima_vencer(self):
        """Test: Detección de semillas próximas a vencer"""
        # Dentro de 30 días
        fecha_proxima = date.today() + timedelta(days=15)
        data_proxima = self.semilla_data.copy()
        data_proxima['fecha_vencimiento'] = fecha_proxima
        semilla = Semilla.objects.create(**data_proxima)
        self.assertTrue(semilla.esta_proxima_vencer())

        # Fuera de 30 días
        fecha_lejana = date.today() + timedelta(days=60)
        data_lejana = self.semilla_data.copy()
        data_lejana['fecha_vencimiento'] = fecha_lejana
        data_lejana['lote'] = "MZ2025002"
        semilla2 = Semilla.objects.create(**data_lejana)
        self.assertFalse(semilla2.esta_proxima_vencer())

    def test_esta_vencida(self):
        """Test: Detección de semillas vencidas"""
        fecha_pasada = date.today() - timedelta(days=1)
        data = self.semilla_data.copy()
        data['fecha_vencimiento'] = fecha_pasada
        semilla = Semilla.objects.create(**data)
        self.assertTrue(semilla.esta_vencida())

    def test_estado_agotada_cantidad_cero(self):
        """Test: Estado AGOTADA cuando cantidad es 0"""
        data = self.semilla_data.copy()
        data['cantidad'] = Decimal('0.00')
        semilla = Semilla.objects.create(**data)
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
        Semilla.objects.create(**self.semilla_data)
        with self.assertRaises(ValidationError):
            Semilla.objects.create(**self.semilla_data)  # Misma combinación especie+variedad+lote

    def test_str_representation(self):
        """Test: Representación string del modelo"""
        semilla = Semilla.objects.create(**self.semilla_data)
        expected = "Maíz - Criollo (Lote: MZ2025001)"
        self.assertEqual(str(semilla), expected)