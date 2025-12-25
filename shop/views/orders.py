"""
Vistas de órdenes y checkout.

Maneja:
- Proceso de checkout con transacciones atómicas
- Detalle de orden
- Historial de órdenes del usuario

✅ COMPLETAMENTE OPTIMIZADO - Sin N+1 queries
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Prefetch
from decimal import Decimal
import uuid
import logging

from ..models import Cart, Order, OrderItem, CartItem
from ..forms import CheckoutStep1Form, CheckoutStep2Form, CheckoutStep3Form
from ..email_utils import send_order_confirmation_email

logger = logging.getLogger(__name__)


@login_required
def checkout(request):
    """
    Checkout multi-paso con progreso visual.
    
    Pasos:
    1. Información de entrega
    2. Fecha, hora y método de pago
    3. Revisión y confirmación
    """
    
    # Cargar carrito optimizado
    cart = get_object_or_404(
        Cart.objects.select_related('user').prefetch_related(
            Prefetch(
                'items',
                queryset=CartItem.objects.select_related(
                    'product',
                    'product__category'
                )
            )
        ),
        user=request.user
    )
    
    # Validar que hay items
    if not cart.items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('shop:cart')
    
    # Obtener paso actual (default: 1)
    current_step = int(request.GET.get('step', 1))
    if current_step not in [1, 2, 3]:
        current_step = 1
    
    # Obtener datos guardados en sesión
    checkout_data = request.session.get('checkout_data', {})
    
    # Pre-llenar con datos del perfil si es paso 1 y no hay datos guardados
    if current_step == 1 and not checkout_data.get('step1'):
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            checkout_data['step1'] = {
                'delivery_address': profile.address,
                'delivery_city': profile.city,
                'delivery_province': profile.province,
                'contact_phone': profile.phone,
            }
    
    # POST: Procesar formulario del paso actual
    if request.method == 'POST':
        
        # =============================================
        # PASO 1: Información de Entrega
        # =============================================
        if current_step == 1:
            form = CheckoutStep1Form(request.POST)
            if form.is_valid():
                # Guardar en sesión
                checkout_data['step1'] = form.cleaned_data
                request.session['checkout_data'] = checkout_data
                request.session.modified = True
                
                # Ir a paso 2
                return redirect('shop:checkout' + '?step=2')
            else:
                # Mostrar errores
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{form.fields[field].label}: {error}')
        
        # =============================================
        # PASO 2: Fecha, Hora y Pago
        # =============================================
        elif current_step == 2:
            # Validar que completó paso 1
            if not checkout_data.get('step1'):
                messages.error(request, 'Por favor completa el paso anterior.')
                return redirect('shop:checkout' + '?step=1')
            
            form = CheckoutStep2Form(request.POST)
            if form.is_valid():
                # Guardar en sesión
                checkout_data['step2'] = form.cleaned_data
                request.session['checkout_data'] = checkout_data
                request.session.modified = True
                
                # Ir a paso 3
                return redirect('shop:checkout' + '?step=3')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{form.fields[field].label}: {error}')
        
        # =============================================
        # PASO 3: Confirmación y Creación de Orden
        # =============================================
        elif current_step == 3:
            # Validar pasos anteriores
            if not checkout_data.get('step1') or not checkout_data.get('step2'):
                messages.error(request, 'Por favor completa todos los pasos.')
                return redirect('shop:checkout' + '?step=1')
            
            form = CheckoutStep3Form(request.POST)
            if form.is_valid():
                try:
                    # TRANSACCIÓN ATÓMICA
                    with transaction.atomic():
                        # Validar stock con lock
                        cart_items = cart.items.select_for_update(nowait=True).select_related('product')
                        
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
                        
                        # Crear orden
                        order = Order()
                        order.user = request.user
                        order.order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
                        
                        # Datos del paso 1
                        step1_data = checkout_data['step1']
                        order.delivery_address = step1_data['delivery_address']
                        order.delivery_city = step1_data['delivery_city']
                        order.delivery_province = step1_data['delivery_province']
                        order.contact_phone = step1_data['contact_phone']
                        
                        # Datos del paso 2
                        step2_data = checkout_data['step2']
                        order.delivery_date = step2_data['delivery_date']
                        order.delivery_time = step2_data['delivery_time']
                        order.payment_method = step2_data['payment_method']
                        
                        # Datos del paso 3
                        order.notes = form.cleaned_data.get('notes', '')
                        
                        # Calcular totales
                        order.subtotal = cart.total
                        order.delivery_fee = Decimal('5.00')
                        order.total = order.subtotal + order.delivery_fee
                        
                        order.save()
                        
                        logger.info(f"Order created: {order.order_number} for user {request.user.username}")
                        
                        # Crear items de orden
                        order_items_to_create = []
                        products_to_update = []
                        
                        for item in cart_items:
                            order_items_to_create.append(
                                OrderItem(
                                    order=order,
                                    product=item.product,
                                    quantity=item.quantity,
                                    price=item.product.price
                                )
                            )
                            
                            item.product.stock = F('stock') - item.quantity
                            products_to_update.append(item.product)
                        
                        OrderItem.objects.bulk_create(order_items_to_create)
                        
                        # Actualizar stock
                        for product in products_to_update:
                            product.save(update_fields=['stock'])
                        
                        # Limpiar carrito
                        cart.items.all().delete()
                        
                        # Limpiar sesión
                        if 'checkout_data' in request.session:
                            del request.session['checkout_data']
                        
                        logger.info(f"Order {order.order_number} completed successfully")
                    
                    # Enviar email
                    email_sent = False
                    try:
                        email_sent = send_order_confirmation_email(order)
                        if email_sent:
                            logger.info(f"Confirmation email sent for order {order.order_number}")
                    except Exception as e:
                        logger.error(f"Exception sending email for order {order.order_number}: {e}")
                    
                    # Mensajes de éxito
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
                    
                    return redirect('shop:order_detail', order_id=order.id)
                    
                except ValueError as e:
                    logger.warning(f"Checkout validation error: {e}")
                    messages.error(request, str(e))
                except Exception as e:
                    logger.exception(f"Unexpected checkout error: {e}")
                    messages.error(
                        request,
                        'Ocurrió un error procesando tu orden. Por favor intenta nuevamente.'
                    )
    
    # GET: Mostrar formulario del paso actual
    if current_step == 1:
        initial_data = checkout_data.get('step1', {})
        form = CheckoutStep1Form(initial=initial_data)
        template = 'shop/checkout_step1.html'
        
    elif current_step == 2:
        # Validar que completó paso 1
        if not checkout_data.get('step1'):
            messages.warning(request, 'Por favor completa el paso anterior.')
            return redirect('shop:checkout' + '?step=1')
        
        initial_data = checkout_data.get('step2', {})
        form = CheckoutStep2Form(initial=initial_data)
        template = 'shop/checkout_step2.html'
        
    elif current_step == 3:
        # Validar pasos anteriores
        if not checkout_data.get('step1') or not checkout_data.get('step2'):
            messages.warning(request, 'Por favor completa todos los pasos.')
            return redirect('shop:checkout' + '?step=1')
        
        initial_data = checkout_data.get('step3', {})
        form = CheckoutStep3Form(initial=initial_data)
        template = 'shop/checkout_step3.html'
    
    context = {
        'form': form,
        'cart': cart,
        'current_step': current_step,
        'checkout_data': checkout_data,
    }
    
    return render(request, template, context)


@login_required
def order_detail(request, order_id):
    """
    Detalle de orden del usuario
    
    ✅ OPTIMIZADO: Prefetch de items con productos
    """
    # ✅ OPTIMIZACIÓN: Cargar orden con items y productos en un query
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related(
                    'product',
                    'product__category'
                )
            )
        ),
        pk=order_id,
        user=request.user
    )
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)


@login_required
def order_history(request):
    """
    Historial de órdenes del usuario
    
    ✅ OPTIMIZADO: Prefetch de items con productos
    """
    # ✅ OPTIMIZACIÓN: Cargar órdenes con items en un query
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product', 'product__category')
        )
    ).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_history.html', context)