"""
Vistas para el sistema de reviews y calificaciones.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q

from ..models import Product, Review, ReviewHelpful, OrderItem
from ..forms import ReviewForm


@login_required
def add_review(request, product_id):
    """
    Agregar un review a un producto.
    Solo si el usuario lo ha comprado.
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    # Verificar si el usuario compró el producto
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status='delivered'
    ).exists()
    
    if not has_purchased:
        messages.error(
            request,
            'Solo puedes dejar un review si has comprado este producto.'
        )
        return redirect('shop:product_detail', pk=product_id)
    
    # Verificar si ya tiene un review
    existing_review = Review.objects.filter(
        user=request.user,
        product=product
    ).first()
    
    if existing_review:
        messages.warning(request, 'Ya has dejado un review para este producto.')
        return redirect('shop:product_detail', pk=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            
            messages.success(request, '¡Gracias por tu opinión!')
            return redirect('shop:product_detail', pk=product_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'shop/reviews/add_review.html', context)


@login_required
def edit_review(request, review_id):
    """Editar un review existente"""
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review actualizado correctamente.')
            return redirect('shop:product_detail', pk=review.product.id)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'product': review.product,
        'review': review,
    }
    return render(request, 'shop/reviews/edit_review.html', context)


@login_required
@require_POST
def delete_review(request, review_id):
    """Eliminar un review"""
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    product_id = review.product.id
    review.delete()
    
    messages.success(request, 'Review eliminado correctamente.')
    return redirect('shop:product_detail', pk=product_id)


@login_required
@require_POST
def mark_review_helpful(request, review_id):
    """Marcar un review como útil"""
    review = get_object_or_404(Review, pk=review_id)
    
    # No permitir votar el propio review
    if review.user == request.user:
        return JsonResponse({
            'success': False,
            'message': 'No puedes votar tu propio review'
        })
    
    # Verificar si ya votó
    vote, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user
    )
    
    if created:
        # Incrementar contador
        review.helpful_count += 1
        review.save(update_fields=['helpful_count'])
        
        return JsonResponse({
            'success': True,
            'helpful_count': review.helpful_count,
            'message': 'Gracias por tu voto'
        })
    else:
        # Ya votó, remover voto
        vote.delete()
        review.helpful_count = max(0, review.helpful_count - 1)
        review.save(update_fields=['helpful_count'])
        
        return JsonResponse({
            'success': True,
            'helpful_count': review.helpful_count,
            'message': 'Voto removido'
        })


def product_reviews(request, product_id):
    """
    Vista de todos los reviews de un producto.
    Con filtros y ordenamiento.
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    # Obtener reviews aprobados
    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    ).select_related('user', 'user__profile')
    
    # Filtros
    rating_filter = request.GET.get('rating')
    if rating_filter:
        try:
            rating_filter = int(rating_filter)
            reviews = reviews.filter(rating=rating_filter)
        except ValueError:
            pass
    
    verified_only = request.GET.get('verified') == 'true'
    if verified_only:
        reviews = reviews.filter(is_verified_purchase=True)
    
    # Ordenamiento
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = {
        'recent': '-created_at',
        'oldest': 'created_at',
        'highest': '-rating',
        'lowest': 'rating',
        'helpful': '-helpful_count'
    }
    reviews = reviews.order_by(valid_sorts.get(sort_by, '-created_at'))
    
    # Estadísticas
    stats = Review.objects.filter(
        product=product,
        is_approved=True
    ).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        five_star=Count('id', filter=Q(rating=5)),
        four_star=Count('id', filter=Q(rating=4)),
        three_star=Count('id', filter=Q(rating=3)),
        two_star=Count('id', filter=Q(rating=2)),
        one_star=Count('id', filter=Q(rating=1)),
    )
    
    # Verificar si el usuario puede dejar review
    can_review = False
    user_review = None
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status='delivered'
        ).exists() and not Review.objects.filter(
            user=request.user,
            product=product
        ).exists()
        
        user_review = Review.objects.filter(
            user=request.user,
            product=product
        ).first()
    
    context = {
        'product': product,
        'reviews': reviews,
        'stats': stats,
        'can_review': can_review,
        'user_review': user_review,
        'rating_filter': rating_filter,
        'verified_only': verified_only,
        'sort_by': sort_by,
    }
    return render(request, 'shop/reviews/product_reviews.html', context)