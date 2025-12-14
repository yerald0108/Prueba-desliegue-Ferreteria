"""
Vistas de órdenes y checkout.

Maneja:
- Proceso de checkout con transacciones atómicas
- Detalle de orden
- Historial de órdenes del usuario
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from decimal import Decimal
import uuid
import logging

from ..models import Cart, Order, OrderItem
from ..forms import CheckoutForm
from ..email_utils import send_order_confirmation_email

logger = logging.getLogger(__name__)


@login_required
def checkout(request):
    """
    Proceso de checkout con transacciones atómicas.
    
    Si algo falla durante el proceso, TODO se revierte automáticamente
    gracias al uso de transaction.atomic().
    
    Pasos:
    1. Validar que el carrito no esté vacío
    2. Validar stock disponible (con lock pessimista)
    3. Crear la orden
    4. Crear items de la orden
    5. Actualizar stock de productos
    6. Limpiar carrito
    7. Enviar email de confirmación (fuera de transacción)
    """
    # Obtener carrito con prefetch para evitar queries extras
    cart = get_object_or_404(
        Cart.objects.select_related('user').prefetch_related('items__product'),
        user=request.user
    )
    
    # ==========================================
    # VALIDACIÓN 1: Verificar que hay items
    # ==========================================
    if not cart.items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('shop:cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            try:
                # ==========================================
                # INICIO DE TRANSACCIÓN ATÓMICA
                # ==========================================
                with transaction.atomic():
                    # ==========================================
                    # VALIDACIÓN 2: Verificar stock con LOCK
                    # select_for_update() bloquea los registros
                    # ==========================================
                    cart_items = cart.items.select_for_update().select_related('product')
                    
                    insufficient_stock = []
                    for item in cart_items:
                        if item.quantity > item.product.stock:
                            insufficient_stock.append(
                                f"{item.product.name} (disponible: {item.product.stock})"
                            )
                    
                    if insufficient_stock:
                        raise ValueError(
                            f"Stock insuficiente para: {', '.join(insufficient_stock)}"
                        )
                    
                    # ==========================================
                    # PASO 1: Crear la orden
                    # ==========================================
                    order = form.save(commit=False)
                    order.user = request.user
                    order.order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
                    order.subtotal = cart.total
                    order.delivery_fee = Decimal('5.00')  # TODO: Hacer dinámico
                    order.total = order.subtotal + order.delivery_fee
                    order.save()
                    
                    logger.info(f"Order created: {order.order_number} for user {request.user.username}")
                    
                    # ==========================================
                    # PASO 2: Crear items de la orden
                    # ==========================================
                    order_items_to_create = []
                    products_to_update = []
                    
                    for item in cart_items:
                        # Crear item de orden
                        order_items_to_create.append(
                            OrderItem(
                                order=order,
                                product=item.product,
                                quantity=item.quantity,
                                price=item.product.price
                            )
                        )
                        
                        # Preparar actualización de stock
                        # Usar F() para actualización atómica
                        item.product.stock = F('stock') - item.quantity
                        products_to_update.append(item.product)
                    
                    # Bulk create para mejor rendimiento
                    OrderItem.objects.bulk_create(order_items_to_create)
                    
                    # ==========================================
                    # PASO 3: Actualizar stock atómicamente
                    # ==========================================
                    for product in products_to_update:
                        product.save(update_fields=['stock'])
                    
                    # ==========================================
                    # PASO 4: Limpiar carrito
                    # ==========================================
                    cart.items.all().delete()
                    
                    logger.info(f"Order {order.order_number} completed successfully")
                
                # ==========================================
                # FIN DE TRANSACCIÓN ATÓMICA
                # ==========================================
                
                # ==========================================
                # PASO 5: Enviar email (fuera de transacción)
                # ==========================================
                email_sent = False
                try:
                    email_sent = send_order_confirmation_email(order)
                    if email_sent:
                        logger.info(f"Confirmation email sent for order {order.order_number}")
                    else:
                        logger.warning(f"Failed to send confirmation email for order {order.order_number}")
                except Exception as e:
                    logger.error(
                        f"Exception sending email for order {order.order_number}: {e}",
                        exc_info=True
                    )
                
                # ==========================================
                # Mensaje de éxito
                # ==========================================
                if email_sent:
                    messages.success(
                        request,
                        f'¡Orden {order.order_number} realizada exitosamente! '
                        'Te hemos enviado un email de confirmación.'
                    )
                else:
                    messages.success(
                        request,
                        f'¡Orden {order.order_number} realizada exitosamente!'
                    )
                    messages.warning(
                        request,
                        'No pudimos enviar el email de confirmación, pero tu orden fue procesada. '
                        'Puedes ver los detalles en "Mis Órdenes".'
                    )
                
                return redirect('shop:order_detail', order_id=order.id)
                
            except ValueError as e:
                # Error de validación (ej: stock insuficiente)
                logger.warning(f"Checkout validation error for user {request.user.username}: {e}")
                messages.error(request, str(e))
            except Exception as e:
                # Error inesperado
                logger.exception(f"Unexpected checkout error for user {request.user.username}: {e}")
                messages.error(
                    request,
                    'Ocurrió un error procesando tu orden. Por favor intenta nuevamente. '
                    'Si el problema persiste, contacta con soporte.'
                )
    else:
        # ==========================================
        # GET: Pre-llenar con datos del perfil
        # ==========================================
        initial_data = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data = {
                'delivery_address': profile.address,
                'delivery_city': profile.city,
                'delivery_province': profile.province,
                'contact_phone': profile.phone,
            }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def order_detail(request, order_id):
    """Detalle de orden del usuario"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)


@login_required
def order_history(request):
    """Historial de órdenes del usuario"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_history.html', context)