from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import TruncDate, TruncMonth
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F, ExpressionWrapper, DecimalField
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
from .email_utils import (
    send_verification_email, 
    send_order_confirmation_email,
    send_order_status_update_email,
    send_welcome_email
)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import uuid
from decimal import Decimal
import json
from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserProfile
from .forms import UserRegistrationForm, UserProfileForm, CheckoutForm, ProductForm


def home(request):
    """Vista principal de la tienda"""
    featured_products = Product.objects.filter(is_active=True, featured=True)[:8]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)


def product_detail(request, pk):
    """Detalle de producto"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def register(request):
    """Registro de usuario"""
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        
        if user_form.is_valid():
            # Crear usuario
            user = user_form.save(commit=False)
            user.is_active = True
            user.save()
            
            # Crear perfil vacío (se completará en /perfil/)
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': '',
                    'address': '',
                    'city': '',
                    'province': '',
                    'email_verified': False,
                }
            )
            
            send_verification_email(user, request)
            login(request, user)
            messages.success(request, '¡Cuenta creada! Por favor verifica tu email para mayor seguridad.')
            return redirect('shop:profile')
    else:
        user_form = UserRegistrationForm()
    
    context = {
        'user_form': user_form,
    }
    return render(request, 'shop/register.html', context)


def verify_email(request, token):
    """Verificar email del usuario"""
    try:
        profile = UserProfile.objects.get(verification_token=token)

        # Verificar si el token no ha expirado
        if not profile.is_verification_token_valid():
            messages.error(
                request, 
                'El enlace de verificación ha expirado. Por favor solicita uno nuevo.'
            )
            return redirect('shop:resend_verification')
        
        profile.email_verified = True
        profile.verification_token = None
        profile.verification_token_created = None
        profile.user.is_active = True
        profile.user.save()
        profile.save()
        send_welcome_email(profile.user)
        return render(request, 'shop/emails/verification_success.html', {
            'user': profile.user,
            'profile': profile,
            'site_name': settings.SITE_NAME,
        })
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'Token de verificación inválido.')
        return redirect('shop:home')

def resend_verification(request):
    """Reenviar email de verificación"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            user = User.objects.get(email=email, is_active=False)
            
            if user.profile.email_verified:
                messages.info(request, 'Esta cuenta ya ha sido verificada.')
                return redirect('shop:login')
            
            # Reenviar email
            if send_verification_email(user, request):
                messages.success(
                    request,
                    f'Email de verificación reenviado a {email}. Por favor revisa tu bandeja de entrada.'
                )
            else:
                messages.error(
                    request,
                    'Hubo un problema al enviar el email. Por favor intenta más tarde.'
                )
                
        except User.DoesNotExist:
            # No revelar si el email existe o no (seguridad)
            messages.info(
                request,
                'Si existe una cuenta con ese email, recibirás un nuevo enlace de verificación.'
            )
        
        return redirect('shop:login')
    
    return render(request, 'shop/emails/resend_verification.html')


def user_login(request):
    """Login de usuario"""
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect': 'shop:home'})
        return redirect('shop:home')
    
    if request.method == 'POST':
        # Ahora el usuario inicia sesión principalmente con su correo electrónico.
        # También aceptamos el username como respaldo por si el usuario lo introduce.
        raw_identifier = request.POST.get('email') or request.POST.get('username') or ''
        identifier = raw_identifier.strip()
        password = request.POST.get('password')

        user = None
        if identifier:
            try:
                from django.contrib.auth.models import User

                # 1) Intentar encontrar por email (case-insensitive)
                user_obj = User.objects.filter(email__iexact=identifier).first()

                # 2) Si no se encuentra por email, intentar por username
                if not user_obj:
                    user_obj = User.objects.filter(username__iexact=identifier).first()

                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
            except Exception:
                user = None
        
        if user is not None:
            if user.is_active:
                login(request, user)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    next_url = request.GET.get('next', 'shop:home')
                    return JsonResponse({'success': True, 'redirect': next_url})
                next_url = request.GET.get('next', 'shop:home')
                return redirect(next_url)
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Por favor verifica tu correo electrónico primero.'}, status=400)
                messages.error(request, 'Por favor verifica tu correo electrónico primero.')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos.'}, status=400)
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'shop/login.html')


@login_required
def user_logout(request):
    """Logout de usuario"""
    logout(request)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'redirect': 'shop:home'})
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('shop:home')


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
    """Agregar producto al carrito"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        return JsonResponse({
            'success': False,
            'message': f'Solo hay {product.stock} unidades disponibles'
        })
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
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
    """Actualizar cantidad en carrito"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > cart_item.product.stock:
        return JsonResponse({
            'success': False,
            'message': f'Solo hay {cart_item.product.stock} unidades disponibles'
        })
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'subtotal': float(cart_item.subtotal) if quantity > 0 else 0,
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


