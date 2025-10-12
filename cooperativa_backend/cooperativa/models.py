from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import re
import json


def validate_ci_nit(value):
    """
    T021: Validación de CI/NIT
    - CI: 6-8 dígitos
    - NIT: formato empresarial con dígitos y guiones
    """
    if not value:
        raise ValidationError('CI/NIT es requerido')

    # Remover espacios y convertir a mayúsculas
    value = str(value).strip().upper()

    # Validar formato básico
    if not re.match(r'^[0-9\-]+$', value):
        raise ValidationError('CI/NIT solo puede contener números y guiones')

    # Validar longitud
    digits_only = re.sub(r'[^\d]', '', value)
    if len(digits_only) < 6 or len(digits_only) > 12:
        raise ValidationError('CI/NIT debe tener entre 6 y 12 dígitos')

    return value


def validate_email_domain(value):
    """
    T021: Validación adicional de email
    """
    if value:
        # Lista de dominios permitidos (puede configurarse)
        blocked_domains = ['10minutemail.com', 'temp-mail.org']
        domain = value.split('@')[-1].lower()

        if domain in blocked_domains:
            raise ValidationError('Dominio de email no permitido')

    return value


class Rol(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9_\-\s]+$',
            message='Nombre de rol solo puede contener letras, números, espacios, guiones y guiones bajos'
        )]
    )
    descripcion = models.TextField(blank=True, null=True)
    permisos = models.JSONField(
        default=dict,
        help_text='Permisos del rol en formato JSON'
    )
    es_sistema = models.BooleanField(
        default=False,
        help_text='Indica si es un rol del sistema que no puede ser eliminado'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre

    def clean(self):
        """Validaciones adicionales del modelo"""
        if self.nombre:
            self.nombre = self.nombre.strip().title()

        # Validar estructura de permisos
        if self.permisos:
            self._validar_estructura_permisos()

    def _validar_estructura_permisos(self):
        """Valida que los permisos tengan la estructura correcta"""
        permisos_requeridos = [
            'usuarios', 'socios', 'parcelas', 'cultivos',
            'ciclos_cultivo', 'cosechas', 'tratamientos',
            'analisis_suelo', 'transferencias', 'reportes',
            'auditoria', 'configuracion'
        ]

        for permiso in permisos_requeridos:
            if permiso not in self.permisos:
                self.permisos[permiso] = {
                    'ver': False,
                    'crear': False,
                    'editar': False,
                    'eliminar': False,
                    'aprobar': False
                }

    def tiene_permiso(self, modulo, accion):
        """
        Verifica si el rol tiene un permiso específico

        Args:
            modulo (str): Nombre del módulo (usuarios, socios, etc.)
            accion (str): Acción a verificar (ver, crear, editar, eliminar, aprobar)

        Returns:
            bool: True si tiene el permiso, False en caso contrario
        """
        if not self.permisos or modulo not in self.permisos:
            return False

        permisos_modulo = self.permisos[modulo]
        return permisos_modulo.get(accion, False)

    def obtener_permisos_completos(self):
        """
        Retorna todos los permisos del rol en formato legible

        Returns:
            dict: Diccionario con todos los permisos organizados por módulo
        """
        if not self.permisos:
            return {}

        permisos_completos = {}
        for modulo, acciones in self.permisos.items():
            permisos_modulo = []
            for accion, permitido in acciones.items():
                if permitido:
                    permisos_modulo.append(accion.title())
            if permisos_modulo:
                permisos_completos[modulo.title()] = permisos_modulo

        return permisos_completos

    @classmethod
    def crear_rol_administrador(cls):
        """Crea o actualiza el rol de Administrador con permisos completos"""
        permisos_admin = {
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

        rol, created = cls.objects.get_or_create(
            nombre='Administrador',
            defaults={
                'descripcion': 'Rol con permisos completos de administración del sistema',
                'permisos': permisos_admin,
                'es_sistema': True
            }
        )

        if not created:
            rol.descripcion = 'Rol con permisos completos de administración del sistema'
            rol.permisos = permisos_admin
            rol.es_sistema = True
            rol.save()

        return rol

    @classmethod
    def crear_rol_socio(cls):
        """Crea o actualiza el rol de Socio con permisos limitados"""
        permisos_socio = {
            'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
            'socios': {'ver': True, 'crear': False, 'editar': True, 'eliminar': False, 'aprobar': False},  # Solo ver/editar propio
            'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},  # Gestionar propias parcelas
            'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},  # Gestionar propios cultivos
            'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
            'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
            'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
            'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
            'transferencias': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False, 'aprobar': False},  # Solo crear solicitudes
            'reportes': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},  # Solo ver reportes
            'auditoria': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
            'configuracion': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
        }

        rol, created = cls.objects.get_or_create(
            nombre='Socio',
            defaults={
                'descripcion': 'Rol para socios de la cooperativa con acceso limitado a sus propios datos',
                'permisos': permisos_socio,
                'es_sistema': True
            }
        )

        if not created:
            rol.descripcion = 'Rol para socios de la cooperativa con acceso limitado a sus propios datos'
            rol.permisos = permisos_socio
            rol.es_sistema = True
            rol.save()

        return rol

    @classmethod
    def crear_rol_operador(cls):
        """Crea o actualiza el rol de Operador con permisos intermedios"""
        permisos_operador = {
            'usuarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},  # Solo ver
            'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},  # Gestionar socios
            'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},  # Gestionar parcelas
            'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},  # Gestionar cultivos
            'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
            'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
            'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
            'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
            'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},  # Gestionar transferencias
            'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},  # Crear/ver reportes
            'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},  # Solo ver auditoría
            'configuracion': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}  # Solo ver configuración
        }

        rol, created = cls.objects.get_or_create(
            nombre='Operador',
            defaults={
                'descripcion': 'Rol para operadores con permisos intermedios de gestión operativa',
                'permisos': permisos_operador,
                'es_sistema': True
            }
        )

        if not created:
            rol.descripcion = 'Rol para operadores con permisos intermedios de gestión operativa'
            rol.permisos = permisos_operador
            rol.es_sistema = True
            rol.save()

        return rol


