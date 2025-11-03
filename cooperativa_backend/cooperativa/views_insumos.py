# ============================================================
# SISTEMA DE VENTAS DE INSUMOS - VIEWS
# ============================================================

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from decimal import Decimal

from .models import (
    PrecioTemporada, PedidoInsumo, DetallePedidoInsumo, PagoInsumo,
    Socio, BitacoraAuditoria
)
from .serializers import (
    PrecioTemporadaSerializer, PedidoInsumoSerializer,
    PedidoInsumoCreateSerializer, PagoInsumoSerializer,
    HistorialComprasInsumosSerializer
)


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PrecioTemporadaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Precios por Temporada
    """
    queryset = PrecioTemporada.objects.all()
    serializer_class = PrecioTemporadaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tipo_insumo', 'temporada', 'activo']
    ordering = ['-fecha_inicio']

    def get_queryset(self):
        """Filtrar precios según parámetros"""
        queryset = super().get_queryset()
        
        # Filtrar solo vigentes
        vigente = self.request.query_params.get('vigente')
        if vigente and vigente.lower() == 'true':
            from django.utils import timezone
            hoy = timezone.now().date()
            queryset = queryset.filter(
                fecha_inicio__lte=hoy,
                fecha_fin__gte=hoy,
                activo=True
            )
        
        return queryset.select_related('semilla', 'pesticida', 'fertilizante')


class PedidoInsumoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Pedidos de Insumos
    """
    queryset = PedidoInsumo.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['estado', 'socio']
    ordering = ['-fecha_pedido']

    def get_serializer_class(self):
        """Usar serializer apropiado según acción"""
        if self.action == 'create':
            return PedidoInsumoCreateSerializer
        return PedidoInsumoSerializer

    def get_queryset(self):
        """Filtrar pedidos según permisos del usuario"""
        queryset = super().get_queryset()
        
        # Restricción: socios solo ven sus pedidos
        if not self.request.user.is_staff:
            try:
                socio = Socio.objects.get(usuario=self.request.user)
                queryset = queryset.filter(socio=socio)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        
        return queryset.select_related(
            'socio__usuario',
            'aprobado_por',
            'entregado_por'
        ).prefetch_related('items', 'pagos_insumo')

    def perform_create(self, serializer):
        """Crear pedido y registrar en bitácora"""
        pedido = serializer.save()
        
        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_PEDIDO_INSUMO',
            tabla_afectada='PedidoInsumo',
            registro_id=pedido.id,
            detalles={
                'numero_pedido': pedido.numero_pedido,
                'socio': pedido.socio.usuario.get_full_name(),
                'total': str(pedido.total),
                'items_count': pedido.items.count()
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """
        Aprobar un pedido de insumos
        POST /api/pedidos-insumos/{id}/aprobar/
        """
        pedido = self.get_object()
        
        # Validar permisos (solo admin)
        if not request.user.is_staff:
            return Response(
                {'error': 'No tiene permisos para aprobar pedidos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar estado
        if pedido.estado != 'SOLICITADO':
            return Response(
                {'error': f'Solo se pueden aprobar pedidos en estado SOLICITADO (actual: {pedido.estado})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aprobar
        pedido.aprobar(request.user)
        
        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='APROBAR_PEDIDO_INSUMO',
            tabla_afectada='PedidoInsumo',
            registro_id=pedido.id,
            detalles={
                'numero_pedido': pedido.numero_pedido,
                'socio': pedido.socio.usuario.get_full_name(),
                'total': str(pedido.total)
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'mensaje': 'Pedido aprobado exitosamente',
            'pedido': PedidoInsumoSerializer(pedido).data
        })

    @action(detail=True, methods=['post'])
    def entregar(self, request, pk=None):
        """
        Marcar pedido como entregado
        POST /api/pedidos-insumos/{id}/entregar/
        """
        pedido = self.get_object()
        
        # Validar permisos (solo admin)
        if not request.user.is_staff:
            return Response(
                {'error': 'No tiene permisos para marcar entregas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Marcar como entregado
        pedido.marcar_entregado(request.user)
        
        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ENTREGAR_PEDIDO_INSUMO',
            tabla_afectada='PedidoInsumo',
            registro_id=pedido.id,
            detalles={
                'numero_pedido': pedido.numero_pedido,
                'socio': pedido.socio.usuario.get_full_name()
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'mensaje': 'Pedido marcado como entregado',
            'pedido': PedidoInsumoSerializer(pedido).data
        })


class PagoInsumoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Pagos de Insumos
    """
    queryset = PagoInsumo.objects.all()
    serializer_class = PagoInsumoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pedido_insumo', 'metodo_pago', 'estado']
    ordering = ['-fecha_pago']

    def get_queryset(self):
        """Filtrar pagos según permisos"""
        queryset = super().get_queryset()
        
        # Restricción: socios solo ven sus pagos
        if not self.request.user.is_staff:
            try:
                socio = Socio.objects.get(usuario=self.request.user)
                queryset = queryset.filter(pedido_insumo__socio=socio)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        
        return queryset.select_related(
            'pedido_insumo__socio__usuario',
            'registrado_por'
        )

    def perform_create(self, serializer):
        """Crear pago y registrar en bitácora"""
        # Asignar usuario que registra
        serializer.validated_data['registrado_por'] = self.request.user
        pago = serializer.save()
        
        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='REGISTRAR_PAGO_INSUMO',
            tabla_afectada='PagoInsumo',
            registro_id=pago.id,
            detalles={
                'numero_recibo': pago.numero_recibo,
                'pedido': pago.pedido_insumo.numero_pedido,
                'monto': str(pago.monto),
                'metodo': pago.get_metodo_pago_display()
            },
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_compras_insumos(request):
    """
    Consultar historial de compras de insumos con estadísticas
    GET /api/ventas/insumos/historial/?socio_id=1&fecha_desde=...&fecha_hasta=...
    """
    # Validar filtros
    serializer = HistorialComprasInsumosSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    
    queryset = PedidoInsumo.objects.select_related('socio__usuario').prefetch_related('items', 'pagos_insumo')
    
    # Restricción: socios solo ven sus compras
    if not request.user.is_staff:
        try:
            socio = Socio.objects.get(usuario=request.user)
            queryset = queryset.filter(socio=socio)
        except Socio.DoesNotExist:
            queryset = queryset.none()
    
    queryset = queryset.order_by('-fecha_pedido')
    
    # Estadísticas generales
    total_pedidos = queryset.count()
    total_gastado = queryset.aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    pedidos = queryset[start:end]
    pedidos_data = PedidoInsumoSerializer(pedidos, many=True).data
    
    return Response({
        'count': total_pedidos,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_pedidos + page_size - 1) // page_size if page_size > 0 else 0,
        'estadisticas': {
            'total_pedidos': total_pedidos,
            'total_gastado': str(total_gastado)
        },
        'results': pedidos_data
    })
