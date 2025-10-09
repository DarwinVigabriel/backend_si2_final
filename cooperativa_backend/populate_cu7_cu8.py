#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo para CU7 (Semillas) y CU8 (Insumos)
"""
import os
import sys
import django
from datetime import date
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from cooperativa.models import Semilla, Pesticida, Fertilizante

def convertir_fecha(fecha_str):
    """Convierte una fecha en formato string 'YYYY-MM-DD' a objeto date"""
    if fecha_str:
        return date.fromisoformat(fecha_str)
    return None

def poblar_datos_cu7_cu8():
    """Poblar datos de ejemplo para CU7 (Semillas) y CU8 (Insumos)"""
    print("🌱 Poblando datos de CU7 (Semillas) y CU8 (Insumos)...")

    # Datos de ejemplo para CU7 - Semillas
    semillas_data = [
        {
            'especie': 'Maíz',
            'variedad': 'Maíz duro híbrido',
            'cantidad': 500.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-12-31',
            'porcentaje_germinacion': 95.0,
            'lote': 'MZ-HYB-2025-001',
            'proveedor': 'AgroSemillas SA',
            'precio_unitario': 25.50,
            'ubicacion_almacen': 'Sector A-01',
            'estado': 'DISPONIBLE',
            'observaciones': 'Semilla híbrida de alto rendimiento'
        },
        {
            'especie': 'Maíz',
            'variedad': 'Maíz dulce',
            'cantidad': 200.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-10-15',
            'porcentaje_germinacion': 92.0,
            'lote': 'MZ-DUL-2025-002',
            'proveedor': 'Semillas del Valle',
            'precio_unitario': 30.00,
            'ubicacion_almacen': 'Sector A-02',
            'estado': 'DISPONIBLE',
            'observaciones': 'Ideal para consumo fresco'
        },
        {
            'especie': 'Papa',
            'variedad': 'Papa blanca',
            'cantidad': 800.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-08-20',
            'porcentaje_germinacion': 88.0,
            'lote': 'PT-BLA-2025-003',
            'proveedor': 'Tubérculos Andinos',
            'precio_unitario': 15.00,
            'ubicacion_almacen': 'Sector B-01',
            'estado': 'DISPONIBLE',
            'observaciones': 'Variedad resistente a enfermedades'
        },
        {
            'especie': 'Papa',
            'variedad': 'Papa amarilla',
            'cantidad': 300.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-09-10',
            'porcentaje_germinacion': 90.0,
            'lote': 'PT-AMA-2025-004',
            'proveedor': 'AgroTubérculos',
            'precio_unitario': 18.50,
            'ubicacion_almacen': 'Sector B-02',
            'estado': 'DISPONIBLE',
            'observaciones': 'Alta producción de almidón'
        },
        {
            'especie': 'Trigo',
            'variedad': 'Trigo panadero',
            'cantidad': 600.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-11-30',
            'porcentaje_germinacion': 94.0,
            'lote': 'TG-PAN-2025-005',
            'proveedor': 'Cereales del Altiplano',
            'precio_unitario': 22.00,
            'ubicacion_almacen': 'Sector C-01',
            'estado': 'DISPONIBLE',
            'observaciones': 'Excelente para panificación'
        },
        {
            'especie': 'Trigo',
            'variedad': 'Trigo duro',
            'cantidad': 400.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-07-15',
            'porcentaje_germinacion': 89.0,
            'lote': 'TG-DUR-2025-006',
            'proveedor': 'Semillas Premium',
            'precio_unitario': 28.00,
            'ubicacion_almacen': 'Sector C-02',
            'estado': 'DISPONIBLE',
            'observaciones': 'Ideal para pastas y couscous'
        },
        {
            'especie': 'Quinoa',
            'variedad': 'Quinoa real',
            'cantidad': 150.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2027-01-20',
            'porcentaje_germinacion': 96.0,
            'lote': 'QN-REA-2025-007',
            'proveedor': 'Andes Seeds',
            'precio_unitario': 45.00,
            'ubicacion_almacen': 'Sector D-01',
            'estado': 'DISPONIBLE',
            'observaciones': 'Superfood andino de alta calidad'
        },
        {
            'especie': 'Soya',
            'variedad': 'Soya transgénica',
            'cantidad': 1000.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-06-30',
            'porcentaje_germinacion': 91.0,
            'lote': 'SY-TGM-2025-008',
            'proveedor': 'Biotech Seeds',
            'precio_unitario': 35.00,
            'ubicacion_almacen': 'Sector E-01',
            'estado': 'DISPONIBLE',
            'observaciones': 'Resistente a herbicidas'
        },
        {
            'especie': 'Tomate',
            'variedad': 'Cherry',
            'cantidad': 50.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-04-10',
            'porcentaje_germinacion': 87.0,
            'lote': 'TM-CHR-2025-009',
            'proveedor': 'Hortalizas Frescas',
            'precio_unitario': 80.00,
            'ubicacion_almacen': 'Sector F-01',
            'estado': 'DISPONIBLE',
            'observaciones': 'Para invernadero'
        },
        {
            'especie': 'Cebolla',
            'variedad': 'Cebolla morada',
            'cantidad': 250.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2026-05-25',
            'porcentaje_germinacion': 93.0,
            'lote': 'CB-MOR-2025-010',
            'proveedor': 'Bulbos y Semillas',
            'precio_unitario': 12.00,
            'ubicacion_almacen': 'Sector F-02',
            'estado': 'DISPONIBLE',
            'observaciones': 'Larga conservación'
        }
    ]

    # Crear semillas
    print("Creando semillas de ejemplo...")
    semillas_creadas = 0
    for semilla_data in semillas_data:
        lote = semilla_data['lote']
        if not Semilla.objects.filter(lote=lote).exists():
            # Convertir fecha_vencimiento a objeto date
            data_to_create = semilla_data.copy()
            data_to_create['fecha_vencimiento'] = convertir_fecha(semilla_data.get('fecha_vencimiento'))
            Semilla.objects.create(**data_to_create)
            semillas_creadas += 1
            print(f"✓ Semilla {lote} creada")
        else:
            print(f"✓ Semilla {lote} ya existe")

    print(f"📦 Total semillas creadas: {semillas_creadas}")

    # Datos de ejemplo para CU8 - Pesticidas
    pesticidas_data = [
        {
            'nombre_comercial': 'Roundup PowerMax',
            'ingrediente_activo': 'Glifosato',
            'tipo_pesticida': 'HERBICIDA',
            'concentracion': '48% SL',
            'registro_sanitario': 'REG-001-2025',
            'cantidad': 200.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-03-15',
            'lote': 'RUPM-2025-001',
            'proveedor': 'Monsanto',
            'precio_unitario': 45.50,
            'ubicacion_almacen': 'Sector P-01',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '2-3 L/ha',
            'observaciones': 'Herbicida sistémico de amplio espectro'
        },
        {
            'nombre_comercial': 'Karate Zeon',
            'ingrediente_activo': 'Lambda cihalotrina',
            'tipo_pesticida': 'INSECTICIDA',
            'concentracion': '5% CS',
            'registro_sanitario': 'REG-002-2025',
            'cantidad': 150.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-01-20',
            'lote': 'KRZ-2025-002',
            'proveedor': 'Syngenta',
            'precio_unitario': 85.00,
            'ubicacion_almacen': 'Sector P-02',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '0.3-0.5 L/ha',
            'observaciones': 'Insecticida piretroide de contacto'
        },
        {
            'nombre_comercial': 'Amistar Top',
            'ingrediente_activo': 'Azoxistrobina + Difenoconazol',
            'tipo_pesticida': 'FUNGICIDA',
            'concentracion': '30% + 12.5% SC',
            'registro_sanitario': 'REG-003-2025',
            'cantidad': 100.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-05-10',
            'lote': 'AMT-2025-003',
            'proveedor': 'Syngenta',
            'precio_unitario': 120.00,
            'ubicacion_almacen': 'Sector P-03',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '0.8-1.0 L/ha',
            'observaciones': 'Fungicida sistémico preventivo y curativo'
        },
        {
            'nombre_comercial': 'Reglone',
            'ingrediente_activo': 'Diquat',
            'tipo_pesticida': 'HERBICIDA',
            'concentracion': '20% SL',
            'registro_sanitario': 'REG-004-2025',
            'cantidad': 80.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2026-12-05',
            'lote': 'RGL-2025-004',
            'proveedor': 'Syngenta',
            'precio_unitario': 65.00,
            'ubicacion_almacen': 'Sector P-04',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '4-6 L/ha',
            'observaciones': 'Herbicida de contacto para desecación'
        },
        {
            'nombre_comercial': 'Decis',
            'ingrediente_activo': 'Deltametrina',
            'tipo_pesticida': 'INSECTICIDA',
            'concentracion': '2.5% EC',
            'registro_sanitario': 'REG-005-2025',
            'cantidad': 120.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-02-28',
            'lote': 'DCS-2025-005',
            'proveedor': 'Bayer',
            'precio_unitario': 75.00,
            'ubicacion_almacen': 'Sector P-05',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '0.5-1.0 L/ha',
            'observaciones': 'Insecticida piretroide para control de plagas'
        },
        {
            'nombre_comercial': 'Score',
            'ingrediente_activo': 'Diflubenzuron',
            'tipo_pesticida': 'INSECTICIDA',
            'concentracion': '25% SC',
            'registro_sanitario': 'REG-006-2025',
            'cantidad': 90.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-04-15',
            'lote': 'SCR-2025-006',
            'proveedor': 'Rohm and Haas',
            'precio_unitario': 95.00,
            'ubicacion_almacen': 'Sector P-06',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '0.2-0.4 L/ha',
            'observaciones': 'Insecticida regulador de crecimiento'
        },
        {
            'nombre_comercial': 'Ridomil Gold',
            'ingrediente_activo': 'Metalaxil-M + Mancozeb',
            'tipo_pesticida': 'FUNGICIDA',
            'concentracion': '6% + 60% WG',
            'registro_sanitario': 'REG-007-2025',
            'cantidad': 75.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2027-06-30',
            'lote': 'RMG-2025-007',
            'proveedor': 'Syngenta',
            'precio_unitario': 110.00,
            'ubicacion_almacen': 'Sector P-07',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '2.5 kg/ha',
            'observaciones': 'Fungicida para control de mildiu'
        },
        {
            'nombre_comercial': 'Gramoxone',
            'ingrediente_activo': 'Paraquat',
            'tipo_pesticida': 'HERBICIDA',
            'concentracion': '20% SL',
            'registro_sanitario': 'REG-008-2025',
            'cantidad': 60.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2026-11-20',
            'lote': 'GRM-2025-008',
            'proveedor': 'Syngenta',
            'precio_unitario': 55.00,
            'ubicacion_almacen': 'Sector P-08',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '3-5 L/ha',
            'observaciones': 'Herbicida no selectivo de contacto'
        },
        {
            'nombre_comercial': 'Confidor',
            'ingrediente_activo': 'Imidacloprid',
            'tipo_pesticida': 'INSECTICIDA',
            'concentracion': '35% SC',
            'registro_sanitario': 'REG-009-2025',
            'cantidad': 110.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-07-10',
            'lote': 'CNF-2025-009',
            'proveedor': 'Bayer',
            'precio_unitario': 90.00,
            'ubicacion_almacen': 'Sector P-09',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '0.3-0.5 L/ha',
            'observaciones': 'Insecticida sistémico neonicotinoide'
        },
        {
            'nombre_comercial': 'Curzate',
            'ingrediente_activo': 'Cymoxanil + Mancozeb',
            'tipo_pesticida': 'FUNGICIDA',
            'concentracion': '8% + 64% WP',
            'registro_sanitario': 'REG-010-2025',
            'cantidad': 85.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2027-08-25',
            'lote': 'CRZ-2025-010',
            'proveedor': 'DuPont',
            'precio_unitario': 85.00,
            'ubicacion_almacen': 'Sector P-10',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '2.0-2.5 kg/ha',
            'observaciones': 'Fungicida para mildiu del tomate y papa'
        }
    ]

    # Crear pesticidas
    print("Creando pesticidas de ejemplo...")
    pesticidas_creados = 0
    for pesticida_data in pesticidas_data:
        lote = pesticida_data['lote']
        if not Pesticida.objects.filter(lote=lote).exists():
            try:
                # Convertir fecha_vencimiento a objeto date
                data_to_create = pesticida_data.copy()
                data_to_create['fecha_vencimiento'] = convertir_fecha(pesticida_data.get('fecha_vencimiento'))
                Pesticida.objects.create(**data_to_create)
                pesticidas_creados += 1
                print(f"✓ Pesticida {lote} creado")
            except Exception as e:
                print(f"❌ Error creando pesticida {lote}: {e}")
                print(f"   Datos: {data_to_create}")
                raise
        else:
            print(f"✓ Pesticida {lote} ya existe")

    print(f"🧪 Total pesticidas creados: {pesticidas_creados}")

    # Datos de ejemplo para CU8 - Fertilizantes
    fertilizantes_data = [
        {
            'nombre_comercial': 'NPK 15-15-15',
            'tipo_fertilizante': 'QUIMICO',
            'composicion_npk': '15-15-15',
            'cantidad': 1000.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2027-12-31',
            'lote': 'NPK151515-2025-001',
            'proveedor': 'Fertilizantes del Valle',
            'precio_unitario': 25.50,
            'ubicacion_almacen': 'Sector F-01',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '200-300 kg/ha',
            'observaciones': 'Fertilizante balanceado para cultivos generales'
        },
        {
            'nombre_comercial': 'Urea 46%',
            'tipo_fertilizante': 'QUIMICO',
            'composicion_npk': '46-0-0',
            'cantidad': 800.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2028-06-30',
            'lote': 'UREA46-2025-002',
            'proveedor': 'Químicos Agrícolas',
            'precio_unitario': 18.00,
            'ubicacion_almacen': 'Sector F-02',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '150-200 kg/ha',
            'observaciones': 'Fuente nitrogenada de liberación rápida'
        },
        {
            'nombre_comercial': 'Superfosfato triple',
            'tipo_fertilizante': 'QUIMICO',
            'composicion_npk': '0-46-0',
            'cantidad': 600.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2028-03-15',
            'lote': 'SPT-2025-003',
            'proveedor': 'Fosfatos Andinos',
            'precio_unitario': 32.00,
            'ubicacion_almacen': 'Sector F-03',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '100-150 kg/ha',
            'observaciones': 'Alta concentración de fósforo disponible'
        },
        {
            'nombre_comercial': 'Cloruro de potasio',
            'tipo_fertilizante': 'QUIMICO',
            'composicion_npk': '0-0-60',
            'cantidad': 500.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2028-09-20',
            'lote': 'KCL60-2025-004',
            'proveedor': 'Sales Minerales',
            'precio_unitario': 28.00,
            'ubicacion_almacen': 'Sector F-04',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '80-120 kg/ha',
            'observaciones': 'Fuente potásica soluble en agua'
        },
        {
            'nombre_comercial': 'NPK 10-30-10',
            'tipo_fertilizante': 'QUIMICO',
            'composicion_npk': '10-30-10',
            'cantidad': 700.0,
            'unidad_medida': 'kg',
            'fecha_vencimiento': '2027-11-10',
            'lote': 'NPK103010-2025-005',
            'proveedor': 'NutriAgro',
            'precio_unitario': 30.00,
            'ubicacion_almacen': 'Sector F-05',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '250-350 kg/ha',
            'observaciones': 'Especial para cultivos que requieren alto fósforo'
        },
        {
            'nombre_comercial': 'Humus de lombriz orgánico',
            'tipo_fertilizante': 'ORGANICO',
            'composicion_npk': '1-0-1',
            'cantidad': 300.0,
            'unidad_medida': 'kg',
            'lote': 'HLO-2025-006',
            'proveedor': 'EcoFertil',
            'precio_unitario': 45.00,
            'ubicacion_almacen': 'Sector O-01',
            'estado': 'DISPONIBLE',
            'materia_orgánica': 85.0,
            'dosis_recomendada': '500-1000 kg/ha',
            'observaciones': 'Fertilizante orgánico rico en microorganismos'
        },
        {
            'nombre_comercial': 'Compost casero',
            'tipo_fertilizante': 'ORGANICO',
            'composicion_npk': '2-1-2',
            'cantidad': 2000.0,
            'unidad_medida': 'kg',
            'lote': 'COMPOST-2025-007',
            'proveedor': 'Producción Local',
            'precio_unitario': 8.00,
            'ubicacion_almacen': 'Sector O-02',
            'estado': 'DISPONIBLE',
            'materia_orgánica': 65.0,
            'dosis_recomendada': '2000-3000 kg/ha',
            'observaciones': 'Compost producido localmente por la cooperativa'
        },
        {
            'nombre_comercial': 'Cal dolomítica',
            'tipo_fertilizante': 'CALCAREO',
            'composicion_npk': '0-0-0',
            'cantidad': 1500.0,
            'unidad_medida': 'kg',
            'lote': 'CALDOL-2025-008',
            'proveedor': 'Minerales del Altiplano',
            'precio_unitario': 12.00,
            'ubicacion_almacen': 'Sector C-01',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '1000-2000 kg/ha',
            'observaciones': 'Para corrección de pH ácido en suelos'
        },
        {
            'nombre_comercial': 'Micronutrientes foliar',
            'tipo_fertilizante': 'MICRONUTRIENTES',
            'composicion_npk': '0-0-0',
            'cantidad': 50.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-04-30',
            'lote': 'MICRO-F-2025-009',
            'proveedor': 'NutriFoliar',
            'precio_unitario': 150.00,
            'ubicacion_almacen': 'Sector M-01',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '1-2 L/ha',
            'observaciones': 'Complejo de micronutrientes para aplicación foliar'
        },
        {
            'nombre_comercial': 'Fertilizante foliar NPK',
            'tipo_fertilizante': 'FOLIARES',
            'composicion_npk': '20-20-20',
            'cantidad': 120.0,
            'unidad_medida': 'L',
            'fecha_vencimiento': '2027-02-15',
            'lote': 'FOL-NPK-2025-010',
            'proveedor': 'AgroFoliar',
            'precio_unitario': 95.00,
            'ubicacion_almacen': 'Sector M-02',
            'estado': 'DISPONIBLE',
            'dosis_recomendada': '2-3 L/ha',
            'observaciones': 'Fertilizante soluble para aplicación foliar'
        }
    ]

    # Crear fertilizantes
    print("Creando fertilizantes de ejemplo...")
    fertilizantes_creados = 0
    for fertilizante_data in fertilizantes_data:
        lote = fertilizante_data['lote']
        if not Fertilizante.objects.filter(lote=lote).exists():
            try:
                # Convertir fecha_vencimiento a objeto date
                data_to_create = fertilizante_data.copy()
                data_to_create['fecha_vencimiento'] = convertir_fecha(fertilizante_data.get('fecha_vencimiento'))
                Fertilizante.objects.create(**data_to_create)
                fertilizantes_creados += 1
                print(f"✓ Fertilizante {lote} creado")
            except Exception as e:
                print(f"❌ Error creando fertilizante {lote}: {e}")
                print(f"   Nombre: {fertilizante_data.get('nombre_comercial')}")
                print(f"   Datos: {data_to_create}")
                raise
        else:
            print(f"✓ Fertilizante {lote} ya existe")

    print(f"🌿 Total fertilizantes creados: {fertilizantes_creados}")

    print("\n✅ Población de CU7 y CU8 completada!")
    print("📊 Resumen final:")
    print(f"   Semillas: {Semilla.objects.count()}")
    print(f"   Pesticidas: {Pesticida.objects.count()}")
    print(f"   Fertilizantes: {Fertilizante.objects.count()}")
    print(f"   Total insumos: {Semilla.objects.count() + Pesticida.objects.count() + Fertilizante.objects.count()}")


if __name__ == '__main__':
    poblar_datos_cu7_cu8()