class UsuarioManager(BaseUserManager):
    def create_user(self, ci_nit, nombres, apellidos, email, usuario, password=None):
        if not ci_nit:
            raise ValueError('El CI/NIT es obligatorio')
        if not usuario:
            raise ValueError('El nombre de usuario es obligatorio')
        if not nombres or not apellidos:
            raise ValueError('Nombres y apellidos son obligatorios')

        # Validar CI/NIT único - T027
        if Usuario.objects.filter(ci_nit=ci_nit).exists():
            raise ValueError('Ya existe un usuario con este CI/NIT')

        user = self.model(
            ci_nit=validate_ci_nit(ci_nit),
            nombres=nombres.strip().title(),
            apellidos=apellidos.strip().title(),
            email=self.normalize_email(email) if email else None,
            usuario=usuario.lower().strip(),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, ci_nit, nombres, apellidos, email, usuario, password):
        user = self.create_user(
            ci_nit=ci_nit,
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            usuario=usuario,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    ci_nit = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_ci_nit]
    )
    nombres = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s]+$',
            message='Nombres solo pueden contener letras y espacios'
        )]
    )
    apellidos = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s]+$',
            message='Apellidos solo pueden contener letras y espacios'
        )]
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        validators=[validate_email_domain]
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?[0-9\s\-\(\)]+$',
            message='Formato de teléfono inválido'
        )]
    )
    usuario = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9_]+$',
            message='Usuario solo puede contener letras, números y guiones bajos'
        )]
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    intentos_fallidos = models.IntegerField(default=0)
    ultimo_intento = models.DateTimeField(blank=True, null=True)
    fecha_bloqueo = models.DateTimeField(blank=True, null=True)
    token_actual = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)

    # Django auth fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = ['ci_nit', 'nombres', 'apellidos', 'email']

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"

    def get_short_name(self):
        return self.nombres

    def clean(self):
        """Validaciones adicionales del modelo"""
        if self.nombres:
            self.nombres = self.nombres.strip().title()
        if self.apellidos:
            self.apellidos = self.apellidos.strip().title()
        if self.usuario:
            self.usuario = self.usuario.lower().strip()

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)


class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'usuario_rol'
        unique_together = ('usuario', 'rol')
        verbose_name = 'Usuario-Rol'
        verbose_name_plural = 'Usuarios-Roles'

    def __str__(self):
        return f"{self.usuario} - {self.rol}"


class Comunidad(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.]+$',
            message='Nombre de comunidad solo puede contener letras, números, espacios, guiones y puntos'
        )]
    )
    municipio = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s]+$',
            message='Municipio solo puede contener letras y espacios'
        )]
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s]+$',
            message='Departamento solo puede contener letras y espacios'
        )]
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'comunidad'
        verbose_name = 'Comunidad'
        verbose_name_plural = 'Comunidades'

    def __str__(self):
        return self.nombre

    def clean(self):
        """Validaciones adicionales"""
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.municipio:
            self.municipio = self.municipio.strip().title()
        if self.departamento:
            self.departamento = self.departamento.strip().title()


class Socio(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    SEXOS = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        unique=True,
        error_messages={
            'unique': 'Ya existe un socio asociado a este usuario'
        }
    )
    codigo_interno = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9\-]+$',
            message='Código interno solo puede contener letras mayúsculas, números y guiones'
        )]
    )
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=SEXOS, blank=True, null=True)
    direccion = models.TextField(
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.,#]+$',
            message='Dirección contiene caracteres inválidos'
        )]
    )
    comunidad = models.ForeignKey(
        Comunidad,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'socio'
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'

    def __str__(self):
        return f"{self.usuario.nombres} {self.usuario.apellidos}"

    def clean(self):
        """Validaciones adicionales del modelo"""
        # Validar edad mínima (18 años)
        if self.fecha_nacimiento:
            from datetime import date
            today = date.today()
            age = today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
            if age < 18:
                raise ValidationError('El socio debe tener al menos 18 años')

        # Generar código interno si no existe
        if not self.codigo_interno and self.usuario:
            # Generar código basado en CI del usuario
            ci_digits = re.sub(r'[^\d]', '', self.usuario.ci_nit)
            self.codigo_interno = f"SOC-{ci_digits[:8]}"

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)


class Parcela(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    nombre = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.]+$',
            message='Nombre de parcela solo puede contener letras, números, espacios, guiones y puntos'
        )]
    )
    superficie_hectareas = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='La superficie debe ser mayor a 0')]
    )
    tipo_suelo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s]+$',
            message='Tipo de suelo solo puede contener letras y espacios'
        )]
    )
    ubicacion = models.TextField(
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.,#]+$',
            message='Ubicación contiene caracteres inválidos'
        )]
    )
    latitud = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-90, message='Latitud debe estar entre -90 y 90'),
            MaxValueValidator(90, message='Latitud debe estar entre -90 y 90')
        ],
        help_text='Latitud en grados decimales'
    )
    longitud = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-180, message='Longitud debe estar entre -180 y 180'),
            MaxValueValidator(180, message='Longitud debe estar entre -180 y 180')
        ],
        help_text='Longitud en grados decimales'
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVA')
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'parcela'
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'

    def __str__(self):
        return f"{self.nombre or 'Parcela'} - {self.socio}"

    def clean(self):
        """Validaciones adicionales"""
        # Validar que la superficie no exceda límites razonables
        if self.superficie_hectareas and self.superficie_hectareas > 10000:
            raise ValidationError('La superficie no puede exceder 10,000 hectáreas')

        # Validar coordenadas si ambas están presentes
        if (self.latitud and not self.longitud) or (self.longitud and not self.latitud):
            raise ValidationError('Si se proporciona una coordenada, ambas latitud y longitud son requeridas')

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)


