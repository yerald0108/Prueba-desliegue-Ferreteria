"""
Vistas para probar páginas de error en desarrollo.

IMPORTANTE: Estas vistas solo deben usarse en desarrollo.
En producción, Django manejará los errores automáticamente.
"""

from django.shortcuts import render
from django.conf import settings


def test_404(request):
    """Vista para probar error 404"""
    if settings.DEBUG:
        return render(request, 'shop/errors/404.html', status=404)
    else:
        return render(request, 'shop/errors/404.html', status=404)


def test_500(request):
    """Vista para probar error 500"""
    if settings.DEBUG:
        return render(request, 'shop/errors/500.html', status=500)
    else:
        return render(request, 'shop/errors/500.html', status=500)


def test_429(request):
    """Vista para probar error 429"""
    if settings.DEBUG:
        return render(request, 'shop/errors/429.html', status=429)
    else:
        return render(request, 'shop/errors/429.html', status=429)