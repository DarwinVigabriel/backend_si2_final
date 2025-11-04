from django.contrib import admin
from django import forms
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    Usuario, Rol, Comunidad, Socio, Parcela, Cultivo, 
    BitacoraAuditoria, UsuarioRol, Semilla, Pesticida, 
    Fertilizante, Labor, ProductoCosechado, Pedido, 
    DetallePedido, Pago, PaymentMethod
)

# Register your models here.

# Branding del panel administrativo (no afecta otros CU)
admin.site.site_header = "🌱 Cooperativa Agrícola – Panel Administrativo"
admin.site.site_title = "Cooperativa Admin"
admin.site.index_title = "Inicio del Panel"

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'es_sistema', 'creado_en')
    list_filter = ('es_sistema', 'creado_en')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('creado_en', 'actualizado_en')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.es_sistema:
            # Si es un rol del sistema, hacer todos los campos readonly excepto permisos
            return ['nombre', 'descripcion', 'es_sistema', 'creado_en', 'actualizado_en']
        return self.readonly_fields

@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'rol', 'creado_en')
    list_filter = ('rol', 'creado_en')
    search_fields = ('usuario__usuario', 'usuario__nombres', 'usuario__apellidos', 'rol__nombre')
    raw_id_fields = ('usuario', 'rol')
    readonly_fields = ('creado_en',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'rol')


class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 0
    readonly_fields = ('creado_en',)
    fields = ('rol', 'creado_en')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rol')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rol":
            # Mostrar solo roles del sistema ordenados por nombre
            kwargs["queryset"] = Rol.objects.filter(es_sistema=True).order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Validar que no se asignen roles duplicados
        def clean(self):
            super(formset, self).clean()
            if hasattr(self, 'cleaned_data'):
                roles = []
                for form in self:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        rol = form.cleaned_data.get('rol')
                        if rol in roles:
                            raise forms.ValidationError("No se puede asignar el mismo rol múltiples veces.")
                        roles.append(rol)
        formset.clean = clean
        return formset


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nombres', 'apellidos', 'email', 'is_staff', 'is_superuser', 'estado', 'get_roles', 'creado_en')
    list_filter = ('estado', 'is_staff', 'is_superuser', 'creado_en')
    search_fields = ('usuario', 'nombres', 'apellidos', 'email', 'ci_nit')
    readonly_fields = ('creado_en', 'actualizado_en', 'ultimo_intento', 'fecha_bloqueo', 'date_joined')
    list_editable = ('is_staff', 'is_superuser', 'estado')
    inlines = [UsuarioRolInline]
    actions = ['asignar_rol_administrador', 'asignar_rol_socio', 'asignar_rol_operador', 'quitar_todos_roles']

    fieldsets = (
        ('Información Personal', {
            'fields': ('ci_nit', 'nombres', 'apellidos', 'email', 'telefono')
        }),
        ('Información de Usuario', {
            'fields': ('usuario', 'estado', 'is_staff', 'is_superuser')
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Seguridad', {
            'fields': ('intentos_fallidos', 'ultimo_intento', 'fecha_bloqueo'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('usuariorol_set__rol')

    def get_roles(self, obj):
        roles = obj.usuariorol_set.all()
        if roles:
            return ", ".join([rol.rol.nombre for rol in roles])
        return "Sin roles asignados"
    get_roles.short_description = 'Roles'
    get_roles.admin_order_field = 'usuariorol__rol__nombre'

    def asignar_rol_administrador(self, request, queryset):
        rol_admin = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={
                'descripcion': 'Rol con permisos completos de administración del sistema',
                'permisos': {
                    'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'auditoria': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'configuracion': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True}
                },
                'es_sistema': True,
                'creado_en': timezone.now(),
                'actualizado_en': timezone.now()
            }
        )[0]

        # Actualizar permisos si el rol ya existe
        if not rol_admin.permisos:
            rol_admin.permisos = {
                'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'auditoria': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'configuracion': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True}
            }
            rol_admin.save()

        for usuario in queryset:
            UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol_admin,
                defaults={'creado_en': timezone.now()}
            )
            usuario.is_staff = True
            usuario.is_superuser = True
            usuario.save()

        self.message_user(request, f'Rol Administrador asignado a {queryset.count()} usuario(s).')
    asignar_rol_administrador.short_description = "Asignar rol Administrador"

    def asignar_rol_socio(self, request, queryset):
        rol_socio = Rol.objects.get_or_create(
            nombre='Socio',
            defaults={
                'descripcion': 'Rol para socios de la cooperativa con acceso limitado a sus propios datos',
                'permisos': {
                    'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'socios': {'ver': True, 'crear': False, 'editar': True, 'eliminar': False, 'aprobar': False},
                    'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                    'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'transferencias': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'reportes': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'auditoria': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'configuracion': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
                },
                'es_sistema': True,
                'creado_en': timezone.now(),
                'actualizado_en': timezone.now()
            }
        )[0]

        # Actualizar permisos si el rol ya existe
        if not rol_socio.permisos:
            rol_socio.permisos = {
                'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'socios': {'ver': True, 'crear': False, 'editar': True, 'eliminar': False, 'aprobar': False},
                'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'transferencias': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False, 'aprobar': False},
                'reportes': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'auditoria': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'configuracion': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
            }
            rol_socio.save()

        for usuario in queryset:
            UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol_socio,
                defaults={'creado_en': timezone.now()}
            )

        self.message_user(request, f'Rol Socio asignado a {queryset.count()} usuario(s).')
    asignar_rol_socio.short_description = "Asignar rol Socio"

    def asignar_rol_operador(self, request, queryset):
        rol_operador = Rol.objects.get_or_create(
            nombre='Operador',
            defaults={
                'descripcion': 'Rol para operadores con permisos intermedios de gestión operativa',
                'permisos': {
                    'usuarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                    'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                    'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                    'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                    'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'configuracion': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
                },
                'es_sistema': True,
                'creado_en': timezone.now(),
                'actualizado_en': timezone.now()
            }
        )[0]

        # Actualizar permisos si el rol ya existe
        if not rol_operador.permisos:
            rol_operador.permisos = {
                'usuarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'configuracion': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
            }
            rol_operador.save()

        for usuario in queryset:
            UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol_operador,
                defaults={'creado_en': timezone.now()}
            )

        self.message_user(request, f'Rol Operador asignado a {queryset.count()} usuario(s).')
    asignar_rol_operador.short_description = "Asignar rol Operador"

    def quitar_todos_roles(self, request, queryset):
        count = 0
        for usuario in queryset:
            count += usuario.usuariorol_set.all().delete()[0]

        self.message_user(request, f'{count} rol(es) removido(s) de {queryset.count()} usuario(s).')
    quitar_todos_roles.short_description = "Quitar todos los roles"

