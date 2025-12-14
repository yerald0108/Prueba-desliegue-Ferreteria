"""
Vistas de gestión del carrito de compras.

Maneja:
- Visualización del carrito
- Agregar productos
- Actualizar cantidades
- Eliminar productos
- Vaciar carrito
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction

from ..models import Product, Cart, CartItem


@login_required
def cart_view(request):
    """Ver carrito de compras"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    context = {
        'cart': cart,
    }
    return render(request, 'shop/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    """
    Agregar producto al carrito con validación de stock.
    
    TODO: Implementar select_for_update() para prevenir race conditions
    en ambientes de alta concurrencia.
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    # Validación básica de cantidad
    if quantity <= 0:
        return JsonResponse({
            'success': False,
            'message': 'Cantidad inválida'
        })
    
    # Validar stock disponible
    if quantity > product.stock:
        return JsonResponse({
            'success': False,
            'message': f'Solo hay {product.stock} unidades disponibles'
        })
    
    # Usar transacción para operaciones atómicas
    with transaction.atomic():
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Item ya existe, incrementar cantidad
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Solo hay {product.stock} unidades disponibles'
                })
            cart_item.quantity = new_quantity
            cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Producto agregado al carrito',
        'cart_count': cart.items_count
    })


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Actualizar cantidad de un item en el carrito"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'Cantidad inválida'
        })
    
    # Validar cantidad positiva
    if quantity <= 0:
        # Si es 0 o negativo, eliminar el item
        cart_item.delete()
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'subtotal': 0,
            'cart_total': float(cart.total),
            'cart_count': cart.items_count
        })
    
    # Validar stock disponible
    if quantity > cart_item.product.stock:
        return JsonResponse({
            'success': False,
            'message': f'Solo hay {cart_item.product.stock} unidades disponibles'
        })
    
    # Actualizar cantidad
    cart_item.quantity = quantity
    cart_item.save()
    
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