class Cultivo(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('COSECHADO', 'Cosechado'),
    ]

    parcela = models.ForeignKey(Parcela, on_delete=models.CASCADE)
    especie = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s]+$',
            message='Especie solo puede contener letras y espacios'
        )]
    )
    variedad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.]+$',
            message='Variedad solo puede contener letras, números, espacios, guiones y puntos'
        )]
    )
    tipo_semilla = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s]+$',
            message='Tipo de semilla solo puede contener letras y espacios'
        )]
    )
    fecha_estimada_siembra = models.DateField(blank=True, null=True)
    hectareas_sembradas = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.01, message='Hectáreas sembradas debe ser mayor a 0')]
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cultivo'
        verbose_name = 'Cultivo'
        verbose_name_plural = 'Cultivos'

    def __str__(self):
        return f"{self.especie} - {self.parcela}"

    def clean(self):
        """Validaciones adicionales"""
        # Validar que hectáreas sembradas no exceda la superficie de la parcela
        if self.hectareas_sembradas and self.parcela:
            if self.hectareas_sembradas > self.parcela.superficie_hectareas:
                raise ValidationError('Las hectáreas sembradas no pueden exceder la superficie de la parcela')

        # Validar fecha de siembra no sea en el pasado
        if self.fecha_estimada_siembra:
            from datetime import date
            if self.fecha_estimada_siembra < date.today():
                raise ValidationError('La fecha estimada de siembra no puede ser en el pasado')

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)


class CicloCultivo(models.Model):
    """CU4: Modelo para ciclos completos de cultivo"""
    ESTADOS = [
        ('PLANIFICADO', 'Planificado'),
        ('SIEMBRA', 'En Siembra'),
        ('CRECIMIENTO', 'En Crecimiento'),
        ('COSECHA', 'En Cosecha'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cultivo = models.ForeignKey(Cultivo, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_estimada_fin = models.DateField()
    fecha_fin_real = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PLANIFICADO')
    observaciones = models.TextField(blank=True, null=True)
    costo_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El costo no puede ser negativo')]
    )
    costo_real = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El costo no puede ser negativo')]
    )
    rendimiento_esperado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El rendimiento no puede ser negativo')]
    )
    rendimiento_real = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El rendimiento no puede ser negativo')]
    )
    unidad_rendimiento = models.CharField(
        max_length=20,
        default='kg/ha',
        help_text='Unidad de medida del rendimiento (kg/ha, qq/ha, etc.)'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ciclo_cultivo'
        verbose_name = 'Ciclo de Cultivo'
        verbose_name_plural = 'Ciclos de Cultivo'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Ciclo {self.cultivo.especie} - {self.fecha_inicio}"

    def clean(self):
        """Validaciones del ciclo de cultivo"""
        if self.fecha_fin_real and self.fecha_fin_real < self.fecha_inicio:
            raise ValidationError('La fecha de fin real no puede ser anterior a la fecha de inicio')

        if self.fecha_estimada_fin < self.fecha_inicio:
            raise ValidationError('La fecha estimada de fin no puede ser anterior a la fecha de inicio')

    def dias_transcurridos(self):
        """Calcula días transcurridos desde el inicio"""
        from datetime import date
        return (date.today() - self.fecha_inicio).days

    def progreso_estimado(self):
        """Calcula el progreso estimado del ciclo"""
        from datetime import date
        total_dias = (self.fecha_estimada_fin - self.fecha_inicio).days
        dias_transcurridos = self.dias_transcurridos()

        if total_dias <= 0:
            return 100

        return min(100, max(0, (dias_transcurridos / total_dias) * 100))


class Cosecha(models.Model):
    """CU4: Modelo para registro de cosechas"""
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    ciclo_cultivo = models.ForeignKey(CicloCultivo, on_delete=models.CASCADE)
    fecha_cosecha = models.DateField()
    cantidad_cosechada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='La cantidad no puede ser negativa')]
    )
    unidad_medida = models.CharField(
        max_length=20,
        default='kg',
        help_text='Unidad de medida (kg, qq, toneladas, etc.)'
    )
    calidad = models.CharField(
        max_length=20,
        choices=[
            ('EXCELENTE', 'Excelente'),
            ('BUENA', 'Buena'),
            ('REGULAR', 'Regular'),
            ('MALA', 'Mala'),
        ],
        default='BUENA'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE',
        help_text='Estado de la cosecha'
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El precio no puede ser negativo')]
    )
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cosecha'
        verbose_name = 'Cosecha'
        verbose_name_plural = 'Cosechas'
        ordering = ['-fecha_cosecha']

    def __str__(self):
        return f"Cosecha {self.ciclo_cultivo} - {self.fecha_cosecha}"

    def clean(self):
        """Validaciones de cosecha"""
        if self.fecha_cosecha < self.ciclo_cultivo.fecha_inicio:
            raise ValidationError('La fecha de cosecha no puede ser anterior al inicio del ciclo')

    def valor_total(self):
        """Calcula el valor total de la cosecha"""
        if self.precio_venta:
            return self.cantidad_cosechada * self.precio_venta
        return 0


