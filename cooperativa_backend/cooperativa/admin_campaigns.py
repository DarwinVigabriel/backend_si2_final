"""
Configuración del Admin de Django para el módulo de Campañas
CU9: Gestión de Campañas Agrícolas
Autor: Backend Developer YANDIRA PONER EN EL ADMIN DA IGUAL COPIAR PEGAR, ARCHIVO APARTE PARA NO MEZCLAR
Fecha: Octubre 2025
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.urls import reverse
from .models import Campaign, CampaignPartner, CampaignPlot


class CampaignPartnerInline(admin.TabularInline):
    """
    Inline para gestionar socios asignados a una campaña
    """
    model = CampaignPartner
    extra = 0
    fields = ('socio', 'rol', 'fecha_asignacion', 'observaciones')
    raw_id_fields = ('socio',)
    readonly_fields = ('creado_en',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('socio', 'socio__usuario')


class CampaignPlotInline(admin.TabularInline):
    """
    Inline para gestionar parcelas asignadas a una campaña
    """
    model = CampaignPlot
    extra = 0
    fields = (
        'parcela', 'fecha_asignacion', 'superficie_comprometida',
        'cultivo_planificado', 'meta_produccion_parcela'
    )
    raw_id_fields = ('parcela',)
    readonly_fields = ('creado_en',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parcela', 'parcela__socio')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """
    Administración avanzada de Campañas Agrícolas
    CU9 - T036: Gestión de Campañas
    """
    list_display = (
        'id', 'nombre', 'estado_badge', 'fecha_inicio', 'fecha_fin',
        'duracion_badge', 'meta_produccion', 'unidad_meta',
        'total_socios_badge', 'total_parcelas_badge',
        'progreso_badge', 'responsable_link', 'creado_en'
    )
    
    list_filter = (
        'estado', 'fecha_inicio', 'fecha_fin', 'responsable', 'creado_en'
    )
    
    search_fields = (
        'nombre', 'descripcion', 'responsable__nombres',
        'responsable__apellidos', 'responsable__usuario'
    )
    
    readonly_fields = (
        'creado_en', 'actualizado_en', 'duracion_dias',
        'progreso_temporal_display', 'dias_restantes', 'total_socios',
        'total_parcelas', 'total_superficie_comprometida',
        'estado_visual'
    )
    
    date_hierarchy = 'fecha_inicio'
    list_per_page = 25
    
    inlines = [CampaignPartnerInline, CampaignPlotInline]
    
    fieldsets = (
        ('📋 Información General', {
            'fields': ('nombre', 'descripcion', 'estado', 'responsable')
        }),
        ('📅 Fechas y Duración', {
            'fields': (
                ('fecha_inicio', 'fecha_fin'),
                'duracion_dias', 'dias_restantes', 'progreso_temporal_display'
            )
        }),
        ('🎯 Metas y Presupuesto', {
            'fields': (
                ('meta_produccion', 'unidad_meta'),
                'presupuesto'
            )
        }),
        ('📊 Estadísticas', {
            'fields': (
                'total_socios', 'total_parcelas',
                'total_superficie_comprometida', 'estado_visual'
            ),
            'classes': ('collapse',)
        }),
        ('🕐 Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'marcar_en_curso',
        'marcar_finalizada',
        'marcar_cancelada',
        'clonar_campana',
        'exportar_reporte_csv'
    ]
    
    # Métodos para list_display
    
    def estado_badge(self, obj):
        """Badge colorido para el estado"""
        colors = {
            'PLANIFICADA': '#17a2b8',  # info
            'EN_CURSO': '#28a745',      # success
            'FINALIZADA': '#6c757d',    # secondary
            'CANCELADA': '#dc3545'      # danger
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.estado, '#6c757d'),
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def duracion_badge(self, obj):
        """Muestra la duración en días"""
        dias = obj.duracion_dias()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 10px;">{} días</span>',
            dias
        )
    duracion_badge.short_description = 'Duración'
    
    def progreso_badge(self, obj):
        """Barra de progreso visual"""
        progreso = obj.progreso_temporal()
        color = '#28a745' if progreso >= 75 else '#ffc107' if progreso >= 50 else '#dc3545'
        progreso_str = f'{progreso:.0f}'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; height: 20px; line-height: 20px; '
            'text-align: center; color: white; font-size: 10px; font-weight: bold;">{}%</div>'
            '</div>',
            progreso_str, color, progreso_str
        )
    progreso_badge.short_description = 'Progreso'
    
    def total_socios_badge(self, obj):
        """Contador de socios asignados"""
        count = obj.socios_asignados.count()
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 2px 8px; '
            'border-radius: 50%; font-size: 11px; font-weight: bold;">{}</span>',
            count
        )
    total_socios_badge.short_description = '👥 Socios'
    
    def total_parcelas_badge(self, obj):
        """Contador de parcelas asignadas"""
        count = obj.parcelas.count()
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 2px 8px; '
            'border-radius: 50%; font-size: 11px; font-weight: bold;">{}</span>',
            count
        )
    total_parcelas_badge.short_description = '🌱 Parcelas'
    
    def responsable_link(self, obj):
        """Link al responsable de la campaña"""
        if obj.responsable:
            url = reverse('admin:cooperativa_usuario_change', args=[obj.responsable.id])
            return format_html(
                '<a href="{}" style="color: #007bff;">{}</a>',
                url, obj.responsable.get_full_name()
            )
        return '-'
    responsable_link.short_description = 'Responsable'
    responsable_link.admin_order_field = 'responsable__nombres'
    
    # Métodos para readonly_fields
    
    def duracion_dias(self, obj):
        """Duración calculada en días"""
        return f"{obj.duracion_dias()} días"
    duracion_dias.short_description = 'Duración Total'
    
    def progreso_temporal_display(self, obj):
        """Progreso temporal de la campaña"""
        progreso = obj.progreso_temporal()
        color = '#28a745' if progreso >= 75 else '#ffc107' if progreso >= 50 else '#dc3545'
        return format_html(
            '<div style="font-size: 14px; font-weight: bold; color: {};">{}</div>',
            color,
            f'{progreso:.1f}%'
        )
    progreso_temporal_display.short_description = 'Progreso Temporal'
    
    def total_socios(self, obj):
        """Total de socios asignados"""
        count = obj.socios_asignados.count()
        return f"{count} socio(s) asignado(s)"
    total_socios.short_description = 'Total Socios'
    
    def total_parcelas(self, obj):
        """Total de parcelas asignadas"""
        count = obj.parcelas.count()
        return f"{count} parcela(s) asignada(s)"
    total_parcelas.short_description = 'Total Parcelas'
    
    def total_superficie_comprometida(self, obj):
        """Superficie total comprometida"""
        total = obj.parcelas.aggregate(
            total=Sum('superficie_comprometida')
        )['total'] or 0
        return f"{total:.2f} hectáreas"
    total_superficie_comprometida.short_description = 'Superficie Total'
    
    def estado_visual(self, obj):
        """Visualización completa del estado"""
        progreso = obj.progreso_temporal()
        dias_rest = obj.dias_restantes()
        return format_html(
            '<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">'
            '<strong>Estado:</strong> {}<br>'
            '<strong>Progreso:</strong> {}%<br>'
            '<strong>Días restantes:</strong> {}<br>'
            '<strong>Socios:</strong> {}<br>'
            '<strong>Parcelas:</strong> {}'
            '</div>',
            obj.get_estado_display(),
            f'{progreso:.1f}',
            dias_rest if dias_rest >= 0 else 'Finalizada',
            obj.socios_asignados.count(),
            obj.parcelas.count()
        )
    estado_visual.short_description = 'Resumen Visual'
    
    # Acciones en lote
    
    def marcar_en_curso(self, request, queryset):
        """Marcar campañas seleccionadas como EN_CURSO"""
        updated = queryset.update(estado='EN_CURSO')
        self.message_user(
            request,
            f'{updated} campaña(s) marcada(s) como EN CURSO.'
        )
    marcar_en_curso.short_description = "▶️ Marcar como EN CURSO"
    
    def marcar_finalizada(self, request, queryset):
        """Marcar campañas seleccionadas como FINALIZADA"""
        updated = queryset.update(estado='FINALIZADA')
        self.message_user(
            request,
            f'{updated} campaña(s) marcada(s) como FINALIZADA.'
        )
    marcar_finalizada.short_description = "✅ Marcar como FINALIZADA"
    
    def marcar_cancelada(self, request, queryset):
        """Marcar campañas seleccionadas como CANCELADA"""
        updated = queryset.update(estado='CANCELADA')
        self.message_user(
            request,
            f'{updated} campaña(s) marcada(s) como CANCELADA.'
        )
    marcar_cancelada.short_description = "❌ Marcar como CANCELADA"
    
    def clonar_campana(self, request, queryset):
        """Clonar campañas seleccionadas"""
        count = 0
        for campaign in queryset:
            # Crear clon sin socios ni parcelas
            campaign_clone = Campaign.objects.create(
                nombre=f"{campaign.nombre} (Copia)",
                descripcion=f"Copia de: {campaign.descripcion or ''}",
                fecha_inicio=campaign.fecha_inicio,
                fecha_fin=campaign.fecha_fin,
                meta_produccion=campaign.meta_produccion,
                unidad_meta=campaign.unidad_meta,
                estado='PLANIFICADA',
                presupuesto=campaign.presupuesto,
                responsable=campaign.responsable
            )
            count += 1
        
        self.message_user(
            request,
            f'{count} campaña(s) clonada(s) exitosamente. '
            f'Recuerda asignar socios y parcelas a las copias.'
        )
    clonar_campana.short_description = "📋 Clonar campaña(s)"
    
    def exportar_reporte_csv(self, request, queryset):
        """Exportar campañas a CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="campañas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response.write('\ufeff')  # BOM para Excel
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nombre', 'Estado', 'Fecha Inicio', 'Fecha Fin',
            'Duración (días)', 'Meta Producción', 'Unidad', 'Presupuesto',
            'Responsable', 'Socios', 'Parcelas', 'Superficie (ha)',
            'Progreso (%)', 'Creado'
        ])
        
        for campaign in queryset:
            socios_count = campaign.socios_asignados.count()
            parcelas_count = campaign.parcelas.count()
            superficie = campaign.parcelas.aggregate(
                total=Sum('superficie_comprometida')
            )['total'] or 0
            
            writer.writerow([
                campaign.id,
                campaign.nombre,
                campaign.get_estado_display(),
                campaign.fecha_inicio,
                campaign.fecha_fin,
                campaign.duracion_dias(),
                campaign.meta_produccion,
                campaign.unidad_meta,
                campaign.presupuesto or '',
                campaign.responsable.get_full_name() if campaign.responsable else '',
                socios_count,
                parcelas_count,
                f"{superficie:.2f}",
                f"{campaign.progreso_temporal():.1f}",
                campaign.creado_en.strftime("%Y-%m-%d %H:%M")
            ])
        
        self.message_user(
            request,
            f'Exportadas {queryset.count()} campaña(s) a CSV.'
        )
        return response
    
    exportar_reporte_csv.short_description = "📊 Exportar a CSV"
    
    def get_queryset(self, request):
        """Optimizar consultas con prefetch"""
        return super().get_queryset(request).select_related(
            'responsable'
        ).prefetch_related(
            'socios_asignados',
            'parcelas'
        )


