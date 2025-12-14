"""
Vistas de autenticación y verificación de usuarios.

Maneja:
- Registro de usuarios
- Login/Logout
- Verificación de email
- Rate limiting para seguridad
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit

from ..models import UserProfile
from ..forms import UserRegistrationForm
from ..email_utils import send_verification_email, send_welcome_email

import logging

logger = logging.getLogger(__name__)


@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def register(request):
    """
    Registro de usuario con rate limiting.
    Límite: 3 registros por hora por IP
    """
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    # Verificar rate limit
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        logger.warning(f"Registration rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
        messages.error(
            request,
            'Demasiados intentos de registro. Por favor espera antes de intentar nuevamente.'
        )
        return render(request, 'shop/register.html', {
            'user_form': UserRegistrationForm()
        })

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


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='user_or_ip', rate='10/h', method='POST', block=True)
def user_login(request):
    """
    Login de usuario con rate limiting.
    
    Límites:
    - 5 intentos por minuto por IP
    - 10 intentos por hora por usuario/IP
    """
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect': 'shop:home'})
        return redirect('shop:home')
    
    # Verificar si fue bloqueado por rate limiting
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        logger.warning(f"Rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Demasiados intentos de inicio de sesión. Por favor espera unos minutos.'
            }, status=429)
        
        messages.error(
            request,
            'Demasiados intentos de inicio de sesión. Por favor espera unos minutos antes de intentar nuevamente.'
        )
        return render(request, 'shop/login.html')
    
    if request.method == 'POST':
        # Obtener credenciales
        raw_identifier = request.POST.get('email') or request.POST.get('username') or ''
        identifier = raw_identifier.strip()
        password = request.POST.get('password')

        user = None
        if identifier:
            try:
                # Intentar encontrar por email (case-insensitive)
                user_obj = User.objects.filter(email__iexact=identifier).first()

                # Si no se encuentra por email, intentar por username
                if not user_obj:
                    user_obj = User.objects.filter(username__iexact=identifier).first()

                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
                    
                    # Log de intento fallido
                    if user is None:
                        logger.warning(
                            f"Failed login attempt for identifier: {identifier} from IP: {request.META.get('REMOTE_ADDR')}"
                        )
            except Exception as e:
                logger.error(f"Login error for {identifier}: {e}")
                user = None
        
        if user is not None:
            if user.is_active:
                login(request, user)
                logger.info(f"Successful login for user: {user.username}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    next_url = request.GET.get('next', 'shop:home')
                    return JsonResponse({'success': True, 'redirect': next_url})
                
                next_url = request.GET.get('next', 'shop:home')
                return redirect(next_url)
            else:
                logger.warning(f"Login attempt for inactive user: {identifier}")
                error_msg = 'Por favor verifica tu correo electrónico primero.'
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
        else:
            error_msg = 'Usuario o contraseña incorrectos.'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
    
    return render(request, 'shop/login.html')


def user_logout(request):
    """Logout de usuario"""
    logout(request)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'redirect': 'shop:home'})
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('shop:home')


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