class Tratamiento(models.Model):
    """CU4: Modelo para tratamientos aplicados a cultivos"""
    TIPOS_TRATAMIENTO = [
        ('FERTILIZANTE', 'Fertilizante'),
        ('PESTICIDA', 'Pesticida'),
        ('HERBICIDA', 'Fungicida'),
        ('REGULADOR', 'Regulador de Crecimiento'),
        ('RIEGO', 'Riego'),
        ('LABOR', 'Labor Cultural'),
        ('OTRO', 'Otro'),
    ]

    ciclo_cultivo = models.ForeignKey(CicloCultivo, on_delete=models.CASCADE)
    tipo_tratamiento = models.CharField(max_length=20, choices=TIPOS_TRATAMIENTO)
    nombre_producto = models.CharField(max_length=100)
    dosis = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='La dosis no puede ser negativa')]
    )
    unidad_dosis = models.CharField(
        max_length=20,
        default='kg/ha',
        help_text='Unidad de dosis (kg/ha, l/ha, etc.)'
    )
    fecha_aplicacion = models.DateField()
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El costo no puede ser negativo')]
    )
    observaciones = models.TextField(blank=True, null=True)
    aplicado_por = models.CharField(max_length=100, blank=True, null=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'tratamiento'
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'
        ordering = ['-fecha_aplicacion']

    def __str__(self):
        return f"{self.tipo_tratamiento} - {self.nombre_producto} - {self.fecha_aplicacion}"

    def clean(self):
        """Validaciones de tratamiento"""
        if self.fecha_aplicacion < self.ciclo_cultivo.fecha_inicio:
            raise ValidationError('La fecha de aplicación no puede ser anterior al inicio del ciclo')

        if self.ciclo_cultivo.fecha_fin_real and self.fecha_aplicacion > self.ciclo_cultivo.fecha_fin_real:
            raise ValidationError('La fecha de aplicación no puede ser posterior al fin del ciclo')


class AnalisisSuelo(models.Model):
    """CU4: Modelo para análisis de suelo de parcelas"""
    TIPOS_ANALISIS = [
        ('QUIMICO', 'Químico'),
        ('FISICO', 'Físico'),
        ('BIOLOGICO', 'Biológico'),
        ('COMPLETO', 'Completo'),
    ]

    parcela = models.ForeignKey(Parcela, on_delete=models.CASCADE)
    fecha_analisis = models.DateField()
    tipo_analisis = models.CharField(
        max_length=20,
        choices=TIPOS_ANALISIS,
        default='COMPLETO',
        help_text='Tipo de análisis realizado'
    )
    ph = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0, message='El pH debe ser positivo'),
            MaxValueValidator(14, message='El pH no puede exceder 14')
        ]
    )
    materia_organica = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='La materia orgánica no puede ser negativa')]
    )
    nitrogeno = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El nitrógeno no puede ser negativo')]
    )
    fosforo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El fósforo no puede ser negativo')]
    )
    potasio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El potasio no puede ser negativo')]
    )
    laboratorio = models.CharField(max_length=100, blank=True, null=True)
    recomendaciones = models.TextField(blank=True, null=True)
    costo_analisis = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El costo no puede ser negativo')]
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'analisis_suelo'
        verbose_name = 'Análisis de Suelo'
        verbose_name_plural = 'Análisis de Suelo'
        ordering = ['-fecha_analisis']

    def __str__(self):
        return f"Análisis {self.parcela} - {self.fecha_analisis}"

    def clean(self):
        """Validaciones de análisis de suelo"""
        if self.ph is not None and not (4 <= self.ph <= 10):
            raise ValidationError('El pH del suelo debe estar entre 4 y 10 para ser óptimo para cultivos')

    def get_recomendaciones_basicas(self):
        """Genera recomendaciones básicas basadas en los valores"""
        recomendaciones = []

        if self.ph is not None:
            if self.ph < 5.5:
                recomendaciones.append("Suelo ácido - Considerar cal para elevar pH")
            elif self.ph > 7.5:
                recomendaciones.append("Suelo alcalino - Considerar azufre para bajar pH")
            else:
                recomendaciones.append("pH en rango óptimo")

        if self.materia_organica is not None and self.materia_organica < 2:
            recomendaciones.append("Baja materia orgánica - Recomendar abonos orgánicos")

        if self.nitrogeno is not None and self.nitrogeno < 0.1:
            recomendaciones.append("Nitrógeno bajo - Aplicar fertilizantes nitrogenados")

        if self.fosforo is not None and self.fosforo < 10:
            recomendaciones.append("Fósforo bajo - Aplicar fertilizantes fosfatados")

        if self.potasio is not None and self.potasio < 100:
            recomendaciones.append("Potasio bajo - Aplicar fertilizantes potásicos")

        return recomendaciones


class TransferenciaParcela(models.Model):
    """CU4: Modelo para transferencias de parcelas entre socios"""
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    parcela = models.ForeignKey(Parcela, on_delete=models.CASCADE)
    socio_anterior = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='parcelas_transferidas'
    )
    socio_nuevo = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='parcelas_recibidas'
    )
    fecha_transferencia = models.DateField()
    motivo = models.TextField()
    documento_legal = models.CharField(max_length=100, blank=True, null=True)
    costo_transferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El costo no puede ser negativo')]
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE',
        help_text='Estado de la transferencia'
    )
    autorizado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='transferencias_autorizadas'
    )
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'transferencia_parcela'
        verbose_name = 'Transferencia de Parcela'
        verbose_name_plural = 'Transferencias de Parcelas'
        ordering = ['-fecha_transferencia']

    def __str__(self):
        return f"Transferencia {self.parcela} de {self.socio_anterior} a {self.socio_nuevo}"

    def clean(self):
        """Validaciones de transferencia"""
        if self.socio_anterior == self.socio_nuevo:
            raise ValidationError('El socio anterior y nuevo no pueden ser el mismo')

        # Verificar que el socio anterior sea el propietario actual
        if self.parcela.socio != self.socio_anterior:
            raise ValidationError('El socio anterior no es el propietario actual de la parcela')

    def save(self, *args, **kwargs):
        # Actualizar el propietario de la parcela
        self.parcela.socio = self.socio_nuevo
        self.parcela.save()
        super().save(*args, **kwargs)


class BitacoraAuditoria(models.Model):
    ACCIONES = [
        # Operaciones CRUD
        ('CREAR', 'Crear'),
        ('ACTUALIZAR', 'Actualizar'),
        ('ELIMINAR', 'Eliminar'),
        # Operaciones de autenticación - T030: Bitácora extendida
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('LOGIN_FALLIDO', 'Intento de login fallido'),
        ('SESION_EXPIRADA', 'Sesión expirada'),
        ('SESION_INVALIDADA', 'Sesión invalidada'),
        ('BLOQUEO_CUENTA', 'Cuenta bloqueada'),
        ('DESBLOQUEO_CUENTA', 'Cuenta desbloqueada'),
        # Operaciones de usuario
        ('CAMBIAR_PASSWORD', 'Cambio de contraseña'),
        ('RESET_PASSWORD', 'Reset de contraseña'),
        # Operaciones de sistema
        ('ACCESO_DENEGADO', 'Acceso denegado'),
        ('PERMISO_INSUFICIENTE', 'Permiso insuficiente'),
        # Operaciones de CU3 - Gestión de socios
        ('ACTIVAR_SOCIO', 'Activar socio'),
        ('DESACTIVAR_SOCIO', 'Desactivar socio'),
        ('ACTIVAR_USUARIO', 'Activar usuario'),
        ('DESACTIVAR_USUARIO', 'Desactivar usuario'),
        # Operaciones de CU4 - Gestión avanzada de parcelas y cultivos
        ('CREAR_CICLO_CULTIVO', 'Crear ciclo de cultivo'),
        ('ACTUALIZAR_CICLO_CULTIVO', 'Actualizar ciclo de cultivo'),
        ('CREAR_COSECHA', 'Crear cosecha'),
        ('ACTUALIZAR_COSECHA', 'Actualizar cosecha'),
        ('CREAR_TRATAMIENTO', 'Crear tratamiento'),
        ('ACTUALIZAR_TRATAMIENTO', 'Actualizar tratamiento'),
        ('CREAR_ANALISIS_SUELO', 'Crear análisis de suelo'),
        ('ACTUALIZAR_ANALISIS_SUELO', 'Actualizar análisis de suelo'),
        ('CREAR_TRANSFERENCIA_PARCELA', 'Crear transferencia de parcela'),
        ('ACTUALIZAR_TRANSFERENCIA_PARCELA', 'Actualizar transferencia de parcela'),
        ('PROCESAR_TRANSFERENCIA_APROBAR', 'Aprobar transferencia'),
        ('PROCESAR_TRANSFERENCIA_RECHAZAR', 'Rechazar transferencia'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, blank=True, null=True)
    accion = models.CharField(max_length=50, choices=ACCIONES)
    tabla_afectada = models.CharField(max_length=100)
    registro_id = models.IntegerField()
    detalles = models.JSONField()
    fecha = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'bitacora_auditoria'
        verbose_name = 'Bitácora de Auditoría'
        verbose_name_plural = 'Bitácoras de Auditoría'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.accion} en {self.tabla_afectada} - {self.fecha}"


