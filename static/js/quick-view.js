/**
 * ================================================================
 * SISTEMA DE VISTA RÁPIDA DE PRODUCTOS
 * ================================================================
 * 
 * Funcionalidades:
 * - Carga datos del producto vía AJAX
 * - Muestra modal con información clave
 * - Permite agregar al carrito desde el modal
 * - Mantiene el contexto de navegación
 */

const QuickView = (function() {
    'use strict';
    
    // ============================================
    // ELEMENTOS DEL DOM
    // ============================================
    let $modal = null;
    let $loading = null;
    let $content = null;
    let modalInstance = null;
    let currentProductId = null;
    
    // Cache de productos ya cargados
    const productCache = new Map();
    
    // ============================================
    // INICIALIZACIÓN
    // ============================================
    function init() {
        // Obtener elementos
        $modal = document.getElementById('quickViewModal');
        $loading = document.getElementById('quickViewLoading');
        $content = document.getElementById('quickViewContent');
        
        if (!$modal) {
            console.warn('⚠️ Modal de vista rápida no encontrado');
            return;
        }
        
        // Crear instancia de Bootstrap Modal
        modalInstance = new bootstrap.Modal($modal);
        
        // Event listeners
        attachEventListeners();
        
        console.log('✅ QuickView inicializado');
    }
    
    // ============================================
    // EVENT LISTENERS
    // ============================================
    function attachEventListeners() {
        // Botones de vista rápida
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.quick-view-btn');
            if (btn) {
                e.preventDefault();
                const productId = btn.dataset.productId;
                openQuickView(productId);
            }
        });
        
        // También permitir clic en imagen del producto
        document.addEventListener('click', function(e) {
            const img = e.target.closest('.product-image');
            if (img && e.ctrlKey) { // Ctrl + Click en imagen
                e.preventDefault();
                const card = img.closest('.product-card-wrapper');
                if (card) {
                    const productId = card.dataset.productId;
                    if (productId) {
                        openQuickView(productId);
                    }
                }
            }
        });
        
        // Botón de agregar al carrito dentro del modal
        const $addToCartBtn = document.getElementById('quickViewAddToCart');
        if ($addToCartBtn) {
            $addToCartBtn.addEventListener('click', addToCartFromQuickView);
        }
        
        // Limpiar al cerrar el modal
        $modal.addEventListener('hidden.bs.modal', function() {
            currentProductId = null;
        });
        
        // Atajo de teclado: ESC para cerrar
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modalInstance && $modal.classList.contains('show')) {
                modalInstance.hide();
            }
        });
    }
    
    // ============================================
    // ABRIR VISTA RÁPIDA
    // ============================================
    function openQuickView(productId) {
        if (!productId) return;
        
        currentProductId = productId;
        
        // Mostrar modal inmediatamente
        modalInstance.show();
        
        // Mostrar estado de carga
        showLoading();
        
        // Verificar cache
        if (productCache.has(productId)) {
            console.log('📦 Usando datos en cache para producto:', productId);
            populateModal(productCache.get(productId));
            return;
        }
        
        // Cargar datos desde el servidor
        loadProductData(productId);
    }
    
    // ============================================
    // CARGAR DATOS DEL PRODUCTO
    // ============================================
    function loadProductData(productId) {
        fetch(`/producto/${productId}/vista-rapida/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Guardar en cache
                productCache.set(productId, data);
                
                // Poblar modal
                populateModal(data);
            } else {
                showError(data.error || 'Error al cargar el producto');
            }
        })
        .catch(error => {
            console.error('❌ Error cargando producto:', error);
            showError('No se pudo cargar el producto. Por favor intenta nuevamente.');
        });
    }
    
    // ============================================
    // POBLAR MODAL CON DATOS
    // ============================================
    function populateModal(data) {
        const product = data.product;
        const specs = data.specifications;
        const reviews = data.reviews;
        
        // Imagen
        const $img = document.getElementById('quickViewImage');
        if (product.image) {
            $img.src = product.image;
            $img.alt = product.name;
        } else {
            $img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect fill="%23ddd" width="400" height="400"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ESin imagen%3C/text%3E%3C/svg%3E';
            $img.alt = 'Sin imagen';
        }
        
        // Badge destacado
        const $featured = document.getElementById('quickViewFeatured');
        if (product.featured) {
            $featured.style.display = 'inline-block';
        } else {
            $featured.style.display = 'none';
        }
        
        // Stock badge
        const $stockBadge = document.getElementById('quickViewStockBadge');
        if (product.stock === 0) {
            $stockBadge.innerHTML = '<span class="badge bg-danger">Agotado</span>';
        } else if (product.stock < 10) {
            $stockBadge.innerHTML = `<span class="badge bg-warning text-dark">Solo ${product.stock} disponibles</span>`;
        } else {
            $stockBadge.innerHTML = '<span class="badge bg-success">Disponible</span>';
        }
        
        // Categoría
        document.getElementById('quickViewCategory').textContent = product.category;
        
        // Nombre
        document.getElementById('quickViewName').textContent = product.name;
        
        // Reviews
        const $reviewsContainer = document.getElementById('quickViewReviewsContainer');
        const $stars = document.getElementById('quickViewStars');
        const $reviewCount = document.getElementById('quickViewReviewCount');
        
        if (reviews.count > 0) {
            $reviewsContainer.style.display = 'block';
            $stars.innerHTML = generateStars(reviews.average);
            $reviewCount.textContent = `(${reviews.count} ${reviews.count === 1 ? 'opinión' : 'opiniones'})`;
        } else {
            $reviewsContainer.style.display = 'none';
        }
        
        // SKU y Marca
        document.getElementById('quickViewSKU').textContent = product.sku;
        document.getElementById('quickViewBrand').textContent = product.marca;
        
        // Precio
        document.getElementById('quickViewPrice').textContent = `$${parseFloat(product.price).toFixed(2)}`;
        
        // Descripción (truncada a 150 caracteres)
        const description = product.description.length > 150 
            ? product.description.substring(0, 150) + '...' 
            : product.description;
        document.getElementById('quickViewDescription').textContent = description;
        
        // Especificaciones
        const $specsContainer = document.getElementById('quickViewSpecsContainer');
        const $specs = document.getElementById('quickViewSpecs');
        
        if (specs && specs.length > 0) {
            $specsContainer.style.display = 'block';
            $specs.innerHTML = specs.map(spec => `
                <div class="d-flex justify-content-between py-2 border-bottom">
                    <span class="text-muted">${spec.label}:</span>
                    <strong>${spec.value}</strong>
                </div>
            `).join('');
        } else {
            $specsContainer.style.display = 'none';
        }
        
        // Botón de agregar al carrito
        const $addToCartBtn = document.getElementById('quickViewAddToCart');
        if (product.stock > 0) {
            $addToCartBtn.disabled = false;
            $addToCartBtn.innerHTML = '<i class="bi bi-cart-plus"></i> Agregar al Carrito';
        } else {
            $addToCartBtn.disabled = true;
            $addToCartBtn.innerHTML = '<i class="bi bi-x-circle"></i> Producto Agotado';
        }
        
        // Link a detalles completos
        document.getElementById('quickViewDetailsLink').href = data.detail_url;
        
        // Ocultar loading y mostrar contenido
        hideLoading();
    }
    
    // ============================================
    // AGREGAR AL CARRITO DESDE MODAL
    // ============================================
    function addToCartFromQuickView() {
        if (!currentProductId) return;
        
        const $btn = document.getElementById('quickViewAddToCart');
        const originalText = $btn.innerHTML;
        
        // Deshabilitar botón
        $btn.disabled = true;
        $btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Agregando...';
        
        fetch(`/agregar-al-carrito/${currentProductId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: `quantity=1&csrfmiddlewaretoken=${getCsrfToken()}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar badge del carrito
                const $cartBadge = document.querySelector('.cart-badge');
                if ($cartBadge) {
                    $cartBadge.textContent = data.cart_count;
                    $cartBadge.style.display = 'inline-block';
                }
                
                // Toast de éxito
                if (typeof Toast !== 'undefined') {
                    Toast.success('¡Agregado!', 'Producto agregado al carrito', {
                        duration: 3000
                    });
                }
                
                // Cambiar botón temporalmente
                $btn.innerHTML = '<i class="bi bi-check-circle"></i> ¡Agregado!';
                $btn.classList.remove('btn-primary');
                $btn.classList.add('btn-success');
                
                setTimeout(() => {
                    $btn.innerHTML = originalText;
                    $btn.classList.remove('btn-success');
                    $btn.classList.add('btn-primary');
                    $btn.disabled = false;
                }, 2000);
            } else {
                $btn.disabled = false;
                $btn.innerHTML = originalText;
                
                if (typeof Toast !== 'undefined') {
                    Toast.error('Error', data.message || 'No se pudo agregar el producto');
                } else {
                    alert(data.message || 'No se pudo agregar el producto');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            $btn.disabled = false;
            $btn.innerHTML = originalText;
            
            if (typeof Toast !== 'undefined') {
                Toast.error('Error', 'No se pudo agregar el producto al carrito');
            }
        });
    }
    
    // ============================================
    // UTILIDADES
    // ============================================
    function showLoading() {
        $loading.style.display = 'flex';
        $content.style.display = 'none';
    }
    
    function hideLoading() {
        $loading.style.display = 'none';
        $content.style.display = 'block';
    }
    
    function showError(message) {
        $loading.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }
    
    function generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        let html = '';
        
        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                html += '⭐';
            } else if (i === fullStars && hasHalfStar) {
                html += '⭐';
            }
        }
        
        return html;
    }
    
    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // ============================================
    // API PÚBLICA
    // ============================================
    return {
        init: init,
        open: openQuickView,
        clearCache: function() {
            productCache.clear();
            console.log('🗑️ Cache de vista rápida limpiado');
        }
    };
})();

// Inicializar al cargar el DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', QuickView.init);
} else {
    QuickView.init();
}

// Exponer globalmente
window.QuickView = QuickView;