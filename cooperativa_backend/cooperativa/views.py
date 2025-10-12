from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Sum, Avg, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django.contrib.sessions.models import Session
from decimal import Decimal
from .models import (
    Rol, Usuario, UsuarioRol, Comunidad, Socio,
    Parcela, Cultivo, BitacoraAuditoria,
    CicloCultivo, Cosecha, Tratamiento, AnalisisSuelo, TransferenciaParcela,
    Semilla, Pesticida, Fertilizante, Labor, ProductoCosechado
)
from .models import Campaign, CampaignPartner, CampaignPlot
from .serializers import (
    RolSerializer, UsuarioSerializer, UsuarioCreateSerializer,
    UsuarioRolSerializer, ComunidadSerializer, SocioSerializer,
    SocioCreateSerializer, SocioCreateSimpleSerializer, SocioUpdateSerializer, ParcelaSerializer, CultivoSerializer,
    BitacoraAuditoriaSerializer, CicloCultivoSerializer,
    CosechaSerializer, TratamientoSerializer, AnalisisSueloSerializer,
    TransferenciaParcelaSerializer, SemillaSerializer, PesticidaSerializer, FertilizanteSerializer,
    CampaignSerializer, CampaignListSerializer, LaborSerializer, LaborListSerializer, LaborCreateSerializer, LaborUpdateSerializer, ProductoCosechadoSerializer, ProductoCosechadoListSerializer,
    ProductoCosechadoCambiarEstadoSerializer, ProductoCosechadoCreateSerializer, ProductoCosechadoUpdateSerializer, ProductoCosechadoVenderSerializer
)
from .reports import CampaignReports


# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Página de inicio simple y bonita en '/'
def home(request):
    html = (
        "<div style='font-family:Inter,Segoe UI,Arial,sans-serif; padding:32px'>"
        "<h1 style='margin:0 0 6px;color:#1b4332'>Cooperativa Agrícola</h1>"
        "<p style='margin:0 0 24px;color:#555'>Backend – Panel y API</p>"
        "<div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px'>"
        "<a href='/admin/' style='background:#2d6a4f;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none'>Ir al Admin</a>"
        "<a href='/api/' style='background:#1d3557;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none'>Explorar API</a>"
        "<a href='/chatbot/' style='background:#6a4c93;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none'>Chatbot</a>"
        "</div>"
        "<div style='background:#f8f9fa;border:1px solid #e9ecef;padding:16px;border-radius:8px'>"
        "<strong>Atajos rápidos (CU9/CU11): YV</strong>"
        "<ul style='margin:8px 0 0 16px;color:#333'>"
        "<li><a href='/admin/cooperativa/campaign/' style='color:#2a9d8f'>Campañas</a> (CU9)</li>"
        "<li>Reportes en detalle de campaña → sección 'Reportes CU11'</li>"
        "</ul>"
        "</div>"
        "</div>"
    )
    return HttpResponse(html)