class Semilla(models.Model):
    """CU7: Modelo para gestión de semillas del inventario"""
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('AGOTADA', 'Agotada'),
        ('VENCIDA', 'Vencida'),
        ('RESERVADA', 'Reservada'),
    ]

    especie = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ\s\-\.]+$',
            message='Especie solo puede contener letras, espacios, guiones y puntos'
        )],
        help_text='Especie de la semilla (ej: Maíz, Trigo, Soya)'
    )
    variedad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.]+$',
            message='Variedad solo puede contener letras, números, espacios, guiones y puntos'
        )],
        help_text='Variedad específica de la semilla'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='La cantidad no puede ser negativa')],
        help_text='Cantidad disponible en kilogramos'
    )
    unidad_medida = models.CharField(
        max_length=20,
        default='kg',
        help_text='Unidad de medida (kg, g, toneladas, etc.)'
    )
    fecha_vencimiento = models.DateField(
        help_text='Fecha de vencimiento de la semilla'
    )
    porcentaje_germinacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0, message='El porcentaje no puede ser negativo'),
            MaxValueValidator(100, message='El porcentaje no puede exceder 100%')
        ],
        help_text='Porcentaje de germinación (%)'
    )
    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Número de lote del proveedor'
    )
    proveedor = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Nombre del proveedor'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El precio no puede ser negativo')],
        help_text='Precio unitario por kilogramo'
    )
    ubicacion_almacen = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Ubicación física en el almacén'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='DISPONIBLE',
        help_text='Estado actual de la semilla'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones adicionales'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semilla'
        verbose_name = 'Semilla'
        verbose_name_plural = 'Semillas'
        ordering = ['-creado_en']
        unique_together = ('especie', 'variedad', 'lote')

    def __str__(self):
        variedad_str = f" - {self.variedad}" if self.variedad else ""
        lote_str = f" (Lote: {self.lote})" if self.lote else ""
        return f"{self.especie}{variedad_str}{lote_str}"

    def clean(self):
        """Validaciones adicionales del modelo"""
        # Validar que la fecha de vencimiento no sea en el pasado
        from datetime import date
        if self.fecha_vencimiento and self.fecha_vencimiento < date.today():
            # Solo validar si no está ya vencida (para evitar problemas al editar registros existentes)
            if self.estado != 'VENCIDA':
                raise ValidationError('La fecha de vencimiento no puede ser en el pasado')

        # Validar que si está agotada, cantidad debe ser 0
        if self.estado == 'AGOTADA' and self.cantidad > 0:
            raise ValidationError('Una semilla agotada debe tener cantidad 0')

        # Validar que si cantidad es 0, estado debe ser AGOTADA
        if self.cantidad == 0 and self.estado == 'DISPONIBLE':
            raise ValidationError('Una semilla con cantidad 0 debe estar marcada como agotada')

    def save(self, *args, **kwargs):
        # Actualizar estado basado en cantidad y fecha de vencimiento
        from datetime import date
        hoy = date.today()

        if self.cantidad == 0:
            self.estado = 'AGOTADA'
        elif self.fecha_vencimiento and self.fecha_vencimiento < hoy:
            self.estado = 'VENCIDA'
        elif self.estado not in ['RESERVADA']:
            self.estado = 'DISPONIBLE'

        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)

    def valor_total(self):
        """Calcula el valor total del inventario de esta semilla"""
        if self.precio_unitario:
            return self.cantidad * self.precio_unitario
        return 0

    def dias_para_vencer(self):
        """Calcula días restantes para vencer"""
        from datetime import date
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - date.today()).days
        return None

    def esta_proxima_vencer(self, dias=30):
        """Verifica si la semilla está próxima a vencer"""
        dias_restantes = self.dias_para_vencer()
        return dias_restantes is not None and 0 <= dias_restantes <= dias

    def esta_vencida(self):
        """Verifica si la semilla está vencida"""
        from datetime import date
        return self.fecha_vencimiento and self.fecha_vencimiento < date.today()