@login_required
def checkout(request):
    """Proceso de checkout"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('shop:cart')
    
    # Verificar stock
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f'No hay suficiente stock de {item.product.name}')
            return redirect('shop:cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            # Crear orden
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
            order.subtotal = cart.total
            order.delivery_fee = Decimal('5.00')  # Fee fijo, puedes hacer esto dinámico
            order.total = order.subtotal + order.delivery_fee
            order.save()
            
            # Crear items de la orden
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                
                # Reducir stock
                item.product.stock -= item.quantity
                item.product.save()
            
            # Limpiar carrito
            cart.items.all().delete()
            
            # Enviar email de confirmación
            if send_order_confirmation_email(order):
                messages.success(
                    request, 
                    f'¡Orden realizada exitosamente! Número de orden: {order.order_number}. '
                    'Te hemos enviado un email de confirmación.'
                )
            else:
                messages.warning(
                    request,
                    f'¡Orden realizada exitosamente! Número de orden: {order.order_number}. '
                    'Sin embargo, hubo un problema al enviar el email de confirmación.'
                )
            
            return redirect('shop:order_detail', order_id=order.id)
    else:
        # Pre-llenar con datos del perfil
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
    """Detalle de orden"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)


@login_required
def order_history(request):
    """Historial de órdenes"""
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_history.html', context)


@login_required
def profile(request):
    """Perfil de usuario"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('shop:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'shop/profile.html', context)

@staff_member_required
def admin_dashboard(request):
    """Dashboard principal de administración"""
    # Estadísticas generales
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    total_revenue = Order.objects.filter(
        status__in=['confirmed', 'preparing', 'in_transit', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0
    
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
    
    # Órdenes recientes
    recent_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')[:10]
    
    # Ventas por día (últimos 7 días)
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
    
    # Productos más vendidos
    top_products = OrderItem.objects.values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:5]
    
    # Ventas por categoría
    sales_by_category = OrderItem.objects.select_related('product__category').values(
        'product__category__name'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('price'))
    ).order_by('-revenue')
    
    # Preparar datos para gráficos
    chart_labels = [sale['date'].strftime('%d/%m') for sale in daily_sales]
    chart_data = [float(sale['total']) for sale in daily_sales]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
        'out_of_stock': out_of_stock,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'sales_by_category': sales_by_category,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'shop/admin/dashboard.html', context)


@staff_member_required
def admin_orders(request):
    """Gestión de órdenes"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    orders = Order.objects.select_related('user').prefetch_related('items')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'shop/admin/orders.html', context)


@staff_member_required
def admin_order_detail(request, order_id):
    """Detalle y gestión de orden"""
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            old_status = order.status
            new_status = request.POST.get('status')
            
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                
                if new_status == 'cancelled':
                    cancellation_reason = request.POST.get('cancellation_reason', '').strip()
                    if cancellation_reason:
                        order.cancellation_reason = cancellation_reason
                    else:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'error': 'Debes proporcionar un motivo para cancelar la orden'
                            }, status=400)
                        messages.error(request, 'Debes proporcionar un motivo para cancelar la orden')
                        return redirect('shop:admin_order_detail', order_id=order.id)
                
                order.save()
                
                email_sent = False
                if old_status != new_status:
                    email_sent = send_order_status_update_email(order)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'Estado actualizado a {order.get_status_display()}',
                        'status': order.status,
                        'status_display': order.get_status_display(),
                        'email_sent': email_sent
                    })
                
                messages.success(request, f'Estado actualizado a {order.get_status_display()}')
                
                if old_status != new_status:
                    if email_sent:
                        messages.success(request, 'Email de actualización enviado al cliente.')
                    else:
                        messages.warning(request, 'No se pudo enviar el email de actualización.')
        
        elif action == 'update_notes':
            order.admin_notes = request.POST.get('admin_notes', '')
            order.save()
            
            # Si es petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Notas actualizadas correctamente'
                })
            
            messages.success(request, 'Notas actualizadas correctamente')
        
        # Si no es AJAX, redirigir normalmente
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return redirect('shop:admin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'shop/admin/order_detail.html', context)


@staff_member_required
def admin_products(request):
    """Gestión de productos"""
    category_filter = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    search_query = request.GET.get('q', '')
    
    products = Product.objects.select_related('category')
    
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
def admin_users(request):
    """Gestión de usuarios"""
    search_query = request.GET.get('q', '')
    
    users = User.objects.select_related('profile').annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total')
    )
    
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
    """Detalle completo de un usuario para administración"""
    user = get_object_or_404(User.objects.select_related('profile'), pk=user_id)

    orders = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')
    order_count = orders.count()
    aggregates = orders.aggregate(total_spent=Sum('total'), avg_order=Avg('total'))
    total_spent = aggregates['total_spent'] or 0
    avg_order = aggregates['avg_order'] or 0
    last_order = orders.first()

    status_breakdown = list(
        orders.values('status').annotate(count=Count('id'), total=Sum('total')).order_by()
    )

    distinct_products = OrderItem.objects.filter(order__user=user).values('product').distinct().count()
    top_products = OrderItem.objects.filter(order__user=user).values(
        'product__id', 'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        revenue=Sum(
            ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField(max_digits=12, decimal_places=2))
        )
    ).order_by('-total_quantity')[:10]

    cart = getattr(user, 'cart', None)

    context = {
        'detail_user': user,
        'profile': getattr(user, 'profile', None),
        'orders': orders,
        'order_count': order_count,
        'total_spent': total_spent,
        'avg_order': avg_order,
        'last_order': last_order,
        'status_breakdown': status_breakdown,
        'distinct_products': distinct_products,
        'top_products': top_products,
        'cart': cart,
    }

    return render(request, 'shop/admin/user_detail.html', context)