@admin.register(CampaignPartner)
class CampaignPartnerAdmin(admin.ModelAdmin):
    """
    Administración de Socios asignados a Campañas
    CU9 - T037: Relación Campaña-Socios
    """
    list_display = (
        'id', 'campaign_link', 'socio_link', 'rol_badge',
        'fecha_asignacion', 'creado_en'
    )
    
    list_filter = ('rol', 'fecha_asignacion', 'creado_en')
    
    search_fields = (
        'campaign__nombre', 'socio__usuario__nombres',
        'socio__usuario__apellidos', 'socio__codigo_interno'
    )
    
    raw_id_fields = ('campaign', 'socio')
    readonly_fields = ('creado_en',)
    date_hierarchy = 'fecha_asignacion'
    
    fieldsets = (
        ('📋 Asignación', {
            'fields': ('campaign', 'socio', 'rol', 'fecha_asignacion')
        }),
        ('📝 Observaciones', {
            'fields': ('observaciones',)
        }),
        ('🕐 Auditoría', {
            'fields': ('creado_en',),
            'classes': ('collapse',)
        }),
    )
    
    def campaign_link(self, obj):
        """Link a la campaña"""
        url = reverse('admin:cooperativa_campaign_change', args=[obj.campaign.id])
        return format_html(
            '<a href="{}" style="color: #007bff; font-weight: bold;">{}</a>',
            url, obj.campaign.nombre
        )
    campaign_link.short_description = 'Campaña'
    campaign_link.admin_order_field = 'campaign__nombre'
    
    def socio_link(self, obj):
        """Link al socio"""
        url = reverse('admin:cooperativa_socio_change', args=[obj.socio.id])
        return format_html(
            '<a href="{}" style="color: #28a745;">{}</a>',
            url, obj.socio.usuario.get_full_name()
        )
    socio_link.short_description = 'Socio'
    socio_link.admin_order_field = 'socio__usuario__nombres'
    
    def rol_badge(self, obj):
        """Badge para el rol"""
        colors = {
            'COORDINADOR': '#dc3545',
            'PRODUCTOR': '#28a745',
            'TECNICO': '#17a2b8',
            'SUPERVISOR': '#ffc107'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.rol, '#6c757d'),
            obj.get_rol_display()
        )
    rol_badge.short_description = 'Rol'
    rol_badge.admin_order_field = 'rol'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'campaign', 'socio', 'socio__usuario'
        )


