"""
Vistas de gestión del carrito de compras.

CORRECCIÓN: Race condition en add_to_cart usando select_for_update()
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Prefetch

from ..models import Product, Cart, CartItem


@login_required
def cart_view(request):
    """
    Ver carrito de compras
    
    ✅ OPTIMIZADO: Prefetch de items con productos
    """
    # ✅ OPTIMIZACIÓN: Cargar cart con items y productos en un query
    cart, created = Cart.objects.prefetch_related(
        Prefetch(
            'items',
            queryset=CartItem.objects.select_related(
                'product',
                'product__category'
            ).order_by('-added_at')
        )
    ).get_or_create(user=request.user)
    
    context = {
        'cart': cart,
    }
    return render(request, 'shop/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    """
    Agregar producto al carrito con validación de stock THREAD-SAFE.
    
    CORRECCIÓN: Usa select_for_update() para prevenir race conditions.
    
    Flujo:
    1. Bloquea el producto con select_for_update()
    2. Verifica stock disponible
    3. Crea/actualiza item del carrito
    4. Todo dentro de una transacción atómica
    
    Si dos usuarios compran simultáneamente, el segundo esperará
    hasta que el primero termine, garantizando datos consistentes.
    """
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'Cantidad inválida'
        })
    
    # Validación básica
    if quantity <= 0:
        return JsonResponse({
            'success': False,
            'message': 'Cantidad debe ser mayor a 0'
        })
    
    # ==========================================
    # TRANSACCIÓN ATÓMICA CON LOCK PESIMISTA
    # ==========================================
    with transaction.atomic():
        # PASO 1: Bloquear el producto para esta transacción
        # select_for_update() evita que otros procesos lean/modifiquen
        # este producto hasta que terminemos
        try:
            product = Product.objects.select_for_update().get(
                pk=product_id,
                is_active=True
            )
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Producto no disponible'
            })
        
        # PASO 2: Verificar stock (ahora es thread-safe)
        if quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Solo hay {product.stock} unidades disponibles'
            })
        
        # PASO 3: Obtener o crear carrito
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # PASO 4: Obtener o crear item del carrito
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # Item ya existe, verificar que podemos agregar más
            new_quantity = cart_item.quantity + quantity
            
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Solo hay {product.stock} unidades disponibles. '
                            f'Ya tienes {cart_item.quantity} en tu carrito.'
                })
            
            cart_item.quantity = new_quantity
            cart_item.save()
    
    # ==========================================
    # FIN DE TRANSACCIÓN ATÓMICA
    # ==========================================
    
    return JsonResponse({
        'success': True,
        'message': 'Producto agregado al carrito',
        'cart_count': cart.items_count
    })


@login_required
@require_POST
def update_cart_item(request, item_id):
    """
    Actualizar cantidad de un item en el carrito.
    
    CORRECCIÓN: También usa select_for_update() para prevenir
    problemas de concurrencia al actualizar cantidades.
    """
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'Cantidad inválida'
        })
    
    # Si la cantidad es 0 o negativa, eliminar el item
    if quantity <= 0:
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        cart_item.delete()
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'subtotal': 0,
            'cart_total': float(cart.total),
            'cart_count': cart.items_count
        })
    
    # ==========================================
    # TRANSACCIÓN ATÓMICA CON LOCK
    # ==========================================
    with transaction.atomic():
        # Bloquear el cart_item y su producto relacionado
        cart_item = CartItem.objects.select_related('product').select_for_update().get(
            pk=item_id,
            cart__user=request.user
        )
        
        # Verificar stock disponible
        if quantity > cart_item.product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Solo hay {cart_item.product.stock} unidades disponibles'
            })
        
        # Actualizar cantidad
        cart_item.quantity = quantity
        cart_item.save()
    
    # Calcular nuevos totales
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'subtotal': float(cart_item.subtotal),
        'cart_total': float(cart.total),
        'cart_count': cart.items_count
    })


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Eliminar producto del carrito"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    
    cart = Cart.objects.get(user=request.user)
    return JsonResponse({
        'success': True,
        'message': 'Producto eliminado del carrito',
        'cart_total': float(cart.total),
        'cart_count': cart.items_count
    })


@login_required
@require_POST
def clear_cart(request):
    """Vaciar todo el carrito del usuario"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()

    return JsonResponse({
        'success': True,
        'message': 'Carrito vaciado correctamente',
        'cart_total': 0.0,
        'cart_count': 0
    })