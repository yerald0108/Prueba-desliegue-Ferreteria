"""
Vistas de perfil de usuario.

Maneja:
- Visualización y edición de perfil
- Cambio de contraseña
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..forms import UserProfileForm, ChangePasswordForm
from ..email_utils import send_password_change_email


@login_required
def profile(request):
    """
    Perfil de usuario con formulario de edición.
    
    Permite editar:
    - Teléfono
    - Dirección
    - Ciudad
    - Provincia
    """
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


@login_required
def change_password(request):
    """
    Vista para cambiar contraseña con validaciones de seguridad.
    
    Validaciones:
    - Contraseña actual correcta
    - Nueva contraseña cumple requisitos de Django
    - Confirmación de contraseña coincide
    
    Después de cambiar:
    - Actualiza la sesión (no cierra sesión)
    - Envía email de notificación
    """
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            # Guardar nueva contraseña
            user = form.save()
            
            # Actualizar la sesión para que no se cierre
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            
            # Enviar email de notificación
            email_sent = send_password_change_email(user, request)
            
            if email_sent:
                messages.success(
                    request,
                    '✅ Contraseña cambiada exitosamente. '
                    'Te hemos enviado un email de confirmación.'
                )
            else:
                messages.success(
                    request,
                    '✅ Contraseña cambiada exitosamente.'
                )
                messages.warning(
                    request,
                    'No se pudo enviar el email de confirmación, pero tu contraseña fue actualizada.'
                )
            
            return redirect('shop:profile')
    else:
        form = ChangePasswordForm(user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'shop/change_password.html', context)