# @staff_member_required
# @require_POST
# def admin_user_toggle_active(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#     if request.user.pk == user.pk:
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({'success': False, 'error': 'No puedes cambiar tu propio estado.'}, status=400)
#         messages.error(request, 'No puedes cambiar tu propio estado.')
#         return redirect('shop:admin_user_detail', user_id=user.id)
#
#     user.is_active = not user.is_active
#     user.save()
#
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse({
#             'success': True,
#             'is_active': user.is_active,
#             'message': 'Usuario activado' if user.is_active else 'Usuario desactivado'
#         })
#
#     messages.success(request, 'Usuario activado' if user.is_active else 'Usuario desactivado')
#     return redirect('shop:admin_user_detail', user_id=user.id)


@staff_member_required
def admin_user_online_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    is_online = False
    for s in Session.objects.filter(expire_date__gt=timezone.now()):
        data = s.get_decoded()
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


@staff_member_required
@require_POST
def admin_toggle_product_status(request, product_id):
    """Activar/Desactivar producto"""
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
    """Actualizar stock de producto"""
    product = get_object_or_404(Product, pk=product_id)
    action = request.POST.get('action')
    
    if action == 'add':
        quantity = int(request.POST.get('quantity', 0))
        product.stock += quantity
    elif action == 'set':
        quantity = int(request.POST.get('quantity', 0))
        product.stock = quantity
    
    product.save()
    
    return JsonResponse({
        'success': True,
        'stock': product.stock,
        'message': 'Stock actualizado correctamente'
    })

def product_list(request):
    """Lista de productos con filtros y paginación inteligente"""
    products = Product.objects.filter(is_active=True)
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
        'popular': '-featured',  # Puedes cambiar esto por ventas reales
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
        # Si la página no es un entero, ir a la primera página
        page = 1
        products_page = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, ir a la última página válida
        if paginator.num_pages > 0:
            products_page = paginator.page(paginator.num_pages)
        else:
            # Si no hay productos, usar page(1) que creará una página vacía
            products_page = paginator.page(1)
    
    # Para AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        
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

@staff_member_required
def admin_product_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save(commit=False)
            
            # Generar SKU automático si está vacío
            if not product.sku:
                import uuid
                product.sku = f'PRD-{uuid.uuid4().hex[:8].upper()}'
            
            product.save()
            
            # Mensaje de éxito diferente según el estado
            if product.is_active:
                messages.success(
                    request, 
                    f'✅ ¡Producto "{product.name}" publicado exitosamente! '
                    f'Ya está visible para los clientes.'
                )
            else:
                messages.success(
                    request,
                    f'✅ Producto "{product.name}" guardado como borrador. '
                    f'Actívalo cuando quieras publicarlo.'
                )
            
            return redirect('shop:admin_product_detail', product_id=product.id)
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
def admin_product_detail(request, product_id):
    """Ver detalle del producto en admin"""
    product = get_object_or_404(Product, pk=product_id)
    
    # Estadísticas del producto
    total_sold = OrderItem.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    revenue = OrderItem.objects.filter(product=product).aggregate(
        total=Sum(
            ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField(max_digits=12, decimal_places=2))
        )
    )['total'] or 0
    
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
@require_POST
def admin_product_delete(request, product_id):
    """Eliminar producto"""
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
