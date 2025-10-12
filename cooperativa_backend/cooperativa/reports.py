"""
CU11: MÓDULO DE REPORTES PARA CAMPAÑAS
T039: Reporte de labores por campaña
T050: Reporte de producción por campaña
T052: Reporte de producción por parcela
"""

from django.db.models import Sum, Avg, Count, Q, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import datetime, date
from .models import (
    Campaign, CampaignPlot, Tratamiento, Cosecha,
    CicloCultivo, Parcela
)


class CampaignReports:
    """
    Clase para generar reportes relacionados con campañas agrícolas
    """

    @staticmethod
    def get_labors_by_campaign(campaign_id, start_date=None, end_date=None, 
                               tipo_tratamiento=None, parcela_id=None):
        """
        T039: Reporte de labores por campaña
        
        Genera un reporte detallado de las labores (tratamientos) realizadas
        en las parcelas de una campaña específica.
        
        Args:
            campaign_id: ID de la campaña
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
            tipo_tratamiento: Tipo de tratamiento a filtrar (opcional)
            parcela_id: ID de parcela específica (opcional)
            
        Returns:
            dict: Diccionario con estadísticas y detalles de labores
        """
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return {
                'error': 'Campaña no encontrada',
                'campaign_id': campaign_id
            }

        # Obtener parcelas de la campaña
        parcelas_ids = campaign.parcelas.values_list('parcela_id', flat=True)
        
        # Construir query de tratamientos
        tratamientos_query = Tratamiento.objects.filter(
            ciclo_cultivo__cultivo__parcela_id__in=parcelas_ids
        )

        # Aplicar filtros opcionales
        if start_date:
            tratamientos_query = tratamientos_query.filter(fecha_aplicacion__gte=start_date)
        if end_date:
            tratamientos_query = tratamientos_query.filter(fecha_aplicacion__lte=end_date)
        if tipo_tratamiento:
            tratamientos_query = tratamientos_query.filter(tipo_tratamiento=tipo_tratamiento)
        if parcela_id:
            tratamientos_query = tratamientos_query.filter(
                ciclo_cultivo__cultivo__parcela_id=parcela_id
            )

        # Estadísticas generales
        total_labors = tratamientos_query.count()
        
        # Labores por tipo
        labors_by_type = tratamientos_query.values('tipo_tratamiento').annotate(
            count=Count('id'),
            costo_total=Sum('costo'),
            dosis_promedio=Avg('dosis')
        ).order_by('-count')

        # Área trabajada (suma de superficies de parcelas con tratamientos)
        parcelas_trabajadas = tratamientos_query.values(
            'ciclo_cultivo__cultivo__parcela'
        ).distinct()
        
        total_area_worked = Parcela.objects.filter(
            id__in=parcelas_trabajadas.values_list('ciclo_cultivo__cultivo__parcela', flat=True)
        ).aggregate(
            total=Sum('superficie_hectareas')
        )['total'] or 0

        # Detalle de labores
        labors_detail = tratamientos_query.select_related(
            'ciclo_cultivo__cultivo__parcela',
            'ciclo_cultivo__cultivo__parcela__socio__usuario'
        ).values(
            'id',
            'tipo_tratamiento',
            'nombre_producto',
            'dosis',
            'unidad_dosis',
            'fecha_aplicacion',
            'costo',
            'observaciones',
            'aplicado_por',
            parcela_nombre=F('ciclo_cultivo__cultivo__parcela__nombre'),
            cultivo_especie=F('ciclo_cultivo__cultivo__especie'),
            socio_nombre=F('ciclo_cultivo__cultivo__parcela__socio__usuario__nombres'),
            socio_apellido=F('ciclo_cultivo__cultivo__parcela__socio__usuario__apellidos')
        ).order_by('-fecha_aplicacion')

        # Costo total de labores
        costo_total_labores = tratamientos_query.aggregate(
            total=Sum('costo')
        )['total'] or 0

        # Labores por mes
        labors_by_month = tratamientos_query.extra(
            select={'mes': "DATE_TRUNC('month', fecha_aplicacion)"}
        ).values('mes').annotate(
            count=Count('id')
        ).order_by('mes')

        return {
            'campaign': {
                'id': campaign.id,
                'nombre': campaign.nombre,
                'fecha_inicio': campaign.fecha_inicio,
                'fecha_fin': campaign.fecha_fin,
                'estado': campaign.estado
            },
            'filtros_aplicados': {
                'start_date': start_date,
                'end_date': end_date,
                'tipo_tratamiento': tipo_tratamiento,
                'parcela_id': parcela_id
            },
            'estadisticas': {
                'total_labors': total_labors,
                'total_area_worked': float(total_area_worked),
                'costo_total_labores': float(costo_total_labores),
                'parcelas_trabajadas': len(parcelas_trabajadas)
            },
            'labors_by_type': list(labors_by_type),
            'labors_by_month': list(labors_by_month),
            'labors_detail': list(labors_detail)
        }

    @staticmethod
    def get_production_by_campaign(campaign_id):
        """
        T050: Reporte de producción por campaña
        
        Genera un reporte completo de la producción obtenida en una campaña,
        incluyendo métricas de rendimiento y comparación con metas.
        
        Args:
            campaign_id: ID de la campaña
            
        Returns:
            dict: Diccionario con estadísticas de producción
        """
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return {
                'error': 'Campaña no encontrada',
                'campaign_id': campaign_id
            }

        # Obtener parcelas de la campaña
        parcelas_ids = campaign.parcelas.values_list('parcela_id', flat=True)
        
        # Consultar cosechas de las parcelas
        cosechas_query = Cosecha.objects.filter(
            ciclo_cultivo__cultivo__parcela_id__in=parcelas_ids,
            estado='COMPLETADA'
        )

        # Producción total
        total_production = cosechas_query.aggregate(
            total=Sum('cantidad_cosechada')
        )['total'] or 0

        # Producción por producto (especie de cultivo)
        production_by_product = cosechas_query.values(
            'unidad_medida'
        ).annotate(
            cultivo_especie=F('ciclo_cultivo__cultivo__especie'),
            cantidad_total=Sum('cantidad_cosechada'),
            numero_cosechas=Count('id'),
            precio_promedio=Avg('precio_venta'),
            valor_total=Sum(
                ExpressionWrapper(
                    F('cantidad_cosechada') * F('precio_venta'),
                    output_field=DecimalField()
                )
            )
        ).order_by('-cantidad_total')

        # Calcular rendimiento promedio por hectárea
        superficie_total = Parcela.objects.filter(
            id__in=parcelas_ids
        ).aggregate(
            total=Sum('superficie_hectareas')
        )['total'] or 1  # Evitar división por cero

        avg_yield_per_hectare = float(total_production) / float(superficie_total)

        # Comparativa con meta de producción
        meta_produccion = float(campaign.meta_produccion)
        porcentaje_cumplimiento = (float(total_production) / meta_produccion * 100) if meta_produccion > 0 else 0
        diferencia_meta = float(total_production) - meta_produccion

        # Distribución de calidad de cosechas
        calidad_distribucion = cosechas_query.values('calidad').annotate(
            count=Count('id'),
            cantidad_total=Sum('cantidad_cosechada')
        ).order_by('-cantidad_total')

        # Cosechas por parcela
        production_by_plot = cosechas_query.values(
            parcela_id=F('ciclo_cultivo__cultivo__parcela__id'),
            parcela_nombre=F('ciclo_cultivo__cultivo__parcela__nombre'),
            socio_nombre=F('ciclo_cultivo__cultivo__parcela__socio__usuario__nombres'),
            socio_apellido=F('ciclo_cultivo__cultivo__parcela__socio__usuario__apellidos')
        ).annotate(
            cantidad_total=Sum('cantidad_cosechada'),
            numero_cosechas=Count('id'),
            valor_total=Sum(
                ExpressionWrapper(
                    F('cantidad_cosechada') * F('precio_venta'),
                    output_field=DecimalField()
                )
            )
        ).order_by('-cantidad_total')

        # Valor económico total
        valor_economico_total = cosechas_query.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('cantidad_cosechada') * F('precio_venta'),
                    output_field=DecimalField()
                )
            )
        )['total'] or 0

        return {
            'campaign': {
                'id': campaign.id,
                'nombre': campaign.nombre,
                'fecha_inicio': campaign.fecha_inicio,
                'fecha_fin': campaign.fecha_fin,
                'estado': campaign.estado,
                'meta_produccion': float(campaign.meta_produccion),
                'unidad_meta': campaign.unidad_meta
            },
            'estadisticas': {
                'total_production': float(total_production),
                'avg_yield_per_hectare': round(avg_yield_per_hectare, 2),
                'superficie_total': float(superficie_total),
                'numero_total_cosechas': cosechas_query.count(),
                'valor_economico_total': float(valor_economico_total)
            },
            'comparativa_meta': {
                'meta_produccion': meta_produccion,
                'produccion_real': float(total_production),
                'diferencia': round(diferencia_meta, 2),
                'porcentaje_cumplimiento': round(porcentaje_cumplimiento, 2),
                'cumplida': total_production >= meta_produccion
            },
            'production_by_product': list(production_by_product),
            'calidad_distribucion': list(calidad_distribucion),
            'production_by_plot': list(production_by_plot)
        }

    @staticmethod
    def get_production_by_plot(plot_id, campaign_id=None, start_date=None, end_date=None):
        """
        T052: Reporte de producción por parcela
        
        Genera un reporte de producción específico de una parcela, con opción
        de filtrar por campaña y rango de fechas.
        
        Args:
            plot_id: ID de la parcela
            campaign_id: ID de la campaña (opcional)
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
            
        Returns:
            dict: Diccionario con estadísticas de producción de la parcela
        """
        try:
            parcela = Parcela.objects.select_related('socio__usuario').get(id=plot_id)
        except Parcela.DoesNotExist:
            return {
                'error': 'Parcela no encontrada',
                'plot_id': plot_id
            }

        # Consultar cosechas de la parcela
        cosechas_query = Cosecha.objects.filter(
            ciclo_cultivo__cultivo__parcela=parcela,
            estado='COMPLETADA'
        )

        # Filtrar por campaña si se especifica
        if campaign_id:
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                # Verificar que la parcela pertenezca a la campaña
                if not campaign.parcelas.filter(parcela=parcela).exists():
                    return {
                        'error': 'La parcela no pertenece a la campaña especificada',
                        'plot_id': plot_id,
                        'campaign_id': campaign_id
                    }
            except Campaign.DoesNotExist:
                return {
                    'error': 'Campaña no encontrada',
                    'campaign_id': campaign_id
                }

        # Aplicar filtros de fecha
        if start_date:
            cosechas_query = cosechas_query.filter(fecha_cosecha__gte=start_date)
        if end_date:
            cosechas_query = cosechas_query.filter(fecha_cosecha__lte=end_date)

        # Producción total
        total_production = cosechas_query.aggregate(
            total=Sum('cantidad_cosechada')
        )['total'] or 0

        # Rendimiento por hectárea
        superficie = float(parcela.superficie_hectareas)
        yield_per_hectare = float(total_production) / superficie if superficie > 0 else 0

        # Productos cosechados
        productos_cosechados = cosechas_query.values(
            'unidad_medida'
        ).annotate(
            cultivo_especie=F('ciclo_cultivo__cultivo__especie'),
            cultivo_variedad=F('ciclo_cultivo__cultivo__variedad'),
            cantidad_total=Sum('cantidad_cosechada'),
            numero_cosechas=Count('id'),
            precio_promedio=Avg('precio_venta'),
            valor_total=Sum(
                ExpressionWrapper(
                    F('cantidad_cosechada') * F('precio_venta'),
                    output_field=DecimalField()
                )
            )
        ).order_by('-cantidad_total')

        # Histórico por campaña (si hay múltiples campañas)
        historico_campañas = []
        campañas_parcela = CampaignPlot.objects.filter(
            parcela=parcela
        ).select_related('campaign').order_by('-campaign__fecha_inicio')

        for cp in campañas_parcela:
            cosechas_campaña = Cosecha.objects.filter(
                ciclo_cultivo__cultivo__parcela=parcela,
                fecha_cosecha__gte=cp.campaign.fecha_inicio,
                fecha_cosecha__lte=cp.campaign.fecha_fin,
                estado='COMPLETADA'
            )

            produccion_campaña = cosechas_campaña.aggregate(
                total=Sum('cantidad_cosechada')
            )['total'] or 0

            historico_campañas.append({
                'campaign_id': cp.campaign.id,
                'campaign_nombre': cp.campaign.nombre,
                'fecha_inicio': cp.campaign.fecha_inicio,
                'fecha_fin': cp.campaign.fecha_fin,
                'produccion_total': float(produccion_campaña),
                'numero_cosechas': cosechas_campaña.count(),
                'cultivo_planificado': cp.cultivo_planificado,
                'meta_parcela': float(cp.meta_produccion_parcela) if cp.meta_produccion_parcela else None
            })

        # Detalle de cosechas
        cosechas_detail = cosechas_query.select_related(
            'ciclo_cultivo__cultivo'
        ).values(
            'id',
            'fecha_cosecha',
            'cantidad_cosechada',
            'unidad_medida',
            'calidad',
            'precio_venta',
            'observaciones',
            cultivo_especie=F('ciclo_cultivo__cultivo__especie'),
            cultivo_variedad=F('ciclo_cultivo__cultivo__variedad')
        ).order_by('-fecha_cosecha')

        # Valor económico total
        valor_economico_total = cosechas_query.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('cantidad_cosechada') * F('precio_venta'),
                    output_field=DecimalField()
                )
            )
        )['total'] or 0

        return {
            'parcela': {
                'id': parcela.id,
                'nombre': parcela.nombre,
                'superficie_hectareas': float(parcela.superficie_hectareas),
                'tipo_suelo': parcela.tipo_suelo,
                'ubicacion': parcela.ubicacion,
                'socio': {
                    'id': parcela.socio.id,
                    'nombre_completo': parcela.socio.usuario.get_full_name(),
                    'ci_nit': parcela.socio.usuario.ci_nit
                }
            },
            'filtros_aplicados': {
                'campaign_id': campaign_id,
                'start_date': start_date,
                'end_date': end_date
            },
            'estadisticas': {
                'total_production': float(total_production),
                'yield_per_hectare': round(yield_per_hectare, 2),
                'numero_total_cosechas': cosechas_query.count(),
                'valor_economico_total': float(valor_economico_total)
            },
            'productos_cosechados': list(productos_cosechados),
            'historico_campañas': historico_campañas,
            'cosechas_detail': list(cosechas_detail)
        }
