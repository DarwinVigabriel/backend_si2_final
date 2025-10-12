#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de prueba
"""
import os
import sys
import django
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from cooperativa.models import (
    Rol, Usuario, Comunidad, Socio, Parcela, Cultivo, 
    Semilla, Pesticida, Fertilizante,
    Campaign, CampaignPartner, CampaignPlot,
    CicloCultivo, Tratamiento, Cosecha
)
from django.db.models import Sum
from datetime import datetime, timedelta, date
from decimal import Decimal
import random


def limpiar_base_datos():
    """Elimina TODOS los datos excepto el superusuario admin de Django"""
    print("\n🗑️  LIMPIANDO BASE DE DATOS...")
    print("⚠️  Se eliminarán TODOS los datos (excepto admin de Django)\n")
    
    # Contar antes de eliminar
    print("📊 Datos actuales:")
    print(f"   Usuarios: {Usuario.objects.count()}")
    print(f"   Socios: {Socio.objects.count()}")
    print(f"   Parcelas: {Parcela.objects.count()}")
    print(f"   Cultivos: {Cultivo.objects.count()}")
    print(f"   Semillas: {Semilla.objects.count()}")
    print(f"   Pesticidas: {Pesticida.objects.count()}")
    print(f"   Fertilizantes: {Fertilizante.objects.count()}")
    print(f"   Campañas: {Campaign.objects.count()}")
    print(f"   Ciclos: {CicloCultivo.objects.count()}")
    print(f"   Tratamientos: {Tratamiento.objects.count()}")
    print(f"   Cosechas: {Cosecha.objects.count()}")
    
    # Eliminar en orden (respetando relaciones FK)
    print("\n🔄 Eliminando datos...")
    
    # 1. Cosechas (dependen de CicloCultivo)
    Cosecha.objects.all().delete()
    print("   ✓ Cosechas eliminadas")
    
    # 2. Tratamientos (dependen de CicloCultivo)
    Tratamiento.objects.all().delete()
    print("   ✓ Tratamientos eliminados")
    
    # 3. Ciclos de cultivo (dependen de Cultivo)
    CicloCultivo.objects.all().delete()
    print("   ✓ Ciclos de cultivo eliminados")
    
    # 4. Asignaciones de campañas
    CampaignPlot.objects.all().delete()
    CampaignPartner.objects.all().delete()
    print("   ✓ Asignaciones de campañas eliminadas")
    
    # 5. Campañas
    Campaign.objects.all().delete()
    print("   ✓ Campañas eliminadas")
    
    # 6. Insumos (CU7 y CU8)
    Semilla.objects.all().delete()
    Pesticida.objects.all().delete()
    Fertilizante.objects.all().delete()
    print("   ✓ Insumos eliminados (semillas, pesticidas, fertilizantes)")
    
    # 7. Cultivos (dependen de Parcela)
    Cultivo.objects.all().delete()
    print("   ✓ Cultivos eliminados")
    
    # 8. Parcelas (dependen de Socio)
    Parcela.objects.all().delete()
    print("   ✓ Parcelas eliminadas")
    
    # 9. Socios (dependen de Usuario)
    Socio.objects.all().delete()
    print("   ✓ Socios eliminados")
    
    # 10. Usuarios (excepto superusuarios)
    usuarios_eliminados = Usuario.objects.exclude(is_superuser=True).count()
    Usuario.objects.exclude(is_superuser=True).delete()
    print(f"   ✓ Usuarios eliminados ({usuarios_eliminados})")
    
    # 11. Comunidades
    Comunidad.objects.all().delete()
    print("   ✓ Comunidades eliminadas")
    
    # 12. Roles
    Rol.objects.all().delete()
    print("   ✓ Roles eliminados")
    
    print("\n✅ Base de datos limpiada!")
    print(f"   Admin preservado: {Usuario.objects.filter(is_superuser=True).count()} superusuario(s)\n")


def convertir_fecha(fecha_str):
    """Convierte una fecha string 'YYYY-MM-DD' a objeto date"""
    if isinstance(fecha_str, str):
        year, month, day = map(int, fecha_str.split('-'))
        return date(year, month, day)
    return fecha_str


def crear_datos_prueba():
    print("Verificando y creando datos de prueba...")

    # Verificar y crear roles usando los métodos del modelo
    print("Verificando roles...")
    admin_rol = Rol.crear_rol_administrador()
    print("✓ Rol Administrador configurado")

    socio_rol = Rol.crear_rol_socio()
    print("✓ Rol Socio configurado")

    operador_rol = Rol.crear_rol_operador()
    print("✓ Rol Operador configurado")

    # Verificar y crear comunidades
    print("Verificando comunidades...")
    if not Comunidad.objects.filter(nombre='Comunidad San Pedro').exists():
        comunidad1 = Comunidad.objects.create(
            nombre='Comunidad San Pedro',
            municipio='Cochabamba',
            departamento='Cochabamba'
        )
        print("✓ Comunidad San Pedro creada")
    else:
        comunidad1 = Comunidad.objects.get(nombre='Comunidad San Pedro')
        print("✓ Comunidad San Pedro ya existe")

    if not Comunidad.objects.filter(nombre='Comunidad Villa Tunari').exists():
        comunidad2 = Comunidad.objects.create(
            nombre='Comunidad Villa Tunari',
            municipio='Villa Tunari',
            departamento='Cochabamba'
        )
        print("✓ Comunidad Villa Tunari creada")
    else:
        comunidad2 = Comunidad.objects.get(nombre='Comunidad Villa Tunari')
        print("✓ Comunidad Villa Tunari ya existe")

    # Verificar y crear usuarios adicionales
    print("Verificando usuarios...")
    if not Usuario.objects.filter(ci_nit='123456780').exists():
        operador_user = Usuario.objects.create_user(
            ci_nit='123456780',
            nombres='Juan Carlos',
            apellidos='Rodriguez Silva',
            email='operador@cooperativa.com',
            usuario='operador1',
            password='operador123'
        )
        print("✓ Usuario operador1 creado")
    else:
        operador_user = Usuario.objects.get(ci_nit='123456780')
        print("✓ Usuario operador1 ya existe")

    if not Usuario.objects.filter(ci_nit='987654320').exists():
        socio1_user = Usuario.objects.create_user(
            ci_nit='987654320',
            nombres='Maria Elena',
            apellidos='Perez Lopez',
            email='maria@cooperativa.com',
            usuario='socio1',
            password='socio123'
        )
        print("✓ Usuario socio1 creado")
    else:
        socio1_user = Usuario.objects.get(ci_nit='987654320')
        print("✓ Usuario socio1 ya existe")

    if not Usuario.objects.filter(ci_nit='456789120').exists():
        socio2_user = Usuario.objects.create_user(
            ci_nit='456789120',
            nombres='Carlos Alberto',
            apellidos='Gomez Martinez',
            email='carlos@cooperativa.com',
            usuario='socio2',
            password='socio123'
        )
        print("✓ Usuario socio2 creado")
    else:
        socio2_user = Usuario.objects.get(ci_nit='456789120')
        print("✓ Usuario socio2 ya existe")

    # Verificar y crear socios
    print("Verificando socios...")
    if not Socio.objects.filter(usuario__usuario='socio1').exists():
        socio1 = Socio.objects.create(
            usuario=socio1_user,
            codigo_interno='SOC001',
            fecha_nacimiento='1985-05-15',
            sexo='F',
            direccion='Zona Norte, Calle Principal 123',
            comunidad=comunidad1
        )
        print("✓ Socio SOC001 creado")
    else:
        socio1 = Socio.objects.get(usuario__usuario='socio1')
        print("✓ Socio SOC001 ya existe")

    if not Socio.objects.filter(usuario__usuario='socio2').exists():
        socio2 = Socio.objects.create(
            usuario=socio2_user,
            codigo_interno='SOC002',
            fecha_nacimiento='1978-12-03',
            sexo='M',
            direccion='Zona Sur, Avenida Central 456',
            comunidad=comunidad2
        )
        print("✓ Socio SOC002 creado")
    else:
        socio2 = Socio.objects.get(usuario__usuario='socio2')
        print("✓ Socio SOC002 ya existe")

    # Verificar y crear parcelas
    print("Verificando parcelas...")
    if not Parcela.objects.filter(socio=socio1, nombre='Parcela Norte').exists():
        parcela1 = Parcela.objects.create(
            socio=socio1,
            nombre='Parcela Norte',
            superficie_hectareas=5.5,
            tipo_suelo='Arcilloso',
            ubicacion='Sector Norte de la comunidad',
            latitud=-17.3895,
            longitud=-66.1568,
            estado='ACTIVA'
        )
        print("✓ Parcela Norte creada")
    else:
        parcela1 = Parcela.objects.get(socio=socio1, nombre='Parcela Norte')
        print("✓ Parcela Norte ya existe")

    if not Parcela.objects.filter(socio=socio1, nombre='Parcela Sur').exists():
        parcela2 = Parcela.objects.create(
            socio=socio1,
            nombre='Parcela Sur',
            superficie_hectareas=3.0,
            tipo_suelo='Arenoso',
            ubicacion='Sector Sur de la comunidad',
            latitud=-17.3912,
            longitud=-66.1589,
            estado='ACTIVA'
        )
        print("✓ Parcela Sur creada")
    else:
        parcela2 = Parcela.objects.get(socio=socio1, nombre='Parcela Sur')
        print("✓ Parcela Sur ya existe")

    if not Parcela.objects.filter(socio=socio2, nombre='Parcela Principal').exists():
        parcela3 = Parcela.objects.create(
            socio=socio2,
            nombre='Parcela Principal',
            superficie_hectareas=8.0,
            tipo_suelo='Franco',
            ubicacion='Centro de la comunidad',
            latitud=-17.3856,
            longitud=-66.1543,
            estado='ACTIVA'
        )
        print("✓ Parcela Principal creada")
    else:
        parcela3 = Parcela.objects.get(socio=socio2, nombre='Parcela Principal')
        print("✓ Parcela Principal ya existe")

    # Verificar y crear cultivos
    print("Verificando cultivos...")
    if not Cultivo.objects.filter(parcela=parcela1, especie='Maíz').exists():
        cultivo1 = Cultivo.objects.create(
            parcela=parcela1,
            especie='Maíz',
            variedad='Maíz duro',
            tipo_semilla='Híbrido',
            fecha_estimada_siembra='2025-11-15',
            hectareas_sembradas=3.0,
            estado='ACTIVO'
        )
        print("✓ Cultivo Maíz creado")
    else:
        print("✓ Cultivo Maíz ya existe")

    if not Cultivo.objects.filter(parcela=parcela2, especie='Papa').exists():
        cultivo2 = Cultivo.objects.create(
            parcela=parcela2,
            especie='Papa',
            variedad='Papa blanca',
            tipo_semilla='Nativa',
            fecha_estimada_siembra='2025-12-20',
            hectareas_sembradas=2.5,
            estado='ACTIVO'
        )
        print("✓ Cultivo Papa creado")
    else:
        print("✓ Cultivo Papa ya existe")

    if not Cultivo.objects.filter(parcela=parcela3, especie='Trigo').exists():
        cultivo3 = Cultivo.objects.create(
            parcela=parcela3,
            especie='Trigo',
            variedad='Trigo panadero',
            tipo_semilla='Mejorada',
            fecha_estimada_siembra='2025-12-01',
            hectareas_sembradas=6.0,
            estado='ACTIVO'
        )
        print("✓ Cultivo Trigo creado")
    else:
        print("✓ Cultivo Trigo ya existe")

    print("\n✅ Verificación completada!")
    print(f"Total Roles: {Rol.objects.count()}")
    print(f"Total Usuarios: {Usuario.objects.count()}")
    print(f"Total Comunidades: {Comunidad.objects.count()}")
    print(f"Total Socios: {Socio.objects.count()}")
    print(f"Total Parcelas: {Parcela.objects.count()}")
    print(f"Total Cultivos: {Cultivo.objects.count()}")

    print("\nCredenciales de acceso:")
    print("Admin: usuario='admin', password='admin123'")
    print("Operador: usuario='operador1', password='operador123'")
    print("Socio1: usuario='socio1', password='socio123'")
    print("Socio2: usuario='socio2', password='socio123'")

    # Asignar roles a usuarios
    print("Asignando roles a usuarios...")
    from cooperativa.models import UsuarioRol

    # Asignar rol Operador al usuario operador1
    if not UsuarioRol.objects.filter(usuario=operador_user, rol=operador_rol).exists():
        UsuarioRol.objects.create(usuario=operador_user, rol=operador_rol)
        print("✓ Rol Operador asignado a operador1")

    # Asignar rol Socio a socio1 y socio2
    if not UsuarioRol.objects.filter(usuario=socio1_user, rol=socio_rol).exists():
        UsuarioRol.objects.create(usuario=socio1_user, rol=socio_rol)
        print("✓ Rol Socio asignado a socio1")

    if not UsuarioRol.objects.filter(usuario=socio2_user, rol=socio_rol).exists():
        UsuarioRol.objects.create(usuario=socio2_user, rol=socio_rol)
        print("✓ Rol Socio asignado a socio2")


def poblar_datos_cu7_cu8():
    """Poblar datos de ejemplo para CU7 (Semillas) y CU8 (Insumos)"""
    print("\n🌱 Poblando datos de CU7 (Semillas) y CU8 (Insumos)...")

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
        # Convertir fecha de vencimiento a objeto date
        if 'fecha_vencimiento' in semilla_data:
            semilla_data['fecha_vencimiento'] = convertir_fecha(semilla_data['fecha_vencimiento'])
        
        lote = semilla_data['lote']
        if not Semilla.objects.filter(lote=lote).exists():
            Semilla.objects.create(**semilla_data)
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
        # Convertir fecha de vencimiento a objeto date
        if 'fecha_vencimiento' in pesticida_data:
            pesticida_data['fecha_vencimiento'] = convertir_fecha(pesticida_data['fecha_vencimiento'])
        
        lote = pesticida_data['lote']
        if not Pesticida.objects.filter(lote=lote).exists():
            Pesticida.objects.create(**pesticida_data)
            pesticidas_creados += 1
            print(f"✓ Pesticida {lote} creado")
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
        # Convertir fecha de vencimiento a objeto date
        if 'fecha_vencimiento' in fertilizante_data:
            fertilizante_data['fecha_vencimiento'] = convertir_fecha(fertilizante_data['fecha_vencimiento'])
        
        lote = fertilizante_data['lote']
        if not Fertilizante.objects.filter(lote=lote).exists():
            Fertilizante.objects.create(**fertilizante_data)
            fertilizantes_creados += 1
            print(f"✓ Fertilizante {lote} creado")
        else:
            print(f"✓ Fertilizante {lote} ya existe")

    print(f"🌿 Total fertilizantes creados: {fertilizantes_creados}")

    print("\n✅ Población de CU7 y CU8 completada!")
    print(f"📊 Resumen final:")
    print(f"   Semillas: {Semilla.objects.count()}")
    print(f"   Pesticidas: {Pesticida.objects.count()}")
    print(f"   Fertilizantes: {Fertilizante.objects.count()}")
    print(f"   Total insumos: {Semilla.objects.count() + Pesticida.objects.count() + Fertilizante.objects.count()}")


def poblar_datos_campanas():
    """Poblar datos de ejemplo para CU9 (Campañas Agrícolas) - SPRINT 2"""
    print("\n🌾 Poblando datos de CU9 (Campañas Agrícolas - Sprint 2)...")

    # Obtener usuarios y socios existentes
    try:
        admin_user = Usuario.objects.get(usuario='admin')
    except Usuario.DoesNotExist:
        print("⚠️ Usuario admin no encontrado. Ejecuta primero crear_datos_prueba()")
        return

    try:
        operador_user = Usuario.objects.get(usuario='operador1')
    except Usuario.DoesNotExist:
        operador_user = admin_user
        print("⚠️ Usuario operador1 no encontrado. Usando admin como responsable")

    # Obtener socios para asignar a campañas
    socios = list(Socio.objects.all())
    if len(socios) < 2:
        print("⚠️ Se necesitan al menos 2 socios. Ejecuta primero crear_datos_prueba()")
        return

    # Obtener parcelas para asignar a campañas
    parcelas = list(Parcela.objects.filter(estado='ACTIVA'))
    if len(parcelas) < 2:
        print("⚠️ Se necesitan al menos 2 parcelas activas. Ejecuta primero crear_datos_prueba()")
        return

    # Datos de campañas de ejemplo
    campanas_data = [
        {
            'nombre': 'Campaña de Maíz 2025-2026',
            'descripcion': 'Campaña agrícola enfocada en la producción de maíz híbrido de alto rendimiento para la temporada 2025-2026. Incluye capacitación técnica, asistencia agronómica y comercialización garantizada.',
            'fecha_inicio': datetime.now().date(),
            'fecha_fin': (datetime.now() + timedelta(days=180)).date(),
            'meta_produccion': Decimal('5000.00'),
            'unidad_meta': 'kg',
            'estado': 'EN_CURSO',
            'presupuesto': Decimal('25000.00'),
            'responsable': operador_user,
            'socios_asignados': 2,
            'parcelas_asignadas': 2
        },
        {
            'nombre': 'Campaña de Papa Orgánica 2026',
            'descripcion': 'Producción de papa orgánica certificada con prácticas agroecológicas. Uso exclusivo de insumos orgánicos, rotación de cultivos y manejo integrado de plagas. Mercado objetivo: exportación.',
            'fecha_inicio': (datetime.now() + timedelta(days=200)).date(),
            'fecha_fin': (datetime.now() + timedelta(days=380)).date(),
            'meta_produccion': Decimal('8000.00'),
            'unidad_meta': 'kg',
            'estado': 'PLANIFICADA',
            'presupuesto': Decimal('35000.00'),
            'responsable': operador_user,
            'socios_asignados': 2,
            'parcelas_asignadas': 2
        },
        {
            'nombre': 'Campaña de Quinoa Real 2026',
            'descripcion': 'Cultivo de quinoa real boliviana con certificación orgánica y de comercio justo. Incluye programa de mejoramiento genético y acceso a mercados internacionales premium.',
            'fecha_inicio': (datetime.now() + timedelta(days=400)).date(),
            'fecha_fin': (datetime.now() + timedelta(days=580)).date(),
            'meta_produccion': Decimal('3000.00'),
            'unidad_meta': 'kg',
            'estado': 'PLANIFICADA',
            'presupuesto': Decimal('40000.00'),
            'responsable': admin_user,
            'socios_asignados': 1,
            'parcelas_asignadas': 1
        },
        {
            'nombre': 'Campaña de Trigo Invierno 2024',
            'descripcion': 'Campaña finalizada de producción de trigo panadero. Resultados exitosos con rendimientos superiores al promedio nacional. Incluye análisis de calidad y almacenamiento.',
            'fecha_inicio': (datetime.now() - timedelta(days=300)).date(),
            'fecha_fin': (datetime.now() - timedelta(days=120)).date(),
            'meta_produccion': Decimal('6000.00'),
            'unidad_meta': 'kg',
            'estado': 'FINALIZADA',
            'presupuesto': Decimal('30000.00'),
            'responsable': operador_user,
            'socios_asignados': 2,
            'parcelas_asignadas': 2
        },
        {
            'nombre': 'Campaña de Hortalizas Diversificadas 2024',
            'descripcion': 'Producción diversificada de hortalizas: tomate, cebolla, zanahoria y lechuga. Sistema de riego por goteo y cultivo en invernadero. Comercialización en mercados locales.',
            'fecha_inicio': (datetime.now() - timedelta(days=100)).date(),
            'fecha_fin': (datetime.now() - timedelta(days=10)).date(),
            'meta_produccion': Decimal('2500.00'),
            'unidad_meta': 'kg',
            'estado': 'FINALIZADA',
            'presupuesto': Decimal('18000.00'),
            'responsable': admin_user,
            'socios_asignados': 1,
            'parcelas_asignadas': 1
        }
    ]

    # Crear campañas con sus relaciones
    print("Creando campañas con socios y parcelas asignados...")
    campanas_creadas = 0
    
    for i, campana_data in enumerate(campanas_data):
        nombre = campana_data['nombre']
        
        # Extraer datos de asignación
        socios_count = campana_data.pop('socios_asignados')
        parcelas_count = campana_data.pop('parcelas_asignadas')
        
        if not Campaign.objects.filter(nombre=nombre).exists():
            # Crear campaña
            campana = Campaign.objects.create(**campana_data)
            campanas_creadas += 1
            print(f"✓ Campaña '{nombre}' creada")
            
            # Asignar socios a la campaña
            roles_socios = ['COORDINADOR', 'PRODUCTOR', 'TECNICO', 'SUPERVISOR']
            for j in range(min(socios_count, len(socios))):
                socio = socios[j % len(socios)]
                rol = roles_socios[j % len(roles_socios)]
                
                CampaignPartner.objects.create(
                    campaign=campana,
                    socio=socio,
                    rol=rol,
                    fecha_asignacion=campana.fecha_inicio,
                    observaciones=f'Asignado como {rol.lower()} en la campaña {campana.nombre}'
                )
                print(f"  ↳ Socio {socio.codigo_interno} asignado como {rol}")
            
            # Asignar parcelas a la campaña
            cultivos = ['Maíz', 'Papa', 'Quinoa', 'Trigo', 'Tomate', 'Cebolla']
            for k in range(min(parcelas_count, len(parcelas))):
                parcela = parcelas[k % len(parcelas)]
                
                # Calcular superficie comprometida (entre 50% y 100% de la parcela)
                porcentaje = 0.7 + (k * 0.1)  # 70%, 80%, 90%, 100%
                superficie_comprometida = float(parcela.superficie_hectareas) * porcentaje
                
                # Calcular meta de producción por parcela (proporción de meta total)
                meta_parcela = float(campana.meta_produccion) * (superficie_comprometida / (float(parcela.superficie_hectareas) * parcelas_count))
                
                CampaignPlot.objects.create(
                    campaign=campana,
                    parcela=parcela,
                    fecha_asignacion=campana.fecha_inicio,
                    superficie_comprometida=Decimal(str(round(superficie_comprometida, 2))),
                    cultivo_planificado=cultivos[k % len(cultivos)],
                    meta_produccion_parcela=Decimal(str(round(meta_parcela, 2))),
                    observaciones=f'Parcela asignada a campaña {campana.nombre} con {porcentaje*100:.0f}% de superficie'
                )
                print(f"  ↳ Parcela '{parcela.nombre}' asignada ({superficie_comprometida:.2f} ha)")
        else:
            print(f"✓ Campaña '{nombre}' ya existe")

    print(f"\n📈 Total campañas creadas: {campanas_creadas}")
    
    # Estadísticas finales
    total_campanas = Campaign.objects.count()
    campanas_activas = Campaign.objects.filter(estado='EN_CURSO').count()
    campanas_planificadas = Campaign.objects.filter(estado='PLANIFICADA').count()
    campanas_finalizadas = Campaign.objects.filter(estado='FINALIZADA').count()
    total_asignaciones_socios = CampaignPartner.objects.count()
    total_asignaciones_parcelas = CampaignPlot.objects.count()
    
    print("\n✅ Población de CU9 (Campañas) completada!")
    print(f"📊 Resumen de Campañas:")
    print(f"   Total campañas: {total_campanas}")
    print(f"   🟢 En curso: {campanas_activas}")
    print(f"   🔵 Planificadas: {campanas_planificadas}")
    print(f"   ⚫ Finalizadas: {campanas_finalizadas}")
    print(f"   👥 Socios asignados: {total_asignaciones_socios}")
    print(f"   🌱 Parcelas asignadas: {total_asignaciones_parcelas}")
    
    # Mostrar detalle de cada campaña
    print("\n📋 Detalle de Campañas:")
    for campana in Campaign.objects.all():
        socios_count = campana.socios_asignados.count()
        parcelas_count = campana.parcelas.count()
        print(f"\n   🌾 {campana.nombre}")
        print(f"      Estado: {campana.get_estado_display()}")
        print(f"      Duración: {campana.duracion_dias()} días")
        print(f"      Progreso: {campana.progreso_temporal():.1f}%")
        print(f"      Meta: {campana.meta_produccion} {campana.unidad_meta}")
        print(f"      Presupuesto: Bs. {campana.presupuesto:,.2f}")
        print(f"      Socios: {socios_count} | Parcelas: {parcelas_count}")
        print(f"      Responsable: {campana.responsable.get_full_name()}")


def poblar_ciclos_cultivo_y_tratamientos():
    """Poblar ciclos de cultivo y tratamientos (labores) para reportes"""
    print("\n🌱 Poblando ciclos de cultivo y tratamientos (labores agrícolas)...")
    
    # Obtener cultivos existentes
    cultivos = list(Cultivo.objects.all())
    if not cultivos:
        print("⚠️ No hay cultivos disponibles. Ejecuta primero crear_datos_prueba()")
        return
    
    # Obtener parcelas
    parcelas = list(Parcela.objects.all())
    
    # Obtener pesticidas y fertilizantes
    pesticidas = list(Pesticida.objects.all()[:5])
    fertilizantes = list(Fertilizante.objects.all()[:5])
    
    if not pesticidas or not fertilizantes:
        print("⚠️ No hay insumos disponibles. Ejecuta primero poblar_datos_cu7_cu8()")
        return
    
    # Obtener campañas
    campanas = Campaign.objects.filter(estado__in=['EN_CURSO', 'FINALIZADA'])
    
    if not campanas:
        print("⚠️ No hay campañas activas o finalizadas")
        return
    
    ciclos_creados = 0
    tratamientos_creados = 0
    
    hoy = datetime.now().date()
    
    # Crear ciclos basados en las campañas y sus parcelas asignadas
    for campana in campanas:
        # Obtener parcelas asignadas a esta campaña
        parcelas_campana = CampaignPlot.objects.filter(campaign=campana).select_related('parcela')
        
        for cp in parcelas_campana:
            parcela = cp.parcela
            
            # Obtener cultivos de esta parcela
            cultivos_parcela = Cultivo.objects.filter(parcela=parcela)
            
            if not cultivos_parcela.exists():
                continue
            
            # Tomar el primer cultivo de la parcela (o crear lógica más compleja)
            cultivo = cultivos_parcela.first()
            
            # Crear ciclo para esta campaña (permitir múltiples ciclos por cultivo)
            # Un cultivo puede tener varios ciclos en diferentes campañas/temporadas
            
            # Fechas basadas en la campaña
            fecha_inicio = campana.fecha_inicio + timedelta(days=random.randint(5, 20))
            duracion_dias = random.randint(90, 150)
            fecha_estimada_fin = fecha_inicio + timedelta(days=duracion_dias)
            
            # Asegurar que no exceda la fecha fin de la campaña
            if fecha_estimada_fin > campana.fecha_fin:
                fecha_estimada_fin = campana.fecha_fin - timedelta(days=random.randint(5, 15))
            
            # Estado según las fechas y estado de campaña
            if campana.estado == 'FINALIZADA':
                estado = 'FINALIZADO'
                fecha_fin_real = fecha_estimada_fin + timedelta(days=random.randint(-5, 5))
            elif fecha_inicio > hoy:
                estado = 'PLANIFICADO'
                fecha_fin_real = None
            elif fecha_estimada_fin < hoy:
                estado = 'FINALIZADO'
                fecha_fin_real = fecha_estimada_fin + timedelta(days=random.randint(-5, 5))
            else:
                # Campaña en curso y ciclo en progreso
                estado = random.choice(['CRECIMIENTO', 'COSECHA'])
                fecha_fin_real = None
            
            ciclo = CicloCultivo.objects.create(
                cultivo=cultivo,
                fecha_inicio=fecha_inicio,
                fecha_estimada_fin=fecha_estimada_fin,
                fecha_fin_real=fecha_fin_real,
                estado=estado,
                costo_estimado=Decimal(str(random.uniform(5000, 15000))),
                costo_real=Decimal(str(random.uniform(4500, 16000))) if estado == 'FINALIZADO' else None,
                rendimiento_esperado=Decimal(str(random.uniform(2000, 5000))),
                rendimiento_real=Decimal(str(random.uniform(1800, 5500))) if estado == 'FINALIZADO' else None,
                unidad_rendimiento='kg/ha',
                observaciones=f'Ciclo de {cultivo.especie} en parcela {cultivo.parcela.nombre} - Campaña: {campana.nombre}'
            )
            ciclos_creados += 1
            print(f"✓ Ciclo de cultivo creado: {ciclo} [{estado}]")
            
            # Crear tratamientos para este ciclo
            num_tratamientos = random.randint(5, 12)
            
            for j in range(num_tratamientos):
                # Fecha de aplicación dentro del ciclo
                dias_desde_inicio = random.randint(5, duracion_dias - 5)
                fecha_aplicacion = fecha_inicio + timedelta(days=dias_desde_inicio)
                
                # Tipo de tratamiento
                tipo = random.choice(['FERTILIZANTE', 'PESTICIDA', 'HERBICIDA', 'RIEGO', 'LABOR'])
                
                if tipo == 'FERTILIZANTE':
                    fertilizante = random.choice(fertilizantes)
                    nombre_producto = fertilizante.nombre_comercial
                    dosis = Decimal(str(random.uniform(100, 300)))
                    unidad_dosis = 'kg/ha'
                    costo = float(dosis) * float(fertilizante.precio_unitario) * float(cultivo.hectareas_sembradas or 1)
                    
                elif tipo == 'PESTICIDA' or tipo == 'HERBICIDA':
                    pesticida = random.choice(pesticidas)
                    nombre_producto = pesticida.nombre_comercial
                    dosis = Decimal(str(random.uniform(0.5, 3.0)))
                    unidad_dosis = 'L/ha'
                    costo = float(dosis) * float(pesticida.precio_unitario) * float(cultivo.hectareas_sembradas or 1)
                    
                elif tipo == 'RIEGO':
                    nombre_producto = 'Riego por aspersión'
                    dosis = Decimal(str(random.uniform(20, 50)))
                    unidad_dosis = 'm³/ha'
                    costo = float(dosis) * 2.5 * float(cultivo.hectareas_sembradas or 1)
                    
                else:  # LABOR
                    labores = ['Deshierbe manual', 'Aporque', 'Poda', 'Raleo', 'Control manual de plagas']
                    nombre_producto = random.choice(labores)
                    dosis = Decimal('1.0')
                    unidad_dosis = 'jornales/ha'
                    costo = 150.0 * float(cultivo.hectareas_sembradas or 1)  # 150 Bs por jornal
                
                aplicadores = [
                    'Juan Pérez', 'María López', 'Carlos Mamani', 
                    'Ana Quispe', 'Pedro Condori', 'Equipo técnico'
                ]
                
                tratamiento = Tratamiento.objects.create(
                    ciclo_cultivo=ciclo,
                    tipo_tratamiento=tipo,
                    nombre_producto=nombre_producto,
                    dosis=dosis,
                    unidad_dosis=unidad_dosis,
                    fecha_aplicacion=fecha_aplicacion,
                    costo=Decimal(str(round(costo, 2))),
                    aplicado_por=random.choice(aplicadores),
                    observaciones=f'Aplicación de {tipo.lower()} en etapa de {estado.lower()}'
                )
                tratamientos_creados += 1
    
    print(f"\n✅ Ciclos de cultivo y tratamientos poblados!")
    print(f"📊 Resumen:")
    print(f"   Ciclos de cultivo creados: {ciclos_creados}")
    print(f"   Tratamientos creados: {tratamientos_creados}")
    print(f"   Total ciclos: {CicloCultivo.objects.count()}")
    print(f"   Total tratamientos: {Tratamiento.objects.count()}")
    
    # Mostrar estadísticas por tipo de tratamiento
    print("\n📋 Tratamientos por tipo:")
    for tipo, nombre in Tratamiento.TIPOS_TRATAMIENTO:
        count = Tratamiento.objects.filter(tipo_tratamiento=tipo).count()
        if count > 0:
            print(f"   {nombre}: {count}")


def poblar_cosechas():
    """Poblar cosechas para reportes de producción"""
    print("\n🌾 Poblando cosechas (producción agrícola)...")
    
    from cooperativa.models import Cosecha
    
    cosechas_creadas = 0
    
    # Obtener ciclos finalizados o en crecimiento/cosecha (estados donde se puede cosechar)
    ciclos = CicloCultivo.objects.filter(
        estado__in=['FINALIZADO', 'CRECIMIENTO', 'COSECHA']
    ).select_related('cultivo__parcela')
    
    print(f"   Encontrados {ciclos.count()} ciclos para cosechar")
    
    calidades = ['EXCELENTE', 'BUENA', 'REGULAR', 'MALA']
    
    for ciclo in ciclos:
        # Verificar si ya tiene cosechas
        if Cosecha.objects.filter(ciclo_cultivo=ciclo).exists():
            continue
            
        parcela = ciclo.cultivo.parcela
        cultivo_especie = ciclo.cultivo.especie
        
        # Determinar cuántas cosechas hacer (1-3 cosechas por ciclo)
        num_cosechas = random.randint(1, 3)
        
        # Calcular producción base según la especie y superficie
        superficie = float(parcela.superficie_hectareas)
        
        # Rendimientos típicos por hectárea (kg/ha)
        rendimientos = {
            'Maíz': random.uniform(2500, 4000),
            'Papa': random.uniform(8000, 15000),
            'Quinoa': random.uniform(800, 1500),
            'Trigo': random.uniform(1500, 3000),
            'Hortalizas': random.uniform(5000, 10000),
        }
        
        # Buscar rendimiento base
        rendimiento_base = 2000  # Default
        for especie, rendimiento in rendimientos.items():
            if especie.lower() in cultivo_especie.lower():
                rendimiento_base = rendimiento
                break
        
        # Producción total del ciclo
        produccion_total_ciclo = superficie * rendimiento_base
        
        # Dividir entre las cosechas
        fecha_inicio_cosecha = ciclo.fecha_estimada_fin - timedelta(days=30)
        
        for i in range(num_cosechas):
            # Distribuir producción (cosechas más grandes al inicio)
            porcentaje = random.uniform(0.25, 0.45) if i == 0 else random.uniform(0.15, 0.35)
            cantidad = produccion_total_ciclo * porcentaje
            
            # Fecha de cosecha
            dias_offset = i * 7  # Cada 7 días una cosecha
            fecha_cosecha = fecha_inicio_cosecha + timedelta(days=dias_offset)
            
            # Asegurar que no sea fecha futura
            if fecha_cosecha > date.today():
                fecha_cosecha = date.today() - timedelta(days=random.randint(1, 15))
            
            # Calidad (mejores al inicio)
            if i == 0:
                calidad = random.choice(['EXCELENTE', 'BUENA'])
            else:
                calidad = random.choice(calidades)
            
            # Precio de venta según calidad
            precios_base = {
                'Maíz': 2.5,
                'Papa': 1.8,
                'Quinoa': 12.0,
                'Trigo': 2.0,
                'Hortalizas': 3.5,
            }
            
            precio_base = 2.0  # Default
            for especie, precio in precios_base.items():
                if especie.lower() in cultivo_especie.lower():
                    precio_base = precio
                    break
            
            # Ajustar precio por calidad
            multiplicadores_calidad = {
                'EXCELENTE': 1.3,
                'BUENA': 1.0,
                'REGULAR': 0.8,
                'MALA': 0.5
            }
            precio_venta = precio_base * multiplicadores_calidad[calidad]
            
            # Crear cosecha
            cosecha = Cosecha.objects.create(
                ciclo_cultivo=ciclo,
                fecha_cosecha=fecha_cosecha,
                cantidad_cosechada=Decimal(str(round(cantidad, 2))),
                unidad_medida='kg',
                calidad=calidad,
                estado='COMPLETADA',
                precio_venta=Decimal(str(round(precio_venta, 2))),
                observaciones=f'Cosecha {i+1} de {num_cosechas} - Calidad {calidad.lower()}'
            )
            cosechas_creadas += 1
            
            print(f"  ✓ Cosecha creada: {ciclo.cultivo.especie} - {cantidad:.2f} kg - {calidad}")
    
    print(f"\n✅ Cosechas pobladas!")
    print(f"📊 Resumen:")
    print(f"   Cosechas creadas: {cosechas_creadas}")
    print(f"   Total cosechas: {Cosecha.objects.count()}")
    print(f"   Producción total: {Cosecha.objects.aggregate(total=Sum('cantidad_cosechada'))['total'] or 0:.2f} kg")
    
    # Estadísticas por calidad
    print("\n📋 Cosechas por calidad:")
    for calidad in ['EXCELENTE', 'BUENA', 'REGULAR', 'MALA']:
        count = Cosecha.objects.filter(calidad=calidad).count()
        if count > 0:
            cantidad_total = Cosecha.objects.filter(calidad=calidad).aggregate(
                total=Sum('cantidad_cosechada')
            )['total'] or 0
            print(f"   {calidad}: {count} cosechas ({cantidad_total:.2f} kg)")


if __name__ == '__main__':
    # LIMPIAR TODO PRIMERO
    limpiar_base_datos()
    
    # RECREAR TODO DESDE CERO
    crear_datos_prueba()
    poblar_datos_cu7_cu8()
    poblar_datos_campanas()
    poblar_ciclos_cultivo_y_tratamientos()
    poblar_cosechas()