"""
Script para poblar precios de temporada de insumos
Ejecutar: python populate_precios_temporada.py
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from cooperativa.models import PrecioTemporada, Semilla, Pesticida, Fertilizante

def crear_precios_temporada():
    """Crear precios de temporada para insumos existentes"""
    
    print("\n" + "="*70)
    print("CREANDO PRECIOS DE TEMPORADA PARA INSUMOS")
    print("="*70 + "\n")
    
    # Obtener insumos existentes (estado=DISPONIBLE)
    semillas = Semilla.objects.filter(estado='DISPONIBLE')[:5]
    pesticidas = Pesticida.objects.filter(estado='DISPONIBLE')[:3]
    fertilizantes = Fertilizante.objects.filter(estado='DISPONIBLE')[:3]
    
    print(f"📊 INSUMOS DISPONIBLES:")
    print(f"   - Semillas disponibles: {semillas.count()}")
    print(f"   - Pesticidas disponibles: {pesticidas.count()}")
    print(f"   - Fertilizantes disponibles: {fertilizantes.count()}\n")
    
    if not semillas.exists() and not pesticidas.exists() and not fertilizantes.exists():
        print("❌ ERROR: No hay insumos disponibles en la base de datos")
        print("   Por favor, crea primero algunos insumos en Django Admin:")
        print("   - Semillas: http://localhost:8000/admin/cooperativa/semilla/")
        print("   - Pesticidas: http://localhost:8000/admin/cooperativa/pesticida/")
        print("   - Fertilizantes: http://localhost:8000/admin/cooperativa/fertilizante/")
        return
    
    # Temporadas del año
    hoy = date.today()
    
    # Temporada actual (vigente por 3 meses)
    temporadas = [
        {
            'nombre': 'VERANO',
            'inicio': hoy - timedelta(days=30),
            'fin': hoy + timedelta(days=60),
        },
        {
            'nombre': 'PRIMAVERA',
            'inicio': hoy + timedelta(days=61),
            'fin': hoy + timedelta(days=151),
        },
    ]
    
    contador = 0
    
    # ========================================
    # PRECIOS PARA SEMILLAS
    # ========================================
    if semillas.exists():
        print("🌱 CREANDO PRECIOS PARA SEMILLAS:")
        for semilla in semillas:
            for temporada in temporadas:
                precio_base = Decimal('25.00') + (Decimal('5.00') * Decimal(str(semilla.id % 5)))
                
                precio, created = PrecioTemporada.objects.update_or_create(
                    tipo_insumo='SEMILLA',
                    semilla=semilla,
                    temporada=temporada['nombre'],
                    fecha_inicio=temporada['inicio'],
                    defaults={
                        'fecha_fin': temporada['fin'],
                        'precio_venta': precio_base,
                        'precio_mayoreo': precio_base * Decimal('0.85'),  # 15% descuento
                        'cantidad_minima_mayoreo': Decimal('100.00'),
                        'activo': True
                    }
                )
                
                nombre_semilla = f"{semilla.especie}"
                if semilla.variedad:
                    nombre_semilla += f" ({semilla.variedad})"
                
                if created:
                    contador += 1
                    print(f"   ✅ {nombre_semilla} - {temporada['nombre']}: Bs. {precio_base}")
        print()
    
    # ========================================
    # PRECIOS PARA PESTICIDAS
    # ========================================
    if pesticidas.exists():
        print("🧪 CREANDO PRECIOS PARA PESTICIDAS:")
        for pesticida in pesticidas:
            for temporada in temporadas:
                precio_base = Decimal('45.00') + (Decimal('10.00') * Decimal(str(pesticida.id % 4)))
                
                precio, created = PrecioTemporada.objects.update_or_create(
                    tipo_insumo='PESTICIDA',
                    pesticida=pesticida,
                    temporada=temporada['nombre'],
                    fecha_inicio=temporada['inicio'],
                    defaults={
                        'fecha_fin': temporada['fin'],
                        'precio_venta': precio_base,
                        'precio_mayoreo': precio_base * Decimal('0.90'),  # 10% descuento
                        'cantidad_minima_mayoreo': Decimal('50.00'),
                        'activo': True
                    }
                )
                
                nombre_pesticida = pesticida.nombre_comercial
                if pesticida.ingrediente_activo:
                    nombre_pesticida += f" ({pesticida.ingrediente_activo})"
                
                if created:
                    contador += 1
                    print(f"   ✅ {nombre_pesticida} - {temporada['nombre']}: Bs. {precio_base}")
        print()
    
    # ========================================
    # PRECIOS PARA FERTILIZANTES
    # ========================================
    if fertilizantes.exists():
        print("🌿 CREANDO PRECIOS PARA FERTILIZANTES:")
        for fertilizante in fertilizantes:
            for temporada in temporadas:
                precio_base = Decimal('35.00') + (Decimal('8.00') * Decimal(str(fertilizante.id % 4)))
                
                precio, created = PrecioTemporada.objects.update_or_create(
                    tipo_insumo='FERTILIZANTE',
                    fertilizante=fertilizante,
                    temporada=temporada['nombre'],
                    fecha_inicio=temporada['inicio'],
                    defaults={
                        'fecha_fin': temporada['fin'],
                        'precio_venta': precio_base,
                        'precio_mayoreo': precio_base * Decimal('0.88'),  # 12% descuento
                        'cantidad_minima_mayoreo': Decimal('75.00'),
                        'activo': True
                    }
                )
                
                nombre_fertilizante = fertilizante.nombre_comercial
                if fertilizante.composicion_npk:
                    nombre_fertilizante += f" ({fertilizante.composicion_npk})"
                
                if created:
                    contador += 1
                    print(f"   ✅ {nombre_fertilizante} - {temporada['nombre']}: Bs. {precio_base}")
        print()
    
    # ========================================
    # RESUMEN
    # ========================================
    total_precios = PrecioTemporada.objects.filter(activo=True).count()
    vigentes = PrecioTemporada.objects.filter(
        activo=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    ).count()
    
    print("="*70)
    print(f"✅ PROCESO COMPLETADO")
    print(f"   - Precios nuevos creados: {contador}")
    print(f"   - Total precios activos: {total_precios}")
    print(f"   - Precios vigentes HOY: {vigentes}")
    print("="*70 + "\n")
    
    print("📝 PRÓXIMOS PASOS:")
    print("   1. Ir al frontend: /pedidos-insumos/nuevo")
    print("   2. Ahora deberías ver los insumos con precios disponibles")
    print("   3. Si no ves precios, verifica en Django Admin:")
    print("      - URL: http://localhost:8000/admin/cooperativa/preciotemporada/")
    print("      - Verifica que 'activo' = True")
    print("      - Verifica que fecha_inicio <= HOY <= fecha_fin\n")

if __name__ == '__main__':
    try:
        crear_precios_temporada()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
