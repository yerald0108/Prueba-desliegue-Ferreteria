"""
Vistas de gestión de órdenes para administradores.

Maneja:
- Listado de órdenes con filtros
- Detalle de orden
- Actualización de estado
- Notas administrativas
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.http import JsonResponse

from ...models import Order, OrderItem
from ...email_utils import send_order_status_update_email


@staff_member_required
def admin_orders(request):
    """
    Listado de órdenes con filtros.
    
    ✅ OPTIMIZADO: Elimina N+1 en user y items
    """
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    # ✅ OPTIMIZACIÓN CLAVE: select_related para user, prefetch_related para items
    orders = Order.objects.select_related(
        'user',
        'user__profile'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product', 'product__category')
        )
    )
    
    # Aplicar filtros
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
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
    """
    Detalle de orden con gestión de estado y notas.
    
    ✅ OPTIMIZADO: Prefetch de items con productos
    """
    # ✅ OPTIMIZACIÓN: Cargar todo en un solo query
    order = get_object_or_404(
        Order.objects.select_related(
            'user',
            'user__profile'
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related(
                    'product',
                    'product__category'
                )
            )
        ),
        pk=order_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # ==========================================
        # ACCIÓN: Actualizar estado
        # ==========================================
        if action == 'update_status':
            old_status = order.status
            new_status = request.POST.get('status')
            
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                
                # Si se cancela, requerir motivo
                if new_status == 'cancelled':
                    cancellation_reason = request.POST.get('cancellation_reason', '').strip()
                    if cancellation_reason:
                        order.cancellation_reason = cancellation_reason
                    else:
                        error_msg = 'Debes proporcionar un motivo para cancelar la orden'
                        
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'error': error_msg
                            }, status=400)
                        
                        messages.error(request, error_msg)
                        return redirect('shop:admin_order_detail', order_id=order.id)
                
                order.save()
                
                # Enviar email si cambió el estado
                email_sent = False
                if old_status != new_status:
                    email_sent = send_order_status_update_email(order)
                
                # Respuesta AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Estado actualizado a {order.get_status_display()}',
                        'status': order.status,
                        'status_display': order.get_status_display(),
                        'email_sent': email_sent
                    })
                
                # Respuesta normal
                messages.success(request, f'Estado actualizado a {order.get_status_display()}')
                
                if old_status != new_status:
                    if email_sent:
                        messages.success(request, 'Email de actualización enviado al cliente.')
                    else:
                        messages.warning(request, 'No se pudo enviar el email de actualización.')
        
        # ==========================================
        # ACCIÓN: Actualizar notas
        # ==========================================
        elif action == 'update_notes':
            order.admin_notes = request.POST.get('admin_notes', '')
            order.save()
            
            # Respuesta AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Notas actualizadas correctamente'
                })
            
            messages.success(request, 'Notas actualizadas correctamente')
        
        # Redirigir si no es AJAX
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return redirect('shop:admin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'shop/admin/order_detail.html', context)