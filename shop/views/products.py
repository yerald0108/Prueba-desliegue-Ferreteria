"""
Vistas públicas de productos.

Maneja:
- Página principal (home)
- Listado de productos con filtros
- Detalle de producto
"""

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string

from ..models import Product, Category


def home(request):
    """
    Vista principal de la tienda
    
    ✅ OPTIMIZADO: select_related para featured products
    """
    # ✅ OPTIMIZACIÓN: Cargar category con select_related
    featured_products = Product.objects.filter(
        is_active=True, 
        featured=True
    ).select_related('category')[:8]
    
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)


def product_list(request):
    """
    Lista de productos con filtros y paginación inteligente.
    
    ✅ OPTIMIZADO: select_related para category
    """
    # ✅ OPTIMIZACIÓN CLAVE
    products = Product.objects.filter(is_active=True).select_related('category')
    
    categories = Category.objects.all()
    
    # Filtro por categoría
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    # Ordenamiento
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-created_at',
        'oldest': 'created_at',
        'popular': '-featured',
    }
    if sort_by in valid_sorts:
        products = products.order_by(valid_sorts[sort_by])
    else:
        products = products.order_by('-created_at')
    
    # Paginación
    try:
        items_per_page = int(request.GET.get('per_page', 12))
        if items_per_page not in [12, 24, 36, 48]:
            items_per_page = 12
    except (ValueError, TypeError):
        items_per_page = 12
    
    paginator = Paginator(products, items_per_page)
    
    # Validar número de página
    try:
        page = int(request.GET.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    # Manejar paginación con validación completa
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        products_page = paginator.page(1)
    except EmptyPage:
        if paginator.num_pages > 0:
            products_page = paginator.page(paginator.num_pages)
        else:
            products_page = paginator.page(1)
    
    # Para AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_html = render_to_string('shop/partials/product_grid.html', {
            'products': products_page,
            'user': request.user,
        })
        
        return JsonResponse({
            'success': True,
            'html': products_html,
            'has_next': products_page.has_next(),
            'has_previous': products_page.has_previous(),
            'current_page': products_page.number,
            'total_pages': paginator.num_pages,
            'total_products': paginator.count,
            'start_index': products_page.start_index(),
            'end_index': products_page.end_index(),
        })
    
    context = {
        'products': products_page,
        'categories': categories,
        'current_category': category_slug,
        'query': query,
        'sort_by': sort_by,
        'items_per_page': items_per_page,
        'paginator': paginator,
    }
    
    return render(request, 'shop/product_list.html', context)


def product_detail(request, pk):
    """
    Detalle de producto con productos relacionados
    
    ✅ OPTIMIZADO: select_related para categorías
    """
    # ✅ OPTIMIZACIÓN
    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=pk, 
        is_active=True
    )
    
    # ✅ OPTIMIZACIÓN: Productos relacionados con category cargada
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(
        pk=pk
    ).select_related('category')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)