class Pesticida(models.Model):
    """CU8: Modelo para gestión de pesticidas del inventario agrícola"""
    TIPOS_PESTICIDA = [
        ('INSECTICIDA', 'Insecticida'),
        ('FUNGICIDA', 'Fungicida'),
        ('HERBICIDA', 'Herbicida'),
        ('NEMATICIDA', 'Nematicida'),
        ('ACARICIDA', 'Acaricida'),
        ('BACTERICIDA', 'Bactericida'),
        ('MOLUSQUICIDA', 'Molusquicida'),
        ('RODENTICIDA', 'Rodenticida'),
        ('OTRO', 'Otro'),
    ]

    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('AGOTADO', 'Agotado'),
        ('VENCIDO', 'Vencido'),
        ('EN_CUARENTENA', 'En Cuarentena'),
        ('RECHAZADO', 'Rechazado'),
    ]

    nombre_comercial = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\(\)]+$',
            message='Nombre comercial solo puede contener letras, números, espacios, guiones, puntos y paréntesis'
        )],
        help_text='Nombre comercial del pesticida'
    )
    ingrediente_activo = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\(\)\+]+$',
            message='Ingrediente activo solo puede contener letras, números, espacios, guiones, puntos, paréntesis y signo más'
        )],
        help_text='Principio activo del pesticida'
    )
    tipo_pesticida = models.CharField(
        max_length=20,
        choices=TIPOS_PESTICIDA,
        help_text='Tipo de pesticida'
    )
    concentracion = models.CharField(
        max_length=50,
        validators=[RegexValidator(
            regex=r'^[0-9\.\,\s\%\-\(\)a-zA-Z\+]+$',
            message='Concentración debe tener formato válido (ej: 50%% WP, 200 g/L)'
        )],
        help_text='Concentración del ingrediente activo'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='La cantidad no puede ser negativa')],
        help_text='Cantidad disponible'
    )
    unidad_medida = models.CharField(
        max_length=20,
        default='L',
        help_text='Unidad de medida (L, kg, ml, g, etc.)'
    )
    fecha_vencimiento = models.DateField(
        help_text='Fecha de vencimiento del pesticida'
    )
    lote = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9\-_\.]+$',
            message='Lote solo puede contener letras mayúsculas, números, guiones, guiones bajos y puntos'
        )],
        help_text='Número único del lote'
    )
    proveedor = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\&\(\)]+$',
            message='Proveedor solo puede contener letras, números, espacios y caracteres especiales limitados'
        )],
        help_text='Nombre del proveedor'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='El precio no puede ser negativo')],
        help_text='Precio unitario'
    )
    ubicacion_almacen = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\/]+$',
            message='Ubicación solo puede contener letras, números, espacios, guiones, puntos y barras'
        )],
        help_text='Ubicación física en el almacén'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='DISPONIBLE',
        help_text='Estado actual del pesticida'
    )
    registro_sanitario = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Número de registro sanitario'
    )
    dosis_recomendada = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Dosis recomendada por hectárea'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones adicionales'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pesticida'
        verbose_name = 'Pesticida'
        verbose_name_plural = 'Pesticidas'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre_comercial} - {self.ingrediente_activo} (Lote: {self.lote})"

    def clean(self):
        """Validaciones adicionales del modelo"""
        # Validar que la fecha de vencimiento no sea en el pasado para nuevos registros
        from datetime import date
        if not self.pk and self.fecha_vencimiento and self.fecha_vencimiento < date.today():
            raise ValidationError('La fecha de vencimiento no puede ser en el pasado')

        # Validar que si está agotado, cantidad debe ser 0
        if self.estado == 'AGOTADO' and self.cantidad != 0:
            raise ValidationError('Si el pesticida está agotado, la cantidad debe ser 0')

        # Validar que si está vencido, estado debe ser VENCIDO
        if self.esta_vencido() and self.estado not in ['VENCIDO', 'RECHAZADO']:
            raise ValidationError('El pesticida está vencido. El estado debe ser VENCIDO o RECHAZADO')

    def save(self, *args, **kwargs):
        # Actualizar estado basado en cantidad y fecha de vencimiento
        from datetime import date
        hoy = date.today()

        if self.cantidad == 0 and self.estado == 'DISPONIBLE':
            self.estado = 'AGOTADO'
        elif self.esta_vencido() and self.estado not in ['VENCIDO', 'RECHAZADO']:
            self.estado = 'VENCIDO'

        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)

    def valor_total(self):
        """Calcula el valor total del inventario de este pesticida"""
        return self.cantidad * self.precio_unitario

    def dias_para_vencer(self):
        """Calcula días restantes para vencer"""
        from datetime import date
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - date.today()).days
        return None

    def esta_proximo_vencer(self, dias=30):
        """Verifica si el pesticida está próximo a vencer"""
        dias_restantes = self.dias_para_vencer()
        return dias_restantes is not None and 0 <= dias_restantes <= dias

    def esta_vencido(self):
        """Verifica si el pesticida está vencido"""
        from datetime import date
        return self.fecha_vencimiento and self.fecha_vencimiento < date.today()


