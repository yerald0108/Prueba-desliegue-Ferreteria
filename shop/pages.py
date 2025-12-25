"""
Vistas para páginas estáticas: Sobre Nosotros, Contacto, FAQ
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit


def about_us(request):
    """Página Sobre Nosotros"""
    context = {
        'page_title': 'Sobre Nosotros',
    }
    return render(request, 'shop/pages/about_us.html', context)


def faq(request):
    """Página de Preguntas Frecuentes"""
    # FAQs organizadas por categorías
    faqs = {
        'Pedidos y Envíos': [
            {
                'question': '¿Cuánto tiempo tarda la entrega?',
                'answer': 'Realizamos entregas en 24-48 horas dentro de la provincia. El tiempo exacto depende de tu ubicación.'
            },
            {
                'question': '¿Cuál es el costo de envío?',
                'answer': 'El costo de envío es de $5.00 para todos los pedidos dentro de la provincia. Ofertas especiales pueden incluir envío gratis.'
            },
            {
                'question': '¿Puedo cambiar la dirección de entrega después de hacer el pedido?',
                'answer': 'Sí, puedes cambiar la dirección mientras el pedido esté en estado "Pendiente". Contáctanos lo antes posible.'
            },
            {
                'question': '¿Entregan los fines de semana?',
                'answer': 'Sí, realizamos entregas de lunes a sábado en horarios de mañana, tarde y noche según tu preferencia.'
            },
        ],
        'Pagos': [
            {
                'question': '¿Qué métodos de pago aceptan?',
                'answer': 'Aceptamos pago en efectivo contra entrega y transferencias bancarias. Próximamente habilitaremos pagos con tarjeta.'
            },
            {
                'question': '¿Es seguro comprar en su sitio?',
                'answer': 'Sí, toda tu información está protegida. Usamos encriptación SSL y nunca almacenamos datos de tarjetas de crédito.'
            },
            {
                'question': '¿Puedo pagar al recibir el pedido?',
                'answer': 'Sí, aceptamos pago en efectivo al momento de la entrega. Es nuestra opción más popular.'
            },
        ],
        'Productos': [
            {
                'question': '¿Todos los productos tienen garantía?',
                'answer': 'Sí, todos nuestros productos cuentan con garantía del fabricante. El tiempo varía según el tipo de producto.'
            },
            {
                'question': '¿Qué hago si recibo un producto defectuoso?',
                'answer': 'Contáctanos inmediatamente. Realizamos cambios sin costo adicional si el producto llega defectuoso.'
            },
            {
                'question': '¿Puedo devolver un producto?',
                'answer': 'Sí, aceptamos devoluciones dentro de los 7 días siguientes a la entrega, siempre que el producto esté sin usar y en su empaque original.'
            },
            {
                'question': '¿Cómo sé si un producto está disponible?',
                'answer': 'El stock se actualiza en tiempo real en nuestra página. Si un producto muestra "Disponible", lo tenemos en inventario.'
            },
        ],
        'Cuenta': [
            {
                'question': '¿Necesito una cuenta para comprar?',
                'answer': 'Sí, necesitas crear una cuenta para realizar compras. Esto nos permite dar seguimiento a tus pedidos y brindarte un mejor servicio.'
            },
            {
                'question': '¿Cómo puedo cambiar mi contraseña?',
                'answer': 'Ve a "Mi Perfil" y selecciona "Cambiar Contraseña". Necesitarás tu contraseña actual para confirmar el cambio.'
            },
            {
                'question': '¿Puedo tener múltiples direcciones de entrega?',
                'answer': 'Actualmente solo puedes tener una dirección guardada en tu perfil, pero puedes especificar una dirección diferente en cada pedido.'
            },
            {
                'question': '¿Cómo verifico mi email?',
                'answer': 'Después de registrarte, te enviamos un email con un enlace de verificación. Haz clic en el enlace para activar tu cuenta.'
            },
        ],
        'Otros': [
            {
                'question': '¿Hacen entregas fuera de la provincia?',
                'answer': 'Actualmente solo realizamos entregas dentro de la provincia. Estamos trabajando para expandir nuestra cobertura.'
            },
            {
                'question': '¿Tienen tienda física?',
                'answer': 'Sí, tenemos una tienda física donde puedes visitar y ver nuestros productos. La dirección está en la sección de Contacto.'
            },
            {
                'question': '¿Ofrecen precios especiales para compras al por mayor?',
                'answer': 'Sí, ofrecemos descuentos especiales para compras al por mayor. Contáctanos para más información.'
            },
        ],
    }
    
    context = {
        'page_title': 'Preguntas Frecuentes',
        'faqs': faqs,
    }
    return render(request, 'shop/pages/faq.html', context)


@ratelimit(key='ip', rate='3/h', method='POST', block=True)
@require_http_methods(["GET", "POST"])
def contact(request):
    """
    Página de Contacto con formulario.
    Rate limit: 3 mensajes por hora por IP
    """
    # Verificar rate limit
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(
            request,
            'Has enviado demasiados mensajes. Por favor espera antes de intentar nuevamente.'
        )
        return render(request, 'shop/pages/contact.html', {
            'page_title': 'Contacto',
            'rate_limited': True
        })
    
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validaciones básicas
        errors = []
        if not name:
            errors.append('El nombre es requerido')
        if not email:
            errors.append('El email es requerido')
        if not subject:
            errors.append('El asunto es requerido')
        if not message:
            errors.append('El mensaje es requerido')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Enviar email
            try:
                full_message = f"""
Nuevo mensaje de contacto desde la web:

Nombre: {name}
Email: {email}
Asunto: {subject}

Mensaje:
{message}

---
Este mensaje fue enviado desde el formulario de contacto.
                """
                
                send_mail(
                    subject=f'[Contacto Web] {subject}',
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                
                messages.success(
                    request,
                    '¡Gracias por contactarnos! Tu mensaje ha sido enviado. '
                    'Te responderemos a la brevedad posible.'
                )
                return redirect('shop:contact')
                
            except Exception as e:
                messages.error(
                    request,
                    'Hubo un error al enviar tu mensaje. Por favor intenta nuevamente o contáctanos directamente.'
                )
                print(f"Error sending contact email: {e}")
    
    context = {
        'page_title': 'Contacto',
    }
    return render(request, 'shop/pages/contact.html', context)