"""
Configuración del Admin de Django para el módulo de campanias
CU9: Gestión de campanias Agrícolas
Autor: Backend Developer YANDIRA PONER EN EL ADMIN DA IGUAL COPIAR PEGAR, ARCHIVO APARTE PARA NO MEZCLAR
Fecha: Octubre 2025
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.urls import reverse, path
from django.http import HttpResponse
from .models import Campaign, CampaignPartner, CampaignPlot
from .reports import CampaignReports


class CampaignPartnerInline(admin.TabularInline):
    """
    Inline para gestionar socios asignados a una campania
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
    Inline para gestionar parcelas asignadas a una campania
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
    Administración avanzada de campanias Agrícolas
    CU9 - T036: Gestión de campanias
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
        'estado_visual', 'reportes_cu11_links'
    )
    
    date_hierarchy = 'fecha_inicio'
    list_per_page = 25
    save_on_top = True
    list_select_related = ('responsable',)
    autocomplete_fields = ('responsable',)
    
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
        ('📈 Reportes CU11', {
            'fields': ('reportes_cu11_links',),
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
        'exportar_reporte_csv',
        'exportar_reporte_produccion_csv',
        'exportar_reporte_labores_csv'
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
        """Link al responsable de la campania"""
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
        """Progreso temporal de la campania"""
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

    # ---------------------------
    # Reportes CU11 en el Admin
    # ---------------------------

    def reportes_cu11_links(self, obj):
        """Muestra accesos rápidos a reportes CU11 dentro del admin."""
        if not obj.pk:
            return '-'
        url_lab = reverse('admin:cooperativa_campaign_report_labors', args=[obj.pk])
        url_prod = reverse('admin:cooperativa_campaign_report_production', args=[obj.pk])
        return format_html(
            '<div style="margin-bottom:8px;color:#555;">'
            'Abre los reportes en una nueva pestaña. Si acabas de crear la campania, guarda primero.'
            '</div>'
            '<div style="display:flex; gap:8px; flex-wrap:wrap;">'
            '<a class="button" target="_blank" href="{}">Reporte de Labores</a>'
            '<a class="button" target="_blank" href="{}">Reporte de Producción</a>'
            '</div>',
            url_lab, url_prod
        )
    reportes_cu11_links.short_description = 'Accesos a Reportes CU11'

    def get_urls(self):
        """Agrega rutas personalizadas para reportes CU11 bajo el namespace del admin."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'report/labors/<int:campaign_id>/',
                self.admin_site.admin_view(self.report_labors_view),
                name='cooperativa_campaign_report_labors'
            ),
            path(
                'report/production/<int:campaign_id>/',
                self.admin_site.admin_view(self.report_production_view),
                name='cooperativa_campaign_report_production'
            ),
        ]
        return custom_urls + urls

    def _html_table(self, headers, rows):
        """Helper para construir una tabla HTML simple y compatible con el admin."""
        thead = ''.join([f'<th style="text-align:left; padding:6px 10px;">{h}</th>' for h in headers])
        trs = []
        for r in rows:
            tds = ''.join([f'<td style="padding:6px 10px;">{(v if v is not None else "-")}</td>' for v in r])
            trs.append(f'<tr>{tds}</tr>')
        tbody = ''.join(trs)
        return f'<table class="adminlist" style="border-collapse:collapse; width:100%;">' \
               f'<thead style="background:#f8f9fa;">{thead}</thead><tbody>{tbody}</tbody></table>'

    def report_labors_view(self, request, campaign_id):
        """Vista HTML sencilla con el reporte de labores (CU11/T039)."""
        data = CampaignReports.get_labors_by_campaign(campaign_id)
        if 'error' in data:
            return HttpResponse(f"<h2>Error</h2><p>{data['error']}</p>")

        camp = data['campaign']
        est = data['estadisticas']

        # Tabla de labores por tipo
        headers = ['Tipo de Tratamiento', 'Cantidad', 'Costo Total', 'Dosis Promedio']
        rows = [
            (
                item.get('tipo_tratamiento', '-'),
                item.get('count', 0),
                f"{float(item.get('costo_total') or 0):.2f}",
                f"{float(item.get('dosis_promedio') or 0):.2f}"
            )
            for item in data.get('labors_by_type', [])
        ]
        table_labors = self._html_table(headers, rows)

        html = f"""
        <div class="container">
          <h2>Reporte de Labores - {camp['nombre']}</h2>
          <p><strong>Periodo:</strong> {camp['fecha_inicio']} a {camp['fecha_fin']} | <strong>Estado:</strong> {camp['estado']}</p>
          <div style="display:flex; gap:20px; flex-wrap:wrap; margin:12px 0;">
            <div><strong>Total de labores:</strong> {est['total_labors']}</div>
            <div><strong>Área trabajada (ha):</strong> {est['total_area_worked']:.2f}</div>
            <div><strong>Costo total (Bs):</strong> {est['costo_total_labores']:.2f}</div>
            <div><strong>Parcelas trabajadas:</strong> {est['parcelas_trabajadas']}</div>
          </div>
          <h3>Labores por tipo</h3>
          {table_labors}
        </div>
        """
        return HttpResponse(html)

    def report_production_view(self, request, campaign_id):
        """Vista HTML sencilla con el reporte de producción (CU11/T050)."""
        data = CampaignReports.get_production_by_campaign(campaign_id)
        if 'error' in data:
            return HttpResponse(f"<h2>Error</h2><p>{data['error']}</p>")

        camp = data['campaign']
        est = data['estadisticas']
        comp = data['comparativa_meta']

        # Producción por producto
        headers_prod = ['Producto', 'Unidad', 'Cantidad Total', 'Nro Cosechas', 'Precio Promedio', 'Valor Total']
        rows_prod = [
            (
                item.get('cultivo_especie', '-'),
                item.get('unidad_medida', '-') if isinstance(item, dict) else '-',
                f"{float(item.get('cantidad_total') or 0):.2f}",
                item.get('numero_cosechas', 0),
                f"{float(item.get('precio_promedio') or 0):.2f}",
                f"{float(item.get('valor_total') or 0):.2f}"
            ) for item in data.get('production_by_product', [])
        ]
        table_prod = self._html_table(headers_prod, rows_prod)

        # Producción por parcela
        headers_plot = ['Parcela', 'Socio', 'Cantidad Total', 'Nro Cosechas', 'Valor Total (Bs)']
        rows_plot = [
            (
                item.get('parcela_nombre', '-'),
                f"{item.get('socio_nombre', '')} {item.get('socio_apellido', '')}",
                f"{float(item.get('cantidad_total') or 0):.2f}",
                item.get('numero_cosechas', 0),
                f"{float(item.get('valor_total') or 0):.2f}"
            ) for item in data.get('production_by_plot', [])
        ]
        table_plot = self._html_table(headers_plot, rows_plot)

        html = f"""
        <div class="container">
          <h2>Reporte de Producción - {camp['nombre']}</h2>
          <p><strong>Periodo:</strong> {camp['fecha_inicio']} a {camp['fecha_fin']} | <strong>Estado:</strong> {camp['estado']}</p>
          <div style=\"display:flex; gap:20px; flex-wrap:wrap; margin:12px 0;\">
            <div><strong>Producción Total:</strong> {est['total_production']:.2f} {camp['unidad_meta']}</div>
            <div><strong>Rendimiento (por ha):</strong> {est['avg_yield_per_hectare']:.2f}</div>
            <div><strong>Superficie (ha):</strong> {est['superficie_total']:.2f}</div>
            <div><strong>Cosechas:</strong> {est['numero_total_cosechas']}</div>
            <div><strong>Valor Económico (Bs):</strong> {est['valor_economico_total']:.2f}</div>
          </div>
          <div style="margin:8px 0 16px;">
            <strong>Meta:</strong> {comp['meta_produccion']:.2f} | <strong>Real:</strong> {comp['produccion_real']:.2f} | 
            <strong>Cumplimiento:</strong> {comp['porcentaje_cumplimiento']:.2f}%
          </div>
          <h3>Producción por producto</h3>
          {table_prod}
          <h3 style="margin-top:16px;">Producción por parcela</h3>
          {table_plot}
        </div>
        """
        return HttpResponse(html)
    
    # Acciones en lote
    
    def marcar_en_curso(self, request, queryset):
        """Marcar campanias seleccionadas como EN_CURSO"""
        updated = queryset.update(estado='EN_CURSO')
        self.message_user(
            request,
            f'{updated} campania(s) marcada(s) como EN CURSO.'
        )
    marcar_en_curso.short_description = "▶️ Marcar como EN CURSO"
    
    def marcar_finalizada(self, request, queryset):
        """Marcar campanias seleccionadas como FINALIZADA"""
        updated = queryset.update(estado='FINALIZADA')
        self.message_user(
            request,
            f'{updated} campania(s) marcada(s) como FINALIZADA.'
        )
    marcar_finalizada.short_description = "✅ Marcar como FINALIZADA"
    
    def marcar_cancelada(self, request, queryset):
        """Marcar campanias seleccionadas como CANCELADA"""
        updated = queryset.update(estado='CANCELADA')
        self.message_user(
            request,
            f'{updated} campania(s) marcada(s) como CANCELADA.'
        )
    marcar_cancelada.short_description = "❌ Marcar como CANCELADA"
    
    def clonar_campana(self, request, queryset):
        """Clonar campanias seleccionadas"""
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
            f'{count} campania(s) clonada(s) exitosamente. '
            f'Recuerda asignar socios y parcelas a las copias.'
        )
    clonar_campana.short_description = "📋 Clonar campania(s)"
    
    def exportar_reporte_csv(self, request, queryset):
        """Exportar campanias a CSV"""
        import csv
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="campanias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
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
            f'Exportadas {queryset.count()} campania(s) a CSV.'
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

    # Acciones específicas CU11 (exports rápidos)

    def exportar_reporte_produccion_csv(self, request, queryset):
        """Exporta un resumen de producción (CU11/T050) para las campanias seleccionadas."""
        import csv
        from datetime import datetime

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="reporte_produccion_cu11_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow([
            'campania', 'Meta', 'Producción Real', 'Cumplimiento (%)',
            'Rendimiento (por ha)', 'Superficie (ha)', 'Cosechas', 'Valor Económico (Bs)'
        ])

        for camp in queryset:
            data = CampaignReports.get_production_by_campaign(camp.id)
            if 'error' in data:
                continue
            est = data['estadisticas']
            comp = data['comparativa_meta']
            writer.writerow([
                camp.nombre,
                f"{comp['meta_produccion']:.2f}",
                f"{comp['produccion_real']:.2f}",
                f"{comp['porcentaje_cumplimiento']:.2f}",
                f"{est['avg_yield_per_hectare']:.2f}",
                f"{est['superficie_total']:.2f}",
                est['numero_total_cosechas'],
                f"{est['valor_economico_total']:.2f}"
            ])

        self.message_user(request, f'Resumen de producción exportado para {queryset.count()} campania(s).')
        return response
    exportar_reporte_produccion_csv.short_description = '📈 Exportar Producción (CU11)'

    def exportar_reporte_labores_csv(self, request, queryset):
        """Exporta un resumen de labores (CU11/T039) para las campanias seleccionadas."""
        import csv
        from datetime import datetime

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="reporte_labores_cu11_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow([
            'campania', 'Total Labores', 'Área Trabajada (ha)', 'Costo Total (Bs)', 'Parcelas Trabajadas'
        ])

        for camp in queryset:
            data = CampaignReports.get_labors_by_campaign(camp.id)
            if 'error' in data:
                continue
            est = data['estadisticas']
            writer.writerow([
                camp.nombre,
                est['total_labors'],
                f"{float(est['total_area_worked']):.2f}",
                f"{float(est['costo_total_labores']):.2f}",
                est['parcelas_trabajadas']
            ])

        self.message_user(request, f'Resumen de labores exportado para {queryset.count()} campania(s).')
        return response
    exportar_reporte_labores_csv.short_description = '🧪 Exportar Labores (CU11)'


@admin.register(CampaignPartner)
class CampaignPartnerAdmin(admin.ModelAdmin):
    """
    Administración de Socios asignados a campanias
    CU9 - T037: Relación campania-Socios
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
        """Link a la campania"""
        url = reverse('admin:cooperativa_campaign_change', args=[obj.campaign.id])
        return format_html(
            '<a href="{}" style="color: #007bff; font-weight: bold;">{}</a>',
            url, obj.campaign.nombre
        )
    campaign_link.short_description = 'campania'
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
    Administración de Parcelas asignadas a campanias
    CU9 - T037: Relación campania-Parcelas
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
        """Link a la campania"""
        url = reverse('admin:cooperativa_campaign_change', args=[obj.campaign.id])
        return format_html(
            '<a href="{}" style="color: #007bff; font-weight: bold;">{}</a>',
            url, obj.campaign.nombre
        )
    campaign_link.short_description = 'campania'
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