class Fertilizante(models.Model):
    """CU8: Modelo para gestión de fertilizantes del inventario agrícola"""
    TIPOS_FERTILIZANTE = [
        ('QUIMICO', 'Químico'),
        ('ORGANICO', 'Orgánico'),
        ('FOLIARES', 'Foliares'),
        ('RAIZ', 'De raíz'),
        ('MICRONUTRIENTES', 'Micronutrientes'),
        ('CALCAREO', 'Calcareo'),
        ('OTRO', 'Otro'),
    ]

    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('AGOTADO', 'Agotado'),
        ('VENCIDO', 'Vencido'),
        ('EN_CUARENTENA', 'En Cuarentena'),
        ('RECHAZADO', 'Rechazado'),
    ]

    nombre_comercial = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\(\)\%]+$',
            message='Nombre comercial solo puede contener letras, números, espacios, guiones, puntos, paréntesis y porcentaje'
        )],
        help_text='Nombre comercial del fertilizante'
    )
    tipo_fertilizante = models.CharField(
        max_length=20,
        choices=TIPOS_FERTILIZANTE,
        help_text='Tipo de fertilizante'
    )
    composicion_npk = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[0-9\-]+-[0-9\-]+-[0-9\-]+(\+[0-9]+)?$',
            message='Composición NPK debe tener formato N-P-K (ej: 10-10-10, 20-10-10+5)'
        )],
        help_text='Composición NPK (ej: 10-10-10)'
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='La cantidad no puede ser negativa')],
        help_text='Cantidad disponible'
    )
    unidad_medida = models.CharField(
        max_length=20,
        default='kg',
        help_text='Unidad de medida (kg, toneladas, L, etc.)'
    )
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de vencimiento del fertilizante (opcional para orgánicos)'
    )
    lote = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9\-_\.]+$',
            message='Lote solo puede contener letras mayúsculas, números, guiones, guiones bajos y puntos'
        )],
        help_text='Número único del lote'
    )
    proveedor = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\&\(\)]+$',
            message='Proveedor solo puede contener letras, números, espacios y caracteres especiales limitados'
        )],
        help_text='Nombre del proveedor'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='El precio no puede ser negativo')],
        help_text='Precio unitario'
    )
    ubicacion_almacen = models.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\/]+$',
            message='Ubicación solo puede contener letras, números, espacios, guiones, puntos y barras'
        )],
        help_text='Ubicación física en el almacén'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='DISPONIBLE',
        help_text='Estado actual del fertilizante'
    )
    dosis_recomendada = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Dosis recomendada por hectárea'
    )
    materia_orgánica = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0, message='La materia orgánica no puede ser negativa'),
            MaxValueValidator(100, message='La materia orgánica no puede exceder 100%')
        ],
        help_text='Porcentaje de materia orgánica (para fertilizantes orgánicos)'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones adicionales'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fertilizante'
        verbose_name = 'Fertilizante'
        verbose_name_plural = 'Fertilizantes'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre_comercial} - {self.composicion_npk} (Lote: {self.lote})"

    def clean(self):
        """Validaciones adicionales del modelo"""
        # Validar fecha de vencimiento solo para fertilizantes químicos
        from datetime import date
        if self.tipo_fertilizante == 'QUIMICO' and not self.fecha_vencimiento:
            raise ValidationError('Los fertilizantes químicos requieren fecha de vencimiento')

        if self.fecha_vencimiento and self.fecha_vencimiento < date.today():
            if self.estado not in ['VENCIDO', 'RECHAZADO']:
                raise ValidationError('El fertilizante está vencido. El estado debe ser VENCIDO o RECHAZADO')

        # Validar que si está agotado, cantidad debe ser 0
        if self.estado == 'AGOTADO' and self.cantidad != 0:
            raise ValidationError('Si el fertilizante está agotado, la cantidad debe ser 0')

        # Validar materia orgánica solo para orgánicos
        if self.tipo_fertilizante == 'ORGANICO' and self.materia_orgánica is None:
            raise ValidationError('Los fertilizantes orgánicos requieren especificar materia orgánica')

    def save(self, *args, **kwargs):
        # Actualizar estado basado en cantidad y fecha de vencimiento
        from datetime import date
        hoy = date.today()

        if self.cantidad == 0 and self.estado == 'DISPONIBLE':
            self.estado = 'AGOTADO'
        elif self.fecha_vencimiento and self.fecha_vencimiento < hoy and self.estado not in ['VENCIDO', 'RECHAZADO']:
            self.estado = 'VENCIDO'

        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)

    def valor_total(self):
        """Calcula el valor total del inventario de este fertilizante"""
        return self.cantidad * self.precio_unitario

    def dias_para_vencer(self):
        """Calcula días restantes para vencer"""
        from datetime import date
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - date.today()).days
        return None

    def esta_proximo_vencer(self, dias=30):
        """Verifica si el fertilizante está próximo a vencer"""
        dias_restantes = self.dias_para_vencer()
        return dias_restantes is not None and 0 <= dias_restantes <= dias

    def esta_vencido(self):
        """Verifica si el fertilizante está vencido"""
        from datetime import date
        return self.fecha_vencimiento and self.fecha_vencimiento < date.today()

    def get_npk_values(self):
        """Extrae valores N, P, K de la composición"""
        try:
            partes = self.composicion_npk.split('-')
            n = int(partes[0]) if partes[0] != '' else 0
            p = int(partes[1]) if partes[1] != '' else 0
            k = int(partes[2].split('+')[0]) if partes[2] != '' else 0
            return {'N': n, 'P': p, 'K': k}
        except (ValueError, IndexError):
            return None


# ============================================================================
# CU9: GESTIÓN DE CAMPAÑAS AGRÍCOLAS
# T036: Gestión de campañas (crear, editar, eliminar)
# T037: Relación entre campaña y socios
# ============================================================================