@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'municipio', 'departamento', 'creado_en')
    list_filter = ('departamento', 'creado_en')
    search_fields = ('nombre', 'municipio', 'departamento')

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'comunidad', 'codigo_interno', 'estado', 'creado_en')
    list_filter = ('estado', 'comunidad', 'creado_en')
    search_fields = ('usuario__usuario', 'usuario__nombres', 'codigo_interno')
    readonly_fields = ('creado_en',)

@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ('id', 'socio', 'nombre', 'superficie_hectareas', 'latitud', 'longitud', 'estado')
    list_filter = ('estado', 'creado_en')
    search_fields = ('nombre', 'socio__usuario__nombres')
    list_editable = ('estado',)

@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'parcela', 'especie', 'variedad', 'fecha_estimada_siembra', 'estado')
    list_filter = ('estado', 'especie', 'fecha_estimada_siembra')
    search_fields = ('especie', 'variedad', 'parcela__nombre')
    readonly_fields = ('creado_en',)

@admin.register(BitacoraAuditoria)
class BitacoraAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'accion', 'tabla_afectada', 'registro_id', 'fecha', 'ip_address')
    list_filter = ('accion', 'tabla_afectada', 'fecha', 'ip_address')
    search_fields = ('usuario__usuario', 'accion', 'tabla_afectada', 'ip_address')
    readonly_fields = ('fecha', 'ip_address', 'user_agent')
    date_hierarchy = 'fecha'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


@admin.register(Semilla)
class SemillaAdmin(admin.ModelAdmin):
    """
    CU7: Administración de semillas en Django Admin
    T-40: Gestión del catálogo de inventario de semillas
    T-41: CRUD de semillas desde el admin
    """
    list_display = (
        'id', 'especie', 'variedad', 'cantidad', 'unidad_medida',
        'fecha_vencimiento', 'porcentaje_germinacion', 'estado',
        'proveedor', 'lote', 'valor_total', 'dias_para_vencer'
    )
    list_filter = (
        'estado', 'especie', 'proveedor', 'fecha_vencimiento',
        'unidad_medida', 'creado_en'
    )
    search_fields = (
        'especie', 'variedad', 'proveedor', 'lote',
        'ubicacion_almacen'
    )
    readonly_fields = (
        'creado_en', 'actualizado_en', 'valor_total',
        'dias_para_vencer', 'esta_proxima_vencer', 'esta_vencida'
    )
    list_editable = ('estado',)
    date_hierarchy = 'fecha_vencimiento'

    fieldsets = (
        ('Información Básica', {
            'fields': ('especie', 'variedad', 'estado')
        }),
        ('Inventario', {
            'fields': ('cantidad', 'unidad_medida', 'ubicacion_almacen')
        }),
        ('Calidad y Vencimiento', {
            'fields': ('fecha_vencimiento', 'porcentaje_germinacion', 'lote')
        }),
        ('Proveedor y Costos', {
            'fields': ('proveedor', 'precio_unitario')
        }),
        ('Información Adicional', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Campos Calculados', {
            'fields': ('valor_total', 'dias_para_vencer', 'esta_proxima_vencer', 'esta_vencida'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )

    actions = [
        'marcar_como_disponible',
        'marcar_como_agotada',
        'marcar_como_vencida',
        'marcar_como_reservada',
        'exportar_inventario_csv'
    ]

    def valor_total(self, obj):
        return f"{obj.valor_total():.2f} Bs" if obj.valor_total() else "N/A"
    valor_total.short_description = 'Valor Total'

    def dias_para_vencer(self, obj):
        dias = obj.dias_para_vencer()
        if dias is None:
            return "N/A"
        elif dias < 0:
            return f"Vencida ({abs(dias)} días)"
        elif dias == 0:
            return "Vence hoy"
        else:
            return f"{dias} días"
    dias_para_vencer.short_description = 'Días para Vencer'

    def marcar_como_disponible(self, request, queryset):
        updated = queryset.update(estado='DISPONIBLE')
        self.message_user(
            request,
            f'{updated} semilla(s) marcada(s) como disponible(s).'
        )
    marcar_como_disponible.short_description = "Marcar como Disponible"

    def marcar_como_agotada(self, request, queryset):
        updated = queryset.update(estado='AGOTADA')
        self.message_user(
            request,
            f'{updated} semilla(s) marcada(s) como agotada(s).'
        )
    marcar_como_agotada.short_description = "Marcar como Agotada"

    def marcar_como_vencida(self, request, queryset):
        updated = queryset.update(estado='VENCIDA')
        self.message_user(
            request,
            f'{updated} semilla(s) marcada(s) como vencida(s).'
        )
    marcar_como_vencida.short_description = "Marcar como Vencida"

    def marcar_como_reservada(self, request, queryset):
        updated = queryset.update(estado='RESERVADA')
        self.message_user(
            request,
            f'{updated} semilla(s) marcada(s) como reservada(s).'
        )
    marcar_como_reservada.short_description = "Marcar como Reservada"

    def exportar_inventario_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="inventario_semillas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Especie', 'Variedad', 'Cantidad', 'Unidad',
            'Fecha Vencimiento', 'PG%', 'Estado', 'Proveedor',
            'Lote', 'Precio Unitario', 'Valor Total', 'Ubicación'
        ])

        for semilla in queryset:
            writer.writerow([
                semilla.id,
                semilla.especie,
                semilla.variedad or '',
                semilla.cantidad,
                semilla.unidad_medida,
                semilla.fecha_vencimiento,
                semilla.porcentaje_germinacion,
                semilla.estado,
                semilla.proveedor or '',
                semilla.lote or '',
                semilla.precio_unitario or '',
                semilla.valor_total(),
                semilla.ubicacion_almacen or ''
            ])

        self.message_user(request, f'Exportadas {queryset.count()} semillas a CSV.')
        return response

    exportar_inventario_csv.short_description = "Exportar inventario a CSV"

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-creado_en')


