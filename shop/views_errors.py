from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited

def handler404(request, exception):
    """Vista personalizada para error 404"""
    return render(request, 'shop/errors/404.html', status=404)

def handler500(request):
    """Vista personalizada para error 500"""
    return render(request, 'shop/errors/500.html', status=500)

def handler429(request, exception):
    """Vista personalizada para rate limiting (429)"""
    return render(request, 'shop/errors/429.html', status=429)