# Vistas de Autenticación
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def test_login(request):
    """
    Test endpoint to debug login request
    """
    print("=" * 50)
    print("TEST LOGIN DEBUG - REQUEST RECEIVED")
    print("=" * 50)
    print(f"Content-Type: {request.content_type}")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")

    # Use DRF's request.data for consistent parsing
    if request.content_type == 'application/json':
        data = request.data
        print(f"Parsed data: {data}")
        print(f"Username from data: {data.get('username')}")
        print(f"Password from data: {data.get('password')}")
    else:
        print("Non-JSON content type, checking POST data")
        if hasattr(request, 'POST') and request.POST:
            print(f"POST data: {dict(request.POST)}")

    print("=" * 50)
    print("END TEST LOGIN DEBUG")
    print("=" * 50)

    return Response({'message': 'Debug info printed to console'})


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """
    CU1: Iniciar sesión (web/móvil)
    T011: Autenticación y gestión de sesiones
    T013: Bitácora de auditoría básica
    """
    try:
        print("=== LOGIN DEBUG ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")
        print(f"Headers: {dict(request.headers)}")

        # Use DRF's request.data for consistent parsing
        if request.content_type == 'application/json':
            data = request.data
            username = data.get('username')
            password = data.get('password')
            print(f"Parsed JSON data: {data}")
            print(f"Username: {username}, Password: {'*' * len(password) if password else None}")
        elif hasattr(request, 'POST') and request.POST:
            # Handle form data
            username = request.POST.get('username')
            password = request.POST.get('password')
        else:
            # Fallback to manual parsing if needed
            try:
                import json
                raw_body = request.body.decode('utf-8')
                data = json.loads(raw_body)
                username = data.get('username')
                password = data.get('password')
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                return Response(
                    {'error': 'Formato de datos no soportado'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not username or not password:
            return Response(
                {'error': 'Usuario y contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Test basic authentication
        user = authenticate(request, username=username, password=password)

        if user:
            # Verificar si el usuario está bloqueado
            if user.estado == 'BLOQUEADO':
                return Response(
                    {'error': 'Cuenta bloqueada. Contacte al administrador'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Login exitoso
            login(request, user)

            # Reset failed attempts
            user.intentos_fallidos = 0
            user.ultimo_intento = timezone.now()
            user.save()

            # Registrar login en bitácora - T013
            BitacoraAuditoria.objects.create(
                usuario=user,
                accion='LOGIN',
                tabla_afectada='usuario',
                registro_id=user.id,
                detalles={
                    'ip': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT'),
                    'metodo_autenticacion': 'credenciales',
                    'estado_usuario': user.estado
                },
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
            )

            # Simple response without serializer for now
            return Response({
                'mensaje': 'Login exitoso',
                'usuario': {
                    'id': user.id,
                    'usuario': user.usuario,
                    'nombres': user.nombres,
                    'apellidos': user.apellidos,
                    'email': user.email,
                    'estado': user.estado,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                },
                'csrf_token': get_token(request)
            })

        else:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        # Catch any unexpected errors
        print(f"Unexpected error in login_view: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def logout_view(request):
    """
    CU2: Cerrar sesión (web/móvil)
    T023: Implementación de cierre de sesión
    T030: Bitácora extendida - Registro de cierres de sesión
    """
    user = request.user

    # Registrar logout en bitácora extendida - T030
    BitacoraAuditoria.objects.create(
        usuario=user,
        accion='LOGOUT',
        tabla_afectada='usuario',
        registro_id=user.id,
        detalles={
            'ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'sesion_duracion': 'calculada'  # Podría calcularse con session start time
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    logout(request)

    return Response({'mensaje': 'Sesión cerrada exitosamente'})


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def csrf_token(request):
    """
    Obtener token CSRF para el frontend
    """
    return Response({'csrf_token': get_token(request)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def session_status(request):
    """
    Verificar estado de la sesión
    """
    serializer = UsuarioSerializer(request.user)
    return Response({
        'autenticado': True,
        'usuario': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invalidate_all_sessions(request):
    """
    CU2: Invalidar todas las sesiones del usuario actual
    T011: Gestión de sesiones
    T030: Bitácora extendida
    """
    user = request.user

    # Invalidar todas las sesiones del usuario
    sessions_deleted = 0

    for session in Session.objects.all():
        session_data = session.get_decoded()
        if session_data.get('_auth_user_id') == str(user.id):
            session.delete()
            sessions_deleted += 1

    # Registrar en bitácora - T030
    BitacoraAuditoria.objects.create(
        usuario=user,
        accion='SESION_INVALIDADA',
        tabla_afectada='usuario',
        registro_id=user.id,
        detalles={
            'ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'sesiones_invalidada': sessions_deleted,
            'razon': 'Invalidación manual de todas las sesiones'
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )

    return Response({
        'mensaje': f'Se invalidaron {sessions_deleted} sesiones',
        'sesiones_invalidada': sessions_deleted
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def session_info(request):
    """
    CU2: Información detallada de la sesión actual
    T011: Gestión de sesiones
    """
    user = request.user
    session_key = request.session.session_key

    return Response({
        'usuario': UsuarioSerializer(user).data,
        'session_id': session_key,
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'session_expiry': request.session.get_expiry_date(),
        'is_secure': request.is_secure(),
        'autenticado': True
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def force_logout_user(request, user_id):
    """
    CU2: Forzar cierre de sesión de otro usuario (solo admin)
    T011: Gestión de sesiones
    T030: Bitácora extendida
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        target_user = Usuario.objects.get(id=user_id)

        # Invalidar sesiones del usuario objetivo
        sessions_deleted = 0

        for session in Session.objects.all():
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(target_user.id):
                session.delete()
                sessions_deleted += 1

        # Registrar en bitácora - T030
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='SESION_INVALIDADA',
            tabla_afectada='usuario',
            registro_id=target_user.id,
            detalles={
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'sesiones_invalidada': sessions_deleted,
                'razon': 'Invalidación forzada por administrador',
                'admin': request.user.usuario
            },
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        return Response({
            'mensaje': f'Se invalidaron {sessions_deleted} sesiones del usuario {target_user.usuario}',
            'usuario_afectado': target_user.usuario,
            'sesiones_invalidada': sessions_deleted
        })

    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Solo administradores pueden ver roles del sistema
        if not self.request.user.is_staff:
            queryset = queryset.filter(es_sistema=False)
        return queryset

    def perform_create(self, serializer):
        """T012: Registrar creación de rol en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='rol',
            registro_id=instance.id,
            detalles={'creado_por': self.request.user.usuario}
        )

    def perform_update(self, serializer):
        """T012: Registrar actualización de rol en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='rol',
            registro_id=instance.id,
            detalles={'actualizado_por': self.request.user.usuario}
        )

    def perform_destroy(self, instance):
        """T012: Registrar eliminación de rol en bitácora"""
        if instance.es_sistema:
            raise serializers.ValidationError('No se puede eliminar un rol del sistema')

        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='rol',
            registro_id=instance.id,
            detalles={'eliminado_por': self.request.user.usuario}
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def asignar_usuario(self, request, pk=None):
        """CU6: Asignar rol a usuario"""
        rol = self.get_object()
        usuario_id = request.data.get('usuario_id')

        if not usuario_id:
            return Response(
                {'error': 'usuario_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar si ya tiene este rol
        if UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
            return Response(
                {'error': 'El usuario ya tiene asignado este rol'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear asignación
        usuario_rol = UsuarioRol.objects.create(usuario=usuario, rol=rol)

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='usuario_rol',
            registro_id=usuario_rol.id,
            detalles={
                'rol_asignado': rol.nombre,
                'usuario_afectado': usuario.usuario,
                'asignado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        serializer = UsuarioRolSerializer(usuario_rol)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def quitar_usuario(self, request, pk=None):
        """CU6: Quitar rol a usuario"""
        rol = self.get_object()
        usuario_id = request.data.get('usuario_id')

        if not usuario_id:
            return Response(
                {'error': 'usuario_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuario.objects.get(id=usuario_id)
            usuario_rol = UsuarioRol.objects.get(usuario=usuario, rol=rol)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except UsuarioRol.DoesNotExist:
            return Response(
                {'error': 'El usuario no tiene asignado este rol'},
                status=status.HTTP_404_NOT_FOUND
            )

        # No permitir quitar roles del sistema si es el último
        if rol.es_sistema:
            otros_roles_sistema = UsuarioRol.objects.filter(
                usuario=usuario,
                rol__es_sistema=True
            ).exclude(id=usuario_rol.id).count()

            if otros_roles_sistema == 0:
                return Response(
                    {'error': 'No se puede quitar el último rol del sistema del usuario'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        usuario_rol_id = usuario_rol.id
        usuario_rol.delete()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ELIMINAR',
            tabla_afectada='usuario_rol',
            registro_id=usuario_rol_id,
            detalles={
                'rol_removido': rol.nombre,
                'usuario_afectado': usuario.usuario,
                'removido_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        return Response({'mensaje': 'Rol removido exitosamente'})

    @action(detail=True, methods=['get'])
    def usuarios(self, request, pk=None):
        """CU6: Obtener usuarios con este rol"""
        rol = self.get_object()
        usuarios_roles = UsuarioRol.objects.filter(rol=rol).select_related('usuario')
        serializer = UsuarioRolSerializer(usuarios_roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicar(self, request, pk=None):
        """CU6: Duplicar rol con nuevos permisos"""
        rol_original = self.get_object()
        nuevo_nombre = request.data.get('nuevo_nombre')

        if not nuevo_nombre:
            return Response(
                {'error': 'nuevo_nombre es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que el nombre no exista
        if Rol.objects.filter(nombre__iexact=nuevo_nombre).exists():
            return Response(
                {'error': 'Ya existe un rol con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear rol duplicado
        nuevo_rol = Rol.objects.create(
            nombre=nuevo_nombre,
            descripcion=request.data.get('descripcion', f'Copia de {rol_original.nombre}'),
            permisos=rol_original.permisos.copy(),
            es_sistema=False
        )

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='rol',
            registro_id=nuevo_rol.id,
            detalles={
                'rol_duplicado': rol_original.nombre,
                'creado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        serializer = self.get_serializer(nuevo_rol)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user if not admin (users can only see themselves)
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(id=user.id)
        return queryset

    def update(self, request, *args, **kwargs):
        """Override update to check permissions"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permisos insuficientes'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """T013: Registrar creación de usuario en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='usuario',
            registro_id=instance.id,
            detalles={'creado_por': self.request.user.usuario}
        )

    def perform_update(self, serializer):
        """T013: Registrar actualización de usuario en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='usuario',
            registro_id=instance.id,
            detalles={'actualizado_por': self.request.user.usuario}
        )

    def perform_destroy(self, instance):
        """T013: Registrar eliminación de usuario en bitácora"""
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='usuario',
            registro_id=instance.id,
            detalles={'eliminado_por': self.request.user.usuario}
        )
        instance.delete()

    @action(detail=False, methods=['post'])
    def login(self, request):
        """CU1: Método de login alternativo (mantener compatibilidad)"""
        return login_view(request)

    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        user = self.get_object()
        nueva_password = request.data.get('nueva_password')

        if nueva_password:
            user.set_password(nueva_password)
            user.save()

            # Registrar cambio de contraseña en bitácora
            BitacoraAuditoria.objects.create(
                usuario=self.request.user,
                accion='CAMBIAR_PASSWORD',
                tabla_afectada='usuario',
                registro_id=user.id,
                detalles={'cambiado_por': self.request.user.usuario}
            )

            return Response({'mensaje': 'Contraseña cambiada exitosamente'})
        return Response(
            {'error': 'Nueva contraseña requerida'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """CU3: Activar usuario"""
        usuario = self.get_object()
        usuario.estado = 'ACTIVO'
        usuario.save()

        # Si es socio, activar también
        try:
            socio = Socio.objects.get(usuario=usuario)
            socio.estado = 'ACTIVO'
            socio.save()
        except Socio.DoesNotExist:
            pass

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ACTIVAR_USUARIO',
            tabla_afectada='usuario',
            registro_id=usuario.id,
            detalles={'activado_por': request.user.usuario}
        )

        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """CU3: Desactivar usuario"""
        usuario = self.get_object()
        usuario.estado = 'INACTIVO'
        usuario.save()

        # Si es socio, desactivar también
        try:
            socio = Socio.objects.get(usuario=usuario)
            socio.estado = 'INACTIVO'
            socio.save()
        except Socio.DoesNotExist:
            pass

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='DESACTIVAR_USUARIO',
            tabla_afectada='usuario',
            registro_id=usuario.id,
            detalles={'desactivado_por': request.user.usuario}
        )

        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """CU3: Obtener roles de un usuario"""
        usuario = self.get_object()
        roles = UsuarioRol.objects.filter(usuario=usuario).select_related('rol')
        serializer = UsuarioRolSerializer(roles, many=True)
        return Response(serializer.data)


class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.select_related('usuario', 'rol')
    serializer_class = UsuarioRolSerializer
    permission_classes = [IsAuthenticated]


class ComunidadViewSet(viewsets.ModelViewSet):
    queryset = Comunidad.objects.all()
    serializer_class = ComunidadSerializer
    permission_classes = [IsAuthenticated]


class SocioViewSet(viewsets.ModelViewSet):
    queryset = Socio.objects.select_related('usuario', 'comunidad')
    serializer_class = SocioSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Usar SocioCreateSimpleSerializer para creación, SocioUpdateSerializer para actualización, SocioSerializer para otras operaciones"""
        if self.action == 'create':
            return SocioCreateSimpleSerializer
        elif self.action == 'update':
            return SocioUpdateSerializer
        return SocioSerializer

    def update(self, request, *args, **kwargs):
        """Override update to check permissions"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permisos insuficientes'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user's socio if not admin
        user = self.request.user
        if not user.is_staff:
            try:
                socio = Socio.objects.get(usuario=user)
                queryset = queryset.filter(id=socio.id)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        """T014: Registrar creación de socio en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='socio',
            registro_id=instance.id,
            detalles={'creado_por': self.request.user.usuario}
        )

    def perform_update(self, serializer):
        """T014: Registrar actualización de socio en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='socio',
            registro_id=instance.id,
            detalles={'actualizado_por': self.request.user.usuario}
        )

    def perform_destroy(self, instance):
        """T014: Registrar eliminación de socio en bitácora"""
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='socio',
            registro_id=instance.id,
            detalles={'eliminado_por': self.request.user.usuario}
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """CU3: Activar socio"""
        socio = self.get_object()
        socio.estado = 'ACTIVO'
        socio.usuario.estado = 'ACTIVO'
        socio.save()
        socio.usuario.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ACTIVAR_SOCIO',
            tabla_afectada='socio',
            registro_id=socio.id,
            detalles={'activado_por': request.user.usuario}
        )

        serializer = self.get_serializer(socio)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """CU3: Desactivar socio"""
        socio = self.get_object()
        socio.estado = 'INACTIVO'
        socio.usuario.estado = 'INACTIVO'
        socio.save()
        socio.usuario.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='DESACTIVAR_SOCIO',
            tabla_afectada='socio',
            registro_id=socio.id,
            detalles={'desactivado_por': request.user.usuario}
        )

        serializer = self.get_serializer(socio)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def parcelas(self, request, pk=None):
        """CU3: Obtener parcelas de un socio"""
        socio = self.get_object()
        parcelas = Parcela.objects.filter(socio=socio)
        serializer = ParcelaSerializer(parcelas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def cultivos(self, request, pk=None):
        """CU3: Obtener cultivos de un socio"""
        socio = self.get_object()
        cultivos = Cultivo.objects.filter(parcela__socio=socio).select_related('parcela')
        serializer = CultivoSerializer(cultivos, many=True)
        return Response(serializer.data)


class ParcelaViewSet(viewsets.ModelViewSet):
    queryset = Parcela.objects.select_related('socio__usuario')
    serializer_class = ParcelaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user's parcels if not admin
        user = self.request.user
        if not user.is_staff:
            try:
                socio = Socio.objects.get(usuario=user)
                queryset = queryset.filter(socio=socio)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        # Validate superficie
        superficie = serializer.validated_data.get('superficie_hectareas')
        if superficie <= 0:
            raise serializers.ValidationError('La superficie debe ser mayor a 0')
        serializer.save()


class CultivoViewSet(viewsets.ModelViewSet):
    queryset = Cultivo.objects.select_related('parcela__socio__usuario')
    serializer_class = CultivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user's crops if not admin
        user = self.request.user
        if not user.is_staff:
            try:
                socio = Socio.objects.get(usuario=user)
                queryset = queryset.filter(parcela__socio=socio)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        return queryset


class BitacoraAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BitacoraAuditoria.objects.select_related('usuario')
    serializer_class = BitacoraAuditoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user if not admin
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(usuario=user)
        return queryset


# CU3: Gestión de Socios - Endpoints adicionales
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_socio_completo(request):
    """
    CU3: Crear socio completo con usuario
    T012: Gestión de usuarios y roles
    T014: CRUD de socios con validaciones
    T021: Validación de datos en formularios
    T027: Validación de duplicados
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = SocioCreateSerializer(data=request.data)
    if serializer.is_valid():
        socio = serializer.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='socio',
            registro_id=socio.id,
            detalles={
                'usuario_creado': socio.usuario.usuario,
                'creado_por': request.user.usuario
            },
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        # Serializar respuesta completa
        response_serializer = SocioSerializer(socio)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activar_desactivar_socio(request, socio_id):
    """
    CU3: Activar o desactivar socio
    T012: Gestión de usuarios (inhabilitar/reactivar)
    T014: CRUD de socios con validaciones
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        socio = Socio.objects.select_related('usuario').get(id=socio_id)
    except Socio.DoesNotExist:
        return Response(
            {'error': 'Socio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    accion = request.data.get('accion')  # 'activar' o 'desactivar'

    if accion not in ['activar', 'desactivar']:
        return Response(
            {'error': 'Acción inválida. Use "activar" o "desactivar"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    nuevo_estado = 'ACTIVO' if accion == 'activar' else 'INACTIVO'
    socio.estado = nuevo_estado
    socio.save()

    # Actualizar estado del usuario también
    socio.usuario.estado = nuevo_estado
    socio.usuario.save()

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='ACTIVAR_SOCIO' if accion == 'activar' else 'DESACTIVAR_SOCIO',
        tabla_afectada='socio',
        registro_id=socio.id,
        detalles={
            'nuevo_estado': nuevo_estado,
            'usuario_afectado': socio.usuario.usuario,
            'modificado_por': request.user.usuario
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = SocioSerializer(socio)
    return Response({
        'mensaje': f'Socio {"activado" if accion == "activar" else "desactivado"} exitosamente',
        'socio': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activar_desactivar_usuario(request, usuario_id):
    """
    CU3: Activar o desactivar usuario
    T012: Gestión de usuarios (inhabilitar/reactivar)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    accion = request.data.get('accion')  # 'activar' o 'desactivar'

    if accion not in ['activar', 'desactivar']:
        return Response(
            {'error': 'Acción inválida. Use "activar" o "desactivar"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    nuevo_estado = 'ACTIVO' if accion == 'activar' else 'INACTIVO'
    usuario.estado = nuevo_estado
    usuario.save()

    # Si el usuario es socio, actualizar también el estado del socio
    try:
        socio = Socio.objects.get(usuario=usuario)
        socio.estado = nuevo_estado
        socio.save()
    except Socio.DoesNotExist:
        pass

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='ACTIVAR_USUARIO' if accion == 'activar' else 'DESACTIVAR_USUARIO',
        tabla_afectada='usuario',
        registro_id=usuario.id,
        detalles={
            'nuevo_estado': nuevo_estado,
            'usuario_afectado': usuario.usuario,
            'modificado_por': request.user.usuario
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = UsuarioSerializer(usuario)
    return Response({
        'mensaje': f'Usuario {"activado" if accion == "activar" else "desactivado"} exitosamente',
        'usuario': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_socios_avanzado(request):
    """
    CU3: Búsqueda avanzada de socios
    T016: Búsquedas y filtros de socios
    T029: Búsqueda avanzada de socios
    """
    # Verificar autenticación manualmente para devolver 401 en lugar de 403
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    queryset = Socio.objects.select_related('usuario', 'comunidad')

    # Filtros de búsqueda
    nombre = request.query_params.get('nombre', '').strip()
    apellido = request.query_params.get('apellido', '').strip()
    ci_nit = request.query_params.get('ci_nit', '').strip()
    comunidad_id = request.query_params.get('comunidad', '').strip()
    estado = request.query_params.get('estado', '').strip()
    codigo_interno = request.query_params.get('codigo_interno', '').strip()
    sexo = request.query_params.get('sexo', '').strip()

    # Aplicar filtros
    if nombre:
        queryset = queryset.filter(usuario__nombres__icontains=nombre)
    if apellido:
        queryset = queryset.filter(usuario__apellidos__icontains=apellido)
    if ci_nit:
        queryset = queryset.filter(usuario__ci_nit__icontains=ci_nit)
    if comunidad_id:
        queryset = queryset.filter(comunidad_id=comunidad_id)
    if estado:
        queryset = queryset.filter(estado=estado)
    if codigo_interno:
        queryset = queryset.filter(codigo_interno__icontains=codigo_interno)
    if sexo:
        queryset = queryset.filter(sexo=sexo)

    # Paginación básica
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    socios = queryset[start:end]

    serializer = SocioSerializer(socios, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_socios_por_cultivo(request):
    """
    CU3: Búsqueda de socios por cultivo
    T016: Búsquedas y filtros de socios (Comunidad/cultivo)
    """
    # Verificar autenticación manualmente para devolver 401 en lugar de 403
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    cultivo_especie = request.query_params.get('especie', '').strip()
    cultivo_estado = request.query_params.get('estado', '').strip()

    if not cultivo_especie:
        return Response(
            {'error': 'Debe especificar la especie del cultivo'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Buscar socios que tienen parcelas con cultivos de la especie especificada
    socios_ids = Cultivo.objects.filter(
        especie__icontains=cultivo_especie
    ).select_related('parcela__socio').values_list('parcela__socio', flat=True).distinct()

    if cultivo_estado:
        socios_ids = Cultivo.objects.filter(
            especie__icontains=cultivo_especie,
            estado=cultivo_estado
        ).select_related('parcela__socio').values_list('parcela__socio', flat=True).distinct()

    queryset = Socio.objects.filter(id__in=socios_ids).select_related('usuario', 'comunidad')

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    socios = queryset[start:end]

    serializer = SocioSerializer(socios, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros': {
            'especie_cultivo': cultivo_especie,
            'estado_cultivo': cultivo_estado
        },
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def reporte_usuarios_socios(request):
    """
    CU3: Reporte inicial de usuarios activos/inactivos y socios registrados
    T031: Reporte inicial de usuarios activos/inactivos y socios registrados
    """
    # Verificar autenticación manualmente para devolver 401 en lugar de 403
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Estadísticas de usuarios
    usuarios_total = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(estado='ACTIVO').count()
    usuarios_inactivos = Usuario.objects.filter(estado='INACTIVO').count()
    usuarios_bloqueados = Usuario.objects.filter(estado='BLOQUEADO').count()

    # Estadísticas de socios
    socios_total = Socio.objects.count()
    socios_activos = Socio.objects.filter(estado='ACTIVO').count()
    socios_inactivos = Socio.objects.filter(estado='INACTIVO').count()

    # Socios por comunidad
    socios_por_comunidad = Comunidad.objects.annotate(
        num_socios=Count('socio')
    ).values('nombre', 'num_socios').order_by('-num_socios')

    # Usuarios por rol
    usuarios_por_rol = Rol.objects.annotate(
        num_usuarios=Count('usuariorol')
    ).values('nombre', 'num_usuarios').order_by('-num_usuarios')

    # Socios registrados por mes (últimos 12 meses)
    socios_por_mes = Socio.objects.annotate(
        mes=TruncMonth('creado_en')
    ).values('mes').annotate(
        count=Count('id')
    ).order_by('mes')[:12]

    return Response({
        'resumen_general': {
            'usuarios_total': usuarios_total,
            'usuarios_activos': usuarios_activos,
            'usuarios_inactivos': usuarios_inactivos,
            'usuarios_bloqueados': usuarios_bloqueados,
            'socios_total': socios_total,
            'socios_activos': socios_activos,
            'socios_inactivos': socios_inactivos
        },
        'socios_por_comunidad': list(socios_por_comunidad),
        'usuarios_por_rol': list(usuarios_por_rol),
        'socios_por_mes': list(socios_por_mes),
        'porcentajes': {
            'usuarios_activos_pct': round((usuarios_activos / usuarios_total * 100), 2) if usuarios_total > 0 else 0,
            'socios_activos_pct': round((socios_activos / socios_total * 100), 2) if socios_total > 0 else 0
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_datos_socio(request):
    """
    CU3: Validar datos de socio antes de crear/editar
    T021: Validación de datos en formularios
    T027: Validación de duplicados
    """
    ci_nit = request.query_params.get('ci_nit', '').strip()
    email = request.query_params.get('email', '').strip()
    usuario = request.query_params.get('usuario', '').strip()
    codigo_interno = request.query_params.get('codigo_interno', '').strip()

    errores = {}

    # Validar CI/NIT
    if ci_nit:
        if Usuario.objects.filter(ci_nit=ci_nit).exists():
            errores['ci_nit'] = 'Ya existe un usuario con este CI/NIT'

    # Validar email
    if email:
        if Usuario.objects.filter(email__iexact=email).exists():
            errores['email'] = 'Ya existe un usuario con este email'

    # Validar usuario
    if usuario:
        if Usuario.objects.filter(usuario__iexact=usuario).exists():
            errores['usuario'] = 'Ya existe un usuario con este nombre de usuario'

    # Validar código interno
    if codigo_interno:
        if Socio.objects.filter(codigo_interno__iexact=codigo_interno).exists():
            errores['codigo_interno'] = 'Ya existe un socio con este código interno'

    if errores:
        return Response({
            'valido': False,
            'errores': errores
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'valido': True,
            'mensaje': 'Todos los datos son válidos'
        })


# CU4: Gestión Avanzada de Parcelas y Cultivos
# ============================================

class CicloCultivoViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Ciclos de Cultivo
    T041: Gestión de ciclos de cultivo
    """
    queryset = CicloCultivo.objects.all().select_related('cultivo__parcela')
    serializer_class = CicloCultivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        cultivo_id = self.request.query_params.get('cultivo_id')
        estado = self.request.query_params.get('estado')
        fecha_inicio_desde = self.request.query_params.get('fecha_inicio_desde')
        fecha_inicio_hasta = self.request.query_params.get('fecha_inicio_hasta')

        if parcela_id:
            queryset = queryset.filter(cultivo__parcela_id=parcela_id)
        if cultivo_id:
            queryset = queryset.filter(cultivo_id=cultivo_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_inicio_desde:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio_desde)
        if fecha_inicio_hasta:
            queryset = queryset.filter(fecha_inicio__lte=fecha_inicio_hasta)

        return queryset.order_by('-fecha_inicio')

    def perform_create(self, serializer):
        # Registrar en bitácora
        ciclo = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_CICLO_CULTIVO',
            tabla_afectada='CicloCultivo',
            registro_id=ciclo.id,
            detalles=f'Ciclo de cultivo creado para parcela {ciclo.cultivo.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        ciclo = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_CICLO_CULTIVO',
            tabla_afectada='CicloCultivo',
            registro_id=ciclo.id,
            detalles=f'Ciclo de cultivo actualizado para parcela {ciclo.cultivo.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class CosechaViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Cosechas
    T042: Gestión de cosechas
    """
    queryset = Cosecha.objects.all().select_related('ciclo_cultivo__cultivo__parcela', 'ciclo_cultivo__cultivo')
    serializer_class = CosechaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        ciclo_cultivo_id = self.request.query_params.get('ciclo_cultivo_id')
        parcela_id = self.request.query_params.get('parcela_id')
        fecha_cosecha_desde = self.request.query_params.get('fecha_cosecha_desde')
        fecha_cosecha_hasta = self.request.query_params.get('fecha_cosecha_hasta')
        estado = self.request.query_params.get('estado')

        if ciclo_cultivo_id:
            queryset = queryset.filter(ciclo_cultivo_id=ciclo_cultivo_id)
        if parcela_id:
            queryset = queryset.filter(ciclo_cultivo__parcela_id=parcela_id)
        if fecha_cosecha_desde:
            queryset = queryset.filter(fecha_cosecha__gte=fecha_cosecha_desde)
        if fecha_cosecha_hasta:
            queryset = queryset.filter(fecha_cosecha__lte=fecha_cosecha_hasta)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset.order_by('-fecha_cosecha')

    def perform_create(self, serializer):
        # Registrar en bitácora
        cosecha = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_COSECHA',
            tabla_afectada='Cosecha',
            registro_id=cosecha.id,
            detalles=f'Cosecha registrada para ciclo {cosecha.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        cosecha = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_COSECHA',
            tabla_afectada='Cosecha',
            registro_id=cosecha.id,
            detalles=f'Cosecha actualizada para ciclo {cosecha.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class TratamientoViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Tratamientos
    T043: Gestión de tratamientos
    """
    queryset = Tratamiento.objects.all().select_related('ciclo_cultivo__cultivo__parcela', 'ciclo_cultivo__cultivo')
    serializer_class = TratamientoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        ciclo_cultivo_id = self.request.query_params.get('ciclo_cultivo_id')
        parcela_id = self.request.query_params.get('parcela_id')
        tipo_tratamiento = self.request.query_params.get('tipo_tratamiento')
        fecha_aplicacion_desde = self.request.query_params.get('fecha_aplicacion_desde')
        fecha_aplicacion_hasta = self.request.query_params.get('fecha_aplicacion_hasta')

        if ciclo_cultivo_id:
            queryset = queryset.filter(ciclo_cultivo_id=ciclo_cultivo_id)
        if parcela_id:
            queryset = queryset.filter(ciclo_cultivo__parcela_id=parcela_id)
        if tipo_tratamiento:
            queryset = queryset.filter(tipo_tratamiento=tipo_tratamiento)
        if fecha_aplicacion_desde:
            queryset = queryset.filter(fecha_aplicacion__gte=fecha_aplicacion_desde)
        if fecha_aplicacion_hasta:
            queryset = queryset.filter(fecha_aplicacion__lte=fecha_aplicacion_hasta)

        return queryset.order_by('-fecha_aplicacion')

    def perform_create(self, serializer):
        # Registrar en bitácora
        tratamiento = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_TRATAMIENTO',
            tabla_afectada='Tratamiento',
            registro_id=tratamiento.id,
            detalles=f'Tratamiento aplicado a ciclo {tratamiento.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        tratamiento = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_TRATAMIENTO',
            tabla_afectada='Tratamiento',
            registro_id=tratamiento.id,
            detalles=f'Tratamiento actualizado para ciclo {tratamiento.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class AnalisisSueloViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Análisis de Suelo
    T044: Gestión de análisis de suelo
    """
    queryset = AnalisisSuelo.objects.all().select_related('parcela')
    serializer_class = AnalisisSueloSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        fecha_analisis_desde = self.request.query_params.get('fecha_analisis_desde')
        fecha_analisis_hasta = self.request.query_params.get('fecha_analisis_hasta')
        tipo_analisis = self.request.query_params.get('tipo_analisis')

        if parcela_id:
            queryset = queryset.filter(parcela_id=parcela_id)
        if fecha_analisis_desde:
            queryset = queryset.filter(fecha_analisis__gte=fecha_analisis_desde)
        if fecha_analisis_hasta:
            queryset = queryset.filter(fecha_analisis__lte=fecha_analisis_hasta)
        if tipo_analisis:
            queryset = queryset.filter(tipo_analisis=tipo_analisis)

        return queryset.order_by('-fecha_analisis')

    def perform_create(self, serializer):
        # Registrar en bitácora
        analisis = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_ANALISIS_SUELO',
            tabla_afectada='AnalisisSuelo',
            registro_id=analisis.id,
            detalles=f'Análisis de suelo realizado para parcela {analisis.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        analisis = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_ANALISIS_SUELO',
            tabla_afectada='AnalisisSuelo',
            registro_id=analisis.id,
            detalles=f'Análisis de suelo actualizado para parcela {analisis.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class TransferenciaParcelaViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Transferencias de Parcelas
    T045: Gestión de transferencias de parcelas
    """
    queryset = TransferenciaParcela.objects.all().select_related(
        'parcela', 'socio_anterior__usuario', 'socio_nuevo__usuario', 'autorizado_por'
    )
    serializer_class = TransferenciaParcelaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        socio_anterior_id = self.request.query_params.get('socio_anterior_id')
        socio_nuevo_id = self.request.query_params.get('socio_nuevo_id')
        fecha_transferencia_desde = self.request.query_params.get('fecha_transferencia_desde')
        fecha_transferencia_hasta = self.request.query_params.get('fecha_transferencia_hasta')
        estado = self.request.query_params.get('estado')

        if parcela_id:
            queryset = queryset.filter(parcela_id=parcela_id)
        if socio_anterior_id:
            queryset = queryset.filter(socio_anterior_id=socio_anterior_id)
        if socio_nuevo_id:
            queryset = queryset.filter(socio_nuevo_id=socio_nuevo_id)
        if fecha_transferencia_desde:
            queryset = queryset.filter(fecha_transferencia__gte=fecha_transferencia_desde)
        if fecha_transferencia_hasta:
            queryset = queryset.filter(fecha_transferencia__lte=fecha_transferencia_hasta)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset.order_by('-fecha_transferencia')

    def perform_create(self, serializer):
        # Registrar en bitácora
        transferencia = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_TRANSFERENCIA_PARCELA',
            tabla_afectada='TransferenciaParcela',
            registro_id=transferencia.id,
            detalles=f'Transferencia de parcela {transferencia.parcela.nombre} de socio {transferencia.socio_anterior.usuario.ci_nit} a socio {transferencia.socio_nuevo.usuario.ci_nit}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        transferencia = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_TRANSFERENCIA_PARCELA',
            tabla_afectada='TransferenciaParcela',
            registro_id=transferencia.id,
            detalles=f'Transferencia actualizada para parcela {transferencia.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


# Endpoints específicos para CU4
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_ciclos_cultivo_avanzado(request):
    """
    CU4: Búsqueda avanzada de ciclos de cultivo
    T041: Gestión de ciclos de cultivo - Búsqueda avanzada
    """
    especie = request.query_params.get('especie', '').strip()
    estado_ciclo = request.query_params.get('estado_ciclo', '').strip()
    comunidad_id = request.query_params.get('comunidad_id')
    fecha_inicio_desde = request.query_params.get('fecha_inicio_desde')
    fecha_inicio_hasta = request.query_params.get('fecha_inicio_hasta')

    queryset = CicloCultivo.objects.select_related(
        'cultivo__parcela__socio__comunidad', 'cultivo'
    ).filter(cultivo__parcela__socio__estado='ACTIVO')

    if especie:
        queryset = queryset.filter(cultivo__especie__icontains=especie)
    if estado_ciclo:
        queryset = queryset.filter(estado=estado_ciclo)
    if comunidad_id:
        queryset = queryset.filter(cultivo__parcela__socio__comunidad_id=comunidad_id)
    if fecha_inicio_desde:
        queryset = queryset.filter(fecha_inicio__gte=fecha_inicio_desde)
    if fecha_inicio_hasta:
        queryset = queryset.filter(fecha_inicio__lte=fecha_inicio_hasta)

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    ciclos = queryset[start:end]

    serializer = CicloCultivoSerializer(ciclos, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros': {
            'especie': especie,
            'estado_ciclo': estado_ciclo,
            'comunidad_id': comunidad_id,
            'fecha_inicio_desde': fecha_inicio_desde,
            'fecha_inicio_hasta': fecha_inicio_hasta
        },
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_productividad_parcelas(request):
    """
    CU4: Reporte de productividad de parcelas
    T046: Reportes de productividad
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Estadísticas generales de cosechas
    cosechas_total = Cosecha.objects.count()
    cosechas_completadas = Cosecha.objects.filter(estado='COMPLETADA').count()
    cosechas_pendientes = Cosecha.objects.filter(estado='PENDIENTE').count()

    # Productividad por especie
    productividad_por_especie = Cultivo.objects.annotate(
        total_cosechado=Sum('ciclocultivo__cosecha__cantidad_cosechada'),
        num_ciclos=Count('ciclocultivo', distinct=True),
        num_cosechas=Count('ciclocultivo__cosecha', distinct=True)
    ).values('especie', 'total_cosechado', 'num_ciclos', 'num_cosechas').order_by('-total_cosechado')

    # Rendimiento promedio por parcela
    rendimiento_parcelas = Parcela.objects.annotate(
        total_cosechado=Sum('cultivo__ciclocultivo__cosecha__cantidad_cosechada'),
        superficie_total=F('superficie_hectareas')
    ).filter(total_cosechado__isnull=False).values(
        'nombre', 'superficie_total', 'total_cosechado'
    ).annotate(
        rendimiento_promedio=Case(
            When(superficie_total__gt=0, then=F('total_cosechado') / F('superficie_total')),
            default=0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('-rendimiento_promedio')[:20]

    # Tratamientos aplicados por mes
    tratamientos_por_mes = Tratamiento.objects.annotate(
        mes=TruncMonth('fecha_aplicacion')
    ).values('mes', 'tipo_tratamiento').annotate(
        count=Count('id')
    ).order_by('mes', 'tipo_tratamiento')[:24]

    # Análisis de suelo por tipo
    analisis_por_tipo = AnalisisSuelo.objects.values('tipo_analisis').annotate(
        count=Count('id'),
        promedio_ph=Avg('ph'),
        promedio_materia_organica=Avg('materia_organica')
    ).order_by('-count')

    return Response({
        'estadisticas_generales': {
            'cosechas_total': cosechas_total,
            'cosechas_completadas': cosechas_completadas,
            'cosechas_pendientes': cosechas_pendientes,
            'porcentaje_completadas': round((cosechas_completadas / cosechas_total * 100), 2) if cosechas_total > 0 else 0
        },
        'productividad_por_especie': list(productividad_por_especie),
        'rendimiento_parcelas_top20': list(rendimiento_parcelas),
        'tratamientos_por_mes': list(tratamientos_por_mes),
        'analisis_suelo_por_tipo': list(analisis_por_tipo)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tipos_suelo(request):
    """
    CU4: Obtener tipos de suelo disponibles
    """
    tipos_suelo = [
        'ARCILLOSO',
        'ARENAL',
        'LIMOSO',
        'FRANCO',
        'FRANCO-ARCILLOSO',
        'FRANCO-ARENAL',
        'FRANCO-LIMOSO',
        'ARCILLO-LIMOSO',
        'ARENAL-LIMOSO',
        'TURBA',
        'CALCAREO',
        'SALINO',
        'PEDREGOSO'
    ]

    return Response({
        'tipos_suelo': tipos_suelo
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_transferencia_parcela(request):
    """
    CU4: Validar transferencia de parcela
    T045: Validación de transferencias de parcelas
    """
    parcela_id = request.query_params.get('parcela_id')
    socio_nuevo_id = request.query_params.get('socio_nuevo_id')

    if not parcela_id or not socio_nuevo_id:
        return Response(
            {'error': 'Debe especificar parcela_id y socio_nuevo_id'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        parcela = Parcela.objects.get(id=parcela_id)
        socio_nuevo = Socio.objects.get(id=socio_nuevo_id)
    except (Parcela.DoesNotExist, Socio.DoesNotExist):
        return Response(
            {'error': 'Parcela o socio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    errores = []

    # Validar que el socio nuevo esté activo
    if socio_nuevo.estado != 'ACTIVO':
        errores.append('El socio nuevo debe estar activo')

    # Validar que la parcela esté activa
    if parcela.estado != 'ACTIVA':
        errores.append('La parcela debe estar activa')

    # Validar que no haya transferencias pendientes para esta parcela
    transferencias_pendientes = TransferenciaParcela.objects.filter(
        parcela=parcela,
        estado='PENDIENTE'
    ).exists()

    if transferencias_pendientes:
        errores.append('Ya existe una transferencia pendiente para esta parcela')

    # Validar que el socio nuevo no sea el mismo que el actual
    if parcela.socio_id == socio_nuevo.id:
        errores.append('El socio nuevo debe ser diferente al socio actual')

    if errores:
        return Response({
            'valido': False,
            'errores': errores
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'valido': True,
            'mensaje': 'La transferencia puede proceder',
            'detalles': {
                'parcela': parcela.nombre,
                'socio_actual': f"{parcela.socio.usuario.ci_nit} - {parcela.socio.usuario.nombres} {parcela.socio.usuario.apellidos}",
                'socio_nuevo': f"{socio_nuevo.usuario.ci_nit} - {socio_nuevo.usuario.nombres} {socio_nuevo.usuario.apellidos}"
            }
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def procesar_transferencia_parcela(request, transferencia_id):
    """
    CU4: Procesar transferencia de parcela (aprobar/rechazar)
    T045: Gestión de transferencias de parcelas
    """
    try:
        transferencia = TransferenciaParcela.objects.get(id=transferencia_id)
    except TransferenciaParcela.DoesNotExist:
        return Response(
            {'error': 'Transferencia no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    accion = request.data.get('accion')
    observaciones = request.data.get('observaciones', '')

    if accion not in ['APROBAR', 'RECHAZAR']:
        return Response(
            {'error': 'Acción debe ser APROBAR o RECHAZAR'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if accion == 'APROBAR':
        # Actualizar la parcela con el nuevo socio
        transferencia.parcela.socio = transferencia.socio_nuevo
        transferencia.parcela.save()

        transferencia.estado = 'APROBADA'
        transferencia.fecha_aprobacion = timezone.now()
        transferencia.aprobado_por = request.user
    else:
        transferencia.estado = 'RECHAZADA'

    transferencia.observaciones = observaciones
    transferencia.save()

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='PROCESAR_TRANSFERENCIA_APROBAR' if accion == 'APROBAR' else 'PROCESAR_TRANSFERENCIA_RECHAZAR',
        tabla_afectada='TransferenciaParcela',
        registro_id=transferencia.id,
        detalles=f'Transferencia {transferencia.id} procesada: {accion}',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    return Response({
        'mensaje': f'Transferencia {accion.lower()} exitosamente',
        'transferencia': TransferenciaParcelaSerializer(transferencia).data
    })


# CU6: Gestión de Roles y Permisos - Endpoints adicionales
# ========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asignar_rol_usuario(request):
    """
    CU6: Asignar rol a usuario
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    usuario_id = request.data.get('usuario_id')
    rol_id = request.data.get('rol_id')

    if not usuario_id or not rol_id:
        return Response(
            {'error': 'usuario_id y rol_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Rol.DoesNotExist:
        return Response(
            {'error': 'Rol no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verificar si ya tiene este rol
    if UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
        return Response(
            {'error': 'El usuario ya tiene asignado este rol'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Crear asignación
    usuario_rol = UsuarioRol.objects.create(usuario=usuario, rol=rol)

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='CREAR',
        tabla_afectada='usuario_rol',
        registro_id=usuario_rol.id,
        detalles={
            'rol_asignado': rol.nombre,
            'usuario_afectado': usuario.usuario,
            'asignado_por': request.user.usuario
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = UsuarioRolSerializer(usuario_rol)
    return Response({
        'mensaje': 'Rol asignado exitosamente',
        'usuario_rol': serializer.data
    }, status=status.HTTP_201_CREATED)
    """
    Debug endpoint para asignar rol a usuario
    """
    print("=" * 80)
    print("DEBUG ASIGNAR ROL - REQUEST RECEIVED")
    print("=" * 80)
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    print(f"User ID: {request.user.id if request.user.is_authenticated else 'N/A'}")
    print(f"Username: {request.user.usuario if request.user.is_authenticated else 'N/A'}")
    print(f"Is staff: {request.user.is_staff if request.user.is_authenticated else 'N/A'}")
    print(f"Is superuser: {request.user.is_superuser if request.user.is_authenticated else 'N/A'}")
    print(f"Request data: {request.data}")
    print(f"Content-Type: {request.content_type}")
    print(f"Method: {request.method}")

    # Check if user is authenticated
    if not request.user.is_authenticated:
        print("ERROR: User not authenticated")
        return Response(
            {'error': 'Usuario no autenticado'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user is staff
    if not request.user.is_staff:
        print("ERROR: User is not staff")
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    usuario_id = request.data.get('usuario_id')
    rol_id = request.data.get('rol_id')

    print(f"usuario_id: {usuario_id} (type: {type(usuario_id)})")
    print(f"rol_id: {rol_id} (type: {type(rol_id)})")

    if not usuario_id or not rol_id:
        print("ERROR: Missing usuario_id or rol_id")
        return Response(
            {'error': 'usuario_id y rol_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        print(f"Usuario found: {usuario.usuario}")
    except Usuario.DoesNotExist:
        print(f"ERROR: Usuario with ID {usuario_id} not found")
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"ERROR getting usuario: {e}")
        return Response(
            {'error': f'Error al buscar usuario: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rol = Rol.objects.get(id=rol_id)
        print(f"Rol found: {rol.nombre}")
    except Rol.DoesNotExist:
        print(f"ERROR: Rol with ID {rol_id} not found")
        return Response(
            {'error': 'Rol no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"ERROR getting rol: {e}")
        return Response(
            {'error': f'Error al buscar rol: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verificar si ya tiene este rol
    if UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
        print("ERROR: Usuario already has this rol")
        return Response(
            {'error': 'El usuario ya tiene asignado este rol'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Crear asignación
        usuario_rol = UsuarioRol.objects.create(usuario=usuario, rol=rol)
        print(f"SUCCESS: Rol asignado - UsuarioRol ID: {usuario_rol.id}")

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='usuario_rol',
            registro_id=usuario_rol.id,
            detalles={
                'rol_asignado': rol.nombre,
                'usuario_afectado': usuario.usuario,
                'asignado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        serializer = UsuarioRolSerializer(usuario_rol)
        return Response({
            'mensaje': 'Rol asignado exitosamente',
            'usuario_rol': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"ERROR creating UsuarioRol: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error al asignar rol: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quitar_rol_usuario(request):
    """
    CU6: Quitar rol a usuario
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    usuario_id = request.data.get('usuario_id')
    rol_id = request.data.get('rol_id')

    if not usuario_id or not rol_id:
        return Response(
            {'error': 'usuario_id y rol_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario_rol = UsuarioRol.objects.get(usuario=usuario, rol=rol)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Rol.DoesNotExist:
        return Response(
            {'error': 'Rol no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except UsuarioRol.DoesNotExist:
        return Response(
            {'error': 'El usuario no tiene asignado este rol'},
            status=status.HTTP_404_NOT_FOUND
        )

    # No permitir quitar roles del sistema si es el último rol del usuario
    if rol.es_sistema:
        otros_roles_usuario = UsuarioRol.objects.filter(
            usuario=usuario
        ).exclude(id=usuario_rol.id).count()

        if otros_roles_usuario == 0:
            return Response(
                {'error': 'No se puede quitar el último rol del usuario'},
                status=status.HTTP_400_BAD_REQUEST
            )

    usuario_rol_id = usuario_rol.id
    usuario_rol.delete()

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='ELIMINAR',
        tabla_afectada='usuario_rol',
        registro_id=usuario_rol_id,
        detalles={
            'rol_removido': rol.nombre,
            'usuario_afectado': usuario.usuario,
            'removido_por': request.user.usuario
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    return Response({'mensaje': 'Rol removido exitosamente'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def permisos_usuario(request, usuario_id):
    """
    CU6: Obtener permisos consolidados de un usuario
    T022: Gestión de permisos
    T034: Validación de permisos
    """
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verificar permisos (solo admin o el propio usuario)
    if not request.user.is_staff and request.user.id != usuario_id:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    roles_usuario = UsuarioRol.objects.filter(usuario=usuario).select_related('rol')

    # Consolidar permisos de todos los roles del usuario
    permisos_consolidados = {}
    modulos = [
        'usuarios', 'socios', 'parcelas', 'cultivos',
        'ciclos_cultivo', 'cosechas', 'tratamientos',
        'analisis_suelo', 'transferencias', 'reportes',
        'auditoria', 'configuracion'
    ]

    for modulo in modulos:
        permisos_modulo = {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}

        # Si el usuario es admin, tiene todos los permisos
        if usuario.is_staff or usuario.is_superuser:
            permisos_modulo = {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True}
        else:
            # Consolidar permisos de todos los roles
            for usuario_rol in roles_usuario:
                rol_permisos = usuario_rol.rol.permisos
                if modulo in rol_permisos:
                    for accion, permitido in rol_permisos[modulo].items():
                        if permitido:
                            permisos_modulo[accion] = True

        permisos_consolidados[modulo] = permisos_modulo

    return Response({
        'usuario_id': usuario.id,
        'usuario': usuario.usuario,
        'nombre_completo': usuario.get_full_name(),
        'roles': [ur.rol.nombre for ur in roles_usuario],
        'permisos': permisos_consolidados
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_permiso_usuario(request):
    """
    CU6: Validar si un usuario tiene un permiso específico
    T022: Gestión de permisos
    T034: Validación de permisos
    """
    usuario_id = request.query_params.get('usuario_id')
    modulo = request.query_params.get('modulo')
    accion = request.query_params.get('accion')

    if not usuario_id or not modulo or not accion:
        return Response(
            {'error': 'usuario_id, modulo y accion son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verificar permisos (solo admin o el propio usuario)
    if not request.user.is_staff and request.user.id != int(usuario_id):
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Verificar si el usuario tiene el permiso
    tiene_permiso = False

    if usuario.is_staff or usuario.is_superuser:
        tiene_permiso = True
    else:
        roles_usuario = UsuarioRol.objects.filter(usuario=usuario).select_related('rol')
        for usuario_rol in roles_usuario:
            if usuario_rol.rol.tiene_permiso(modulo, accion):
                tiene_permiso = True
                break

    return Response({
        'usuario_id': usuario.id,
        'usuario': usuario.usuario,
        'modulo': modulo,
        'accion': accion,
        'tiene_permiso': tiene_permiso
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_roles_permisos(request):
    """
    CU6: Reporte de roles y permisos
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    T034: Validación de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Estadísticas de roles
    total_roles = Rol.objects.count()
    roles_sistema = Rol.objects.filter(es_sistema=True).count()
    roles_personalizados = Rol.objects.filter(es_sistema=False).count()

    # Usuarios por rol
    usuarios_por_rol = Rol.objects.annotate(
        num_usuarios=Count('usuariorol')
    ).values('id', 'nombre', 'es_sistema', 'num_usuarios').order_by('-num_usuarios')

    # Roles más utilizados
    roles_mas_utilizados = list(usuarios_por_rol[:10])

    # Permisos más comunes
    permisos_comunes = {}
    modulos = [
        'usuarios', 'socios', 'parcelas', 'cultivos',
        'ciclos_cultivo', 'cosechas', 'tratamientos',
        'analisis_suelo', 'transferencias', 'reportes',
        'auditoria', 'configuracion'
    ]

    for modulo in modulos:
        permisos_modulo = {'ver': 0, 'crear': 0, 'editar': 0, 'eliminar': 0, 'aprobar': 0}
        roles_con_modulo = Rol.objects.filter(permisos__has_key=modulo)

        for rol in roles_con_modulo:
            if modulo in rol.permisos:
                for accion, permitido in rol.permisos[modulo].items():
                    if permitido:
                        permisos_modulo[accion] += 1

        permisos_comunes[modulo] = permisos_modulo

    # Usuarios sin roles asignados
    usuarios_sin_roles = Usuario.objects.exclude(
        id__in=UsuarioRol.objects.values_list('usuario_id', flat=True)
    ).count()

    return Response({
        'estadisticas_generales': {
            'total_roles': total_roles,
            'roles_sistema': roles_sistema,
            'roles_personalizados': roles_personalizados,
            'usuarios_sin_roles': usuarios_sin_roles
        },
        'usuarios_por_rol': list(usuarios_por_rol),
        'roles_mas_utilizados': roles_mas_utilizados,
        'permisos_comunes': permisos_comunes
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_rol_personalizado(request):
    """
    CU6: Crear rol personalizado con permisos específicos
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    nombre = request.data.get('nombre')
    descripcion = request.data.get('descripcion', '')
    permisos = request.data.get('permisos', {})

    if not nombre:
        return Response(
            {'error': 'El nombre del rol es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verificar que el nombre no exista
    if Rol.objects.filter(nombre__iexact=nombre).exists():
        return Response(
            {'error': 'Ya existe un rol con este nombre'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Crear rol personalizado
    rol = Rol.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        permisos=permisos,
        es_sistema=False
    )

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='CREAR',
        tabla_afectada='rol',
        registro_id=rol.id,
        detalles={
            'tipo_rol': 'personalizado',
            'creado_por': request.user.usuario
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = RolSerializer(rol)
    return Response({
        'mensaje': 'Rol personalizado creado exitosamente',
        'rol': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_roles_avanzado(request):
    """
    CU6: Búsqueda avanzada de roles
    T012: Gestión de usuarios y roles
    """
    nombre = request.query_params.get('nombre', '').strip()
    es_sistema = request.query_params.get('es_sistema')
    modulo_permiso = request.query_params.get('modulo_permiso')
    accion_permiso = request.query_params.get('accion_permiso')

    queryset = Rol.objects.all()

    if nombre:
        queryset = queryset.filter(nombre__icontains=nombre)

    if es_sistema is not None:
        es_sistema_bool = es_sistema.lower() == 'true'
        queryset = queryset.filter(es_sistema=es_sistema_bool)

    if modulo_permiso and accion_permiso:
        # Filtrar roles que tienen un permiso específico
        queryset = queryset.filter(
            permisos__has_key=modulo_permiso
        ).filter(
            **{f'permisos__{modulo_permiso}__{accion_permiso}': True}
        )

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    roles = queryset[start:end]

    serializer = RolSerializer(roles, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros': {
            'nombre': nombre,
            'es_sistema': es_sistema,
            'modulo_permiso': modulo_permiso,
            'accion_permiso': accion_permiso
        },
        'results': serializer.data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def debug_update_socio(request, socio_id):
    """
    Debug endpoint to check permissions and session for socio update
    """
    print("=" * 80)
    print("DEBUG UPDATE SOCIO - REQUEST RECEIVED")
    print("=" * 80)
    print(f"Socio ID: {socio_id}")
    print(f"Method: {request.method}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    print(f"User ID: {request.user.id if request.user.is_authenticated else 'N/A'}")
    print(f"Username: {request.user.usuario if request.user.is_authenticated else 'N/A'}")
    print(f"Is staff: {request.user.is_staff if request.user.is_authenticated else 'N/A'}")
    print(f"Is superuser: {request.user.is_superuser if request.user.is_authenticated else 'N/A'}")
    print(f"Session key: {request.session.session_key}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Content-Type: {request.content_type}")

    # Check if user is authenticated
    if not request.user.is_authenticated:
        print("ERROR: User not authenticated")
        return Response(
            {'error': 'Usuario no autenticado'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user is staff
    if not request.user.is_staff:
        print("ERROR: User is not staff")
        return Response(
            {'error': 'Permisos insuficientes - no es staff'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if socio exists
    try:
        socio = Socio.objects.select_related('usuario').get(id=socio_id)
        print(f"Socio found: {socio.usuario.ci_nit} - {socio.usuario.nombres} {socio.usuario.apellidos}")
    except Socio.DoesNotExist:
        print(f"ERROR: Socio with ID {socio_id} not found")
        return Response(
            {'error': 'Socio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check CSRF token
    csrf_token = request.META.get('HTTP_X_CSRFTOKEN', 'Not found')
    print(f"CSRF token from header: {csrf_token}")

    # Check session data
    session_data = request.session._session_cache if hasattr(request.session, '_session_cache') else 'No cache'
    print(f"Session data: {session_data}")

    # Try to update the socio (similar to the real update)
    try:
        if request.content_type == 'application/json':
            data = request.data
            print(f"Request data: {data}")

            # Update socio fields
            socio_fields = ['telefono', 'direccion', 'fecha_nacimiento', 'sexo', 'estado_civil', 'fecha_ingreso', 'estado']
            for field in socio_fields:
                if field in data:
                    setattr(socio, field, data[field])

            # Update usuario fields if provided
            if 'usuario' in data:
                usuario_data = data['usuario']
                usuario_fields = ['usuario', 'nombres', 'apellidos', 'ci_nit', 'email', 'telefono', 'estado']
                for field in usuario_fields:
                    if field in usuario_data:
                        setattr(socio.usuario, field, usuario_data[field])

            socio.save()
            socio.usuario.save()

            print("SUCCESS: Socio updated successfully")
            serializer = SocioSerializer(socio)
            return Response(serializer.data)

        else:
            print("ERROR: Content type is not JSON")
            return Response(
                {'error': 'Content type debe ser application/json'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        print(f"ERROR during update: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_session_status(request):
    """
    Debug endpoint for detailed session information
    """
    user = request.user
    session_key = request.session.session_key

    # Get all active sessions for debugging
    user_sessions = []
    total_sessions = 0

    for session in Session.objects.all():
        session_data = session.get_decoded()
        if session_data.get('_auth_user_id') == str(user.id):
            total_sessions += 1
            user_sessions.append({
                'session_key': session.session_key,
                'expire_date': session.expire_date,
                'is_current': session.session_key == session_key
            })

    return Response({
        'debug_info': {
            'timestamp': timezone.now(),
            'request_method': request.method,
            'request_path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'remote_addr': request.META.get('REMOTE_ADDR'),
            'is_secure': request.is_secure(),
            'session_engine': request.session.__class__.__name__,
        },
        'session_info': {
            'session_key': session_key,
            'session_expiry': request.session.get_expiry_date(),
            'session_age': (timezone.now() - request.session.get('created_at', timezone.now())).total_seconds() if request.session.get('created_at') else None,
            'total_user_sessions': total_sessions,
            'user_sessions': user_sessions[:5]  # Limit to first 5 for brevity
        },
        'user_info': {
            'id': user.id,
            'username': user.usuario,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'last_login': user.last_login,
            'date_joined': user.date_joined
        },
        'authentication_status': {
            'is_authenticated': True,
            'backend': getattr(user, 'backend', None),
            'auth_time': getattr(request.session, '_auth_user_time', None)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_parcelas_avanzado(request):
    """
    CU4: Búsqueda avanzada de parcelas
    T016: Búsquedas y filtros de parcelas
    """
    queryset = Parcela.objects.select_related('socio__usuario')

    # Filtros de búsqueda
    nombre = request.query_params.get('nombre', '').strip()
    socio_id = request.query_params.get('socio_id', '').strip()
    socio_nombre = request.query_params.get('socio_nombre', '').strip()
    tipo_suelo = request.query_params.get('tipo_suelo', '').strip()
    estado = request.query_params.get('estado', '').strip()
    ubicacion = request.query_params.get('ubicacion', '').strip()
    superficie_min = request.query_params.get('superficie_min', '').strip()
    superficie_max = request.query_params.get('superficie_max', '').strip()
    fecha_desde = request.query_params.get('fecha_desde', '').strip()
    fecha_hasta = request.query_params.get('fecha_hasta', '').strip()

    # Aplicar filtros
    if nombre:
        queryset = queryset.filter(nombre__icontains=nombre)
    if socio_id:
        queryset = queryset.filter(socio_id=socio_id)
    if socio_nombre:
        queryset = queryset.filter(
            Q(socio__usuario__nombres__icontains=socio_nombre) |
            Q(socio__usuario__apellidos__icontains=socio_nombre)
        )
    if tipo_suelo:
        queryset = queryset.filter(tipo_suelo__icontains=tipo_suelo)
    if estado:
        queryset = queryset.filter(estado=estado)
    if ubicacion:
        queryset = queryset.filter(ubicacion__icontains=ubicacion)
    if superficie_min:
        try:
            superficie_min_val = float(superficie_min)
            queryset = queryset.filter(superficie_hectareas__gte=superficie_min_val)
        except ValueError:
            pass
    if superficie_max:
        try:
            superficie_max_val = float(superficie_max)
            queryset = queryset.filter(superficie_hectareas__lte=superficie_max_val)
        except ValueError:
            pass
    if fecha_desde:
        queryset = queryset.filter(creado_en__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(creado_en__lte=fecha_hasta)

    # Paginación básica
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    parcelas = queryset[start:end]

    serializer = ParcelaSerializer(parcelas, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'results': serializer.data
    })


# CU7: Gestión de Semillas
# ========================

class SemillaPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class SemillaViewSet(viewsets.ModelViewSet):
    """
    CU7: ViewSet para gestión completa de semillas del inventario
    T-40: Implementar el catálogo de inventario de Semillas
    T-41: CRUD de Semillas (especie, variedad, cantidad, vencimiento, PG%)
    """
    queryset = Semilla.objects.all()
    serializer_class = SemillaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['especie', 'variedad', 'cantidad', 'fecha_vencimiento', 'porcentaje_germinacion', 'creado_en']
    ordering = ['-creado_en']  # Orden por defecto
    pagination_class = SemillaPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros de búsqueda
        especie = self.request.query_params.get('especie', '').strip()
        variedad = self.request.query_params.get('variedad', '').strip()
        estado = self.request.query_params.get('estado', '').strip()
        proveedor = self.request.query_params.get('proveedor', '').strip()
        lote = self.request.query_params.get('lote', '').strip()
        ubicacion = self.request.query_params.get('ubicacion', '').strip()
        fecha_vencimiento_desde = self.request.query_params.get('fecha_vencimiento_desde')
        fecha_vencimiento_hasta = self.request.query_params.get('fecha_vencimiento_hasta')
        porcentaje_germinacion_min = self.request.query_params.get('pg_min')
        porcentaje_germinacion_max = self.request.query_params.get('pg_max')

        if especie:
            queryset = queryset.filter(especie__icontains=especie)
        if variedad:
            queryset = queryset.filter(variedad__icontains=variedad)
        if estado:
            queryset = queryset.filter(estado=estado)
        if proveedor:
            queryset = queryset.filter(proveedor__icontains=proveedor)
        if lote:
            queryset = queryset.filter(lote__icontains=lote)
        if ubicacion:
            queryset = queryset.filter(ubicacion_almacen__icontains=ubicacion)
        if fecha_vencimiento_desde:
            queryset = queryset.filter(fecha_vencimiento__gte=fecha_vencimiento_desde)
        if fecha_vencimiento_hasta:
            queryset = queryset.filter(fecha_vencimiento__lte=fecha_vencimiento_hasta)
        if porcentaje_germinacion_min:
            queryset = queryset.filter(porcentaje_germinacion__gte=porcentaje_germinacion_min)
        if porcentaje_germinacion_max:
            queryset = queryset.filter(porcentaje_germinacion__lte=porcentaje_germinacion_max)

        return queryset

    def perform_create(self, serializer):
        # Registrar en bitácora
        semilla = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_SEMILLA',
            tabla_afectada='Semilla',
            registro_id=semilla.id,
            detalles=f'Semilla creada: {semilla.especie} {semilla.variedad or ""}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        semilla = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_SEMILLA',
            tabla_afectada='Semilla',
            registro_id=semilla.id,
            detalles=f'Semilla actualizada: {semilla.especie} {semilla.variedad or ""}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_destroy(self, instance):
        # Registrar en bitácora antes de eliminar
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR_SEMILLA',
            tabla_afectada='Semilla',
            registro_id=instance.id,
            detalles=f'Semilla eliminada: {instance.especie} {instance.variedad or ""}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def actualizar_cantidad(self, request, pk=None):
        """
        CU7: Actualizar cantidad de semilla (entrada/salida de inventario)
        """
        semilla = self.get_object()
        cantidad_cambio = request.data.get('cantidad_cambio')
        motivo = request.data.get('motivo', '').strip()

        if cantidad_cambio is None:
            return Response(
                {'error': 'cantidad_cambio es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cantidad_cambio = Decimal(str(cantidad_cambio))
        except (ValueError, TypeError):
            return Response(
                {'error': 'cantidad_cambio debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nueva_cantidad = semilla.cantidad + cantidad_cambio

        if nueva_cantidad < 0:
            return Response(
                {'error': 'La cantidad resultante no puede ser negativa'},
                status=status.HTTP_400_BAD_REQUEST
            )

        semilla.cantidad = nueva_cantidad
        semilla.save()

        # Registrar en bitácora
        tipo_movimiento = 'ENTRADA' if cantidad_cambio > 0 else 'SALIDA'
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion=f'MOVIMIENTO_INVENTARIO_{tipo_movimiento}',
            tabla_afectada='Semilla',
            registro_id=semilla.id,
            detalles={
                'tipo_movimiento': tipo_movimiento,
                'cantidad_cambio': float(cantidad_cambio),
                'cantidad_anterior': float(semilla.cantidad - cantidad_cambio),
                'cantidad_nueva': float(semilla.cantidad),
                'motivo': motivo
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        serializer = self.get_serializer(semilla)
        return Response({
            'mensaje': f'Cantidad actualizada exitosamente',
            'tipo_movimiento': tipo_movimiento,
            'cantidad_cambio': cantidad_cambio,
            'semilla': serializer.data
        })

    @action(detail=True, methods=['post'])
    def marcar_vencida(self, request, pk=None):
        """
        CU7: Marcar semilla como vencida
        """
        semilla = self.get_object()

        if semilla.estado == 'VENCIDA':
            return Response(
                {'error': 'La semilla ya está marcada como vencida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        semilla.estado = 'VENCIDA'
        # Usar update para evitar que save() sobrescriba el estado
        Semilla.objects.filter(pk=semilla.pk).update(estado='VENCIDA')

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='MARCAR_SEMILLA_VENCIDA',
            tabla_afectada='Semilla',
            registro_id=semilla.id,
            detalles=f'Semilla marcada como vencida: {semilla.especie} {semilla.variedad or ""}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Refrescar el objeto desde BD
        semilla.refresh_from_db()

        serializer = self.get_serializer(semilla)
        return Response({
            'mensaje': 'Semilla marcada como vencida exitosamente',
            'semilla': serializer.data
        })

    @action(detail=False, methods=['get'])
    def inventario_bajo(self, request):
        """
        CU7: Obtener semillas con inventario bajo
        """
        limite = float(request.query_params.get('limite', 10))  # kg por defecto

        semillas = self.get_queryset().filter(
            cantidad__lte=limite,
            estado='DISPONIBLE'
        )

        serializer = self.get_serializer(semillas, many=True)
        return Response({
            'count': semillas.count(),
            'limite': limite,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def proximas_vencer(self, request):
        """
        CU7: Obtener semillas próximas a vencer
        """
        dias = int(request.query_params.get('dias', 30))

        # Si dias=0, incluir semillas vencidas y las que vencen hoy
        if dias == 0:
            semillas = self.get_queryset().filter(
                estado__in=['DISPONIBLE', 'VENCIDA']
            )
        else:
            semillas = self.get_queryset().filter(
                estado='DISPONIBLE'
            )

        # Filtrar las que están próximas a vencer o vencidas
        proximas_vencer = []
        for semilla in semillas:
            if dias == 0:
                # Para dias=0, incluir vencidas y las que vencen hoy
                if semilla.esta_vencida() or semilla.esta_proxima_vencer(0):
                    proximas_vencer.append(semilla)
            else:
                # Para otros días, usar la lógica normal
                if semilla.esta_proxima_vencer(dias):
                    proximas_vencer.append(semilla)

        serializer = self.get_serializer(proximas_vencer, many=True)
        return Response({
            'count': len(proximas_vencer),
            'dias': dias,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """
        CU7: Obtener semillas vencidas
        """
        semillas = self.get_queryset().filter(
            estado='VENCIDA'
        )

        serializer = self.get_serializer(semillas, many=True)
        return Response({
            'count': semillas.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def reporte_inventario(self, request):
        """
        CU7: Reporte general del inventario de semillas
        """
        from django.db.models import Sum, Count, Avg

        # Estadísticas generales
        total_semillas = Semilla.objects.count()
        semillas_disponibles = Semilla.objects.filter(estado='DISPONIBLE').count()
        semillas_agotadas = Semilla.objects.filter(estado='AGOTADO').count()
        semillas_vencidas = Semilla.objects.filter(estado='VENCIDA').count()
        semillas_reservadas = Semilla.objects.filter(estado='RESERVADA').count()

        # Valor total del inventario
        valor_total = Semilla.objects.filter(
            estado='DISPONIBLE'
        ).aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField())
        )['total'] or 0

        # Cantidad total por especie
        cantidad_por_especie = Semilla.objects.values('especie').annotate(
            total_cantidad=Sum('cantidad'),
            num_variedades=Count('id')
        ).order_by('-total_cantidad')[:10]

        # Semillas por proveedor
        semillas_por_proveedor = Semilla.objects.values('proveedor').annotate(
            num_semillas=Count('id'),
            total_cantidad=Sum('cantidad')
        ).exclude(proveedor__isnull=True).order_by('-num_semillas')[:10]

        # Promedio de porcentaje de germinación
        promedio_pg = Semilla.objects.filter(
            estado='DISPONIBLE'
        ).aggregate(avg_pg=Avg('porcentaje_germinacion'))['avg_pg'] or 0

        return Response({
            'resumen': {
                'total_semillas': total_semillas,
                'semillas_disponibles': semillas_disponibles,
                'semillas_agotadas': semillas_agotadas,
                'semillas_vencidas': semillas_vencidas,
                'semillas_reservadas': semillas_reservadas,
                'valor_total_inventario': round(float(valor_total), 2),
                'promedio_porcentaje_germinacion': round(float(promedio_pg), 2)
            },
            'cantidad_por_especie': list(cantidad_por_especie),
            'semillas_por_proveedor': list(semillas_por_proveedor)
        })


# CU8: Gestión de Insumos Agrícolas
# ==================================

class PesticidaPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class PesticidaViewSet(viewsets.ModelViewSet):
    """
    CU8: ViewSet para gestión completa de pesticidas del inventario
    T-42: Gestión de Inventario de Pesticidas
    """
    queryset = Pesticida.objects.all()
    serializer_class = PesticidaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['nombre_comercial', 'tipo_pesticida', 'cantidad', 'fecha_vencimiento', 'creado_en']
    ordering = ['-creado_en']
    pagination_class = PesticidaPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros de búsqueda
        nombre = self.request.query_params.get('nombre', '').strip()
        tipo = self.request.query_params.get('tipo', '').strip()
        estado = self.request.query_params.get('estado', '').strip()
        proveedor = self.request.query_params.get('proveedor', '').strip()
        lote = self.request.query_params.get('lote', '').strip()
        ubicacion = self.request.query_params.get('ubicacion', '').strip()
        fecha_vencimiento_desde = self.request.query_params.get('fecha_vencimiento_desde')
        fecha_vencimiento_hasta = self.request.query_params.get('fecha_vencimiento_hasta')

        if nombre:
            queryset = queryset.filter(nombre_comercial__icontains=nombre)
        if tipo:
            queryset = queryset.filter(tipo_pesticida=tipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if proveedor:
            queryset = queryset.filter(proveedor__icontains=proveedor)
        if lote:
            queryset = queryset.filter(lote__icontains=lote)
        if ubicacion:
            queryset = queryset.filter(ubicacion_almacen__icontains=ubicacion)
        if fecha_vencimiento_desde:
            queryset = queryset.filter(fecha_vencimiento__gte=fecha_vencimiento_desde)
        if fecha_vencimiento_hasta:
            queryset = queryset.filter(fecha_vencimiento__lte=fecha_vencimiento_hasta)

        return queryset

    def perform_create(self, serializer):
        pesticida = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_PESTICIDA',
            tabla_afectada='Pesticida',
            registro_id=pesticida.id,
            detalles=f'Pesticida creado: {pesticida.nombre_comercial}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        pesticida = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_PESTICIDA',
            tabla_afectada='Pesticida',
            registro_id=pesticida.id,
            detalles=f'Pesticida actualizado: {pesticida.nombre_comercial}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_destroy(self, instance):
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR_PESTICIDA',
            tabla_afectada='Pesticida',
            registro_id=instance.id,
            detalles=f'Pesticida eliminado: {instance.nombre_comercial}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def actualizar_cantidad(self, request, pk=None):
        """Actualizar cantidad de pesticida"""
        pesticida = self.get_object()
        cantidad_cambio = request.data.get('cantidad_cambio')
        motivo = request.data.get('motivo', '').strip()

        if cantidad_cambio is None:
            return Response(
                {'error': 'cantidad_cambio es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cantidad_cambio = Decimal(str(cantidad_cambio))
        except (ValueError, TypeError):
            return Response(
                {'error': 'cantidad_cambio debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nueva_cantidad = pesticida.cantidad + cantidad_cambio
        if nueva_cantidad < 0:
            return Response(
                {'error': 'La cantidad resultante no puede ser negativa'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pesticida.cantidad = nueva_cantidad
        pesticida.save()

        tipo_movimiento = 'ENTRADA' if cantidad_cambio > 0 else 'SALIDA'
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion=f'MOVIMIENTO_INVENTARIO_PESTICIDA_{tipo_movimiento}',
            tabla_afectada='Pesticida',
            registro_id=pesticida.id,
            detalles={
                'tipo_movimiento': tipo_movimiento,
                'cantidad_cambio': float(cantidad_cambio),
                'cantidad_anterior': float(pesticida.cantidad - cantidad_cambio),
                'cantidad_nueva': float(pesticida.cantidad),
                'motivo': motivo
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        serializer = self.get_serializer(pesticida)
        return Response({
            'mensaje': 'Cantidad actualizada exitosamente',
            'tipo_movimiento': tipo_movimiento,
            'cantidad_cambio': cantidad_cambio,
            'pesticida': serializer.data
        })

    @action(detail=True, methods=['post'])
    def marcar_vencido(self, request, pk=None):
        """Marcar pesticida como vencido"""
        pesticida = self.get_object()

        if pesticida.estado == 'VENCIDO':
            return Response(
                {'error': 'El pesticida ya está marcado como vencido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pesticida.estado = 'VENCIDO'
        Pesticida.objects.filter(pk=pesticida.pk).update(estado='VENCIDO')

        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='MARCAR_PESTICIDA_VENCIDO',
            tabla_afectada='Pesticida',
            registro_id=pesticida.id,
            detalles=f'Pesticida marcado como vencido: {pesticida.nombre_comercial}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        pesticida.refresh_from_db()
        serializer = self.get_serializer(pesticida)
        return Response({
            'mensaje': 'Pesticida marcado como vencido exitosamente',
            'pesticida': serializer.data
        })

    @action(detail=False, methods=['get'])
    def proximos_vencer(self, request):
        """Obtener pesticidas próximos a vencer"""
        dias = int(request.query_params.get('dias', 30))

        proximos_vencer = []
        for pesticida in self.get_queryset().filter(estado='DISPONIBLE'):
            if pesticida.esta_proximo_vencer(dias):
                proximos_vencer.append(pesticida)

        serializer = self.get_serializer(proximos_vencer, many=True)
        return Response({
            'count': len(proximos_vencer),
            'dias': dias,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Obtener pesticidas vencidos"""
        pesticidas = self.get_queryset().filter(estado='VENCIDO')
        serializer = self.get_serializer(pesticidas, many=True)
        return Response({
            'count': pesticidas.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def reporte_inventario(self, request):
        """Reporte general del inventario de pesticidas"""
        from django.db.models import Sum, Count, Avg

        total_pesticidas = Pesticida.objects.count()
        pesticidas_disponibles = Pesticida.objects.filter(estado='DISPONIBLE').count()
        pesticidas_agotados = Pesticida.objects.filter(estado='AGOTADO').count()
        pesticidas_vencidos = Pesticida.objects.filter(estado='VENCIDO').count()

        valor_total = Pesticida.objects.filter(estado='DISPONIBLE').aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField())
        )['total'] or 0

        cantidad_por_tipo = Pesticida.objects.values('tipo_pesticida').annotate(
            total_cantidad=Sum('cantidad'),
            num_pesticidas=Count('id')
        ).order_by('-total_cantidad')

        pesticidas_por_proveedor = Pesticida.objects.values('proveedor').annotate(
            num_pesticidas=Count('id'),
            total_cantidad=Sum('cantidad')
        ).exclude(proveedor__isnull=True).order_by('-num_pesticidas')[:10]

        return Response({
            'resumen': {
                'total_pesticidas': total_pesticidas,
                'pesticidas_disponibles': pesticidas_disponibles,
                'pesticidas_agotados': pesticidas_agotados,
                'pesticidas_vencidos': pesticidas_vencidos,
                'valor_total_inventario': round(float(valor_total), 2)
            },
            'cantidad_por_tipo': list(cantidad_por_tipo),
            'pesticidas_por_proveedor': list(pesticidas_por_proveedor)
        })


class FertilizantePagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class FertilizanteViewSet(viewsets.ModelViewSet):
    """
    CU8: ViewSet para gestión completa de fertilizantes del inventario
    T-45: Gestión de Inventario de Fertilizantes
    """
    queryset = Fertilizante.objects.all()
    serializer_class = FertilizanteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['nombre_comercial', 'tipo_fertilizante', 'cantidad', 'fecha_vencimiento', 'creado_en']
    ordering = ['-creado_en']
    pagination_class = FertilizantePagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros de búsqueda
        nombre = self.request.query_params.get('nombre', '').strip()
        tipo = self.request.query_params.get('tipo', '').strip()
        estado = self.request.query_params.get('estado', '').strip()
        proveedor = self.request.query_params.get('proveedor', '').strip()
        lote = self.request.query_params.get('lote', '').strip()
        ubicacion = self.request.query_params.get('ubicacion', '').strip()
        fecha_vencimiento_desde = self.request.query_params.get('fecha_vencimiento_desde')
        fecha_vencimiento_hasta = self.request.query_params.get('fecha_vencimiento_hasta')

        if nombre:
            queryset = queryset.filter(nombre_comercial__icontains=nombre)
        if tipo:
            queryset = queryset.filter(tipo_fertilizante=tipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if proveedor:
            queryset = queryset.filter(proveedor__icontains=proveedor)
        if lote:
            queryset = queryset.filter(lote__icontains=lote)
        if ubicacion:
            queryset = queryset.filter(ubicacion_almacen__icontains=ubicacion)
        if fecha_vencimiento_desde:
            queryset = queryset.filter(fecha_vencimiento__gte=fecha_vencimiento_desde)
        if fecha_vencimiento_hasta:
            queryset = queryset.filter(fecha_vencimiento__lte=fecha_vencimiento_hasta)

        return queryset

    def perform_create(self, serializer):
        fertilizante = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_FERTILIZANTE',
            tabla_afectada='Fertilizante',
            registro_id=fertilizante.id,
            detalles=f'Fertilizante creado: {fertilizante.nombre_comercial}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        fertilizante = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_FERTILIZANTE',
            tabla_afectada='Fertilizante',
            registro_id=fertilizante.id,
            detalles=f'Fertilizante actualizado: {fertilizante.nombre_comercial}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_destroy(self, instance):
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR_FERTILIZANTE',
            tabla_afectada='Fertilizante',
            registro_id=instance.id,
            detalles=f'Fertilizante eliminado: {instance.nombre_comercial}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def actualizar_cantidad(self, request, pk=None):
        """Actualizar cantidad de fertilizante"""
        fertilizante = self.get_object()
        cantidad_cambio = request.data.get('cantidad_cambio')
        motivo = request.data.get('motivo', '').strip()

        if cantidad_cambio is None:
            return Response(
                {'error': 'cantidad_cambio es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cantidad_cambio = Decimal(str(cantidad_cambio))
        except (ValueError, TypeError):
            return Response(
                {'error': 'cantidad_cambio debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nueva_cantidad = fertilizante.cantidad + cantidad_cambio
        if nueva_cantidad < 0:
            return Response(
                {'error': 'La cantidad resultante no puede ser negativa'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fertilizante.cantidad = nueva_cantidad
        fertilizante.save()

        tipo_movimiento = 'ENTRADA' if cantidad_cambio > 0 else 'SALIDA'
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion=f'MOVIMIENTO_INVENTARIO_FERTILIZANTE_{tipo_movimiento}',
            tabla_afectada='Fertilizante',
            registro_id=fertilizante.id,
            detalles={
                'tipo_movimiento': tipo_movimiento,
                'cantidad_cambio': float(cantidad_cambio),
                'cantidad_anterior': float(fertilizante.cantidad - cantidad_cambio),
                'cantidad_nueva': float(fertilizante.cantidad),
                'motivo': motivo
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        serializer = self.get_serializer(fertilizante)
        return Response({
            'mensaje': 'Cantidad actualizada exitosamente',
            'tipo_movimiento': tipo_movimiento,
            'cantidad_cambio': cantidad_cambio,
            'fertilizante': serializer.data
        })

    @action(detail=True, methods=['post'])
    def marcar_vencido(self, request, pk=None):
        """Marcar fertilizante como vencido"""
        fertilizante = self.get_object()

        if fertilizante.estado == 'VENCIDO':
            return Response(
                {'error': 'El fertilizante ya está marcado como vencido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fertilizante.estado = 'VENCIDO'
        Fertilizante.objects.filter(pk=fertilizante.pk).update(estado='VENCIDO')

        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='MARCAR_FERTILIZANTE_VENCIDO',
            tabla_afectada='Fertilizante',
            registro_id=fertilizante.id,
            detalles=f'Fertilizante marcado como vencido: {fertilizante.nombre_comercial}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        fertilizante.refresh_from_db()
        serializer = self.get_serializer(fertilizante)
        return Response({
            'mensaje': 'Fertilizante marcado como vencido exitosamente',
            'fertilizante': serializer.data
        })

    @action(detail=False, methods=['get'])
    def proximos_vencer(self, request):
        """Obtener fertilizantes próximos a vencer"""
        dias = int(request.query_params.get('dias', 30))

        proximos_vencer = []
        for fertilizante in self.get_queryset().filter(estado='DISPONIBLE'):
            if fertilizante.esta_proximo_vencer(dias):
                proximos_vencer.append(fertilizante)

        serializer = self.get_serializer(proximos_vencer, many=True)
        return Response({
            'count': len(proximos_vencer),
            'dias': dias,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Obtener fertilizantes vencidos"""
        fertilizantes = self.get_queryset().filter(estado='VENCIDO')
        serializer = self.get_serializer(fertilizantes, many=True)
        return Response({
            'count': fertilizantes.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def reporte_inventario(self, request):
        """Reporte general del inventario de fertilizantes"""
        from django.db.models import Sum, Count, Avg

        total_fertilizantes = Fertilizante.objects.count()
        fertilizantes_disponibles = Fertilizante.objects.filter(estado='DISPONIBLE').count()
        fertilizantes_agotados = Fertilizante.objects.filter(estado='AGOTADO').count()
        fertilizantes_vencidos = Fertilizante.objects.filter(estado='VENCIDO').count()

        valor_total = Fertilizante.objects.filter(estado='DISPONIBLE').aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField())
        )['total'] or 0

        cantidad_por_tipo = Fertilizante.objects.values('tipo_fertilizante').annotate(
            total_cantidad=Sum('cantidad'),
            num_fertilizantes=Count('id')
        ).order_by('-total_cantidad')

        fertilizantes_por_proveedor = Fertilizante.objects.values('proveedor').annotate(
            num_fertilizantes=Count('id'),
            total_cantidad=Sum('cantidad')
        ).exclude(proveedor__isnull=True).order_by('-num_fertilizantes')[:10]

        return Response({
            'resumen': {
                'total_fertilizantes': total_fertilizantes,
                'fertilizantes_disponibles': fertilizantes_disponibles,
                'fertilizantes_agotados': fertilizantes_agotados,
                'fertilizantes_vencidos': fertilizantes_vencidos,
                'valor_total_inventario': round(float(valor_total), 2)
            },
            'cantidad_por_tipo': list(cantidad_por_tipo),
            'fertilizantes_por_proveedor': list(fertilizantes_por_proveedor)
        })



# ============================================================================
# CU9: GESTIÓN DE CAMPAÑAS AGRÍCOLAS - VIEWSETS Y VISTAS
# T036: Gestión de campañas (crear, editar, eliminar)
# T037: Relación entre campaña y socios/parcelas
# ============================================================================

class CampaignViewSet(viewsets.ModelViewSet):
    """
    CU9: ViewSet para gestión completa de campañas agrícolas
    T036: CRUD completo (list, create, retrieve, update, destroy)
    T037: Endpoints para asignar/desasignar socios y parcelas
    """
    queryset = Campaign.objects.all().select_related('responsable').prefetch_related(
        'socios_asignados__socio__usuario',
        'parcelas__parcela__socio__usuario'
    )
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Usar serializer simplificado para list, completo para retrieve"""
        if self.action == 'list':
            return CampaignListSerializer
        return CampaignSerializer

    def get_queryset(self):
        """Filtros opcionales por query params"""
        queryset = super().get_queryset()
        
        # Filtros
        estado = self.request.query_params.get('estado')
        fecha_inicio_desde = self.request.query_params.get('fecha_inicio_desde')
        fecha_inicio_hasta = self.request.query_params.get('fecha_inicio_hasta')
        responsable_id = self.request.query_params.get('responsable_id')
        nombre = self.request.query_params.get('nombre')

        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_inicio_desde:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio_desde)
        if fecha_inicio_hasta:
            queryset = queryset.filter(fecha_inicio__lte=fecha_inicio_hasta)
        if responsable_id:
            queryset = queryset.filter(responsable_id=responsable_id)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

        return queryset.order_by('-fecha_inicio')

    def perform_create(self, serializer):
        """Registrar creación en bitácora"""
        campaign = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='campaign',
            registro_id=campaign.id,
            detalles={
                'campaign_nombre': campaign.nombre,
                'creado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        """Registrar actualización en bitácora"""
        campaign = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='campaign',
            registro_id=campaign.id,
            detalles={
                'campaign_nombre': campaign.nombre,
                'actualizado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def destroy(self, request, *args, **kwargs):
        """
        T036: Validar que no se elimine campaña con labores o cosechas asociadas
        """
        campaign = self.get_object()

        # Validar que puede ser eliminada
        if not campaign.puede_eliminar():
            return Response({
                'error': 'No se puede eliminar la campaña porque tiene labores o cosechas asociadas'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Registrar eliminación en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ELIMINAR',
            tabla_afectada='campaign',
            registro_id=campaign.id,
            detalles={
                'campaign_nombre': campaign.nombre,
                'eliminado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        campaign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def assign_partner(self, request, pk=None):
        """
        T037: Asignar socio a campaña
        POST /api/campaigns/{id}/assign_partner/
        """
        campaign = self.get_object()
        socio_id = request.data.get('socio_id')
        rol = request.data.get('rol', 'PRODUCTOR')
        fecha_asignacion = request.data.get('fecha_asignacion', timezone.now().date())
        observaciones = request.data.get('observaciones', '')

        if not socio_id:
            return Response({
                'error': 'socio_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            socio = Socio.objects.get(id=socio_id)
        except Socio.DoesNotExist:
            return Response({
                'error': 'Socio no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar si ya está asignado
        if CampaignPartner.objects.filter(campaign=campaign, socio=socio).exists():
            return Response({
                'error': 'El socio ya está asignado a esta campaña'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Crear asignación
        serializer = CampaignPartnerSerializer(data={
            'campaign': campaign.id,
            'socio': socio.id,
            'rol': rol,
            'fecha_asignacion': fecha_asignacion,
            'observaciones': observaciones
        })

        if serializer.is_valid():
            assignment = serializer.save()

            # Registrar en bitácora
            BitacoraAuditoria.objects.create(
                usuario=request.user,
                accion='CREAR',
                tabla_afectada='campaign_partner',
                registro_id=assignment.id,
                detalles={
                    'campaign': campaign.nombre,
                    'socio': socio.usuario.get_full_name(),
                    'rol': rol,
                    'asignado_por': request.user.usuario
                },
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_partner(self, request, pk=None):
        """
        T037: Desasignar socio de campaña
        POST /api/campaigns/{id}/remove_partner/
        """
        campaign = self.get_object()
        socio_id = request.data.get('socio_id')

        if not socio_id:
            return Response({
                'error': 'socio_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignment = CampaignPartner.objects.get(campaign=campaign, socio_id=socio_id)
        except CampaignPartner.DoesNotExist:
            return Response({
                'error': 'El socio no está asignado a esta campaña'
            }, status=status.HTTP_404_NOT_FOUND)

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ELIMINAR',
            tabla_afectada='campaign_partner',
            registro_id=assignment.id,
            detalles={
                'campaign': campaign.nombre,
                'socio': assignment.socio.usuario.get_full_name(),
                'desasignado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        assignment.delete()
        return Response({
            'mensaje': 'Socio desasignado exitosamente'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def partners(self, request, pk=None):
        """
        T037: Obtener socios asignados a la campaña
        GET /api/campaigns/{id}/partners/
        """
        campaign = self.get_object()
        partners = campaign.socios_asignados.all()
        serializer = CampaignPartnerSerializer(partners, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_plot(self, request, pk=None):
        """
        T037: Asignar parcela a campaña
        POST /api/campaigns/{id}/assign_plot/
        """
        campaign = self.get_object()
        parcela_id = request.data.get('parcela_id')
        fecha_asignacion = request.data.get('fecha_asignacion', timezone.now().date())
        superficie_comprometida = request.data.get('superficie_comprometida')
        cultivo_planificado = request.data.get('cultivo_planificado', '')
        meta_produccion_parcela = request.data.get('meta_produccion_parcela')
        observaciones = request.data.get('observaciones', '')

        if not parcela_id:
            return Response({
                'error': 'parcela_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            parcela = Parcela.objects.get(id=parcela_id)
        except Parcela.DoesNotExist:
            return Response({
                'error': 'Parcela no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verificar si ya está asignada
        if CampaignPlot.objects.filter(campaign=campaign, parcela=parcela).exists():
            return Response({
                'error': 'La parcela ya está asignada a esta campaña'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Crear asignación
        serializer = CampaignPlotSerializer(data={
            'campaign': campaign.id,
            'parcela': parcela.id,
            'fecha_asignacion': fecha_asignacion,
            'superficie_comprometida': superficie_comprometida,
            'cultivo_planificado': cultivo_planificado,
            'meta_produccion_parcela': meta_produccion_parcela,
            'observaciones': observaciones
        })

        if serializer.is_valid():
            assignment = serializer.save()

            # Registrar en bitácora
            BitacoraAuditoria.objects.create(
                usuario=request.user,
                accion='CREAR',
                tabla_afectada='campaign_plot',
                registro_id=assignment.id,
                detalles={
                    'campaign': campaign.nombre,
                    'parcela': parcela.nombre,
                    'asignado_por': request.user.usuario
                },
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_plot(self, request, pk=None):
        """
        T037: Desasignar parcela de campaña
        POST /api/campaigns/{id}/remove_plot/
        """
        campaign = self.get_object()
        parcela_id = request.data.get('parcela_id')

        if not parcela_id:
            return Response({
                'error': 'parcela_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignment = CampaignPlot.objects.get(campaign=campaign, parcela_id=parcela_id)
        except CampaignPlot.DoesNotExist:
            return Response({
                'error': 'La parcela no está asignada a esta campaña'
            }, status=status.HTTP_404_NOT_FOUND)

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ELIMINAR',
            tabla_afectada='campaign_plot',
            registro_id=assignment.id,
            detalles={
                'campaign': campaign.nombre,
                'parcela': assignment.parcela.nombre,
                'desasignado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        assignment.delete()
        return Response({
            'mensaje': 'Parcela desasignada exitosamente'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def plots(self, request, pk=None):
        """
        T037: Obtener parcelas asignadas a la campaña
        GET /api/campaigns/{id}/plots/
        """
        campaign = self.get_object()
        plots = campaign.parcelas.all()
        serializer = CampaignPlotSerializer(plots, many=True)
        return Response(serializer.data)


# ============================================================================
# CU11: REPORTES DE CAMPAÑAS - VISTAS
# T039: Reporte de labores por campaña
# T050: Reporte de producción por campaña
# T052: Reporte de producción por parcela
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_labors_by_campaign(request):
    """
    T039: Reporte de labores por campaña
    GET /api/reports/labors-by-campaign/?campaign_id=X&start_date=Y&end_date=Z&tipo_tratamiento=T&parcela_id=P
    
    Parámetros:
    - campaign_id (requerido): ID de la campaña
    - start_date (opcional): Fecha de inicio (YYYY-MM-DD)
    - end_date (opcional): Fecha de fin (YYYY-MM-DD)
    - tipo_tratamiento (opcional): Tipo de tratamiento a filtrar
    - parcela_id (opcional): ID de parcela específica
    """
    campaign_id = request.query_params.get('campaign_id')
    
    if not campaign_id:
        return Response({
            'error': 'campaign_id es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)

    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    tipo_tratamiento = request.query_params.get('tipo_tratamiento')
    parcela_id = request.query_params.get('parcela_id')

    # Convertir fechas si están presentes
    if start_date:
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de start_date inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

    if end_date:
        try:
            from datetime import datetime
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de end_date inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

    # Generar reporte
    report_data = CampaignReports.get_labors_by_campaign(
        campaign_id=campaign_id,
        start_date=start_date,
        end_date=end_date,
        tipo_tratamiento=tipo_tratamiento,
        parcela_id=parcela_id
    )

    # Verificar si hay error
    if 'error' in report_data:
        return Response(report_data, status=status.HTTP_404_NOT_FOUND)

    return Response(report_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_production_by_campaign(request):
    """
    T050: Reporte de producción por campaña
    GET /api/reports/production-by-campaign/?campaign_id=X
    
    Parámetros:
    - campaign_id (requerido): ID de la campaña
    """
    campaign_id = request.query_params.get('campaign_id')
    
    if not campaign_id:
        return Response({
            'error': 'campaign_id es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Generar reporte
    report_data = CampaignReports.get_production_by_campaign(campaign_id=campaign_id)

    # Verificar si hay error
    if 'error' in report_data:
        return Response(report_data, status=status.HTTP_404_NOT_FOUND)

    return Response(report_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_production_by_plot(request):
    """
    T052: Reporte de producción por parcela
    GET /api/reports/production-by-plot/?plot_id=X&campaign_id=Y&start_date=Z&end_date=W
    
    Parámetros:
    - plot_id (requerido): ID de la parcela
    - campaign_id (opcional): ID de la campaña
    - start_date (opcional): Fecha de inicio (YYYY-MM-DD)
    - end_date (opcional): Fecha de fin (YYYY-MM-DD)
    """
    plot_id = request.query_params.get('plot_id')
    
    if not plot_id:
        return Response({
            'error': 'plot_id es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)

    campaign_id = request.query_params.get('campaign_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    # Convertir fechas si están presentes
    if start_date:
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date.strip(), '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': f'Formato de start_date inválido. Use YYYY-MM-DD. Recibido: "{start_date}"'
            }, status=status.HTTP_400_BAD_REQUEST)

    if end_date:
        try:
            from datetime import datetime
            end_date = datetime.strptime(end_date.strip(), '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': f'Formato de end_date inválido. Use YYYY-MM-DD. Recibido: "{end_date}"'
            }, status=status.HTTP_400_BAD_REQUEST)

    # Generar reporte
    report_data = CampaignReports.get_production_by_plot(
        plot_id=plot_id,
        campaign_id=campaign_id,
        start_date=start_date,
        end_date=end_date
    )

    # Verificar si hay error
    if 'error' in report_data:
        return Response(report_data, status=status.HTTP_404_NOT_FOUND)

    return Response(report_data)


# ============================================================================
# CU10: GESTIÓN DE LABORES AGRÍCOLAS - VIEWSETS Y VISTAS
# T047: Gestión de labores (registrar, editar, eliminar)
# T048: Descuento de insumos del inventario (coordinado con CU12)
# T049: Validación de fechas dentro de campaña
# ============================================================================

class LaborPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class LaborViewSet(viewsets.ModelViewSet):
    """
    CU10: ViewSet para gestión completa de labores agrícolas
    T047: CRUD completo (list, create, retrieve, update, destroy)
    T048: Descuento automático de insumos cuando la labor se completa
    T049: Validación de fechas dentro del rango de campaña
    """
    queryset = Labor.objects.all().select_related(
        'campaña', 'parcela__socio__usuario', 'insumo', 'responsable'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['fecha_labor', 'labor', 'estado', 'creado_en']
    ordering = ['-fecha_labor', '-creado_en']
    pagination_class = LaborPagination

    def get_serializer_class(self):
        """Usar serializer específico según la acción"""
        if self.action == 'create':
            return LaborCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return LaborUpdateSerializer
        elif self.action == 'list':
            return LaborListSerializer
        return LaborSerializer

    def get_queryset(self):
        """Filtros opcionales por query params"""
        queryset = super().get_queryset()
        
        # Filtros
        fecha_labor_desde = self.request.query_params.get('fecha_labor_desde')
        fecha_labor_hasta = self.request.query_params.get('fecha_labor_hasta')
        labor_tipo = self.request.query_params.get('labor_tipo')
        estado = self.request.query_params.get('estado')
        campaña_id = self.request.query_params.get('campaña_id')
        parcela_id = self.request.query_params.get('parcela_id')
        socio_id = self.request.query_params.get('socio_id')
        insumo_id = self.request.query_params.get('insumo_id')
        responsable_id = self.request.query_params.get('responsable_id')

        if fecha_labor_desde:
            queryset = queryset.filter(fecha_labor__gte=fecha_labor_desde)
        if fecha_labor_hasta:
            queryset = queryset.filter(fecha_labor__lte=fecha_labor_hasta)
        if labor_tipo:
            queryset = queryset.filter(labor=labor_tipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if campaña_id:
            queryset = queryset.filter(campaña_id=campaña_id)
        if parcela_id:
            queryset = queryset.filter(parcela_id=parcela_id)
        if socio_id:
            queryset = queryset.filter(parcela__socio_id=socio_id)
        if insumo_id:
            queryset = queryset.filter(insumo_id=insumo_id)
        if responsable_id:
            queryset = queryset.filter(responsable_id=responsable_id)

        return queryset

    def perform_create(self, serializer):
        """Registrar creación en bitácora y manejar descuento de insumos si es necesario"""
        labor = serializer.save()
        
        # Si la labor se crea como COMPLETADA y usa insumos, descontar del inventario
        if labor.estado == 'COMPLETADA' and labor.insumo and labor.cantidad_insumo:
            labor._descontar_insumo()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='labor',
            registro_id=labor.id,
            detalles={
                'labor_tipo': labor.labor,
                'fecha_labor': labor.fecha_labor.isoformat(),
                'campaña': labor.campaña.nombre if labor.campaña else None,
                'parcela': labor.parcela.nombre if labor.parcela else None,
                'creado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        """Registrar actualización en bitácora y manejar cambios de estado"""
        labor_anterior = self.get_object()
        estado_anterior = labor_anterior.estado
        insumo_anterior = labor_anterior.insumo
        cantidad_anterior = labor_anterior.cantidad_insumo

        labor = serializer.save()

        # Si cambia de estado a COMPLETADA y usa insumos, descontar del inventario
        if (estado_anterior != 'COMPLETADA' and labor.estado == 'COMPLETADA' and 
            labor.insumo and labor.cantidad_insumo):
            labor._descontar_insumo()

        # Si cambia el insumo o la cantidad y ya estaba completada, ajustar inventario
        if (estado_anterior == 'COMPLETADA' and labor.estado == 'COMPLETADA' and
            (insumo_anterior != labor.insumo or cantidad_anterior != labor.cantidad_insumo)):
            
            # Revertir descuento anterior si había insumo
            if insumo_anterior and cantidad_anterior:
                insumo_anterior.cantidad_disponible += cantidad_anterior
                insumo_anterior.save()
            
            # Aplicar nuevo descuento si hay nuevo insumo
            if labor.insumo and labor.cantidad_insumo:
                labor._descontar_insumo()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='labor',
            registro_id=labor.id,
            detalles={
                'labor_tipo': labor.labor,
                'fecha_labor': labor.fecha_labor.isoformat(),
                'estado_anterior': estado_anterior,
                'estado_nuevo': labor.estado,
                'actualizado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_destroy(self, instance):
        """Registrar eliminación en bitácora y revertir descuento de insumos si es necesario"""
        # Si la labor estaba completada y usaba insumos, revertir el descuento
        if instance.estado == 'COMPLETADA' and instance.insumo and instance.cantidad_insumo:
            instance.insumo.cantidad_disponible += instance.cantidad_insumo
            instance.insumo.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='labor',
            registro_id=instance.id,
            detalles={
                'labor_tipo': instance.labor,
                'fecha_labor': instance.fecha_labor.isoformat(),
                'eliminado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

        instance.delete()

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        CU10: Cambiar estado de una labor específica
        POST /api/labores/{id}/cambiar_estado/
        """
        labor = self.get_object()
        nuevo_estado = request.data.get('estado')
        observaciones = request.data.get('observaciones', '')

        if not nuevo_estado:
            return Response({
                'error': 'estado es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        if nuevo_estado not in dict(Labor.ESTADOS):
            return Response({
                'error': f'Estado inválido. Estados válidos: {", ".join(dict(Labor.ESTADOS).keys())}'
            }, status=status.HTTP_400_BAD_REQUEST)

        estado_anterior = labor.estado
        labor.estado = nuevo_estado
        
        if observaciones:
            labor.observaciones = observaciones

        # Si cambia a COMPLETADA y usa insumos, descontar del inventario
        if (estado_anterior != 'COMPLETADA' and nuevo_estado == 'COMPLETADA' and 
            labor.insumo and labor.cantidad_insumo):
            labor._descontar_insumo()

        labor.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ACTUALIZAR',
            tabla_afectada='labor',
            registro_id=labor.id,
            detalles={
                'labor_tipo': labor.labor,
                'cambio_estado': True,
                'estado_anterior': estado_anterior,
                'estado_nuevo': nuevo_estado,
                'observaciones': observaciones,
                'modificado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        serializer = self.get_serializer(labor)
        return Response({
            'mensaje': f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
            'labor': serializer.data
        })

    @action(detail=True, methods=['post'])
    def actualizar_insumo(self, request, pk=None):
        """
        CU10: Actualizar insumo utilizado en la labor
        POST /api/labores/{id}/actualizar_insumo/
        """
        labor = self.get_object()
        insumo_id = request.data.get('insumo_id')
        cantidad_insumo = request.data.get('cantidad_insumo')

        # Validaciones
        if insumo_id is None and cantidad_insumo is None:
            return Response({
                'error': 'Debe proporcionar insumo_id o cantidad_insumo'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Guardar estado anterior para reversión si es necesario
        estado_anterior = labor.estado
        insumo_anterior = labor.insumo
        cantidad_anterior = labor.cantidad_insumo

        # Actualizar campos
        if insumo_id is not None:
            try:
                if insumo_id == '':
                    labor.insumo = None
                else:
                    from .models import Insumo  # Asumiendo que el modelo Insumo existe para CU12
                    labor.insumo = Insumo.objects.get(id=insumo_id)
            except Insumo.DoesNotExist:
                return Response({
                    'error': 'Insumo no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)

        if cantidad_insumo is not None:
            if cantidad_insumo < 0:
                return Response({
                    'error': 'La cantidad de insumo no puede ser negativa'
                }, status=status.HTTP_400_BAD_REQUEST)
            labor.cantidad_insumo = cantidad_insumo

        # Si la labor estaba completada, ajustar inventario
        if estado_anterior == 'COMPLETADA':
            # Revertir descuento anterior si había insumo
            if insumo_anterior and cantidad_anterior:
                insumo_anterior.cantidad_disponible += cantidad_anterior
                insumo_anterior.save()
            
            # Aplicar nuevo descuento si hay nuevo insumo
            if labor.insumo and labor.cantidad_insumo:
                # Validar stock disponible
                if labor.cantidad_insumo > labor.insumo.cantidad_disponible:
                    # Revertir cambios si no hay suficiente stock
                    if insumo_anterior and cantidad_anterior:
                        insumo_anterior.cantidad_disponible -= cantidad_anterior
                        insumo_anterior.save()
                    return Response({
                        'error': f'Stock insuficiente. Disponible: {labor.insumo.cantidad_disponible}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                labor._descontar_insumo()

        labor.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ACTUALIZAR',
            tabla_afectada='labor',
            registro_id=labor.id,
            detalles={
                'labor_tipo': labor.labor,
                'cambio_insumo': True,
                'insumo_anterior': str(insumo_anterior) if insumo_anterior else None,
                'insumo_nuevo': str(labor.insumo) if labor.insumo else None,
                'cantidad_anterior': float(cantidad_anterior) if cantidad_anterior else None,
                'cantidad_nueva': float(labor.cantidad_insumo) if labor.cantidad_insumo else None,
                'modificado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        serializer = self.get_serializer(labor)
        return Response({
            'mensaje': 'Insumo actualizado exitosamente',
            'labor': serializer.data
        })

    @action(detail=False, methods=['get'])
    def tipos_labor(self, request):
        """
        CU10: Obtener lista de tipos de labor disponibles
        GET /api/labores/tipos_labor/
        """
        tipos = [
            {'valor': tipo[0], 'etiqueta': tipo[1]} 
            for tipo in Labor.TIPOS_LABOR
        ]
        return Response(tipos)

    @action(detail=False, methods=['get'])
    def estados_labor(self, request):
        """
        CU10: Obtener lista de estados disponibles para labores
        GET /api/labores/estados_labor/
        """
        estados = [
            {'valor': estado[0], 'etiqueta': estado[1]} 
            for estado in Labor.ESTADOS
        ]
        return Response(estados)

    @action(detail=False, methods=['get'])
    def labores_con_insumos(self, request):
        """
        CU10: Obtener labores que pueden descontar insumos
        GET /api/labores/labores_con_insumos/
        """
        labores_con_insumos = ['FERTILIZACION', 'FUMIGACION', 'SIEMBRA']
        tipos = [
            {'valor': tipo[0], 'etiqueta': tipo[1]} 
            for tipo in Labor.TIPOS_LABOR 
            if tipo[0] in labores_con_insumos
        ]
        return Response({
            'labores_con_insumos': labores_con_insumos,
            'tipos': tipos
        })

    @action(detail=False, methods=['get'])
    def reporte_labores_por_periodo(self, request):
        """
        CU10: Reporte de labores por período
        GET /api/labores/reporte_labores_por_periodo/?fecha_desde=YYYY-MM-DD&fecha_hasta=YYYY-MM-DD
        """
        from django.db.models import Count, Sum, Avg
        from datetime import datetime

        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')

        # Validar fechas
        if not fecha_desde or not fecha_hasta:
            return Response({
                'error': 'fecha_desde y fecha_hasta son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Filtrar labores por período
        labores = Labor.objects.filter(
            fecha_labor__range=[fecha_desde, fecha_hasta]
        )

        # Estadísticas generales
        total_labores = labores.count()
        labores_completadas = labores.filter(estado='COMPLETADA').count()
        labores_planificadas = labores.filter(estado='PLANIFICADA').count()
        labores_en_proceso = labores.filter(estado='EN_PROCESO').count()
        labores_canceladas = labores.filter(estado='CANCELADA').count()

        # Labores por tipo
        labores_por_tipo = labores.values('labor').annotate(
            count=Count('id'),
            completadas=Count('id', filter=Q(estado='COMPLETADA')),
            costo_promedio=Avg('costo_estimado'),
            duracion_promedio=Avg('duracion_horas')
        ).order_by('-count')

        # Labores que usaron insumos
        labores_con_insumos = labores.filter(insumo__isnull=False).count()
        costo_total_insumos = labores.filter(
            insumo__isnull=False, 
            estado='COMPLETADA'
        ).aggregate(
            total=Sum(F('cantidad_insumo') * F('insumo__precio_unitario'))
        )['total'] or 0

        # Costo total estimado
        costo_total_estimado = labores.aggregate(
            total=Sum('costo_estimado')
        )['total'] or 0

        # Labores por campaña
        labores_por_campaña = labores.filter(campaña__isnull=False).values(
            'campaña__nombre'
        ).annotate(
            count=Count('id'),
            completadas=Count('id', filter=Q(estado='COMPLETADA'))
        ).order_by('-count')

        # Labores por parcela
        labores_por_parcela = labores.filter(parcela__isnull=False).values(
            'parcela__nombre'
        ).annotate(
            count=Count('id'),
            completadas=Count('id', filter=Q(estado='COMPLETADA'))
        ).order_by('-count')[:10]  # Top 10 parcelas

        return Response({
            'periodo': {
                'fecha_desde': fecha_desde.isoformat(),
                'fecha_hasta': fecha_hasta.isoformat(),
                'dias': (fecha_hasta - fecha_desde).days
            },
            'estadisticas_generales': {
                'total_labores': total_labores,
                'labores_completadas': labores_completadas,
                'labores_planificadas': labores_planificadas,
                'labores_en_proceso': labores_en_proceso,
                'labores_canceladas': labores_canceladas,
                'tasa_completitud': round((labores_completadas / total_labores * 100), 2) if total_labores > 0 else 0
            },
            'costos': {
                'costo_total_estimado': float(costo_total_estimado),
                'costo_total_insumos': float(costo_total_insumos),
                'costo_total': float(costo_total_estimado + costo_total_insumos),
                'labores_con_insumos': labores_con_insumos
            },
            'labores_por_tipo': list(labores_por_tipo),
            'labores_por_campaña': list(labores_por_campaña),
            'labores_por_parcela': list(labores_por_parcela)
        })

    @action(detail=False, methods=['get'])
    def validar_fecha_campaña(self, request):
        """
        CU10: Validar si una fecha está dentro del rango de una campaña
        GET /api/labores/validar_fecha_campaña/?campaña_id=X&fecha=YYYY-MM-DD
        """
        campaña_id = request.query_params.get('campaña_id')
        fecha_str = request.query_params.get('fecha')

        if not campaña_id or not fecha_str:
            return Response({
                'error': 'campaña_id y fecha son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            from datetime import datetime
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            campaña = Campaign.objects.get(id=campaña_id)
        except Campaign.DoesNotExist:
            return Response({
                'error': 'Campaña no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar fecha
        valida = True
        errores = []

        if fecha < campaña.fecha_inicio:
            valida = False
            errores.append(f'La fecha no puede ser anterior al inicio de la campaña ({campaña.fecha_inicio})')

        if campaña.fecha_fin and fecha > campaña.fecha_fin:
            valida = False
            errores.append(f'La fecha no puede ser posterior al fin de la campaña ({campaña.fecha_fin})')

        return Response({
            'valida': valida,
            'fecha': fecha.isoformat(),
            'campaña': campaña.nombre,
            'rango_campaña': {
                'fecha_inicio': campaña.fecha_inicio.isoformat(),
                'fecha_fin': campaña.fecha_fin.isoformat() if campaña.fecha_fin else None
            },
            'errores': errores
        })


# Endpoints adicionales para CU10
# ================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_labor_rapida(request):
    """
    CU10: Crear labor rápida (sin campos opcionales)
    POST /api/labores/crear_rapida/
    """
    serializer = LaborCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        labor = serializer.save()
        
        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='labor',
            registro_id=labor.id,
            detalles={
                'labor_tipo': labor.labor,
                'fecha_labor': labor.fecha_labor.isoformat(),
                'creado_por': request.user.usuario,
                'tipo_creacion': 'rapida'
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        response_serializer = LaborSerializer(labor)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_labores_avanzado(request):
    """
    CU10: Búsqueda avanzada de labores
    GET /api/labores/buscar_avanzado/?param1=valor1&param2=valor2...
    """
    queryset = Labor.objects.select_related(
        'campaña', 'parcela__socio__usuario', 'insumo', 'responsable'
    )

    # Filtros de búsqueda
    fecha_labor_desde = request.query_params.get('fecha_labor_desde')
    fecha_labor_hasta = request.query_params.get('fecha_labor_hasta')
    labor_tipo = request.query_params.get('labor_tipo')
    estado = request.query_params.get('estado')
    campaña_id = request.query_params.get('campaña_id')
    parcela_id = request.query_params.get('parcela_id')
    socio_id = request.query_params.get('socio_id')
    insumo_id = request.query_params.get('insumo_id')
    responsable_id = request.query_params.get('responsable_id')
    con_insumos = request.query_params.get('con_insumos')
    sin_insumos = request.query_params.get('sin_insumos')

    # Aplicar filtros
    if fecha_labor_desde:
        queryset = queryset.filter(fecha_labor__gte=fecha_labor_desde)
    if fecha_labor_hasta:
        queryset = queryset.filter(fecha_labor__lte=fecha_labor_hasta)
    if labor_tipo:
        queryset = queryset.filter(labor=labor_tipo)
    if estado:
        queryset = queryset.filter(estado=estado)
    if campaña_id:
        queryset = queryset.filter(campaña_id=campaña_id)
    if parcela_id:
        queryset = queryset.filter(parcela_id=parcela_id)
    if socio_id:
        queryset = queryset.filter(parcela__socio_id=socio_id)
    if insumo_id:
        queryset = queryset.filter(insumo_id=insumo_id)
    if responsable_id:
        queryset = queryset.filter(responsable_id=responsable_id)
    if con_insumos:
        queryset = queryset.filter(insumo__isnull=False)
    if sin_insumos:
        queryset = queryset.filter(insumo__isnull=True)

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    labores = queryset[start:end]

    serializer = LaborListSerializer(labores, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros_aplicados': {
            'fecha_labor_desde': fecha_labor_desde,
            'fecha_labor_hasta': fecha_labor_hasta,
            'labor_tipo': labor_tipo,
            'estado': estado,
            'campaña_id': campaña_id,
            'parcela_id': parcela_id,
            'socio_id': socio_id,
            'insumo_id': insumo_id,
            'responsable_id': responsable_id,
            'con_insumos': con_insumos,
            'sin_insumos': sin_insumos
        },
        'results': serializer.data
    })

# ============================================================================
# CU15: GESTIÓN DE PRODUCTOS COSECHADOS - VIEWSETS Y VISTAS
# Registrar productos cosechados por campaña y parcela
# ============================================================================

class ProductoCosechadoPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductoCosechadoViewSet(viewsets.ModelViewSet):
    """
    CU15: ViewSet para gestión completa de productos cosechados
    CRUD completo (list, create, retrieve, update, destroy)
    """
    queryset = ProductoCosechado.objects.all().select_related(
        'cultivo', 'labor', 'campania', 'parcela__socio__usuario'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['fecha_cosecha', 'cantidad', 'estado', 'lote', 'creado_en']
    ordering = ['-fecha_cosecha', '-creado_en']
    pagination_class = ProductoCosechadoPagination

    def get_serializer_class(self):
        """Usar serializer específico según la acción"""
        if self.action == 'create':
            return ProductoCosechadoCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProductoCosechadoUpdateSerializer
        elif self.action == 'list':
            return ProductoCosechadoListSerializer
        return ProductoCosechadoSerializer

    def get_queryset(self):
        """Filtros opcionales por query params"""
        queryset = super().get_queryset()
        
        # Filtros
        fecha_cosecha_desde = self.request.query_params.get('fecha_cosecha_desde')
        fecha_cosecha_hasta = self.request.query_params.get('fecha_cosecha_hasta')
        cultivo_id = self.request.query_params.get('cultivo_id')
        campania_id = self.request.query_params.get('campania_id')
        parcela_id = self.request.query_params.get('parcela_id')
        estado = self.request.query_params.get('estado')
        lote = self.request.query_params.get('lote')
        calidad = self.request.query_params.get('calidad')
        labor_id = self.request.query_params.get('labor_id')
        socio_id = self.request.query_params.get('socio_id')

        if fecha_cosecha_desde:
            queryset = queryset.filter(fecha_cosecha__gte=fecha_cosecha_desde)
        if fecha_cosecha_hasta:
            queryset = queryset.filter(fecha_cosecha__lte=fecha_cosecha_hasta)
        if cultivo_id:
            queryset = queryset.filter(cultivo_id=cultivo_id)
        if campania_id:
            queryset = queryset.filter(campania_id=campania_id)
        if parcela_id:
            queryset = queryset.filter(parcela_id=parcela_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if lote:
            queryset = queryset.filter(lote=lote)
        if calidad:
            queryset = queryset.filter(calidad__icontains=calidad)
        if labor_id:
            queryset = queryset.filter(labor_id=labor_id)
        if socio_id:
            # Filtrar por socio a través de parcela o campaña
            queryset = queryset.filter(
                Q(parcela__socio_id=socio_id) | 
                Q(campania__socios_asignados__socio_id=socio_id)
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        """Registrar creación en bitácora"""
        producto = serializer.save()
        
        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='producto_cosechado',
            registro_id=producto.id,
            detalles={
                'cultivo': producto.cultivo.especie,
                'cantidad': float(producto.cantidad),
                'unidad_medida': producto.unidad_medida,
                'origen': producto.origen_display,
                'creado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        """Registrar actualización en bitácora"""
        producto_anterior = self.get_object()
        producto = serializer.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='producto_cosechado',
            registro_id=producto.id,
            detalles={
                'cultivo': producto.cultivo.especie,
                'cantidad': float(producto.cantidad),
                'unidad_medida': producto.unidad_medida,
                'estado_anterior': producto_anterior.estado,
                'estado_nuevo': producto.estado,
                'actualizado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_destroy(self, instance):
        """Registrar eliminación en bitácora"""
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='producto_cosechado',
            registro_id=instance.id,
            detalles={
                'cultivo': instance.cultivo.especie,
                'cantidad': float(instance.cantidad),
                'eliminado_por': self.request.user.usuario
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

        instance.delete()

    @action(detail=True, methods=['post'])
    def vender_producto(self, request, pk=None):
        """
        CU15: Vender producto cosechado
        POST /api/productos-cosechados/{id}/vender_producto/
        """
        producto = self.get_object()
        
        serializer = ProductoCosechadoVenderSerializer(
            data=request.data,
            context={'producto': producto}
        )
        
        if serializer.is_valid():
            producto = serializer.save()
            
            # Registrar en bitácora
            BitacoraAuditoria.objects.create(
                usuario=request.user,
                accion='VENDER_PRODUCTO_COSECHADO',
                tabla_afectada='producto_cosechado',
                registro_id=producto.id,
                detalles={
                    'cultivo': producto.cultivo.especie,
                    'cantidad_vendida': float(serializer.validated_data['cantidad_vendida']),
                    'estado_nuevo': producto.estado,
                    'observaciones': serializer.validated_data.get('observaciones', ''),
                    'vendido_por': request.user.usuario
                },
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            response_serializer = ProductoCosechadoSerializer(producto)
            return Response({
                'mensaje': 'Producto vendido exitosamente',
                'producto': response_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        CU15: Cambiar estado del producto cosechado
        POST /api/productos-cosechados/{id}/cambiar_estado/
        """
        producto = self.get_object()
        
        serializer = ProductoCosechadoCambiarEstadoSerializer(
            data=request.data,
            context={'producto': producto}
        )
        
        if serializer.is_valid():
            producto = serializer.save()
            
            # Registrar en bitácora
            BitacoraAuditoria.objects.create(
                usuario=request.user,
                accion='CAMBIAR_ESTADO_PRODUCTO_COSECHADO',
                tabla_afectada='producto_cosechado',
                registro_id=producto.id,
                detalles={
                    'cultivo': producto.cultivo.especie,
                    'estado_anterior': self.get_object().estado,
                    'estado_nuevo': serializer.validated_data['nuevo_estado'],
                    'observaciones': serializer.validated_data.get('observaciones', ''),
                    'cambiado_por': request.user.usuario
                },
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            response_serializer = ProductoCosechadoSerializer(producto)
            return Response({
                'mensaje': f'Estado cambiado a {serializer.validated_data["nuevo_estado"]}',
                'producto': response_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def estados_disponibles(self, request):
        """
        CU15: Obtener lista de estados disponibles
        GET /api/productos-cosechados/estados_disponibles/
        """
        estados = [
            {'valor': estado[0], 'etiqueta': estado[1]} 
            for estado in ProductoCosechado.ESTADO_OPCIONES
        ]
        return Response(estados)

    @action(detail=False, methods=['get'])
    def productos_por_vencer(self, request):
        """
        CU15: Obtener productos próximos a vencer (en almacén por mucho tiempo)
        GET /api/productos-cosechados/productos_por_vencer/?dias_umbral=30
        """
        dias_umbral = int(request.query_params.get('dias_umbral', 30))
        
        productos = self.get_queryset().filter(estado='En Almacén')
        productos_por_vencer = [
            producto for producto in productos 
            if producto.esta_proximo_vencer(dias_umbral)
        ]
        
        serializer = ProductoCosechadoListSerializer(productos_por_vencer, many=True)
        return Response({
            'count': len(productos_por_vencer),
            'dias_umbral': dias_umbral,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def productos_vendibles(self, request):
        """
        CU15: Obtener productos que pueden ser vendidos
        GET /api/productos-cosechados/productos_vendibles/
        """
        productos_vendibles = self.get_queryset().filter(
            estado='En Almacén',
            cantidad__gt=0
        )
        
        serializer = ProductoCosechadoListSerializer(productos_vendibles, many=True)
        return Response({
            'count': productos_vendibles.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def reporte_inventario(self, request):
        """
        CU15: Reporte general del inventario de productos cosechados
        GET /api/productos-cosechados/reporte_inventario/
        """
        from django.db.models import Sum, Count, Avg

        # Estadísticas generales
        total_productos = ProductoCosechado.objects.count()
        productos_almacen = ProductoCosechado.objects.filter(estado='En Almacén').count()
        productos_vendidos = ProductoCosechado.objects.filter(estado='Vendido').count()
        productos_procesados = ProductoCosechado.objects.filter(estado='Procesado').count()
        productos_vencidos = ProductoCosechado.objects.filter(estado='Vencido').count()
        productos_revision = ProductoCosechado.objects.filter(estado='En revision').count()

        # Cantidad total por estado
        cantidad_por_estado = ProductoCosechado.objects.values('estado').annotate(
            total_cantidad=Sum('cantidad'),
            num_productos=Count('id')
        ).order_by('-total_cantidad')

        # Productos por cultivo
        productos_por_cultivo = ProductoCosechado.objects.values(
            'cultivo__especie', 'cultivo__variedad'
        ).annotate(
            total_cantidad=Sum('cantidad'),
            num_productos=Count('id')
        ).order_by('-total_cantidad')[:10]

        # Productos por campaña
        productos_por_campania = ProductoCosechado.objects.filter(
            campania__isnull=False
        ).values('campania__nombre').annotate(
            total_cantidad=Sum('cantidad'),
            num_productos=Count('id')
        ).order_by('-total_cantidad')

        # Productos por parcela
        productos_por_parcela = ProductoCosechado.objects.filter(
            parcela__isnull=False
        ).values('parcela__nombre').annotate(
            total_cantidad=Sum('cantidad'),
            num_productos=Count('id')
        ).order_by('-total_cantidad')[:10]

        # Promedio de días en almacén
        promedio_dias_almacen = ProductoCosechado.objects.filter(
            estado='En Almacén'
        ).aggregate(
            avg_dias=Avg(F('dias_en_almacen'))
        )['avg_dias'] or 0

        return Response({
            'resumen': {
                'total_productos': total_productos,
                'productos_almacen': productos_almacen,
                'productos_vendidos': productos_vendidos,
                'productos_procesados': productos_procesados,
                'productos_vencidos': productos_vencidos,
                'productos_revision': productos_revision,
                'promedio_dias_almacen': round(float(promedio_dias_almacen), 2)
            },
            'cantidad_por_estado': list(cantidad_por_estado),
            'productos_por_cultivo': list(productos_por_cultivo),
            'productos_por_campania': list(productos_por_campania),
            'productos_por_parcela': list(productos_por_parcela)
        })

    @action(detail=False, methods=['get'])
    def validar_lote(self, request):
        """
        CU15: Validar número de lote único
        GET /api/productos-cosechados/validar_lote/?lote=123.45
        """
        lote = request.query_params.get('lote', '').strip()
        
        if not lote:
            return Response({
                'error': 'lote es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            lote_float = float(lote)
        except ValueError:
            return Response({
                'error': 'lote debe ser un número válido'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el lote ya existe
        existe = ProductoCosechado.objects.filter(lote=lote_float).exists()
        
        return Response({
            'lote': lote_float,
            'existe': existe,
            'mensaje': 'Lote ya existe' if existe else 'Lote disponible'
        })


# Endpoints adicionales para CU15
# ================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_producto_cosechado_rapido(request):
    """
    CU15: Crear producto cosechado rápido (sin campos opcionales)
    POST /api/productos-cosechados/crear_rapido/
    """
    serializer = ProductoCosechadoCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        producto = serializer.save()
        
        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='producto_cosechado',
            registro_id=producto.id,
            detalles={
                'cultivo': producto.cultivo.especie,
                'cantidad': float(producto.cantidad),
                'unidad_medida': producto.unidad_medida,
                'origen': producto.origen_display,
                'creado_por': request.user.usuario,
                'tipo_creacion': 'rapida'
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        response_serializer = ProductoCosechadoSerializer(producto)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_productos_cosechados_avanzado(request):
    """
    CU15: Búsqueda avanzada de productos cosechados
    GET /api/productos-cosechados/buscar_avanzado/?param1=valor1&param2=valor2...
    """
    queryset = ProductoCosechado.objects.select_related(
        'cultivo', 'labor', 'campania', 'parcela__socio__usuario'
    )

    # Filtros de búsqueda
    fecha_cosecha_desde = request.query_params.get('fecha_cosecha_desde')
    fecha_cosecha_hasta = request.query_params.get('fecha_cosecha_hasta')
    cultivo_id = request.query_params.get('cultivo_id')
    campania_id = request.query_params.get('campania_id')
    parcela_id = request.query_params.get('parcela_id')
    estado = request.query_params.get('estado')
    lote = request.query_params.get('lote')
    calidad = request.query_params.get('calidad')
    labor_id = request.query_params.get('labor_id')
    socio_id = request.query_params.get('socio_id')
    especie = request.query_params.get('especie')
    unidad_medida = request.query_params.get('unidad_medida')
    ubicacion_almacen = request.query_params.get('ubicacion_almacen')

    # Aplicar filtros
    if fecha_cosecha_desde:
        queryset = queryset.filter(fecha_cosecha__gte=fecha_cosecha_desde)
    if fecha_cosecha_hasta:
        queryset = queryset.filter(fecha_cosecha__lte=fecha_cosecha_hasta)
    if cultivo_id:
        queryset = queryset.filter(cultivo_id=cultivo_id)
    if campania_id:
        queryset = queryset.filter(campania_id=campania_id)
    if parcela_id:
        queryset = queryset.filter(parcela_id=parcela_id)
    if estado:
        queryset = queryset.filter(estado=estado)
    if lote:
        queryset = queryset.filter(lote=lote)
    if calidad:
        queryset = queryset.filter(calidad__icontains=calidad)
    if labor_id:
        queryset = queryset.filter(labor_id=labor_id)
    if socio_id:
        queryset = queryset.filter(
            Q(parcela__socio_id=socio_id) | 
            Q(campania__socios_asignados__socio_id=socio_id)
        ).distinct()
    if especie:
        queryset = queryset.filter(cultivo__especie__icontains=especie)
    if unidad_medida:
        queryset = queryset.filter(unidad_medida__icontains=unidad_medida)
    if ubicacion_almacen:
        queryset = queryset.filter(ubicacion_almacen__icontains=ubicacion_almacen)

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    productos = queryset[start:end]

    serializer = ProductoCosechadoListSerializer(productos, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros_aplicados': {
            'fecha_cosecha_desde': fecha_cosecha_desde,
            'fecha_cosecha_hasta': fecha_cosecha_hasta,
            'cultivo_id': cultivo_id,
            'campania_id': campania_id,
            'parcela_id': parcela_id,
            'estado': estado,
            'lote': lote,
            'calidad': calidad,
            'labor_id': labor_id,
            'socio_id': socio_id,
            'especie': especie,
            'unidad_medida': unidad_medida,
            'ubicacion_almacen': ubicacion_almacen
        },
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_productos_cosechados_por_periodo(request):
    """
    CU15: Reporte de productos cosechados por período
    GET /api/productos-cosechados/reporte_por_periodo/?fecha_desde=YYYY-MM-DD&fecha_hasta=YYYY-MM-DD
    """
    from django.db.models import Count, Sum, Avg
    from datetime import datetime

    fecha_desde = request.query_params.get('fecha_desde')
    fecha_hasta = request.query_params.get('fecha_hasta')

    # Validar fechas
    if not fecha_desde or not fecha_hasta:
        return Response({
            'error': 'fecha_desde y fecha_hasta son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    except ValueError:
        return Response({
            'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Filtrar productos por período
    productos = ProductoCosechado.objects.filter(
        fecha_cosecha__range=[fecha_desde, fecha_hasta]
    )

    # Estadísticas generales
    total_productos = productos.count()
    total_cantidad = productos.aggregate(total=Sum('cantidad'))['total'] or 0

    # Productos por cultivo
    productos_por_cultivo = productos.values('cultivo__especie').annotate(
        cantidad_total=Sum('cantidad'),
        num_productos=Count('id')
    ).order_by('-cantidad_total')[:10]

    # Productos por estado
    productos_por_estado = productos.values('estado').annotate(
        cantidad_total=Sum('cantidad'),
        num_productos=Count('id')
    ).order_by('-cantidad_total')

    # Productos por campaña
    productos_por_campania = productos.filter(campania__isnull=False).values(
        'campania__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        num_productos=Count('id')
    ).order_by('-cantidad_total')

    # Productos por parcela
    productos_por_parcela = productos.filter(parcela__isnull=False).values(
        'parcela__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        num_productos=Count('id')
    ).order_by('-cantidad_total')[:10]

    # Evolución mensual
    evolucion_mensual = productos.annotate(
        mes=TruncMonth('fecha_cosecha')
    ).values('mes').annotate(
        cantidad_mensual=Sum('cantidad'),
        productos_mensual=Count('id')
    ).order_by('mes')

    return Response({
        'periodo': {
            'fecha_desde': fecha_desde.isoformat(),
            'fecha_hasta': fecha_hasta.isoformat(),
            'dias': (fecha_hasta - fecha_desde).days
        },
        'estadisticas_generales': {
            'total_productos': total_productos,
            'total_cantidad': float(total_cantidad),
            'promedio_cantidad_por_producto': float(total_cantidad / total_productos) if total_productos > 0 else 0
        },
        'productos_por_cultivo': list(productos_por_cultivo),
        'productos_por_estado': list(productos_por_estado),
        'productos_por_campania': list(productos_por_campania),
        'productos_por_parcela': list(productos_por_parcela),
        'evolucion_mensual': list(evolucion_mensual)
    })