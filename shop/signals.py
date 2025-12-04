from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Cart


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil de usuario automáticamente al registrarse"""
    if created:
        # Solo crear si no existe (para evitar errores con usuarios creados antes)
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Crear carrito de compras automáticamente al registrarse"""
    if created:
        Cart.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar perfil cuando se guarda el usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()