@admin.register(Pesticida)
class PesticidaAdmin(admin.ModelAdmin):
    """
    CU8: Administración de pesticidas en Django Admin
    T-42: Gestión de Inventario de Pesticidas
    """
    list_display = (
        'id', 'nombre_comercial', 'ingrediente_activo', 'tipo_pesticida',
        'cantidad', 'unidad_medida', 'fecha_vencimiento', 'estado',
        'proveedor', 'lote', 'valor_total', 'dias_para_vencer'
    )
    list_filter = (
        'estado', 'tipo_pesticida', 'proveedor', 'fecha_vencimiento',
        'unidad_medida', 'creado_en'
    )
    search_fields = (
        'nombre_comercial', 'ingrediente_activo', 'proveedor', 'lote',
        'ubicacion_almacen'
    )
    readonly_fields = (
        'creado_en', 'actualizado_en', 'valor_total',
        'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido'
    )
    list_editable = ('estado',)
    date_hierarchy = 'fecha_vencimiento'

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_comercial', 'ingrediente_activo', 'tipo_pesticida', 'estado')
        }),
        ('Composición y Concentración', {
            'fields': ('concentracion', 'registro_sanitario')
        }),
        ('Inventario', {
            'fields': ('cantidad', 'unidad_medida', 'ubicacion_almacen')
        }),
        ('Vencimiento y Dosis', {
            'fields': ('fecha_vencimiento', 'dosis_recomendada')
        }),
        ('Proveedor y Costos', {
            'fields': ('proveedor', 'precio_unitario', 'lote')
        }),
        ('Información Adicional', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Campos Calculados', {
            'fields': ('valor_total', 'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )

    actions = [
        'marcar_como_disponible',
        'marcar_como_agotado',
        'marcar_como_vencido',
        'marcar_como_en_cuarentena',
        'exportar_inventario_csv'
    ]

    def valor_total(self, obj):
        return f"{obj.valor_total():.2f} Bs" if obj.valor_total() else "N/A"
    valor_total.short_description = 'Valor Total'

    def dias_para_vencer(self, obj):
        dias = obj.dias_para_vencer()
        if dias is None:
            return "N/A"
        elif dias < 0:
            return f"Vencido ({abs(dias)} días)"
        elif dias == 0:
            return "Vence hoy"
        else:
            return f"{dias} días"
    dias_para_vencer.short_description = 'Días para Vencer'

    def marcar_como_disponible(self, request, queryset):
        updated = queryset.update(estado='DISPONIBLE')
        self.message_user(
            request,
            f'{updated} pesticida(s) marcado(s) como disponible(s).'
        )
    marcar_como_disponible.short_description = "Marcar como Disponible"

    def marcar_como_agotado(self, request, queryset):
        updated = queryset.update(estado='AGOTADO')
        self.message_user(
            request,
            f'{updated} pesticida(s) marcado(s) como agotado(s).'
        )
    marcar_como_agotado.short_description = "Marcar como Agotado"

    def marcar_como_vencido(self, request, queryset):
        updated = queryset.update(estado='VENCIDO')
        self.message_user(
            request,
            f'{updated} pesticida(s) marcado(s) como vencido(s).'
        )
    marcar_como_vencido.short_description = "Marcar como Vencida"

    def marcar_como_en_cuarentena(self, request, queryset):
        updated = queryset.update(estado='EN_CUARENTENA')
        self.message_user(
            request,
            f'{updated} pesticida(s) marcado(s) en cuarentena.'
        )
    marcar_como_en_cuarentena.short_description = "Marcar en Cuarentena"

    def exportar_inventario_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="inventario_pesticidas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nombre Comercial', 'Ingrediente Activo', 'Tipo',
            'Concentración', 'Cantidad', 'Unidad', 'Fecha Vencimiento',
            'Estado', 'Proveedor', 'Lote', 'Precio Unitario', 'Valor Total', 'Ubicación'
        ])

        for pesticida in queryset:
            writer.writerow([
                pesticida.id,
                pesticida.nombre_comercial,
                pesticida.ingrediente_activo,
                pesticida.tipo_pesticida,
                pesticida.concentracion,
                pesticida.cantidad,
                pesticida.unidad_medida,
                pesticida.fecha_vencimiento,
                pesticida.estado,
                pesticida.proveedor,
                pesticida.lote,
                pesticida.precio_unitario,
                pesticida.valor_total(),
                pesticida.ubicacion_almacen or ''
            ])

        self.message_user(request, f'Exportados {queryset.count()} pesticidas a CSV.')
        return response

    exportar_inventario_csv.short_description = "Exportar inventario a CSV"

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-creado_en')


