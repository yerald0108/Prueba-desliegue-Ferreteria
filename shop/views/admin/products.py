"""
Vistas de gestión de productos para administradores.

Maneja:
- Listado de productos con filtros
- Crear producto
- Editar producto
- Ver detalle con estadísticas
- Eliminar producto
- Toggle estado activo/inactivo
- Actualizar stock
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField
from django.http import JsonResponse
import uuid

from ...models import Product, Category, OrderItem
from ...forms import ProductForm


@staff_member_required
def admin_products(request):
    """
    Listado de productos con filtros.
    
    Filtros:
    - category: filtrar por slug de categoría
    - stock: 'low' (<=10) o 'out' (=0)
    - q: búsqueda por nombre, SKU o descripción
    """
    category_filter = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    search_query = request.GET.get('q', '')
    
    products = Product.objects.select_related('category')
    
    # Aplicar filtros
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    if stock_filter == 'low':
        products = products.filter(stock__lte=10, stock__gt=0)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    products = products.order_by('-created_at')
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'search_query': search_query,
    }
    
    return render(request, 'shop/admin/products.html', context)


@staff_member_required
def admin_product_detail(request, product_id):
    """
    Ver detalle del producto con estadísticas de ventas.
    
    Muestra:
    - Información del producto
    - Total vendido
    - Ingresos generados
    - Órdenes recientes
    """
    product = get_object_or_404(Product, pk=product_id)
    
    # Estadísticas del producto
    total_sold = OrderItem.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    revenue = OrderItem.objects.filter(product=product).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantity') * F('price'), 
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
    )['total'] or 0
    
    # Órdenes recientes que incluyen este producto
    recent_orders = OrderItem.objects.filter(
        product=product
    ).select_related('order__user').order_by('-order__created_at')[:10]
    
    context = {
        'product': product,
        'total_sold': total_sold,
        'revenue': revenue,
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/admin/product_detail_admin.html', context)


@staff_member_required
def admin_product_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save(commit=False)
            
            # Generar SKU automático si está vacío
            if not product.sku:
                product.sku = f'PRD-{uuid.uuid4().hex[:8].upper()}'
            
            product.save()
            
            # ✅ Mensaje según el estado del producto
            if product.is_active:
                messages.success(
                    request, 
                    f'Producto "{product.name}" publicado exitosamente'
                )
            else:
                messages.success(
                    request,
                    f'Producto "{product.name}" guardado como borrador'
                )
            
            return redirect('shop:admin_product_detail', product_id=product.id)
        else:
            # ✅ Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    
    context = {
        'form': form,
        'categories': categories,
        'is_new': True,
    }
    return render(request, 'shop/admin/product_form.html', context)


@staff_member_required
def admin_product_edit(request, product_id):
    """Editar producto existente"""
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            product = form.save()
            
            messages.success(
                request,
                f'✅ Producto "{product.name}" actualizado exitosamente.'
            )
            
            return redirect('shop:admin_product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    categories = Category.objects.all()
    
    context = {
        'form': form,
        'product': product,
        'categories': categories,
        'is_new': False,
    }
    return render(request, 'shop/admin/product_form.html', context)


@staff_member_required
@require_POST
def admin_product_delete(request, product_id):
    """
    Eliminar producto (solo si no tiene órdenes asociadas).
    
    Si tiene órdenes, sugiere desactivarlo en su lugar.
    """
    product = get_object_or_404(Product, pk=product_id)
    product_name = product.name
    
    # No eliminar si tiene órdenes asociadas
    if OrderItem.objects.filter(product=product).exists():
        return JsonResponse({
            'success': False,
            'message': 'No se puede eliminar este producto porque tiene órdenes asociadas. '
                      'Puedes desactivarlo en su lugar.'
        })
    
    product.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Producto "{product_name}" eliminado exitosamente.'
    })


@staff_member_required
@require_POST
def admin_toggle_product_status(request, product_id):
    """Activar/Desactivar producto (toggle)"""
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = not product.is_active
    product.save()
    
    return JsonResponse({
        'success': True,
        'is_active': product.is_active,
        'message': f'Producto {"activado" if product.is_active else "desactivado"} correctamente'
    })


@staff_member_required
@require_POST
def admin_update_stock(request, product_id):
    """
    Actualizar stock de producto.
    
    Acciones:
    - 'add': Incrementar stock
    - 'set': Establecer cantidad exacta
    """
    product = get_object_or_404(Product, pk=product_id)
    action = request.POST.get('action')
    
    try:
        quantity = int(request.POST.get('quantity', 0))
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'Cantidad inválida'
        })
    
    if action == 'add':
        product.stock += quantity
    elif action == 'set':
        product.stock = quantity
    else:
        return JsonResponse({
            'success': False,
            'message': 'Acción no válida'
        })
    
    product.save()
    
    return JsonResponse({
        'success': True,
        'stock': product.stock,
        'message': 'Stock actualizado correctamente'
    })