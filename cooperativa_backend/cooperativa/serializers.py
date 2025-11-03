from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator
from .models import (
    Rol, Usuario, UsuarioRol, Comunidad, Socio,
    Parcela, Cultivo, BitacoraAuditoria,
    CicloCultivo, Cosecha, Tratamiento, AnalisisSuelo, TransferenciaParcela,
    Semilla, Pesticida, Fertilizante,
    Campaign, CampaignPartner, CampaignPlot, Labor, ProductoCosechado,
    Pedido, DetallePedido, Pago,
    PrecioTemporada, PedidoInsumo, DetallePedidoInsumo, PagoInsumo
)


class RolSerializer(serializers.ModelSerializer):
    permisos_legibles = serializers.SerializerMethodField()
    usuarios_count = serializers.SerializerMethodField()

    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'descripcion', 'permisos', 'permisos_legibles',
            'es_sistema', 'creado_en', 'actualizado_en', 'usuarios_count'
        ]
        read_only_fields = ['es_sistema'] if not hasattr(serializers, 'context') else []

    def get_permisos_legibles(self, obj):
        """Retorna los permisos en formato legible"""
        return obj.obtener_permisos_completos()

    def get_usuarios_count(self, obj):
        """Retorna el número de usuarios con este rol"""
        return UsuarioRol.objects.filter(rol=obj).count()

    def validate_permisos(self, value):
        """Validar estructura de permisos"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Los permisos deben ser un objeto JSON válido')

        # Validar que todos los módulos requeridos estén presentes
        modulos_requeridos = [
            'usuarios', 'socios', 'parcelas', 'cultivos',
            'ciclos_cultivo', 'cosechas', 'tratamientos',
            'analisis_suelo', 'transferencias', 'reportes',
            'auditoria', 'configuracion'
        ]

        for modulo in modulos_requeridos:
            if modulo not in value:
                value[modulo] = {
                    'ver': False,
                    'crear': False,
                    'editar': False,
                    'eliminar': False,
                    'aprobar': False
                }

        return value

    def validate(self, data):
        """Validaciones adicionales"""
        nombre = data.get('nombre')
        instance = self.instance

        # Validar nombre único
        if nombre and Rol.objects.filter(nombre__iexact=nombre).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({'nombre': 'Ya existe un rol con este nombre'})

        # Validar que no se pueda modificar roles del sistema
        if instance and instance.es_sistema:
            # Solo permitir modificar descripción y permisos para roles del sistema
            campos_modificables = {'descripcion', 'permisos'}
            campos_en_data = set(data.keys())
            campos_invalidos = campos_en_data - campos_modificables
            if campos_invalidos:
                raise serializers.ValidationError({
                    field: f'No se puede modificar el campo {field} de un rol del sistema'
                    for field in campos_invalidos
                })

        return data


class UsuarioSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    edad = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario', 'estado', 'intentos_fallidos', 'ultimo_intento',
            'fecha_bloqueo', 'creado_en', 'actualizado_en', 'roles',
            'nombre_completo', 'edad'
        ]
        extra_kwargs = {
            'contrasena_hash': {'write_only': True},
            'token_actual': {'write_only': True},
        }

    def get_roles(self, obj):
        roles = UsuarioRol.objects.filter(usuario=obj).select_related('rol')
        return [usuario_rol.rol.nombre for usuario_rol in roles]

    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"

    def get_edad(self, obj):
        # Calcular edad si hay fecha de nacimiento en socio relacionado
        try:
            socio = Socio.objects.get(usuario=obj)
            if socio.fecha_nacimiento:
                from datetime import date
                today = date.today()
                age = today.year - socio.fecha_nacimiento.year - (
                    (today.month, today.day) < (socio.fecha_nacimiento.month, socio.fecha_nacimiento.day)
                )
                return age
        except Socio.DoesNotExist:
            pass
        return None

    def validate_ci_nit(self, value):
        """T021, T027: Validación de CI/NIT único"""
        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = getattr(self.parent.instance.usuario, 'id', None) if hasattr(self.parent.instance, 'usuario') else None

        queryset = Usuario.objects.filter(ci_nit=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un usuario con este CI/NIT')
        return value

    def validate_email(self, value):
        """T021: Validación de email único"""
        if not value:
            return value

        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = getattr(self.parent.instance.usuario, 'id', None) if hasattr(self.parent.instance, 'usuario') else None

        queryset = Usuario.objects.filter(email__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un usuario con este email')
        return value

    def validate_usuario(self, value):
        """T021: Validación de usuario único"""
        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = getattr(self.parent.instance.usuario, 'id', None) if hasattr(self.parent.instance, 'usuario') else None

        queryset = Usuario.objects.filter(usuario__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un usuario con este nombre de usuario')
        return value


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario', 'password', 'confirm_password', 'roles'
        ]

    def validate(self, data):
        """T021: Validaciones generales del formulario"""
        # Validar contraseñas coincidan
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Las contraseñas no coinciden'})

        # Validar fortaleza de contraseña
        password = data.get('password', '')
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({'password': 'La contraseña debe contener al menos un número'})
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError({'password': 'La contraseña debe contener al menos una mayúscula'})

        return data

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', [])
        validated_data.pop('confirm_password')  # Remover campo de confirmación
        password = validated_data.pop('password')

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        # Assign roles
        for rol_nombre in roles_data:
            try:
                rol = Rol.objects.get(nombre=rol_nombre)
                UsuarioRol.objects.create(usuario=user, rol=rol)
            except Rol.DoesNotExist:
                pass  # Skip invalid roles

        return user


class UsuarioRolSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = UsuarioRol
        fields = ['id', 'usuario', 'rol', 'usuario_nombre', 'rol_nombre', 'creado_en']


class ComunidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunidad
        fields = '__all__'

    def validate_nombre(self, value):
        """T021: Validación de nombre único"""
        if Comunidad.objects.filter(nombre__iexact=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('Ya existe una comunidad con este nombre')
        return value


class SocioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    comunidad = ComunidadSerializer(read_only=True)
    edad = serializers.SerializerMethodField()

    class Meta:
        model = Socio
        fields = [
            'id', 'usuario', 'codigo_interno',
            'fecha_nacimiento', 'sexo', 'direccion', 'comunidad',
            'estado', 'creado_en', 'edad'
        ]

    def get_edad(self, obj):
        """Calcular edad del socio"""
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            age = today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
            return age
        return None

    def validate_codigo_interno(self, value):
        """T027: Validación de código interno único"""
        if not value:
            return value

        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = self.parent.instance.id if self.parent.instance else None

        queryset = Socio.objects.filter(codigo_interno__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un socio con este código interno')
        return value

    def validate_usuario(self, value):
        """T027: Validación de usuario único para socio"""
        if Socio.objects.filter(usuario=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('Este usuario ya está asociado a otro socio')
        return value


class SocioCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para creación de socios con usuario incluido"""
    # Campos del usuario
    ci_nit = serializers.CharField(max_length=20, write_only=True)
    nombres = serializers.CharField(max_length=100, write_only=True)
    apellidos = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    telefono = serializers.CharField(max_length=20, required=False, write_only=True)
    usuario_username = serializers.CharField(max_length=50, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Socio
        fields = [
            'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario_username', 'password', 'codigo_interno',
            'fecha_nacimiento', 'sexo', 'direccion', 'comunidad'
        ]

    def validate_ci_nit(self, value):
        """T027: Validación de CI/NIT único"""
        from .models import validate_ci_nit
        validate_ci_nit(value)
        if Usuario.objects.filter(ci_nit=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este CI/NIT')
        return value

    def validate_usuario_username(self, value):
        """T021: Validación de usuario único"""
        if Usuario.objects.filter(usuario__iexact=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este nombre de usuario')
        return value

    def create(self, validated_data):
        # Extraer datos del usuario
        user_data = {
            'ci_nit': validated_data.pop('ci_nit'),
            'nombres': validated_data.pop('nombres'),
            'apellidos': validated_data.pop('apellidos'),
            'email': validated_data.pop('email', None),
            'usuario': validated_data.pop('usuario_username'),
            'password': validated_data.pop('password'),
        }

        # Extraer teléfono por separado
        telefono = validated_data.pop('telefono', None)

        # Crear usuario
        user = Usuario.objects.create_user(**user_data)

        # Asignar teléfono si fue proporcionado
        if telefono:
            user.telefono = telefono
            user.save()

        # Crear socio
        socio = Socio.objects.create(usuario=user, **validated_data)

        return socio


class SocioCreateSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para creación de socios (solo campos del socio, sin usuario)"""
    class Meta:
        model = Socio
        fields = [
            'codigo_interno', 'fecha_nacimiento', 'sexo',
            'direccion', 'comunidad', 'estado'
        ]

    def validate_codigo_interno(self, value):
        """T027: Validación de código interno único"""
        if not value:
            return value

        if Socio.objects.filter(codigo_interno__iexact=value).exists():
            raise serializers.ValidationError('Ya existe un socio con este código interno')
        return value


class SocioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualización de socios"""
    class Meta:
        model = Socio
        fields = [
            'codigo_interno', 'fecha_nacimiento', 'sexo',
            'direccion', 'comunidad', 'estado'
        ]

    def validate_codigo_interno(self, value):
        """T027: Validación de código interno único"""
        if not value:
            return value

        queryset = Socio.objects.filter(codigo_interno__iexact=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un socio con este código interno')
        return value


class ParcelaSerializer(serializers.ModelSerializer):
    socio_nombre = serializers.CharField(source='socio.usuario.get_full_name', read_only=True)
    # Campos adicionales para compatibilidad con frontend
    superficie = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True,
        required=False,
        validators=[MinValueValidator(0.01, message='La superficie debe ser mayor a 0')]
    )
    coordenadas = serializers.CharField(write_only=True, required=False)
    descripcion = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Parcela
        fields = [
            'id', 'socio', 'socio_nombre', 'nombre', 'superficie_hectareas',
            'tipo_suelo', 'ubicacion', 'latitud', 'longitud', 'estado', 'creado_en',
            # Campos adicionales para compatibilidad
            'superficie', 'coordenadas', 'descripcion'
        ]
        extra_kwargs = {
            'superficie_hectareas': {'required': False},
            'latitud': {'required': False},
            'longitud': {'required': False},
        }

    def validate_superficie(self, value):
        """T021: Validación de superficie"""
        if value <= 0:
            raise serializers.ValidationError('La superficie debe ser mayor a 0')
        if value > 10000:
            raise serializers.ValidationError('La superficie no puede exceder 10,000 hectáreas')
        return value

    def validate_coordenadas(self, value):
        """Validar formato de coordenadas"""
        if not value:
            return value

        try:
            # Esperar formato "latitud, longitud"
            parts = value.split(',')
            if len(parts) != 2:
                raise serializers.ValidationError('Formato de coordenadas inválido. Use: latitud,longitud')

            lat = float(parts[0].strip())
            lng = float(parts[1].strip())

            if lat < -90 or lat > 90:
                raise serializers.ValidationError('Latitud debe estar entre -90 y 90 grados')
            if lng < -180 or lng > 180:
                raise serializers.ValidationError('Longitud debe estar entre -180 y 180 grados')

            return value
        except (ValueError, IndexError):
            raise serializers.ValidationError('Formato de coordenadas inválido. Use números decimales separados por coma')

    def to_internal_value(self, data):
        """Convertir campos del frontend a campos del modelo"""
        # Convertir 'superficie' a 'superficie_hectareas'
        if 'superficie' in data and data['superficie'] is not None:
            data = data.copy()
            data['superficie_hectareas'] = data.pop('superficie')

        # Convertir 'coordenadas' a 'latitud' y 'longitud'
        if 'coordenadas' in data and data['coordenadas']:
            try:
                parts = data['coordenadas'].split(',')
                if len(parts) == 2:
                    data = data.copy()
                    data['latitud'] = float(parts[0].strip())
                    data['longitud'] = float(parts[1].strip())
            except (ValueError, AttributeError):
                pass

        # Convertir 'descripcion' a parte de 'ubicacion' o 'nombre'
        if 'descripcion' in data and data['descripcion']:
            if not data.get('ubicacion'):
                data = data.copy()
                data['ubicacion'] = data['descripcion']
            elif not data.get('nombre'):
                data = data.copy()
                data['nombre'] = data['descripcion'][:100]  # Limitar longitud

        # Convertir 'socio_id' a 'socio' si es necesario
        if 'socio_id' in data and data['socio_id']:
            try:
                from .models import Socio
                socio = Socio.objects.get(id=data['socio_id'])
                data = data.copy()
                data['socio'] = socio.id
                data.pop('socio_id')
            except (Socio.DoesNotExist, ValueError):
                pass

        # Remover campos que no existen en el modelo
        campos_invalidos = ['fecha_registro']
        for campo in campos_invalidos:
            if campo in data:
                data = data.copy()
                data.pop(campo)

        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Convertir campos del modelo a formato del frontend"""
        data = super().to_representation(instance)

        # Agregar campo 'superficie' para compatibilidad
        if instance.superficie_hectareas:
            data['superficie'] = instance.superficie_hectareas

        # Agregar campo 'coordenadas' para compatibilidad
        if instance.latitud and instance.longitud:
            data['coordenadas'] = f"{instance.latitud}, {instance.longitud}"

        # Agregar campo 'descripcion' para compatibilidad
        data['descripcion'] = instance.ubicacion or instance.nombre or ''

        return data

    def validate(self, data):
        """T021: Validaciones de coordenadas"""
        latitud = data.get('latitud')
        longitud = data.get('longitud')

        if (latitud and not longitud) or (longitud and not latitud):
            raise serializers.ValidationError('Si se proporciona una coordenada, ambas latitud y longitud son requeridas')

        if latitud and (latitud < -90 or latitud > 90):
            raise serializers.ValidationError('Latitud debe estar entre -90 y 90 grados')

        if longitud and (longitud < -180 or longitud > 180):
            raise serializers.ValidationError('Longitud debe estar entre -180 y 180 grados')

        return data


class CultivoSerializer(serializers.ModelSerializer):
    parcela_nombre = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = Cultivo
        fields = [
            'id', 'parcela', 'parcela_nombre', 'socio_nombre', 'especie',
            'variedad', 'tipo_semilla', 'fecha_estimada_siembra',
            'hectareas_sembradas', 'estado', 'creado_en'
        ]

    def validate_hectareas_sembradas(self, value):
        """T021: Validación de hectáreas sembradas"""
        if value and value <= 0:
            raise serializers.ValidationError('Las hectáreas sembradas deben ser mayor a 0')
        return value

    def validate_fecha_estimada_siembra(self, value):
        """T021: Validación de fecha de siembra"""
        if value:
            from datetime import date
            if value < date.today():
                raise serializers.ValidationError('La fecha estimada de siembra no puede ser en el pasado')
        return value

    def validate(self, data):
        """T021: Validaciones entre campos"""
        hectareas_sembradas = data.get('hectareas_sembradas')
        parcela = data.get('parcela') or (self.instance.parcela if self.instance else None)

        if hectareas_sembradas and parcela:
            if hectareas_sembradas > parcela.superficie_hectareas:
                raise serializers.ValidationError({
                    'hectareas_sembradas': 'Las hectáreas sembradas no pueden exceder la superficie de la parcela'
                })

        return data


class BitacoraAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)

    class Meta:
        model = BitacoraAuditoria
        fields = [
            'id', 'usuario', 'usuario_nombre', 'accion', 'tabla_afectada',
            'registro_id', 'detalles', 'fecha', 'ip_address', 'user_agent'
        ]


class SemillaSerializer(serializers.ModelSerializer):
    """CU7: Serializer para gestión de semillas"""
    valor_total = serializers.SerializerMethodField()
    dias_para_vencer = serializers.SerializerMethodField()
    esta_proxima_vencer = serializers.SerializerMethodField()
    esta_vencida = serializers.SerializerMethodField()

    class Meta:
        model = Semilla
        fields = [
            'id', 'especie', 'variedad', 'cantidad', 'unidad_medida',
            'fecha_vencimiento', 'porcentaje_germinacion', 'lote',
            'proveedor', 'precio_unitario', 'ubicacion_almacen',
            'estado', 'observaciones', 'creado_en', 'actualizado_en',
            # Campos calculados
            'valor_total', 'dias_para_vencer', 'esta_proxima_vencer', 'esta_vencida'
        ]
        read_only_fields = ['valor_total', 'dias_para_vencer', 'esta_proxima_vencer', 'esta_vencida']

    def get_valor_total(self, obj):
        return obj.valor_total()

    def get_dias_para_vencer(self, obj):
        return obj.dias_para_vencer()

    def get_esta_proxima_vencer(self, obj):
        return obj.esta_proxima_vencer()

    def get_esta_vencida(self, obj):
        return obj.esta_vencida()

    def validate_porcentaje_germinacion(self, value):
        """Validación específica del porcentaje de germinación"""
        if value < 0 or value > 100:
            raise serializers.ValidationError('El porcentaje de germinación debe estar entre 0 y 100')
        return value

    def validate_fecha_vencimiento(self, value):
        """Validación de fecha de vencimiento"""
        from datetime import date
        if value and value < date.today():
            # Solo validar si no está ya vencida (para evitar problemas al editar registros existentes)
            estado = self.initial_data.get('estado') if hasattr(self, 'initial_data') else getattr(self.instance, 'estado', None) if self.instance else None
            if estado != 'VENCIDA':
                raise serializers.ValidationError('La fecha de vencimiento no puede ser en el pasado')
        return value

    def validate_cantidad(self, value):
        """Validación de cantidad"""
        if value < 0:
            raise serializers.ValidationError('La cantidad no puede ser negativa')
        return value

    def validate_precio_unitario(self, value):
        """Validación de precio unitario"""
        if value is not None and value < 0:
            raise serializers.ValidationError('El precio unitario no puede ser negativo')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        # Validar que si está agotada, cantidad debe ser 0
        estado = data.get('estado')
        cantidad = data.get('cantidad')

        if estado == 'AGOTADA' and cantidad != 0:
            raise serializers.ValidationError({
                'cantidad': 'Una semilla agotada debe tener cantidad 0'
            })

        return data


class CicloCultivoSerializer(serializers.ModelSerializer):
    """CU4: Serializer para ciclos de cultivo"""
    cultivo_especie = serializers.CharField(source='cultivo.especie', read_only=True)
    parcela_nombre = serializers.CharField(source='cultivo.parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='cultivo.parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = CicloCultivo
        fields = [
            'id', 'cultivo', 'cultivo_especie', 'parcela_nombre', 'socio_nombre',
            'fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real',
            'estado', 'observaciones', 'creado_en'
        ]

    def validate_fecha_inicio(self, value):
        """Validación de fecha de inicio"""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError('La fecha de inicio no puede ser en el pasado')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin_estimada = data.get('fecha_fin_estimada')

        if fecha_inicio and fecha_fin_estimada and fecha_fin_estimada <= fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin_estimada': 'La fecha de fin estimada debe ser posterior a la fecha de inicio'
            })

        return data


class CosechaSerializer(serializers.ModelSerializer):
    """CU4: Serializer para cosechas"""
    ciclo_cultivo_especie = serializers.CharField(source='ciclo_cultivo.cultivo.especie', read_only=True)
    parcela_nombre = serializers.CharField(source='ciclo_cultivo.cultivo.parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='ciclo_cultivo.cultivo.parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = Cosecha
        fields = [
            'id', 'ciclo_cultivo', 'ciclo_cultivo_especie', 'parcela_nombre', 'socio_nombre',
            'fecha_cosecha', 'cantidad_cosechada', 'unidad_medida',
            'calidad', 'estado', 'observaciones', 'creado_en'
        ]

    def validate_cantidad_cosechada(self, value):
        """Validación de cantidad cosechada"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad cosechada debe ser mayor a 0')
        return value

    def validate_fecha_cosecha(self, value):
        """Validación de fecha de cosecha"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError('La fecha de cosecha no puede ser en el futuro')
        return value


class TratamientoSerializer(serializers.ModelSerializer):
    """CU4: Serializer para tratamientos"""
    ciclo_cultivo_especie = serializers.CharField(source='ciclo_cultivo.cultivo.especie', read_only=True)
    parcela_nombre = serializers.CharField(source='ciclo_cultivo.cultivo.parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='ciclo_cultivo.cultivo.parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = Tratamiento
        fields = [
            'id', 'ciclo_cultivo', 'ciclo_cultivo_especie', 'parcela_nombre', 'socio_nombre',
            'tipo_tratamiento', 'producto_utilizado', 'cantidad_aplicada',
            'unidad_medida', 'fecha_aplicacion', 'responsable_aplicacion',
            'observaciones', 'creado_en'
        ]

    def validate_cantidad_aplicada(self, value):
        """Validación de cantidad aplicada"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad aplicada debe ser mayor a 0')
        return value

    def validate_fecha_aplicacion(self, value):
        """Validación de fecha de aplicación"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError('La fecha de aplicación no puede ser en el futuro')
        return value


class AnalisisSueloSerializer(serializers.ModelSerializer):
    """CU4: Serializer para análisis de suelo"""
    parcela_nombre = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = AnalisisSuelo
        fields = [
            'id', 'parcela', 'parcela_nombre', 'socio_nombre',
            'fecha_analisis', 'tipo_analisis', 'ph', 'materia_organica',
            'nitrogeno', 'fosforo', 'potasio', 'laboratorio',
            'responsable_analisis', 'observaciones', 'creado_en'
        ]

    def validate_ph(self, value):
        """Validación de pH"""
        if value < 0 or value > 14:
            raise serializers.ValidationError('El pH debe estar entre 0 y 14')
        return value

    def validate_fecha_analisis(self, value):
        """Validación de fecha de análisis"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError('La fecha de análisis no puede ser en el futuro')
        return value


class TransferenciaParcelaSerializer(serializers.ModelSerializer):
    """CU4: Serializer para transferencias de parcelas"""
    parcela_nombre = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_anterior_nombre = serializers.CharField(source='socio_anterior.usuario.get_full_name', read_only=True)
    socio_nuevo_nombre = serializers.CharField(source='socio_nuevo.usuario.get_full_name', read_only=True)
    autorizado_por_nombre = serializers.CharField(source='autorizado_por.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = TransferenciaParcela
        fields = [
            'id', 'parcela', 'parcela_nombre', 'socio_anterior', 'socio_anterior_nombre',
            'socio_nuevo', 'socio_nuevo_nombre', 'fecha_transferencia',
            'motivo_transferencia', 'documentacion_adjunta', 'estado',
            'autorizado_por', 'autorizado_por_nombre', 'fecha_aprobacion',
            'observaciones', 'creado_en'
        ]
        read_only_fields = ['autorizado_por', 'fecha_aprobacion']

    def validate_fecha_transferencia(self, value):
        """Validación de fecha de transferencia"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError('La fecha de transferencia no puede ser en el futuro')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        socio_anterior = data.get('socio_anterior')
        socio_nuevo = data.get('socio_nuevo')

        if socio_anterior and socio_nuevo and socio_anterior == socio_nuevo:
            raise serializers.ValidationError({
                'socio_nuevo': 'El socio nuevo debe ser diferente al socio anterior'
            })

        return data


class PesticidaSerializer(serializers.ModelSerializer):
    """CU8: Serializer para gestión de pesticidas"""
    valor_total = serializers.SerializerMethodField()
    dias_para_vencer = serializers.SerializerMethodField()
    esta_proximo_vencer = serializers.SerializerMethodField()
    esta_vencido = serializers.SerializerMethodField()

    class Meta:
        model = Pesticida
        fields = [
            'id', 'nombre_comercial', 'ingrediente_activo', 'tipo_pesticida',
            'concentracion', 'cantidad', 'unidad_medida', 'fecha_vencimiento',
            'lote', 'proveedor', 'precio_unitario', 'ubicacion_almacen',
            'estado', 'registro_sanitario', 'dosis_recomendada', 'observaciones',
            'creado_en', 'actualizado_en',
            # Campos calculados
            'valor_total', 'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido'
        ]
        read_only_fields = ['valor_total', 'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido']

    def get_valor_total(self, obj):
        return obj.valor_total()

    def get_dias_para_vencer(self, obj):
        return obj.dias_para_vencer()

    def get_esta_proximo_vencer(self, obj):
        return obj.esta_proximo_vencer()

    def get_esta_vencido(self, obj):
        return obj.esta_vencido()

    def validate_fecha_vencimiento(self, value):
        """Validación de fecha de vencimiento"""
        from datetime import date
        if value and value < date.today():
            raise serializers.ValidationError('La fecha de vencimiento no puede ser en el pasado')
        return value

    def validate_cantidad(self, value):
        """Validación de cantidad"""
        if value < 0:
            raise serializers.ValidationError('La cantidad no puede ser negativa')
        return value

    def validate_precio_unitario(self, value):
        """Validación de precio unitario"""
        if value <= 0:
            raise serializers.ValidationError('El precio unitario debe ser mayor a 0')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        estado = data.get('estado')
        cantidad = data.get('cantidad')

        if estado == 'AGOTADO' and cantidad != 0:
            raise serializers.ValidationError({
                'cantidad': 'Un pesticida agotado debe tener cantidad 0'
            })

        return data


class FertilizanteSerializer(serializers.ModelSerializer):
    """CU8: Serializer para gestión de fertilizantes"""
    valor_total = serializers.SerializerMethodField()
    dias_para_vencer = serializers.SerializerMethodField()
    esta_proximo_vencer = serializers.SerializerMethodField()
    esta_vencido = serializers.SerializerMethodField()
    npk_values = serializers.SerializerMethodField()

    class Meta:
        model = Fertilizante
        fields = [
            'id', 'nombre_comercial', 'tipo_fertilizante', 'composicion_npk',
            'cantidad', 'unidad_medida', 'fecha_vencimiento', 'lote',
            'proveedor', 'precio_unitario', 'ubicacion_almacen', 'estado',
            'dosis_recomendada', 'materia_orgánica', 'observaciones',
            'creado_en', 'actualizado_en',
            # Campos calculados
            'valor_total', 'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido', 'npk_values'
        ]
        read_only_fields = ['valor_total', 'dias_para_vencer', 'esta_proximo_vencer', 'esta_vencido', 'npk_values']

    def get_valor_total(self, obj):
        return obj.valor_total()

    def get_dias_para_vencer(self, obj):
        return obj.dias_para_vencer()

    def get_esta_proximo_vencer(self, obj):
        return obj.esta_proximo_vencer()

    def get_esta_vencido(self, obj):
        return obj.esta_vencido()

    def get_npk_values(self, obj):
        return obj.get_npk_values()

    def validate_fecha_vencimiento(self, value):
        """Validación de fecha de vencimiento"""
        from datetime import date
        tipo_fertilizante = self.initial_data.get('tipo_fertilizante') if hasattr(self, 'initial_data') else getattr(self.instance, 'tipo_fertilizante', None) if self.instance else None

        if tipo_fertilizante == 'QUIMICO' and not value:
            raise serializers.ValidationError('Los fertilizantes químicos requieren fecha de vencimiento')

        if value and value < date.today():
            raise serializers.ValidationError('La fecha de vencimiento no puede ser en el pasado')
        return value

    def validate_cantidad(self, value):
        """Validación de cantidad"""
        if value < 0:
            raise serializers.ValidationError('La cantidad no puede ser negativa')
        return value

    def validate_precio_unitario(self, value):
        """Validación de precio unitario"""
        if value <= 0:
            raise serializers.ValidationError('El precio unitario debe ser mayor a 0')
        return value

    def validate_materia_orgánica(self, value):
        """Validación de materia orgánica"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError('La materia orgánica debe estar entre 0 y 100%')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        estado = data.get('estado')
        cantidad = data.get('cantidad')
        tipo_fertilizante = data.get('tipo_fertilizante')
        materia_orgánica = data.get('materia_orgánica')

        if estado == 'AGOTADO' and cantidad != 0:
            raise serializers.ValidationError({
                'cantidad': 'Un fertilizante agotado debe tener cantidad 0'
            })

        if tipo_fertilizante == 'ORGANICO' and materia_orgánica is None:
            raise serializers.ValidationError({
                'materia_orgánica': 'Los fertilizantes orgánicos requieren especificar materia orgánica'
            })

        return data


        # ============================================================================
# CU9: SERIALIZERS PARA GESTIÓN DE campaniaS AGRÍCOLAS
# T036: Gestión de campanias (crear, editar, eliminar)
# T037: Relación entre campania y socios/parcelas
# ============================================================================

class CampaignPartnerSerializer(serializers.ModelSerializer):
    """
    CU9: Serializer para relación Campaign-Socio
    T037: Relación entre campania y socios
    """
    socio_nombre = serializers.CharField(source='socio.usuario.get_full_name', read_only=True)
    socio_ci_nit = serializers.CharField(source='socio.usuario.ci_nit', read_only=True)
    socio_codigo = serializers.CharField(source='socio.codigo_interno', read_only=True)

    class Meta:
        model = CampaignPartner
        fields = [
            'id', 'campaign', 'socio', 'socio_nombre', 'socio_ci_nit', 'socio_codigo',
            'rol', 'fecha_asignacion', 'observaciones', 'creado_en'
        ]
        read_only_fields = ['creado_en']

    def validate_socio(self, value):
        """Validar que el socio esté activo"""
        if value.estado != 'ACTIVO':
            raise serializers.ValidationError('Solo se pueden asignar socios con estado ACTIVO')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        campaign = data.get('campaign') or (self.instance.campaign if self.instance else None)
        fecha_asignacion = data.get('fecha_asignacion')

        if campaign and fecha_asignacion and fecha_asignacion < campaign.fecha_inicio:
            raise serializers.ValidationError({
                'fecha_asignacion': 'La fecha de asignación no puede ser anterior al inicio de la campania'
            })

        return data


class CampaignPlotSerializer(serializers.ModelSerializer):
    """
    CU9: Serializer para relación Campaign-Parcela
    T037: Relación entre campania y parcelas
    """
    parcela_nombre = serializers.CharField(source='parcela.nombre', read_only=True)
    parcela_superficie = serializers.DecimalField(
        source='parcela.superficie_hectareas',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    socio_nombre = serializers.CharField(source='parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = CampaignPlot
        fields = [
            'id', 'campaign', 'parcela', 'parcela_nombre', 'parcela_superficie',
            'socio_nombre', 'fecha_asignacion', 'superficie_comprometida',
            'cultivo_planificado', 'meta_produccion_parcela', 'observaciones', 'creado_en'
        ]
        read_only_fields = ['creado_en']

    def validate_parcela(self, value):
        """Validar que la parcela esté activa"""
        if value.estado != 'ACTIVA':
            raise serializers.ValidationError('Solo se pueden asignar parcelas con estado ACTIVA')
        return value

    def validate_superficie_comprometida(self, value):
        """Validar superficie comprometida"""
        if value is not None and value <= 0:
            raise serializers.ValidationError('La superficie comprometida debe ser mayor a 0')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        parcela = data.get('parcela') or (self.instance.parcela if self.instance else None)
        superficie_comprometida = data.get('superficie_comprometida')
        campaign = data.get('campaign') or (self.instance.campaign if self.instance else None)
        fecha_asignacion = data.get('fecha_asignacion')

        # Validar superficie
        if parcela and superficie_comprometida:
            if superficie_comprometida > parcela.superficie_hectareas:
                raise serializers.ValidationError({
                    'superficie_comprometida': f'La superficie comprometida no puede exceder la superficie total de la parcela ({parcela.superficie_hectareas} ha)'
                })

        # Validar fecha de asignación
        if campaign and fecha_asignacion and fecha_asignacion < campaign.fecha_inicio:
            raise serializers.ValidationError({
                'fecha_asignacion': 'La fecha de asignación no puede ser anterior al inicio de la campania'
            })

        return data


class CampaignSerializer(serializers.ModelSerializer):
    """
    CU9: Serializer principal para Campaign
    T036: Gestión de campanias (crear, editar, eliminar)
    T037: Mostrar socios y parcelas en Campaign (serializers anidados)
    """
    # Campos calculados
    duracion_dias = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()
    progreso_temporal = serializers.SerializerMethodField()
    puede_eliminar = serializers.SerializerMethodField()

    # Serializers anidados para mostrar relaciones (solo lectura)
    socios_asignados = CampaignPartnerSerializer(many=True, read_only=True)
    parcelas = CampaignPlotSerializer(many=True, read_only=True)

    # Información del responsable
    responsable_nombre = serializers.CharField(source='responsable.get_full_name', read_only=True)

    # Contadores
    total_socios = serializers.SerializerMethodField()
    total_parcelas = serializers.SerializerMethodField()
    total_superficie = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'nombre', 'fecha_inicio', 'fecha_fin', 'meta_produccion',
            'unidad_meta', 'estado', 'descripcion', 'presupuesto', 'responsable',
            'responsable_nombre', 'creado_en', 'actualizado_en',
            # Campos calculados
            'duracion_dias', 'dias_restantes', 'progreso_temporal', 'puede_eliminar',
            # Relaciones anidadas
            'socios_asignados', 'parcelas',
            # Contadores
            'total_socios', 'total_parcelas', 'total_superficie'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_duracion_dias(self, obj):
        return obj.duracion_dias()

    def get_dias_restantes(self, obj):
        return obj.dias_restantes()

    def get_progreso_temporal(self, obj):
        return round(obj.progreso_temporal(), 2)

    def get_puede_eliminar(self, obj):
        return obj.puede_eliminar()

    def get_total_socios(self, obj):
        return obj.socios_asignados.count()

    def get_total_parcelas(self, obj):
        return obj.parcelas.count()

    def get_total_superficie(self, obj):
        from django.db.models import Sum
        resultado = obj.parcelas.aggregate(
            total=Sum('superficie_comprometida')
        )
        return resultado['total'] or 0

    def validate_nombre(self, value):
        """Validar que el nombre sea único"""
        instance_id = self.instance.id if self.instance else None
        queryset = Campaign.objects.filter(nombre__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe una campania con este nombre')
        return value

    def validate_meta_produccion(self, value):
        """Validar meta de producción"""
        if value <= 0:
            raise serializers.ValidationError('La meta de producción debe ser mayor a 0')
        return value

    def validate_presupuesto(self, value):
        """Validar presupuesto"""
        if value is not None and value < 0:
            raise serializers.ValidationError('El presupuesto no puede ser negativo')
        return value

    def validate(self, data):
        """
        Validaciones entre campos
        T036: Validaciones (fecha_fin > fecha_inicio, no solapes)
        """
        fecha_inicio = data.get('fecha_inicio') or (self.instance.fecha_inicio if self.instance else None)
        fecha_fin = data.get('fecha_fin') or (self.instance.fecha_fin if self.instance else None)

        # Validar fecha_fin > fecha_inicio
        if fecha_inicio and fecha_fin and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
            })

        # Validar solape de fechas con otras campanias
        if fecha_inicio and fecha_fin:
            self._validar_solape_fechas(fecha_inicio, fecha_fin)

        return data

    def _validar_solape_fechas(self, fecha_inicio, fecha_fin):
        """
        Valida que no haya solape de fechas con otras campanias activas
        T036: Validación de no solapes entre campanias
        """
        from django.db.models import Q

        queryset = Campaign.objects.filter(
            Q(estado__in=['PLANIFICADA', 'EN_CURSO']) &
            (
                Q(fecha_inicio__lte=fecha_inicio, fecha_fin__gte=fecha_inicio) |
                Q(fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_fin) |
                Q(fecha_inicio__gte=fecha_inicio, fecha_fin__lte=fecha_fin)
            )
        )

        # Excluir la instancia actual si es una actualización
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            campanias_solapadas = ', '.join([c.nombre for c in queryset])
            raise serializers.ValidationError({
                'fecha_inicio': f'Las fechas se solapan con las siguientes campanias: {campanias_solapadas}. '
                               f'No puede haber campanias simultáneas.'
            })


class CampaignListSerializer(serializers.ModelSerializer):
    """
    CU9: Serializer simplificado para listados de campanias (sin relaciones anidadas)
    T036: Optimización de consultas para listados
    """
    responsable_nombre = serializers.CharField(source='responsable.get_full_name', read_only=True)
    duracion_dias = serializers.SerializerMethodField()
    total_socios = serializers.SerializerMethodField()
    total_parcelas = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'nombre', 'fecha_inicio', 'fecha_fin', 'meta_produccion',
            'unidad_meta', 'estado', 'responsable_nombre', 'duracion_dias',
            'total_socios', 'total_parcelas', 'creado_en'
        ]

    def get_duracion_dias(self, obj):
        return obj.duracion_dias()

    def get_total_socios(self, obj):
        return obj.socios_asignados.count()

    def get_total_parcelas(self, obj):
        return obj.parcelas.count()
    

# --- LABOR SERIALIZERS (REWRITE SIN INSUMO/RESPONSABLE) ---

class LaborBaseSerializer(serializers.ModelSerializer):
    # Fuerzan escritura/lectura por PK (evita objetos anidados en POST/PUT)
    campania = serializers.PrimaryKeyRelatedField(
        queryset=Campaign.objects.all(), allow_null=True, required=False
    )
    parcela = serializers.PrimaryKeyRelatedField(
        queryset=Parcela.objects.all(), allow_null=True, required=False
    )

    # Campos “solo lectura” para la UI
    campania_nombre = serializers.CharField(source='campania.nombre', read_only=True)
    parcela_nombre  = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_nombre    = serializers.SerializerMethodField()
    tipo_labor_display = serializers.SerializerMethodField()

    class Meta:
        model = Labor
        fields = [
            'id', 'fecha_labor', 'labor', 'tipo_labor_display', 'estado',
            'campania', 'campania_nombre', 'parcela', 'parcela_nombre',
            'socio_nombre', 'observaciones', 'creado_en', 'actualizado_en',
        ]
        read_only_fields = [
            'id', 'campania_nombre', 'parcela_nombre', 'socio_nombre',
            'tipo_labor_display', 'creado_en', 'actualizado_en'
        ]

    # ========= helpers de lectura =========
    def get_tipo_labor_display(self, obj):
        return obj.get_labor_display()

    def get_socio_nombre(self, obj):
        # Seguro ante nulos y método callable
        try:
            usuario = obj.parcela.socio.usuario
            return usuario.get_full_name() if usuario else None
        except Exception:
            return None

    # ========= validaciones =========
    def validate_fecha_labor(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError('La fecha de la labor no puede ser en el futuro.')
        return value

    def validate(self, data):
        instance = getattr(self, 'instance', None)

        campania = data.get('campania', getattr(instance, 'campania', None))
        parcela  = data.get('parcela',  getattr(instance, 'parcela',  None))
        fecha    = data.get('fecha_labor', getattr(instance, 'fecha_labor', None))

        # Reglas: al menos una ubicación
        if not campania and not parcela:
            raise serializers.ValidationError({
                'campania': 'Debe especificar campaña o parcela.',
                'parcela':  'Debe especificar campaña o parcela.',
            })

        # Parcela debe estar ACTIVA si se envía
        if parcela and getattr(parcela, 'estado', None) != 'ACTIVA':
            raise serializers.ValidationError({'parcela': 'Solo se pueden asignar labores a parcelas activas.'})

        # Fecha dentro del rango de la campaña (si hay campaña)
        if campania and fecha:
            if getattr(campania, 'fecha_inicio', None) and fecha < campania.fecha_inicio:
                raise serializers.ValidationError({
                    'fecha_labor': f'No puede ser anterior al inicio de la campaña ({campania.fecha_inicio}).'
                })
            if getattr(campania, 'fecha_fin', None) and fecha > campania.fecha_fin:
                raise serializers.ValidationError({
                    'fecha_labor': f'No puede ser posterior al fin de la campaña ({campania.fecha_fin}).'
                })

        return data


# Lectura/Detalle (usa todo lo de Base)
class LaborSerializer(LaborBaseSerializer):
    pass


# Creación (solo campos editables)
class LaborCreateSerializer(LaborBaseSerializer):
    class Meta(LaborBaseSerializer.Meta):
        fields = ['fecha_labor', 'labor', 'estado', 'campania', 'parcela', 'observaciones']


# Actualización (mismos campos que create)
class LaborUpdateSerializer(LaborBaseSerializer):
    class Meta(LaborBaseSerializer.Meta):
        fields = ['fecha_labor', 'labor', 'estado', 'campania', 'parcela', 'observaciones']


# Listado “liviano” para tablas
class LaborListSerializer(serializers.ModelSerializer):
    campania_nombre = serializers.CharField(source='campania.nombre', read_only=True)
    parcela_nombre  = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_nombre    = serializers.SerializerMethodField()
    tipo_labor_display = serializers.SerializerMethodField()

    class Meta:
        model = Labor
        fields = [
            'id', 'fecha_labor', 'labor', 'tipo_labor_display', 'estado',
            'campania_nombre', 'parcela_nombre', 'socio_nombre', 
            'observaciones',  
            'creado_en',
        ]

    def get_tipo_labor_display(self, obj):
        return obj.get_labor_display()

    def get_socio_nombre(self, obj):
        try:
            usuario = obj.parcela.socio.usuario
            return usuario.get_full_name() if usuario else None
        except Exception:
            return None
# ============================================================================
# CU15: SERIALIZERS PARA REGISTRO DE PRODUCTOS COSECHADOS
# Registrar productos cosechados por campania y parcela
# ============================================================================

class ProductoCosechadoSerializer(serializers.ModelSerializer):
    """CU15: Serializer principal para Productos Cosechados"""
    
    # Campos de relación (solo lectura para mostrar información)
    cultivo_especie = serializers.CharField(source='cultivo.especie', read_only=True)
    cultivo_variedad = serializers.CharField(source='cultivo.variedad', read_only=True)
    labor_nombre = serializers.CharField(source='labor.labor', read_only=True)
    campania_nombre = serializers.CharField(source='campania.nombre', read_only=True)
    parcela_nombre = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_nombre = serializers.SerializerMethodField()
    
    # Campos calculados
    origen_display = serializers.SerializerMethodField()
    dias_en_almacen = serializers.SerializerMethodField()
    esta_proximo_vencer = serializers.SerializerMethodField()
    puede_vender = serializers.SerializerMethodField()

    class Meta:
        model = ProductoCosechado
        fields = [
            'id', 'fecha_cosecha', 'cantidad', 'unidad_medida', 'calidad',
            'cultivo', 'cultivo_especie', 'cultivo_variedad',
            'labor', 'labor_nombre',
            'estado', 'lote', 'ubicacion_almacen',
            'campania', 'campania_nombre', 'parcela', 'parcela_nombre', 'socio_nombre',
            'observaciones', 'creado_en', 'actualizado_en',
            # Campos calculados
            'origen_display', 'dias_en_almacen', 'esta_proximo_vencer', 'puede_vender'
        ]
        read_only_fields = ['creado_en', 'actualizado_en']

    def get_socio_nombre(self, obj):
        """Obtener el nombre del socio desde cultivo o parcela"""
        if obj.parcela:
            return obj.parcela.socio.usuario.get_full_name()
        elif obj.campania and obj.campania.socios_asignados.exists():
            # Intentar obtener el socio de la campania
            socio_campania = obj.campania.socios_asignados.first()
            return socio_campania.socio.usuario.get_full_name()
        elif obj.cultivo:
            return obj.cultivo.parcela.socio.usuario.get_full_name()
        return "No asignado"

    def get_origen_display(self, obj):
        return obj.origen_display

    def get_dias_en_almacen(self, obj):
        return obj.dias_en_almacen()

    def get_esta_proximo_vencer(self, obj):
        return obj.esta_proximo_vencer()

    def get_puede_vender(self, obj):
        return obj.puede_vender()

    def validate_fecha_cosecha(self, value):
        """Validación de fecha de cosecha"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError('La fecha de cosecha no puede ser en el futuro')
        return value

    def validate_cantidad(self, value):
        """Validación de cantidad"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a 0')
        return value

    def validate_lote(self, value):
        """Validación de lote"""
        if value <= 0:
            raise serializers.ValidationError('El número de lote debe ser mayor a 0')
        return value

    def validate(self, data):
        """Validaciones entre campos"""
        campania = data.get('campania') or (self.instance.campania if self.instance else None)
        parcela = data.get('parcela') or (self.instance.parcela if self.instance else None)
        labor = data.get('labor') or (self.instance.labor if self.instance else None)

        # Validar que al menos una de las dos (campania o parcela) esté presente
        if not campania and not parcela:
            raise serializers.ValidationError({
                'campania': 'Debe especificar al menos una campania o una parcela.',
                'parcela': 'Debe especificar al menos una campania o una parcela.'
            })

        # Validar que no se especifiquen ambas opciones
        if campania and parcela:
            raise serializers.ValidationError({
                'campania': 'Solo puede especificar campania O parcela, no ambas.',
                'parcela': 'Solo puede especificar campania O parcela, no ambas.'
            })

        # Validar que la labor esté relacionada con la misma campania/parcela si se especifica
        if labor:
            if campania and labor.campania != campania:
                raise serializers.ValidationError({
                    'labor': f'La labor seleccionada no pertenece a la campania {campania.nombre}.'
                })

            if parcela and labor.parcela != parcela:
                raise serializers.ValidationError({
                    'labor': f'La labor seleccionada no pertenece a la parcela {parcela.nombre}.'
                })

        return data

    def create(self, validated_data):
        """Crear un nuevo producto cosechado con validaciones adicionales"""
        # Llamar al método clean del modelo para validaciones adicionales
        producto = ProductoCosechado(**validated_data)
        producto.clean()  # Ejecutar validaciones del modelo
        
        # Guardar el producto
        producto.save()
        return producto

    def update(self, instance, validated_data):
        """Actualizar un producto cosechado existente con validaciones adicionales"""
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Llamar al método clean del modelo para validaciones adicionales
        instance.clean()  # Ejecutar validaciones del modelo
        
        # Guardar el producto
        instance.save()
        return instance


class ProductoCosechadoCreateSerializer(serializers.ModelSerializer):
    """CU15: Serializer específico para creación de productos cosechados (sin campos de solo lectura)"""
    class Meta:
        model = ProductoCosechado
        fields = [
            'fecha_cosecha', 'cantidad', 'unidad_medida', 'calidad',
            'cultivo', 'labor', 'estado', 'lote', 'ubicacion_almacen',
            'campania', 'parcela', 'observaciones'
        ]

    def validate(self, data):
        """Validaciones específicas para creación"""
        # Llamar a las validaciones del serializer principal
        serializer = ProductoCosechadoSerializer(data=data, context=self.context)
        serializer.is_valid(raise_exception=True)
        return data


class ProductoCosechadoUpdateSerializer(serializers.ModelSerializer):
    """CU15: Serializer específico para actualización de productos cosechados"""
    class Meta:
        model = ProductoCosechado
        fields = [
            'fecha_cosecha', 'cantidad', 'unidad_medida', 'calidad',
            'cultivo', 'labor', 'estado', 'lote', 'ubicacion_almacen',
            'campania', 'parcela', 'observaciones'
        ]

    def validate(self, data):
        """Validaciones específicas para actualización"""
        # Llamar a las validaciones del serializer principal
        if self.instance:
            serializer = ProductoCosechadoSerializer(self.instance, data=data, partial=True, context=self.context)
        else:
            serializer = ProductoCosechadoSerializer(data=data, context=self.context)
        serializer.is_valid(raise_exception=True)
        return data


class ProductoCosechadoListSerializer(serializers.ModelSerializer):
    """CU15: Serializer simplificado para listados de productos cosechados"""
    cultivo_especie = serializers.CharField(source='cultivo.especie', read_only=True)
    origen_display = serializers.SerializerMethodField()
    socio_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ProductoCosechado
        fields = [
            'id', 'fecha_cosecha', 'cantidad', 'unidad_medida', 'calidad',
            'cultivo_especie', 'estado', 'lote', 'ubicacion_almacen',
            'origen_display', 'socio_nombre', 'creado_en'
        ]

    def get_origen_display(self, obj):
        return obj.origen_display

    def get_socio_nombre(self, obj):
        """Obtener el nombre del socio desde cultivo o parcela"""
        if obj.parcela:
            return obj.parcela.socio.usuario.get_full_name()
        elif obj.campania and obj.campania.socios_asignados.exists():
            socio_campania = obj.campania.socios_asignados.first()
            return socio_campania.socio.usuario.get_full_name()
        elif obj.cultivo:
            return obj.cultivo.parcela.socio.usuario.get_full_name()
        return "No asignado"


class ProductoCosechadoVenderSerializer(serializers.Serializer):
    """CU15: Serializer específico para vender productos cosechados"""
    cantidad_vendida = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='La cantidad vendida debe ser mayor a 0')]
    )
    observaciones = serializers.CharField(required=False, allow_blank=True)

    def validate_cantidad_vendida(self, value):
        """Validar que la cantidad a vender sea válida"""
        producto = self.context.get('producto')
        if producto and value > producto.cantidad:
            raise serializers.ValidationError(
                f'Cantidad insuficiente. Disponible: {producto.cantidad}'
            )
        return value

    def save(self, **kwargs):
        """Ejecutar la venta del producto"""
        producto = self.context.get('producto')
        cantidad_vendida = self.validated_data['cantidad_vendida']
        observaciones = self.validated_data.get('observaciones', '')

        if producto:
            producto.vender_producto(cantidad_vendida, observaciones)
        
        return producto


class ProductoCosechadoCambiarEstadoSerializer(serializers.Serializer):
    """CU15: Serializer específico para cambiar estado de productos cosechados"""
    nuevo_estado = serializers.ChoiceField(
        choices=ProductoCosechado.ESTADO_OPCIONES
    )
    observaciones = serializers.CharField(required=False, allow_blank=True)

    def validate_nuevo_estado(self, value):
        """Validar el nuevo estado"""
        producto = self.context.get('producto')
        if producto and producto.estado == value:
            raise serializers.ValidationError(
                f'El producto ya se encuentra en estado {value}'
            )
        return value

    def save(self, **kwargs):
        """Ejecutar el cambio de estado"""
        producto = self.context.get('producto')
        nuevo_estado = self.validated_data['nuevo_estado']
        observaciones = self.validated_data.get('observaciones', '')

        if producto:
            producto.cambiar_estado(nuevo_estado, observaciones)
        
        return producto


# ============================================================================
# SISTEMA DE PAGOS - SERIALIZERS
# Serializers para gestión de pedidos, pagos y ventas
# ============================================================================

class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializer para Detalle de Pedido"""
    producto_cosechado_nombre = serializers.CharField(
        source='producto_cosechado.cultivo.especie',
        read_only=True
    )
    
    class Meta:
        model = DetallePedido
        fields = [
            'id', 'pedido', 'producto_cosechado', 'producto_cosechado_nombre',
            'producto_nombre', 'producto_descripcion', 'cantidad',
            'unidad_medida', 'precio_unitario', 'subtotal', 'creado_en'
        ]
        read_only_fields = ['subtotal', 'creado_en']

    def validate_cantidad(self, value):
        """Validar cantidad"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a 0')
        return value

    def validate_precio_unitario(self, value):
        """Validar precio unitario"""
        if value < 0:
            raise serializers.ValidationError('El precio no puede ser negativo')
        return value


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer principal para Pedido"""
    items = DetallePedidoSerializer(many=True, read_only=True)
    socio_nombre = serializers.CharField(
        source='socio.usuario.get_full_name',
        read_only=True
    )
    creado_por_nombre = serializers.CharField(
        source='creado_por.get_full_name',
        read_only=True
    )
    total_pagado = serializers.SerializerMethodField()
    saldo_pendiente = serializers.SerializerMethodField()
    estado_pago = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = [
            'id', 'numero_pedido', 'socio', 'socio_nombre',
            'cliente_nombre', 'cliente_email', 'cliente_telefono', 'cliente_direccion',
            'fecha_pedido', 'fecha_entrega_estimada', 'fecha_entrega_real',
            'subtotal', 'impuestos', 'descuento', 'total',
            'estado', 'observaciones', 'creado_por', 'creado_por_nombre',
            'creado_en', 'actualizado_en', 'items',
            'total_pagado', 'saldo_pendiente', 'estado_pago'
        ]
        read_only_fields = [
            'numero_pedido', 'total', 'creado_en', 'actualizado_en',
            'total_pagado', 'saldo_pendiente', 'estado_pago'
        ]

    def get_total_pagado(self, obj):
        """Calcula el total pagado del pedido"""
        from django.db.models import Sum
        from decimal import Decimal
        total = obj.pagos.filter(estado='COMPLETADO').aggregate(
            total=Sum('monto')
        )['total']
        return total or Decimal('0')

    def get_saldo_pendiente(self, obj):
        """Calcula el saldo pendiente del pedido"""
        return obj.total - self.get_total_pagado(obj)

    def get_estado_pago(self, obj):
        """Determina el estado del pago"""
        saldo = self.get_saldo_pendiente(obj)
        if saldo <= 0:
            return 'PAGADO'
        elif saldo < obj.total:
            return 'PARCIAL'
        else:
            return 'PENDIENTE'

    def validate(self, data):
        """Validaciones del pedido"""
        # Validar que tenga cliente_nombre o socio
        socio = data.get('socio')
        cliente_nombre = data.get('cliente_nombre')
        
        if not socio and not cliente_nombre:
            raise serializers.ValidationError({
                'cliente_nombre': 'Debe especificar un socio o un nombre de cliente'
            })

        # Validar fechas
        fecha_entrega_estimada = data.get('fecha_entrega_estimada')
        fecha_pedido = data.get('fecha_pedido') or timezone.now().date()
        
        if fecha_entrega_estimada and fecha_entrega_estimada < fecha_pedido:
            raise serializers.ValidationError({
                'fecha_entrega_estimada': 'La fecha de entrega no puede ser anterior a la fecha del pedido'
            })

        return data


class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de pedidos con items"""
    items = DetallePedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = [
            'socio', 'cliente_nombre', 'cliente_email', 'cliente_telefono',
            'cliente_direccion', 'fecha_entrega_estimada', 'descuento',
            'observaciones', 'items'
        ]

    def create(self, validated_data):
        """Crear pedido con sus items"""
        items_data = validated_data.pop('items')
        pedido = Pedido.objects.create(**validated_data)

        # Crear items
        for item_data in items_data:
            DetallePedido.objects.create(pedido=pedido, **item_data)

        return pedido


class PagoSerializer(serializers.ModelSerializer):
    """Serializer principal para Pago"""
    pedido_numero = serializers.CharField(source='pedido.numero_pedido', read_only=True)
    cliente_nombre = serializers.CharField(source='pedido.cliente_nombre', read_only=True)
    procesado_por_nombre = serializers.CharField(
        source='procesado_por.get_full_name',
        read_only=True
    )
    metodo_pago_display = serializers.CharField(
        source='get_metodo_pago_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )

    class Meta:
        model = Pago
        fields = [
            'id', 'numero_recibo', 'pedido', 'pedido_numero', 'cliente_nombre',
            'fecha_pago', 'monto', 'metodo_pago', 'metodo_pago_display',
            'estado', 'estado_display', 'referencia_bancaria', 'banco',
            'comprobante_archivo', 'observaciones', 'stripe_payment_intent_id',
            'stripe_charge_id', 'procesado_por', 'procesado_por_nombre',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = [
            'numero_recibo', 'stripe_payment_intent_id', 'stripe_charge_id',
            'creado_en', 'actualizado_en'
        ]

    def validate_monto(self, value):
        """Validar monto"""
        if value <= 0:
            raise serializers.ValidationError('El monto debe ser mayor a 0')
        return value

    def validate(self, data):
        """Validaciones del pago"""
        pedido = data.get('pedido')
        monto = data.get('monto')
        metodo_pago = data.get('metodo_pago')

        # Validar que el pedido no esté cancelado
        if pedido and pedido.estado == 'CANCELADO':
            raise serializers.ValidationError({
                'pedido': 'No se puede registrar un pago para un pedido cancelado'
            })

        # Validar que el monto no exceda el saldo pendiente
        if pedido and monto:
            from django.db.models import Sum
            from decimal import Decimal
            total_pagado = pedido.pagos.filter(estado='COMPLETADO').aggregate(
                total=Sum('monto')
            )['total'] or Decimal('0')
            saldo_pendiente = pedido.total - total_pagado

            if monto > saldo_pendiente:
                raise serializers.ValidationError({
                    'monto': f'El monto excede el saldo pendiente (Bs. {saldo_pendiente})'
                })

        # Validar campos según método de pago
        if metodo_pago == 'TRANSFERENCIA':
            if not data.get('referencia_bancaria') or not data.get('banco'):
                raise serializers.ValidationError({
                    'referencia_bancaria': 'La referencia bancaria y banco son requeridos para transferencias',
                    'banco': 'La referencia bancaria y banco son requeridos para transferencias'
                })

        return data


class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de pagos"""
    class Meta:
        model = Pago
        fields = [
            'pedido', 'monto', 'metodo_pago', 'referencia_bancaria',
            'banco', 'comprobante_archivo', 'observaciones'
        ]

    def create(self, validated_data):
        """Crear pago y actualizar estado si es completado"""
        # Si es pago en efectivo o transferencia, marcar como completado automáticamente
        metodo = validated_data.get('metodo_pago')
        if metodo in ['EFECTIVO', 'TRANSFERENCIA', 'QR']:
            validated_data['estado'] = 'COMPLETADO'

        pago = Pago.objects.create(**validated_data)
        return pago


class PagoStripeSerializer(serializers.Serializer):
    """Serializer para procesar pagos con Stripe"""
    pedido_id = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method_id = serializers.CharField(max_length=200)
    observaciones = serializers.CharField(required=False, allow_blank=True)

    def validate_monto(self, value):
        """Validar monto"""
        if value <= 0:
            raise serializers.ValidationError('El monto debe ser mayor a 0')
        return value

    def validate_pedido_id(self, value):
        """Validar que el pedido exista"""
        try:
            Pedido.objects.get(id=value)
        except Pedido.DoesNotExist:
            raise serializers.ValidationError('El pedido no existe')
        return value


class HistorialVentasSerializer(serializers.Serializer):
    """Serializer para filtros de historial de ventas"""
    fecha_desde = serializers.DateField(required=False)
    fecha_hasta = serializers.DateField(required=False)
    cliente_nombre = serializers.CharField(required=False, allow_blank=True)
    socio_id = serializers.IntegerField(required=False)
    estado_pedido = serializers.ChoiceField(
        choices=Pedido.ESTADOS_PEDIDO,
        required=False
    )
    metodo_pago = serializers.ChoiceField(
        choices=Pago.METODOS_PAGO,
        required=False
    )

    def validate(self, data):
        """Validar fechas"""
        fecha_desde = data.get('fecha_desde')
        fecha_hasta = data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise serializers.ValidationError({
                'fecha_hasta': 'La fecha hasta no puede ser anterior a la fecha desde'
            })

        return data


# ============================================================
# SISTEMA DE VENTAS DE INSUMOS - SERIALIZERS
# ============================================================

class PrecioTemporadaSerializer(serializers.ModelSerializer):
    """Serializer para PrecioTemporada"""
    semilla_detalle = serializers.SerializerMethodField()
    pesticida_detalle = serializers.SerializerMethodField()
    fertilizante_detalle = serializers.SerializerMethodField()
    tipo_insumo_display = serializers.CharField(source='get_tipo_insumo_display', read_only=True)
    temporada_display = serializers.CharField(source='get_temporada_display', read_only=True)
    esta_vigente = serializers.SerializerMethodField()

    class Meta:
        model = PrecioTemporada
        fields = [
            'id', 'tipo_insumo', 'tipo_insumo_display', 'semilla', 'semilla_detalle',
            'pesticida', 'pesticida_detalle', 'fertilizante', 'fertilizante_detalle',
            'temporada', 'temporada_display', 'fecha_inicio', 'fecha_fin',
            'precio_venta', 'precio_mayoreo', 'cantidad_minima_mayoreo',
            'activo', 'esta_vigente', 'creado_en', 'actualizado_en'
        ]

    def get_semilla_detalle(self, obj):
        if obj.semilla:
            return {
                'id': obj.semilla.id,
                'especie': obj.semilla.especie,
                'variedad': obj.semilla.variedad
            }
        return None

    def get_pesticida_detalle(self, obj):
        if obj.pesticida:
            return {
                'id': obj.pesticida.id,
                'nombre_comercial': obj.pesticida.nombre_comercial,
                'ingrediente_activo': obj.pesticida.ingrediente_activo
            }
        return None

    def get_fertilizante_detalle(self, obj):
        if obj.fertilizante:
            return {
                'id': obj.fertilizante.id,
                'nombre_comercial': obj.fertilizante.nombre_comercial,
                'tipo_fertilizante': obj.fertilizante.tipo_fertilizante,
                'composicion_npk': obj.fertilizante.composicion_npk
            }
        return None

    def get_esta_vigente(self, obj):
        return obj.esta_vigente()


class DetallePedidoInsumoSerializer(serializers.ModelSerializer):
    """Serializer para DetallePedidoInsumo"""
    tipo_insumo_display = serializers.CharField(source='get_tipo_insumo_display', read_only=True)

    class Meta:
        model = DetallePedidoInsumo
        fields = [
            'id', 'pedido_insumo', 'tipo_insumo', 'tipo_insumo_display',
            'semilla', 'pesticida', 'fertilizante',
            'insumo_nombre', 'insumo_descripcion',
            'cantidad', 'unidad_medida', 'precio_unitario', 'subtotal',
            'temporada_aplicada', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['insumo_nombre', 'insumo_descripcion', 'subtotal']

    def validate(self, data):
        """Validar que solo se especifique un insumo"""
        tipo_insumo = data.get('tipo_insumo')
        semilla = data.get('semilla')
        pesticida = data.get('pesticida')
        fertilizante = data.get('fertilizante')

        count = sum([bool(semilla), bool(pesticida), bool(fertilizante)])
        if count != 1:
            raise serializers.ValidationError(
                'Debe especificar exactamente un insumo (semilla, pesticida o fertilizante)'
            )

        # Validar que el tipo coincida con el insumo
        if tipo_insumo == 'SEMILLA' and not semilla:
            raise serializers.ValidationError('Debe especificar una semilla')
        if tipo_insumo == 'PESTICIDA' and not pesticida:
            raise serializers.ValidationError('Debe especificar un pesticida')
        if tipo_insumo == 'FERTILIZANTE' and not fertilizante:
            raise serializers.ValidationError('Debe especificar un fertilizante')

        return data


class PedidoInsumoSerializer(serializers.ModelSerializer):
    """Serializer principal para PedidoInsumo"""
    socio_nombre = serializers.CharField(source='socio.usuario.get_full_name', read_only=True)
    aprobado_por_nombre = serializers.SerializerMethodField()
    entregado_por_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    items = DetallePedidoInsumoSerializer(many=True, read_only=True)
    total_pagado = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    estado_pago = serializers.CharField(read_only=True)

    class Meta:
        model = PedidoInsumo
        fields = [
            'id', 'numero_pedido', 'socio', 'socio_nombre',
            'fecha_pedido', 'fecha_entrega_solicitada', 'fecha_entrega_real',
            'subtotal', 'descuento', 'total',
            'total_pagado', 'saldo_pendiente', 'estado_pago',
            'estado', 'estado_display', 'motivo_solicitud', 'observaciones',
            'aprobado_por', 'aprobado_por_nombre', 'fecha_aprobacion',
            'entregado_por', 'entregado_por_nombre',
            'items', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = [
            'numero_pedido', 'fecha_aprobacion', 'creado_en', 'actualizado_en'
        ]

    def get_aprobado_por_nombre(self, obj):
        if obj.aprobado_por:
            return obj.aprobado_por.get_full_name()
        return None

    def get_entregado_por_nombre(self, obj):
        if obj.entregado_por:
            return obj.entregado_por.get_full_name()
        return None


class PedidoInsumoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear PedidoInsumo con items"""
    items = DetallePedidoInsumoSerializer(many=True)

    class Meta:
        model = PedidoInsumo
        fields = [
            'socio', 'fecha_entrega_solicitada', 'motivo_solicitud',
            'observaciones', 'items'
        ]

    def create(self, validated_data):
        """Crear pedido con sus items"""
        items_data = validated_data.pop('items')
        pedido = PedidoInsumo.objects.create(**validated_data)

        for item_data in items_data:
            DetallePedidoInsumo.objects.create(pedido_insumo=pedido, **item_data)

        pedido.calcular_totales()
        return pedido

    def validate_items(self, value):
        """Validar que haya al menos un item"""
        if not value or len(value) == 0:
            raise serializers.ValidationError('Debe agregar al menos un item')
        return value


class PagoInsumoSerializer(serializers.ModelSerializer):
    """Serializer principal para PagoInsumo"""
    pedido_numero = serializers.CharField(source='pedido_insumo.numero_pedido', read_only=True)
    socio_nombre = serializers.CharField(
        source='pedido_insumo.socio.usuario.get_full_name',
        read_only=True
    )
    registrado_por_nombre = serializers.SerializerMethodField()
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = PagoInsumo
        fields = [
            'id', 'numero_recibo', 'pedido_insumo', 'pedido_numero', 'socio_nombre',
            'fecha_pago', 'monto', 'metodo_pago', 'metodo_pago_display',
            'estado', 'estado_display', 'referencia_bancaria', 'banco',
            'comprobante_archivo', 'observaciones',
            'registrado_por', 'registrado_por_nombre',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['numero_recibo', 'creado_en', 'actualizado_en']

    def get_registrado_por_nombre(self, obj):
        if obj.registrado_por:
            return obj.registrado_por.get_full_name()
        return None

    def validate(self, data):
        """Validaciones del pago"""
        pedido = data.get('pedido_insumo')
        monto = data.get('monto')
        metodo_pago = data.get('metodo_pago')

        # Validar que el pedido no esté cancelado
        if pedido and pedido.estado == 'CANCELADO':
            raise serializers.ValidationError({
                'pedido_insumo': 'No se puede registrar un pago para un pedido cancelado'
            })

        # Validar que el monto no exceda el saldo pendiente
        if pedido and monto:
            if monto > pedido.saldo_pendiente:
                raise serializers.ValidationError({
                    'monto': f'El monto excede el saldo pendiente (Bs. {pedido.saldo_pendiente})'
                })

        # Validar campos según método de pago
        if metodo_pago == 'TRANSFERENCIA':
            if not data.get('referencia_bancaria') or not data.get('banco'):
                raise serializers.ValidationError({
                    'referencia_bancaria': 'La referencia bancaria y banco son requeridos',
                    'banco': 'La referencia bancaria y banco son requeridos'
                })

        return data


class HistorialComprasInsumosSerializer(serializers.Serializer):
    """Serializer para filtros de historial de compras de insumos"""
    socio_id = serializers.IntegerField(required=False)
    fecha_desde = serializers.DateField(required=False)
    fecha_hasta = serializers.DateField(required=False)
    estado = serializers.ChoiceField(
        choices=PedidoInsumo.ESTADOS_PEDIDO,
        required=False
    )
    tipo_insumo = serializers.ChoiceField(
        choices=PrecioTemporada.TIPO_INSUMO,
        required=False
    )

    def validate(self, data):
        """Validar fechas"""
        fecha_desde = data.get('fecha_desde')
        fecha_hasta = data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise serializers.ValidationError({
                'fecha_hasta': 'La fecha hasta no puede ser anterior a la fecha desde'
            })

        return data