@admin.register(Fertilizante)
class FertilizanteAdmin(admin.ModelAdmin):
    """
    CU8: Administración de fertilizantes en Django Admin
    T-45: Gestión de Inventario de Fertilizantes
    """
    list_display = (
        'id', 'nombre_comercial', 'tipo_fertilizante', 'composicion_npk',
        'cantidad', 'unidad_medida', 'fecha_vencimiento', 'estado',
        'proveedor', 'lote', 'valor_total', 'dias_para_vencer'
    )
    list_filter = (
        'estado', 'tipo_fertilizante', 'proveedor', 'fecha_vencimiento',
        'unidad_medida', 'creado_en'
    )
    search_fields = (
        'nombre_comercial', 'composicion_npk', 'proveedor', 'lote',
        'ubicacion_almacen'
    )
    readonly_fields = (
        'creado_en', 'actualizado_en', 'valor_total',
        'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido', 'npk_values'
    )
    list_editable = ('estado',)
    date_hierarchy = 'fecha_vencimiento'

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_comercial', 'tipo_fertilizante', 'estado')
        }),
        ('Composición', {
            'fields': ('composicion_npk', 'materia_orgánica')
        }),
        ('Inventario', {
            'fields': ('cantidad', 'unidad_medida', 'ubicacion_almacen')
        }),
        ('Vencimiento y Dosis', {
            'fields': ('fecha_vencimiento', 'dosis_recomendada')
        }),
        ('Proveedor y Costos', {
            'fields': ('proveedor', 'precio_unitario', 'lote')
        }),
        ('Información Adicional', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Campos Calculados', {
            'fields': ('valor_total', 'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido', 'npk_values'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )

    actions = [
        'marcar_como_disponible',
        'marcar_como_agotado',
        'marcar_como_vencido',
        'marcar_como_en_cuarentena',
        'exportar_inventario_csv'
    ]

    def valor_total(self, obj):
        return f"{obj.valor_total():.2f} Bs" if obj.valor_total() else "N/A"
    valor_total.short_description = 'Valor Total'

    def dias_para_vencer(self, obj):
        dias = obj.dias_para_vencer()
        if dias is None:
            return "N/A"
        elif dias < 0:
            return f"Vencido ({abs(dias)} días)"
        elif dias == 0:
            return "Vence hoy"
        else:
            return f"{dias} días"
    dias_para_vencer.short_description = 'Días para Vencer'

    def npk_values(self, obj):
        values = obj.get_npk_values()
        if values:
            return f"N: {values.get('N', 0)}%, P: {values.get('P', 0)}%, K: {values.get('K', 0)}%"
        return "N/A"
    npk_values.short_description = 'Valores NPK'

    def marcar_como_disponible(self, request, queryset):
        updated = queryset.update(estado='DISPONIBLE')
        self.message_user(
            request,
            f'{updated} fertilizante(s) marcado(s) como disponible(s).'
        )
    marcar_como_disponible.short_description = "Marcar como Disponible"

    def marcar_como_agotado(self, request, queryset):
        updated = queryset.update(estado='AGOTADO')
        self.message_user(
            request,
            f'{updated} fertilizante(s) marcado(s) como agotado(s).'
        )
    marcar_como_agotado.short_description = "Marcar como Agotado"

    def marcar_como_vencido(self, request, queryset):
        updated = queryset.update(estado='VENCIDO')
        self.message_user(
            request,
            f'{updated} fertilizante(s) marcado(s) como vencido(s).'
        )
    marcar_como_vencido.short_description = "Marcar como Vencido"

    def marcar_como_en_cuarentena(self, request, queryset):
        updated = queryset.update(estado='EN_CUARENTENA')
        self.message_user(
            request,
            f'{updated} fertilizante(s) marcado(s) en cuarentena.'
        )
    marcar_como_en_cuarentena.short_description = "Marcar en Cuarentena"

    def exportar_inventario_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="inventario_fertilizantes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nombre Comercial', 'Tipo', 'Composición NPK',
            'Cantidad', 'Unidad', 'Fecha Vencimiento', 'Estado',
            'Proveedor', 'Lote', 'Precio Unitario', 'Valor Total', 'Ubicación'
        ])

        for fertilizante in queryset:
            writer.writerow([
                fertilizante.id,
                fertilizante.nombre_comercial,
                fertilizante.tipo_fertilizante,
                fertilizante.composicion_npk,
                fertilizante.cantidad,
                fertilizante.unidad_medida,
                fertilizante.fecha_vencimiento,
                fertilizante.estado,
                fertilizante.proveedor,
                fertilizante.lote,
                fertilizante.precio_unitario,
                fertilizante.valor_total(),
                fertilizante.ubicacion_almacen or ''
            ])

        self.message_user(request, f'Exportados {queryset.count()} fertilizantes a CSV.')
        return response

    exportar_inventario_csv.short_description = "Exportar inventario a CSV"

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-creado_en')