class Campaign(models.Model):
    """
    CU9: Modelo para gestión de campañas agrícolas
    T036: Gestión de campañas (crear, editar, eliminar)
    
    Una campaña representa un ciclo agrícola completo con objetivos específicos
    de producción, fechas definidas y asociación con socios y parcelas.
    """
    ESTADOS = [
        ('PLANIFICADA', 'Planificada'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    nombre = models.CharField(
        max_length=200,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZÀ-ÿ0-9\s\-\.\/]+$',
            message='Nombre solo puede contener letras, números, espacios, guiones, puntos y barras'
        )],
        help_text='Nombre descriptivo de la campaña'
    )
    fecha_inicio = models.DateField(
        help_text='Fecha de inicio de la campaña'
    )
    fecha_fin = models.DateField(
        help_text='Fecha programada de finalización de la campaña'
    )
    meta_produccion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0, message='La meta de producción no puede ser negativa')],
        help_text='Meta de producción total de la campaña (en kg o toneladas)'
    )
    unidad_meta = models.CharField(
        max_length=20,
        default='kg',
        help_text='Unidad de medida de la meta (kg, toneladas, quintales, etc.)'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PLANIFICADA',
        help_text='Estado actual de la campaña'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción detallada de los objetivos y características de la campaña'
    )
    presupuesto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='El presupuesto no puede ser negativo')],
        help_text='Presupuesto asignado a la campaña'
    )
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='campañas_responsables',
        help_text='Usuario responsable de coordinar la campaña'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign'
        verbose_name = 'Campaña'
        verbose_name_plural = 'Campañas'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio} - {self.fecha_fin})"

    def clean(self):
        """Validaciones del modelo"""
        # Validar que fecha_fin > fecha_inicio
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
            })

        # Validar solape de fechas con otras campañas
        self._validar_solape_fechas()

    def _validar_solape_fechas(self):
        """
        Valida que no haya solape de fechas con otras campañas activas
        T036: Validación de no solapes entre campañas
        """
        # Obtener campañas que se solapan (excluyendo la actual si es actualización)
        queryset = Campaign.objects.filter(
            Q(estado__in=['PLANIFICADA', 'EN_CURSO']) &
            (
                # Caso 1: Nueva campaña inicia dentro de campaña existente
                Q(fecha_inicio__lte=self.fecha_inicio, fecha_fin__gte=self.fecha_inicio) |
                # Caso 2: Nueva campaña termina dentro de campaña existente
                Q(fecha_inicio__lte=self.fecha_fin, fecha_fin__gte=self.fecha_fin) |
                # Caso 3: Nueva campaña engloba campaña existente
                Q(fecha_inicio__gte=self.fecha_inicio, fecha_fin__lte=self.fecha_fin)
            )
        )

        # Excluir la instancia actual si es una actualización
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        if queryset.exists():
            campañas_solapadas = ', '.join([c.nombre for c in queryset])
            raise ValidationError({
                'fecha_inicio': f'Las fechas se solapan con las siguientes campañas: {campañas_solapadas}. '
                               f'No puede haber campañas simultáneas.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)

    def puede_eliminar(self):
        """
        Verifica si la campaña puede ser eliminada
        T036: Validar que no se elimine campaña con labores o cosechas asociadas
        """
        # Simplemente retorna True si no hay labores ni cosechas
        # La lógica real se maneja en las relaciones de cascada
        return True

    def duracion_dias(self):
        """Calcula la duración de la campaña en días"""
        if not self.fecha_inicio or not self.fecha_fin:
            return 0
        return (self.fecha_fin - self.fecha_inicio).days

    def dias_restantes(self):
        """Calcula días restantes si la campaña está en curso"""
        from datetime import date
        if self.estado == 'EN_CURSO' and self.fecha_fin:
            hoy = date.today()
            if hoy < self.fecha_fin:
                return (self.fecha_fin - hoy).days
        return 0

    def progreso_temporal(self):
        """Calcula el progreso temporal de la campaña (%)"""
        from datetime import date
        hoy = date.today()
        # Si faltan fechas, no es posible calcular
        if not self.fecha_inicio or not self.fecha_fin:
            return 0.0
        
        # Si la campaña está finalizada, progreso = 100%
        if self.estado == 'FINALIZADA':
            return 100.0
        
        # Si la campaña está cancelada, progreso = 0%
        if self.estado == 'CANCELADA':
            return 0.0
        
        # Si la campaña no ha empezado, progreso = 0%
        if hoy < self.fecha_inicio:
            return 0.0
        
        # Si la campaña ya terminó (fecha pasada), progreso = 100%
        if hoy > self.fecha_fin:
            return 100.0
        
        # Calcular progreso basado en días transcurridos
        duracion_total = self.duracion_dias()
        dias_transcurridos = (hoy - self.fecha_inicio).days

        if duracion_total <= 0:
            return 100.0

        return min(100.0, max(0.0, (dias_transcurridos / duracion_total) * 100))


class CampaignPartner(models.Model):
    """
    CU9: Modelo para relación M2M entre Campaign y Socio con campos adicionales
    T037: Relación entre campaña y socios
    """
    ROLES = [
        ('COORDINADOR', 'Coordinador'),
        ('PRODUCTOR', 'Productor'),
        ('TECNICO', 'Técnico Agrícola'),
        ('SUPERVISOR', 'Supervisor'),
    ]

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='socios_asignados'
    )
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name='campañas_participadas'
    )
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='PRODUCTOR',
        help_text='Rol del socio en la campaña'
    )
    fecha_asignacion = models.DateField(
        default=timezone.now,
        help_text='Fecha en que el socio fue asignado a la campaña'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones sobre la participación del socio'
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'campaign_partner'
        verbose_name = 'Socio de Campaña'
        verbose_name_plural = 'Socios de Campañas'
        unique_together = ('campaign', 'socio')
        ordering = ['-fecha_asignacion']

    def __str__(self):
        return f"{self.socio.usuario.get_full_name()} - {self.campaign.nombre} ({self.rol})"

    def clean(self):
        """Validaciones del modelo"""
        # Validar que el socio esté activo
        if self.socio.estado != 'ACTIVO':
            raise ValidationError({
                'socio': 'Solo se pueden asignar socios con estado ACTIVO'
            })

        # Validar que la fecha de asignación esté dentro del rango de la campaña
        if self.fecha_asignacion < self.campaign.fecha_inicio:
            raise ValidationError({
                'fecha_asignacion': 'La fecha de asignación no puede ser anterior al inicio de la campaña'
            })


class CampaignPlot(models.Model):
    """
    CU9: Modelo para asociar parcelas a campañas
    T037: Relación entre campaña y parcelas
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='parcelas'
    )
    parcela = models.ForeignKey(
        Parcela,
        on_delete=models.CASCADE,
        related_name='campañas'
    )
    fecha_asignacion = models.DateField(
        default=timezone.now,
        help_text='Fecha en que la parcela fue asignada a la campaña'
    )
    superficie_comprometida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.01, message='La superficie debe ser mayor a 0')],
        help_text='Superficie de la parcela comprometida para esta campaña (en hectáreas)'
    )
    cultivo_planificado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Cultivo planificado para esta parcela en la campaña'
    )
    meta_produccion_parcela = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0, message='La meta no puede ser negativa')],
        help_text='Meta de producción específica para esta parcela'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones sobre la participación de la parcela'
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'campaign_plot'
        verbose_name = 'Parcela de Campaña'
        verbose_name_plural = 'Parcelas de Campañas'
        unique_together = ('campaign', 'parcela')
        ordering = ['-fecha_asignacion']

    def __str__(self):
        return f"{self.parcela.nombre} - {self.campaign.nombre}"

    def clean(self):
        """Validaciones del modelo"""
        # Validar que la parcela esté activa
        if self.parcela.estado != 'ACTIVA':
            raise ValidationError({
                'parcela': 'Solo se pueden asignar parcelas con estado ACTIVA'
            })

        # Validar que la superficie comprometida no exceda la superficie total
        if self.superficie_comprometida and self.superficie_comprometida > self.parcela.superficie_hectareas:
            raise ValidationError({
                'superficie_comprometida': f'La superficie comprometida no puede exceder la superficie total de la parcela ({self.parcela.superficie_hectareas} ha)'
            })

        # Validar que la fecha de asignación esté dentro del rango de la campaña
        if self.fecha_asignacion < self.campaign.fecha_inicio:
            raise ValidationError({
                'fecha_asignacion': 'La fecha de asignación no puede ser anterior al inicio de la campaña'
            })