@admin.register(CampaignPlot)
class CampaignPlotAdmin(admin.ModelAdmin):
    """
    Administración de Parcelas asignadas a Campañas
    CU9 - T037: Relación Campaña-Parcelas
    """
    list_display = (
        'id', 'campaign_link', 'parcela_link', 'socio_nombre',
        'superficie_badge', 'cultivo_planificado', 'meta_badge',
        'fecha_asignacion', 'creado_en'
    )
    
    list_filter = ('fecha_asignacion', 'creado_en', 'cultivo_planificado')
    
    search_fields = (
        'campaign__nombre', 'parcela__nombre',
        'parcela__socio__usuario__nombres', 'cultivo_planificado'
    )
    
    raw_id_fields = ('campaign', 'parcela')
    readonly_fields = ('creado_en', 'porcentaje_superficie')
    date_hierarchy = 'fecha_asignacion'
    
    fieldsets = (
        ('📋 Asignación', {
            'fields': ('campaign', 'parcela', 'fecha_asignacion')
        }),
        ('🌱 Cultivo y Producción', {
            'fields': (
                'cultivo_planificado',
                ('superficie_comprometida', 'porcentaje_superficie'),
                'meta_produccion_parcela'
            )
        }),
        ('📝 Observaciones', {
            'fields': ('observaciones',)
        }),
        ('🕐 Auditoría', {
            'fields': ('creado_en',),
            'classes': ('collapse',)
        }),
    )
    
    def campaign_link(self, obj):
        """Link a la campaña"""
        url = reverse('admin:cooperativa_campaign_change', args=[obj.campaign.id])
        return format_html(
            '<a href="{}" style="color: #007bff; font-weight: bold;">{}</a>',
            url, obj.campaign.nombre
        )
    campaign_link.short_description = 'Campaña'
    campaign_link.admin_order_field = 'campaign__nombre'
    
    def parcela_link(self, obj):
        """Link a la parcela"""
        url = reverse('admin:cooperativa_parcela_change', args=[obj.parcela.id])
        return format_html(
            '<a href="{}" style="color: #28a745; font-weight: bold;">{}</a>',
            url, obj.parcela.nombre
        )
    parcela_link.short_description = 'Parcela'
    parcela_link.admin_order_field = 'parcela__nombre'
    
    def socio_nombre(self, obj):
        """Nombre del socio propietario"""
        return obj.parcela.socio.usuario.get_full_name()
    socio_nombre.short_description = 'Socio'
    socio_nombre.admin_order_field = 'parcela__socio__usuario__nombres'
    
    def superficie_badge(self, obj):
        """Badge de superficie"""
        if obj.superficie_comprometida:
            porcentaje = (float(obj.superficie_comprometida) / float(obj.parcela.superficie_hectareas)) * 100
            color = '#28a745' if porcentaje <= 100 else '#dc3545'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">{} ha ({}%)</span>',
                color, 
                f'{float(obj.superficie_comprometida):.2f}',
                f'{porcentaje:.0f}'
            )
        return '-'
    superficie_badge.short_description = 'Superficie'
    
    def meta_badge(self, obj):
        """Badge de meta de producción"""
        if obj.meta_produccion_parcela:
            return format_html(
                '<span style="background-color: #ffc107; color: #000; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
                f'{float(obj.meta_produccion_parcela):.2f}'
            )
        return '-'
    meta_badge.short_description = 'Meta Producción'
    
    def porcentaje_superficie(self, obj):
        """Porcentaje de superficie comprometida"""
        if obj.superficie_comprometida:
            porcentaje = (float(obj.superficie_comprometida) / float(obj.parcela.superficie_hectareas)) * 100
            return format_html(
                '<div style="font-size: 14px; font-weight: bold; color: {};">'
                '{}% de la parcela ({}/{} ha)'
                '</div>',
                '#28a745' if porcentaje <= 100 else '#dc3545',
                f'{porcentaje:.1f}',
                f'{float(obj.superficie_comprometida):.2f}',
                f'{float(obj.parcela.superficie_hectareas):.2f}'
            )
        return '-'
    porcentaje_superficie.short_description = 'Porcentaje Comprometido'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related(
            'campaign', 'parcela', 'parcela__socio', 'parcela__socio__usuario'
        )