@admin.register(Labor)
class LaborAdmin(admin.ModelAdmin):
    """
    CU: Administración de Labores Agrícolas en Django Admin
    Gestión de labores agrícolas (siembra, riego, fertilización, cosecha, fumigación)
    """
    list_display = (
        'id', 'labor_display', 'fecha_labor', 'estado_badge', 
        'campania_display', 'parcela_display', 'creado_en'
    )
    
    list_filter = (
        'labor', 'estado', 'fecha_labor', 'campania', 'parcela__socio',
        'creado_en'
    )
    
    search_fields = (
        'labor', 'observaciones', 'campania__nombre', 
        'parcela__nombre', 'parcela__socio__usuario__nombres'
    )
    
    readonly_fields = (
        'creado_en', 'actualizado_en', 'validaciones_info'
    )
    
    list_editable = ('fecha_labor',)
    
    date_hierarchy = 'fecha_labor'
    
    fieldsets = (
        ('Información Principal', {
            'fields': (
                'fecha_labor', 'labor', 'estado', 'observaciones'
            )
        }),
        ('Relaciones', {
            'fields': (
                'campania', 'parcela'
            )
        }),
        ('Auditoría', {
            'fields': (
                'validaciones_info', 'creado_en', 'actualizado_en'
            ),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('campania', 'parcela')
    
    actions = [
        'marcar_como_completada',
        'marcar_como_en_proceso', 
        'marcar_como_planificada',
        'marcar_como_cancelada',
        'exportar_labores_csv'
    ]

    def labor_display(self, obj):
        """Muestra el tipo de labor con icono"""
        icons = {
            'SIEMBRA': '🌱',
            'RIEGO': '💧',
            'FERTILIZACION': '🧪',
            'COSECHA': '📦',
            'FUMIGACION': '🦠'
        }
        icon = icons.get(obj.labor, '📋')
        return f"{icon} {obj.get_labor_display()}"
    labor_display.short_description = 'Labor'
    labor_display.admin_order_field = 'labor'

    def estado_badge(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'PLANIFICADA': 'blue',
            'EN_PROCESO': 'orange',
            'COMPLETADA': 'green',
            'CANCELADA': 'red'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'

    def campania_display(self, obj):
        if obj.campania:
         return format_html(
            '<span title="{}">{}</span>',
            f"{obj.campania.fecha_inicio} a {obj.campania.fecha_fin}",
            obj.campania.nombre
        )
        return "—"
    campania_display.short_description = 'campania'

    def parcela_display(self, obj):
        """Muestra información de la parcela"""
        if obj.parcela:
            socio = obj.parcela.socio
            return format_html(
                '{}<br><small style="color: #666;">{}</small>',
                obj.parcela.nombre,
                f"{socio.usuario.nombres} {socio.usuario.apellidos}"
            )
        return "—"
    parcela_display.short_description = 'Parcela'

    def validaciones_info(self, obj):
        """Muestra información de validaciones"""
        messages = []
        
        # Validar fecha con campania
        if obj.campania and obj.fecha_labor:
            if obj.fecha_labor < obj.campania.fecha_inicio:
                messages.append(f"⚠️ La fecha está ANTES de la campania")
            elif obj.fecha_labor > obj.campania.fecha_fin:
                messages.append(f"⚠️ La fecha está DESPUÉS de la campania")
            else:
                messages.append("✅ Fecha dentro del rango de campania")
        
        # Validar estado de parcela
        if obj.parcela:
            if obj.parcela.estado == 'ACTIVA':
                messages.append("✅ Parcela activa")
            else:
                messages.append(f"❌ Parcela {obj.parcela.get_estado_display().lower()}")
        
        # Validar que tenga al menos campania o parcela
        if not obj.campania and not obj.parcela:
            messages.append("❌ Falta campania y parcela")
        else:
            messages.append("✅ Tiene campania o parcela")
        
        return format_html("<br>".join(messages))
    validaciones_info.short_description = 'Validaciones'

    def marcar_como_completada(self, request, queryset):
        """Acción para marcar labores como completadas"""
        updated = queryset.update(estado='COMPLETADA')
        self.message_user(
            request, 
            f'{updated} labor(es) marcada(s) como completada(s).'
        )
    marcar_como_completada.short_description = "Marcar como COMPLETADA"

    def marcar_como_en_proceso(self, request, queryset):
        """Acción para marcar labores como en proceso"""
        updated = queryset.update(estado='EN_PROCESO')
        self.message_user(
            request, 
            f'{updated} labor(es) marcada(s) como en proceso.'
        )
    marcar_como_en_proceso.short_description = "Marcar como EN PROCESO"

    def marcar_como_planificada(self, request, queryset):
        """Acción para marcar labores como planificadas"""
        updated = queryset.update(estado='PLANIFICADA')
        self.message_user(
            request, 
            f'{updated} labor(es) marcada(s) como planificada(s).'
        )
    marcar_como_planificada.short_description = "Marcar como PLANIFICADA"

    def marcar_como_cancelada(self, request, queryset):
        """Acción para marcar labores como canceladas"""
        updated = queryset.update(estado='CANCELADA')
        self.message_user(
            request, 
            f'{updated} labor(es) marcada(s) como cancelada(s).'
        )
    marcar_como_cancelada.short_description = "Marcar como CANCELADA"

    def exportar_labores_csv(self, request, queryset):
        """Exportar labores seleccionadas a CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="labores_agricolas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Labor', 'Fecha', 'Estado', 'campania', 
            'Parcela', 'Observaciones', 'Creado'
        ])

        for labor in queryset:
            writer.writerow([
                labor.id,
                labor.get_labor_display(),
                labor.fecha_labor,
                labor.get_estado_display(),
                labor.campania.nombre if labor.campania else '',
                labor.parcela.nombre if labor.parcela else '',
                labor.observaciones or '',
                labor.creado_en.strftime('%Y-%m-%d %H:%M')
            ])

        self.message_user(request, f'Exportadas {queryset.count()} labores a CSV.')
        return response
    exportar_labores_csv.short_description = "Exportar labores a CSV"

    def get_queryset(self, request):
        """Optimizar consultas relacionadas"""
        return super().get_queryset(request).select_related(
            'campania', 'parcela__socio__usuario'
        ).order_by('-fecha_labor')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar parcelas activas en el formulario"""
        if db_field.name == "parcela":
            kwargs["queryset"] = Parcela.objects.filter(estado='ACTIVA').select_related('socio__usuario')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(ProductoCosechado)
class ProductoCosechadoAdmin(admin.ModelAdmin):
    """
    CU15: Configuración del admin para Productos Cosechados
    """
    list_display = [
        'id', 'cultivo_especie_display', 'cantidad_display', 'fecha_cosecha', 
        'estado_badge', 'origen_display', 'lote', 'ubicacion_almacen', 'creado_en'
    ]
    
    list_filter = [
        'estado', 'fecha_cosecha', 'cultivo__especie', 'calidad',
        'campania', 'parcela'
    ]
    
    search_fields = [
        'cultivo__especie', 'cultivo__variedad', 'lote', 
        'ubicacion_almacen', 'calidad'
    ]
    
    readonly_fields = [
        'creado_en', 'actualizado_en', 'origen_display', 
        'dias_en_almacen_display', 'puede_vender_display'
    ]
    
    fieldsets = (
        ('Información Principal', {
            'fields': (
                'fecha_cosecha', 'cantidad', 'unidad_medida', 'calidad',
                'estado', 'lote', 'ubicacion_almacen'
            )
        }),
        ('Relaciones', {
            'fields': (
                'cultivo', 'labor', 'campania', 'parcela'
            )
        }),
        ('Información Adicional', {
            'fields': (
                'observaciones',
            )
        }),
        ('Auditoría', {
            'fields': (
                'origen_display', 'dias_en_almacen_display', 
                'puede_vender_display', 'creado_en', 'actualizado_en'
            ),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ['cultivo', 'labor', 'campania', 'parcela']
    
    date_hierarchy = 'fecha_cosecha'
    
    list_per_page = 25
    
    actions = ['marcar_como_vendido', 'marcar_como_procesado', 'marcar_como_vencido']
    
    def cultivo_especie_display(self, obj):
        """Muestra la especie y variedad del cultivo"""
        if obj.cultivo.variedad:
            return f"{obj.cultivo.especie} - {obj.cultivo.variedad}"
        return obj.cultivo.especie
    cultivo_especie_display.short_description = 'Cultivo'
    
    def cantidad_display(self, obj):
        """Muestra la cantidad formateada"""
        return f"{obj.cantidad} {obj.unidad_medida}"
    cantidad_display.short_description = 'Cantidad'
    
    def estado_badge(self, obj):
        """Muestra el estado con colores"""
        colors = {
            'En Almacén': 'blue',
            'Vendido': 'green', 
            'Procesado': 'orange',
            'Vencido': 'red',
            'En revision': 'gray'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.estado
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def origen_display(self, obj):
        """Muestra el origen (campania o parcela)"""
        return obj.origen_display
    origen_display.short_description = 'Origen'
    
    def dias_en_almacen_display(self, obj):
        """Muestra días en almacén"""
        dias = obj.dias_en_almacen()
        if dias > 30:
            color = 'red'
        elif dias > 15:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} días</span>',
            color,
            dias
        )
    dias_en_almacen_display.short_description = 'Días en Almacén'
    
    def puede_vender_display(self, obj):
        """Indica si el producto puede ser vendido"""
        if obj.puede_vender():
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ SÍ</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ NO</span>'
        )
    puede_vender_display.short_description = 'Puede Vender'
    
    def marcar_como_vendido(self, request, queryset):
        """Acción para marcar productos como vendidos"""
        updated = queryset.update(estado='Vendido')
        self.message_user(
            request, 
            f'{updated} productos marcados como vendidos.'
        )
    marcar_como_vendido.short_description = "Marcar seleccionados como VENDIDO"
    
    def marcar_como_procesado(self, request, queryset):
        """Acción para marcar productos como procesados"""
        updated = queryset.update(estado='Procesado')
        self.message_user(
            request, 
            f'{updated} productos marcados como procesados.'
        )
    marcar_como_procesado.short_description = "Marcar seleccionados como PROCESADO"
    
    def marcar_como_vencido(self, request, queryset):
        """Acción para marcar productos como vencidos"""
        updated = queryset.update(estado='Vencido')
        self.message_user(
            request, 
            f'{updated} productos marcados como vencidos.'
        )
    marcar_como_vencido.short_description = "Marcar seleccionados como VENCIDO"
    
    def get_queryset(self, request):
        """Optimizar consultas relacionadas"""
        return super().get_queryset(request).select_related(
            'cultivo', 'labor', 'campania', 'parcela__socio__usuario'
        )

# =============================================================================
# IMPORTAR ADMINISTRACIÓN DE campaniaS (CU9 - SPRINT 2)
# =============================================================================
# Se importan las clases de administración de campanias desde admin_campaigns.py
# Esto mantiene el código organizado y modular
from .admin_campaigns import CampaignAdmin, CampaignPartnerAdmin, CampaignPlotAdmin

# Las clases ya están registradas con @admin.register en admin_campaigns.py
# No es necesario volver a registrarlas aquí

# =============================================================================
# ADMINISTRACIÓN DEL SISTEMA DE PAGOS (CU16)
# =============================================================================

class DetallePedidoInline(admin.TabularInline):
    """Inline para mostrar los detalles de un pedido"""
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('producto_cosechado', 'producto_nombre', 'cantidad', 'unidad_medida', 'precio_unitario', 'subtotal')
    raw_id_fields = ('producto_cosechado',)
    
    def subtotal(self, obj):
        if obj.id:
            return f"{obj.subtotal:.2f} Bs"
        return "0.00 Bs"
    subtotal.short_description = 'Subtotal'


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """
    CU16: Administración de pedidos en Django Admin
    Sistema de gestión de pedidos con integración de pagos
    """
    list_display = (
        'numero_pedido', 'socio_display', 'cliente_nombre', 
        'total_display', 'total_pagado_display', 'saldo_pendiente_display',
        'estado_badge', 'estado_pago_badge', 'fecha_pedido'
    )
    
    list_filter = (
        'estado', 'fecha_pedido', 'socio', 'creado_en'
    )
    
    search_fields = (
        'numero_pedido', 'cliente_nombre', 'cliente_email', 
        'cliente_telefono', 'socio__usuario__nombres', 'socio__usuario__apellidos'
    )
    
    readonly_fields = (
        'numero_pedido', 'creado_en', 'actualizado_en', 
        'total_display', 'total_pagado_display', 
        'saldo_pendiente_display', 'estado_pago_display'
    )
    
    inlines = [DetallePedidoInline]
    
    date_hierarchy = 'fecha_pedido'
    
    list_per_page = 25
    
    actions = ['marcar_como_confirmado', 'marcar_como_completado', 'marcar_como_cancelado']
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': (
                'numero_pedido', 'socio', 'fecha_pedido', 'estado'
            )
        }),
        ('Información del Cliente', {
            'fields': (
                'cliente_nombre', 'cliente_email', 'cliente_telefono', 'cliente_direccion'
            )
        }),
        ('Montos', {
            'fields': (
                'subtotal', 'descuento', 'impuestos', 'total',
                'total_display', 'total_pagado_display', 
                'saldo_pendiente_display', 'estado_pago_display'
            )
        }),
        ('Información Adicional', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def socio_display(self, obj):
        """Muestra información del socio"""
        if obj.socio:
            return format_html(
                '{}<br><small style="color: #666;">{}</small>',
                f"{obj.socio.usuario.nombres} {obj.socio.usuario.apellidos}",
                obj.socio.codigo_interno
            )
        return "—"
    socio_display.short_description = 'Socio'
    
    def total_display(self, obj):
        """Muestra el monto total formateado"""
        return f"{obj.total:.2f} Bs"
    total_display.short_description = 'Monto Total'
    
    def total_pagado_display(self, obj):
        """Muestra el total pagado formateado"""
        total = obj.total_pagado
        if total > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{:.2f} Bs</span>',
                total
            )
        return "0.00 Bs"
    total_pagado_display.short_description = 'Total Pagado'
    
    def saldo_pendiente_display(self, obj):
        """Muestra el saldo pendiente formateado"""
        saldo = obj.saldo_pendiente
        if saldo > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">{:.2f} Bs</span>',
                saldo
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">0.00 Bs</span>'
        )
    saldo_pendiente_display.short_description = 'Saldo Pendiente'
    
    def estado_badge(self, obj):
        """Muestra el estado del pedido con colores"""
        colors = {
            'PENDIENTE': 'gray',
            'CONFIRMADO': 'blue',
            'EN_PROCESO': 'orange',
            'COMPLETADO': 'green',
            'CANCELADO': 'red'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def estado_pago_badge(self, obj):
        """Muestra el estado del pago con colores"""
        estado = obj.estado_pago
        colors = {
            'PENDIENTE': 'red',
            'PARCIAL': 'orange',
            'PAGADO': 'green'
        }
        color = colors.get(estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            estado
        )
    estado_pago_badge.short_description = 'Estado Pago'
    
    def estado_pago_display(self, obj):
        """Muestra el estado del pago con detalles"""
        return obj.estado_pago
    estado_pago_display.short_description = 'Estado de Pago'
    
    def marcar_como_confirmado(self, request, queryset):
        """Acción para confirmar pedidos"""
        updated = queryset.filter(estado='PENDIENTE').update(estado='CONFIRMADO')
        self.message_user(
            request, 
            f'{updated} pedido(s) confirmado(s).'
        )
    marcar_como_confirmado.short_description = "Marcar como CONFIRMADO"
    
    def marcar_como_completado(self, request, queryset):
        """Acción para completar pedidos"""
        updated = queryset.filter(
            estado__in=['CONFIRMADO', 'EN_PROCESO']
        ).update(estado='COMPLETADO')
        self.message_user(
            request, 
            f'{updated} pedido(s) completado(s).'
        )
    marcar_como_completado.short_description = "Marcar como COMPLETADO"
    
    def marcar_como_cancelado(self, request, queryset):
        """Acción para cancelar pedidos"""
        updated = queryset.exclude(
            estado__in=['COMPLETADO', 'CANCELADO']
        ).update(estado='CANCELADO')
        self.message_user(
            request, 
            f'{updated} pedido(s) cancelado(s).'
        )
    marcar_como_cancelado.short_description = "Marcar como CANCELADO"
    
    def get_queryset(self, request):
        """Optimizar consultas relacionadas"""
        return super().get_queryset(request).select_related(
            'socio__usuario'
        ).prefetch_related('items__producto')


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    """
    CU16: Administración de detalles de pedidos
    """
    list_display = (
        'id', 'pedido_numero', 'producto_nombre', 'cantidad', 
        'unidad_medida', 'precio_unitario_display', 'subtotal_display'
    )
    
    list_filter = ('pedido__fecha_pedido', 'unidad_medida')
    
    search_fields = (
        'pedido__numero_pedido', 'producto_nombre', 
        'producto_cosechado__cultivo__especie'
    )
    
    readonly_fields = ('subtotal', 'creado_en')
    
    raw_id_fields = ('pedido', 'producto_cosechado')
    
    def pedido_numero(self, obj):
        """Muestra el número de pedido"""
        return obj.pedido.numero_pedido
    pedido_numero.short_description = 'Pedido'
    pedido_numero.admin_order_field = 'pedido__numero_pedido'
    
    def precio_unitario_display(self, obj):
        """Muestra el precio unitario formateado"""
        return f"{obj.precio_unitario:.2f} Bs"
    precio_unitario_display.short_description = 'Precio Unitario'
    
    def subtotal_display(self, obj):
        """Muestra el subtotal formateado"""
        return f"{obj.subtotal:.2f} Bs"
    subtotal_display.short_description = 'Subtotal'
    
    def get_queryset(self, request):
        """Optimizar consultas relacionadas"""
        return super().get_queryset(request).select_related(
            'pedido', 'producto_cosechado__cultivo'
        )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """
    CU16: Administración de pagos en Django Admin
    Sistema de gestión de pagos con integración Stripe
    """
    list_display = (
        'numero_recibo', 'pedido_numero', 'monto_display', 'metodo_pago_display',
        'estado_badge', 'fecha_pago', 'payment_intent_id_short'
    )
    
    list_filter = (
        'estado', 'metodo_pago', 'fecha_pago', 'creado_en'
    )
    
    search_fields = (
        'pedido__numero_pedido', 'numero_recibo', 'stripe_payment_intent_id', 
        'stripe_charge_id', 'stripe_customer_id', 'referencia_bancaria', 'banco'
    )
    
    readonly_fields = (
        'numero_recibo', 'creado_en', 'actualizado_en', 'stripe_payment_intent_id',
        'stripe_charge_id', 'stripe_customer_id', 'fecha_pago'
    )
    
    date_hierarchy = 'fecha_pago'
    
    list_per_page = 25
    
    actions = ['marcar_como_completado', 'marcar_como_cancelado']
    
    fieldsets = (
        ('Información del Pago', {
            'fields': (
                'numero_recibo', 'pedido', 'monto', 'metodo_pago', 'estado', 'fecha_pago'
            )
        }),
        ('Información Stripe', {
            'fields': (
                'stripe_payment_intent_id', 'stripe_charge_id', 
                'stripe_customer_id'
            ),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': (
                'referencia_bancaria', 'banco', 'comprobante_archivo', 'observaciones'
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ('pedido',)
    
    def pedido_numero(self, obj):
        """Muestra el número de pedido"""
        return obj.pedido.numero_pedido
    pedido_numero.short_description = 'Pedido'
    pedido_numero.admin_order_field = 'pedido__numero_pedido'
    
    def monto_display(self, obj):
        """Muestra el monto formateado"""
        return format_html(
            '<span style="font-weight: bold;">{:.2f} Bs</span>',
            obj.monto
        )
    monto_display.short_description = 'Monto'
    
    def metodo_pago_display(self, obj):
        """Muestra el método de pago con icono"""
        icons = {
            'EFECTIVO': '💵',
            'TRANSFERENCIA': '🏦',
            'STRIPE': '💳',
            'QR': '📱',
            'OTRO': '📋'
        }
        icon = icons.get(obj.metodo_pago, '❓')
        return f"{icon} {obj.get_metodo_pago_display()}"
    metodo_pago_display.short_description = 'Método de Pago'
    metodo_pago_display.admin_order_field = 'metodo_pago'
    
    def estado_badge(self, obj):
        """Muestra el estado del pago con colores"""
        colors = {
            'PENDIENTE': 'gray',
            'PROCESANDO': 'blue',
            'COMPLETADO': 'green',
            'FALLIDO': 'red',
            'REEMBOLSADO': 'orange',
            'CANCELADO': 'darkred'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'
    
    def payment_intent_id_short(self, obj):
        """Muestra una versión corta del payment intent ID"""
        if obj.stripe_payment_intent_id:
            return f"{obj.stripe_payment_intent_id[:20]}..."
        return "—"
    payment_intent_id_short.short_description = 'Payment Intent'
    
    def marcar_como_completado(self, request, queryset):
        """Acción para marcar pagos como completados"""
        # Solo pagos en efectivo o transferencia pueden ser completados manualmente
        updated = queryset.filter(
            metodo_pago__in=['EFECTIVO', 'TRANSFERENCIA', 'QR', 'OTRO'],
            estado='PENDIENTE'
        ).update(estado='COMPLETADO')
        self.message_user(
            request, 
            f'{updated} pago(s) marcado(s) como completado(s).'
        )
    marcar_como_completado.short_description = "Marcar como COMPLETADO (solo no-Stripe)"
    
    def marcar_como_cancelado(self, request, queryset):
        """Acción para cancelar pagos"""
        updated = queryset.filter(
            estado__in=['PENDIENTE', 'PROCESANDO']
        ).update(estado='CANCELADO')
        self.message_user(
            request, 
            f'{updated} pago(s) cancelado(s).'
        )
    marcar_como_cancelado.short_description = "Marcar como CANCELADO"
    
    def get_queryset(self, request):
        """Optimizar consultas relacionadas"""
        return super().get_queryset(request).select_related(
            'pedido__socio__usuario'
        )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    CU16: Administración de métodos de pago en Django Admin
    Versión corregida con los campos actualizados del modelo
    """
    list_display = (
        'id', 'nombre', 'tipo_badge', 'activo', 'orden', 
        'creado_por_display', 'creado_en_display'
    )
    
    list_filter = (
        'tipo', 'activo', 'creado_en'
    )
    
    search_fields = (
        'nombre', 'descripcion', 'creado_por__usuario', 
        'creado_por__nombres', 'creado_por__apellidos'
    )
    
    readonly_fields = (
        'creado_en', 'actualizado_en', 'creado_por_display', 
        'actualizado_por_display', 'puede_eliminarse_display'
    )
    
    list_editable = ('orden', 'activo')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'activo', 'orden')
        }),
        ('Descripción y Configuración', {
            'fields': ('descripcion', 'configuracion'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'creado_por', 'actualizado_por',  # ← CAMBIADO: usar campos reales, no métodos display
                'creado_en', 'actualizado_en', 'puede_eliminarse_display'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'activar_metodos',
        'desactivar_metodos', 
        'reordenar_secuencialmente',
        'exportar_metodos_csv',
        'crear_metodos_por_defecto'
    ]

    def tipo_badge(self, obj):
        """Muestra el tipo de método de pago con ícono y color"""
        tipos_iconos = {
            'EFECTIVO': '💰',
            'TRANSFERENCIA': '🏦', 
            'TARJETA_CREDITO': '💳',
            'TARJETA_DEBITO': '💳',
            'CHEQUE': '📄',
            'DIGITAL': '📱',
            'OTRO': '🔧'
        }
        
        tipos_colores = {
            'EFECTIVO': 'green',
            'TRANSFERENCIA': 'blue',
            'TARJETA_CREDITO': 'purple',
            'TARJETA_DEBITO': 'orange',
            'CHEQUE': 'brown',
            'DIGITAL': 'teal',
            'OTRO': 'gray'
        }
        
        icono = tipos_iconos.get(obj.tipo, '❓')
        color = tipos_colores.get(obj.tipo, 'black')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icono,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    tipo_badge.admin_order_field = 'tipo'

    def creado_en_display(self, obj):
        """Formatea la fecha de creación para mejor visualización"""
        if obj.creado_en:
            return obj.creado_en.strftime('%Y-%m-%d %H:%M')
        return "-"
    creado_en_display.short_description = 'Creado'
    creado_en_display.admin_order_field = 'creado_en'

    def creado_por_display(self, obj):
        """Muestra información del creador"""
        if obj.creado_por:
            return format_html(
                '{}<br><small style="color: #666;">{}</small>',
                obj.creado_por.get_full_name() or obj.creado_por.usuario,
                obj.creado_en.strftime('%Y-%m-%d %H:%M') if obj.creado_en else ''
            )
        return "—"
    creado_por_display.short_description = 'Creado Por'

    def actualizado_por_display(self, obj):
        """Muestra información del último actualizador"""
        if obj.actualizado_por:
            return format_html(
                '{}<br><small style="color: #666;">{}</small>',
                obj.actualizado_por.get_full_name() or obj.actualizado_por.usuario,
                obj.actualizado_en.strftime('%Y-%m-%d %H:%M') if obj.actualizado_en else ''
            )
        return "—"
    actualizado_por_display.short_description = 'Actualizado Por'

    def puede_eliminarse_display(self, obj):
        """Indica si el método puede ser eliminado"""
        if obj.puede_eliminarse:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ SÍ</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">❌ NO (tiene pagos asociados)</span>'
        )
    puede_eliminarse_display.short_description = '¿Puede Eliminarse?'

    def activar_metodos(self, request, queryset):
        """Acción para activar métodos de pago seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(
            request, 
            f'{updated} método(s) de pago activado(s).'
        )
    activar_metodos.short_description = "🔓 Activar métodos seleccionados"

    def desactivar_metodos(self, request, queryset):
        """Acción para desactivar métodos de pago seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(
            request, 
            f'{updated} método(s) de pago desactivado(s).'
        )
    desactivar_metodos.short_description = "🔒 Desactivar métodos seleccionados"

    def reordenar_secuencialmente(self, request, queryset):
        """Acción para reordenar métodos de pago secuencialmente"""
        metodos = queryset.order_by('orden', 'nombre')
        for index, metodo in enumerate(metodos, start=1):
            metodo.orden = index
            metodo.save(update_fields=['orden'])
        
        self.message_user(
            request, 
            f'{metodos.count()} método(s) de pago reordenado(s) secuencialmente.'
        )
    reordenar_secuencialmente.short_description = "🔄 Reordenar secuencialmente"

    def exportar_metodos_csv(self, request, queryset):
        """Exportar métodos de pago seleccionados a CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="metodos_pago_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nombre', 'Tipo', 'Activo', 'Orden', 'Descripción',
            'Creado Por', 'Fecha Creación', 'Actualizado Por', 'Fecha Actualización'
        ])

        for metodo in queryset:
            writer.writerow([
                metodo.id,
                metodo.nombre,
                metodo.get_tipo_display(),
                'Sí' if metodo.activo else 'No',
                metodo.orden,
                metodo.descripcion or '',
                metodo.creado_por.get_full_name() if metodo.creado_por else '',
                metodo.creado_en.strftime('%Y-%m-%d %H:%M') if metodo.creado_en else '',
                metodo.actualizado_por.get_full_name() if metodo.actualizado_por else '',
                metodo.actualizado_en.strftime('%Y-%m-%d %H:%M') if metodo.actualizado_en else ''
            ])

        self.message_user(request, f'Exportados {queryset.count()} métodos de pago a CSV.')
        return response
    exportar_metodos_csv.short_description = "📄 Exportar a CSV"

    def crear_metodos_por_defecto(self, request, queryset):
        """Acción para crear métodos de pago por defecto"""
        from django.core.management import call_command
        try:
            call_command('seed_payment_methods')
            self.message_user(request, '✅ Métodos de pago por defecto creados exitosamente.')
        except Exception as e:
            self.message_user(request, f'❌ Error al crear métodos por defecto: {str(e)}', level='ERROR')
    crear_metodos_por_defecto.short_description = "🌱 Crear métodos por defecto"

    def get_queryset(self, request):
        """Optimizar consultas relacionadas"""
        return super().get_queryset(request).select_related(
            'creado_por', 'actualizado_por'
        ).order_by('orden', 'nombre')

    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el usuario actual al crear/actualizar"""
        if not change:
            # Es un nuevo registro
            obj.creado_por = request.user
        else:
            # Es una actualización
            obj.actualizado_por = request.user
        
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Campos de solo lectura - versión simplificada"""
        if obj and not obj.puede_eliminarse:
            # Si no se puede eliminar, mostrar advertencia pero no hacer todos los campos readonly
            return list(self.readonly_fields) + ['puede_eliminarse_display']
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar solo si puede_eliminarse es True"""
        if obj and not obj.puede_eliminarse:
            return False
        return super().has_delete_permission(request, obj)