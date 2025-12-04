from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


def send_verification_email(user, request):
    """Enviar email de verificación al usuario"""
    profile = user.profile
    token = profile.generate_verification_token()
    
    # Construir URL de verificación usando SITE_URL de settings
    verification_url = settings.SITE_URL.rstrip('/') + reverse('shop:verify_email', kwargs={'token': token})
    
    # Contexto para el template
    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    }
    
    # Renderizar email HTML
    html_content = render_to_string('shop/emails/verification_email.html', context)
    text_content = strip_tags(html_content)
    
    # Crear email
    subject = f'Verifica tu cuenta en {settings.SITE_NAME}'
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar email de verificación: {e}")
        return False


def send_order_confirmation_email(order):
    """Enviar email de confirmación de orden"""
    user = order.user
    
    context = {
        'user': user,
        'order': order,
        'items': order.items.all(),
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    }
    
    # Renderizar email HTML
    html_content = render_to_string('shop/emails/order_confirmation.html', context)
    text_content = strip_tags(html_content)
    
    subject = f'Confirmación de Orden {order.order_number}'
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar email de confirmación: {e}")
        return False


def send_order_status_update_email(order):
    """Enviar email cuando cambia el estado de la orden"""
    user = order.user
    
    context = {
        'user': user,
        'order': order,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    }
    
    html_content = render_to_string('shop/emails/order_status_update.html', context)
    text_content = strip_tags(html_content)
    
    subject = f'Actualización de tu Orden {order.order_number}'
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar email de actualización: {e}")
        return False


def send_welcome_email(user):
    """Enviar email de bienvenida después de verificar"""
    context = {
        'user': user,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    }
    
    html_content = render_to_string('shop/emails/welcome_email.html', context)
    text_content = strip_tags(html_content)
    
    subject = f'¡Bienvenido a {settings.SITE_NAME}!'
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar email de bienvenida: {e}")
        return False