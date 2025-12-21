from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F, Q, Avg
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
import json

from ...models import Product, Order, OrderItem, User


@staff_member_required
def admin_dashboard(request):
    """
    Dashboard principal con estadísticas avanzadas y múltiples gráficos.
    
    ✅ OPTIMIZADO: Consultas eficientes para todos los gráficos
    """
    
    # ==========================================
    # ESTADÍSTICAS GENERALES
    # ==========================================
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    
    # Ingresos totales
    total_revenue = Order.objects.filter(
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # ==========================================
    # ALERTAS Y ESTADOS
    # ==========================================
    pending_orders = Order.objects.filter(status='pending').count()
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock__lte=10,
        stock__gt=0
    ).count()
    out_of_stock = Product.objects.filter(is_active=True, stock=0).count()
    
    # ==========================================
    # MÉTRICAS DE CRECIMIENTO
    # ==========================================
    today = timezone.now()
    last_month = today - timedelta(days=30)
    
    # Órdenes del último mes
    orders_last_month = Order.objects.filter(
        created_at__gte=last_month,
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).count()
    
    # Nuevos usuarios del último mes
    new_users_last_month = User.objects.filter(
        date_joined__gte=last_month
    ).count()
    
    # Ticket promedio
    avg_order_value = Order.objects.filter(
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).aggregate(avg=Avg('total'))['avg'] or 0
    
    # ==========================================
    # ÓRDENES RECIENTES
    # ==========================================
    recent_orders = Order.objects.select_related(
        'user',
        'user__profile'
    ).prefetch_related('items__product').order_by('-created_at')[:10]
    
    # ==========================================
    # GRÁFICO 1: VENTAS DIARIAS (Últimos 30 días)
    # ==========================================
    thirty_days_ago = today - timedelta(days=30)
    daily_sales = Order.objects.filter(
        created_at__gte=thirty_days_ago,
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total'),
        count=Count('id')
    ).order_by('date')
    
    # Preparar datos para Chart.js
    sales_labels = []
    sales_data = []
    sales_count = []
    
    for sale in daily_sales:
        sales_labels.append(sale['date'].strftime('%d/%m'))
        sales_data.append(float(sale['total']))
        sales_count.append(sale['count'])
    
    # ==========================================
    # GRÁFICO 2: VENTAS POR CATEGORÍA (Pastel)
    # ==========================================
    category_sales = OrderItem.objects.select_related(
        'product__category'
    ).values(
        'product__category__name'
    ).annotate(
        total=Sum(F('quantity') * F('price'))
    ).order_by('-total')[:6]  # Top 6 categorías
    
    category_labels = []
    category_data = []
    
    for cat in category_sales:
        if cat['product__category__name']:
            category_labels.append(cat['product__category__name'])
            category_data.append(float(cat['total']))
    
    # ==========================================
    # GRÁFICO 3: TOP 10 PRODUCTOS (Barras)
    # ==========================================
    top_products = OrderItem.objects.values(
        'product__name', 
        'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('price'))
    ).order_by('-revenue')[:10]
    
    products_labels = []
    products_revenue = []
    products_quantity = []
    
    for product in top_products:
        # Truncar nombres largos
        name = product['product__name']
        if len(name) > 20:
            name = name[:20] + '...'
        products_labels.append(name)
        products_revenue.append(float(product['revenue']))
        products_quantity.append(product['total_sold'])
    
    # ==========================================
    # GRÁFICO 4: ÓRDENES POR ESTADO (Donut)
    # ==========================================
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    status_labels = []
    status_data = []
    status_colors = {
        'pending': '#fbbf24',
        'confirmed': '#3b82f6',
        'preparing': '#8b5cf6',
        'in_transit': '#06b6d4',
        'delivered': '#10b981',
        'cancelled': '#ef4444'
    }
    status_bg_colors = []
    
    for item in orders_by_status:
        status_labels.append(dict(Order.STATUS_CHOICES).get(item['status'], item['status']))
        status_data.append(item['count'])
        status_bg_colors.append(status_colors.get(item['status'], '#6b7280'))
    
    # ==========================================
    # GRÁFICO 5: USUARIOS REGISTRADOS (Área)
    # ==========================================
    users_by_month = User.objects.filter(
        date_joined__gte=today - timedelta(days=180)  # Últimos 6 meses
    ).annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    users_labels = []
    users_data = []
    
    for item in users_by_month:
        users_labels.append(item['month'].strftime('%B'))
        users_data.append(item['count'])
    
    # ==========================================
    # GRÁFICO 6: MÉTODOS DE PAGO (Barras horizontales)
    # ==========================================
    payment_methods = Order.objects.filter(
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total')
    ).order_by('-total')
    
    payment_labels = []
    payment_data = []
    
    for item in payment_methods:
        payment_labels.append(dict(Order.PAYMENT_CHOICES).get(item['payment_method'], item['payment_method']))
        payment_data.append(float(item['total']))
    
    # ==========================================
    # TABLA: VENTAS POR CATEGORÍA
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
    # CONTEXTO PARA EL TEMPLATE
    # ==========================================
    context = {
        # Estadísticas principales
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
        
        # Métricas de crecimiento
        'orders_last_month': orders_last_month,
        'new_users_last_month': new_users_last_month,
        'avg_order_value': avg_order_value,
        
        # Alertas
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
        'out_of_stock': out_of_stock,
        
        # Datos para tablas
        'recent_orders': recent_orders,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        
        # Datos para gráficos (JSON)
        'sales_labels': json.dumps(sales_labels),
        'sales_data': json.dumps(sales_data),
        'sales_count': json.dumps(sales_count),
        
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        
        'products_labels': json.dumps(products_labels),
        'products_revenue': json.dumps(products_revenue),
        'products_quantity': json.dumps(products_quantity),
        
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'status_colors': json.dumps(status_bg_colors),
        
        'users_labels': json.dumps(users_labels),
        'users_data': json.dumps(users_data),
        
        'payment_labels': json.dumps(payment_labels),
        'payment_data': json.dumps(payment_data),
    }
    
    return render(request, 'shop/admin/dashboard.html', context)