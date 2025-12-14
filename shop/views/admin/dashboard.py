"""
Vista del dashboard de administración.

Proporciona:
- Estadísticas generales
- Gráficos de ventas
- Órdenes recientes
- Productos más vendidos
- Alertas de stock
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json

from ...models import Product, Order, OrderItem, User


@staff_member_required
def admin_dashboard(request):
    """
    Dashboard principal de administración con estadísticas y gráficos.
    """
    # ==========================================
    # ESTADÍSTICAS GENERALES
    # ==========================================
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    
    # Ingresos totales (solo órdenes confirmadas o entregadas)
    total_revenue = Order.objects.filter(
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # ==========================================
    # ALERTAS
    # ==========================================
    # Órdenes pendientes
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Productos con bajo stock
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock__lte=10,
        stock__gt=0
    ).count()
    
    # Productos agotados
    out_of_stock = Product.objects.filter(is_active=True, stock=0).count()
    
    # ==========================================
    # ÓRDENES RECIENTES
    # ==========================================
    recent_orders = Order.objects.select_related('user').prefetch_related(
        'items'
    ).order_by('-created_at')[:10]
    
    # ==========================================
    # VENTAS POR DÍA (últimos 7 días)
    # ==========================================
    seven_days_ago = timezone.now() - timedelta(days=7)
    daily_sales = Order.objects.filter(
        created_at__gte=seven_days_ago,
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total'),
        count=Count('id')
    ).order_by('date')
    
    # ==========================================
    # PRODUCTOS MÁS VENDIDOS
    # ==========================================
    top_products = OrderItem.objects.values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:5]
    
    # ==========================================
    # VENTAS POR CATEGORÍA
    # ==========================================
    sales_by_category = OrderItem.objects.select_related(
        'product__category'
    ).values(
        'product__category__name'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('price'))
    ).order_by('-revenue')
    
    # ==========================================
    # PREPARAR DATOS PARA GRÁFICOS
    # ==========================================
    chart_labels = [sale['date'].strftime('%d/%m') for sale in daily_sales]
    chart_data = [float(sale['total']) for sale in daily_sales]
    
    context = {
        # Estadísticas
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
        
        # Alertas
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
        'out_of_stock': out_of_stock,
        
        # Datos para tablas
        'recent_orders': recent_orders,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        
        # Datos para gráficos (JSON)
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'shop/admin/dashboard.html', context)