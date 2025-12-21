"""
Vistas para el sistema de wishlist (lista de deseos).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Prefetch

from ..models import Product, Wishlist, WishlistItem


@login_required
def wishlist_view(request):
    """
    Ver la lista de deseos del usuario.
    
    ✅ OPTIMIZADO: Prefetch de items con productos
    """
    wishlist, created = Wishlist.objects.prefetch_related(
        Prefetch(
            'items',
            queryset=WishlistItem.objects.select_related(
                'product',
                'product__category'
            ).order_by('-added_at')
        )
    ).get_or_create(user=request.user)
    
    context = {
        'wishlist': wishlist,
    }
    return render(request, 'shop/wishlist/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """
    Agregar producto a la wishlist.
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    # Obtener o crear wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Verificar si ya está en la wishlist
    item, item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if item_created:
        return JsonResponse({
            'success': True,
            'message': 'Producto agregado a tu lista de deseos',
            'wishlist_count': wishlist.items_count,
            'in_wishlist': True
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Este producto ya está en tu lista de deseos',
            'wishlist_count': wishlist.items_count,
            'in_wishlist': True
        })


@login_required
@require_POST
def remove_from_wishlist(request, item_id):
    """
    Remover producto de la wishlist.
    """
    item = get_object_or_404(
        WishlistItem,
        pk=item_id,
        wishlist__user=request.user
    )
    
    wishlist = item.wishlist
    item.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Producto eliminado de tu lista de deseos',
        'wishlist_count': wishlist.items_count
    })


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    """
    Toggle: agregar o quitar de wishlist.
    Útil para botones de favorito.
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    try:
        # Si existe, eliminarlo
        item = WishlistItem.objects.get(
            wishlist=wishlist,
            product=product
        )
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Eliminado de favoritos',
            'in_wishlist': False,
            'wishlist_count': wishlist.items_count
        })
    except WishlistItem.DoesNotExist:
        # Si no existe, agregarlo
        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Agregado a favoritos',
            'in_wishlist': True,
            'wishlist_count': wishlist.items_count
        })


@login_required
@require_POST
def move_to_cart(request, item_id):
    """
    Mover producto de wishlist al carrito.
    """
    from ..models import Cart, CartItem
    
    item = get_object_or_404(
        WishlistItem,
        pk=item_id,
        wishlist__user=request.user
    )
    
    product = item.product
    
    # Verificar stock
    if product.stock <= 0:
        return JsonResponse({
            'success': False,
            'message': 'Este producto está agotado'
        })
    
    # Agregar al carrito
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not item_created:
        # Si ya está en el carrito, incrementar cantidad
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            return JsonResponse({
                'success': False,
                'message': f'Solo hay {product.stock} unidades disponibles'
            })
    
    # Remover de wishlist
    item.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Producto movido al carrito',
        'cart_count': cart.items_count,
        'wishlist_count': item.wishlist.items_count
    })


@login_required
@require_POST
def clear_wishlist(request):
    """Vaciar toda la wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.items.all().delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Lista de deseos vaciada',
        'wishlist_count': 0
    })