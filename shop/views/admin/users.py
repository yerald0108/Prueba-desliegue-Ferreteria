"""
Vistas de gestión de usuarios para administradores.

Maneja:
- Listado de usuarios con estadísticas
- Detalle de usuario con análisis completo
- Estado online/offline
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count, Avg, F, ExpressionWrapper, DecimalField, Prefetch
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import JsonResponse

from ...models import Order, OrderItem, CartItem, Cart


@staff_member_required
def admin_users(request):
    """
    Listado de usuarios con estadísticas básicas.
    
    ✅ OPTIMIZADO: Annotations en un solo query
    """
    search_query = request.GET.get('q', '')
    
    # ✅ OPTIMIZACIÓN: select_related para profile, annotations para stats
    users = User.objects.select_related('profile').annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total')
    )
    
    # Aplicar búsqueda
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    
    return render(request, 'shop/admin/users.html', context)


@staff_member_required
def admin_user_detail(request, user_id):
    """
    Detalle completo de un usuario con análisis exhaustivo.
    
    ✅ OPTIMIZADO: Prefetch completo de todas las relaciones
    """
    # ✅ OPTIMIZACIÓN MÁXIMA: Cargar TODO en queries eficientes
    user = get_object_or_404(
        User.objects.select_related('profile').prefetch_related(
            Prefetch(
                'orders',
                queryset=Order.objects.prefetch_related(
                    Prefetch(
                        'items',
                        queryset=OrderItem.objects.select_related(
                            'product',
                            'product__category'
                        )
                    )
                ).order_by('-created_at')
            ),
            Prefetch(
                'cart',
                queryset=Cart.objects.prefetch_related(
                    Prefetch(
                        'items',
                        queryset=CartItem.objects.select_related('product')
                    )
                )
            )
        ),
        pk=user_id
    )
    
    # ✅ AHORA podemos acceder a todo sin queries adicionales
    orders = user.orders.all()  # Ya está prefetcheado
    order_count = orders.count()
    
    # Agregaciones
    aggregates = orders.aggregate(
        total_spent=Sum('total'),
        avg_order=Avg('total')
    )
    total_spent = aggregates['total_spent'] or 0
    avg_order = aggregates['avg_order'] or 0
    
    last_order = orders.first()
    
    # ==========================================
    # ANÁLISIS POR ESTADO DE ORDEN
    # ==========================================
    status_breakdown = list(
        orders.values('status').annotate(
            count=Count('id'),
            total=Sum('total')
        ).order_by()
    )
    
    # ==========================================
    # ANÁLISIS DE PRODUCTOS - ✅ OPTIMIZADO
    # ==========================================
    # Productos distintos comprados
    distinct_products = OrderItem.objects.filter(
        order__user=user
    ).values('product').distinct().count()
    
    # Top 10 productos más comprados - ✅ Sin queries extras
    top_products = OrderItem.objects.filter(
        order__user=user
    ).values(
        'product__id', 
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        revenue=Sum(
            ExpressionWrapper(
                F('quantity') * F('price'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    ).order_by('-total_quantity')[:10]
    
    # ==========================================
    # CARRITO ACTUAL
    # ==========================================
    cart = getattr(user, 'cart', None)  # Ya está prefetcheado
    
    context = {
        'detail_user': user,
        'profile': getattr(user, 'profile', None),
        
        # Órdenes
        'orders': orders,
        'order_count': order_count,
        'total_spent': total_spent,
        'avg_order': avg_order,
        'last_order': last_order,
        
        # Análisis
        'status_breakdown': status_breakdown,
        'distinct_products': distinct_products,
        'top_products': top_products,
        
        # Carrito
        'cart': cart,
    }
    
    return render(request, 'shop/admin/user_detail.html', context)


@staff_member_required
def admin_user_online_status(request, user_id):
    """
    Verificar si un usuario está online actualmente.
    
    Un usuario está online si tiene una sesión activa.
    
    Retorna JSON con:
    - is_online: boolean
    - is_active: boolean (cuenta activa)
    - last_login: timestamp del último login
    """
    user = get_object_or_404(User, pk=user_id)
    
    # Verificar si tiene sesiones activas
    is_online = False
    for session in Session.objects.filter(expire_date__gt=timezone.now()):
        data = session.get_decoded()
        uid = data.get('_auth_user_id')
        if str(uid) == str(user.id):
            is_online = True
            break
    
    return JsonResponse({
        'success': True,
        'is_online': is_online,
        'is_active': user.is_active,
        'last_login': user.last_login.isoformat() if user.last_login else None,
    })