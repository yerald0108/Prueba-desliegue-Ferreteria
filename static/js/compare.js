/**
 * ================================================================
 * SISTEMA DE COMPARACIÓN DE PRODUCTOS
 * ================================================================
 * 
 * Funcionalidades:
 * - Selección de productos (hasta 4)
 * - Botón flotante con contador
 * - Persistencia en sesión
 * - Validaciones y UX
 */

const ProductCompare = (function() {
    'use strict';
    
    // ============================================
    // CONFIGURACIÓN
    // ============================================
    const config = {
        maxProducts: 4,
        storageKey: 'compare_list',
        floatingBtnId: 'compareFloatingButton',
    };
    
    // ============================================
    // ESTADO
    // ============================================
    let compareList = [];
    let $floatingBtn = null;
    
    // ============================================
    // INICIALIZACIÓN
    // ============================================
    function init() {
        $floatingBtn = document.getElementById(config.floatingBtnId);
        
        // Cargar lista desde servidor (sesión)
        loadCompareList();
        
        // Event listeners
        attachEventListeners();
        
        // Actualizar UI inicial
        updateUI();
    }
    
    // ============================================
    // CARGAR LISTA DESDE SESIÓN (AJAX)
    // ============================================
    function loadCompareList() {
        // En este caso, la sesión se maneja en el servidor
        // Aquí solo inicializamos con checkboxes marcados
        const checkboxes = document.querySelectorAll('.compare-checkbox:checked');
        compareList = Array.from(checkboxes).map(cb => parseInt(cb.value));
        updateUI();
    }
    
    // ============================================
    // EVENT LISTENERS
    // ============================================
    function attachEventListeners() {
        // Checkboxes de productos
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('compare-checkbox')) {
                handleCheckboxChange(e.target);
            }
        });
        
        // Botón flotante
        if ($floatingBtn) {
            const $actionBtn = $floatingBtn.querySelector('.btn-compare-action');
            if ($actionBtn) {
                $actionBtn.addEventListener('click', goToComparison);
            }
        }
    }
    
    // ============================================
    // MANEJAR CAMBIO DE CHECKBOX
    // ============================================
    function handleCheckboxChange(checkbox) {
        const productId = parseInt(checkbox.value);
        const isChecked = checkbox.checked;
        
        if (isChecked) {
            // Intentar agregar
            if (compareList.length >= config.maxProducts) {
                // Límite alcanzado
                checkbox.checked = false;
                Toast.warning(
                    'Límite alcanzado',
                    `Solo puedes comparar hasta ${config.maxProducts} productos`,
                    { duration: 3000 }
                );
                return;
            }
            
            addToCompare(productId, checkbox);
        } else {
            // Remover
            removeFromCompare(productId, checkbox);
        }
    }
    
    // ============================================
    // AGREGAR A COMPARACIÓN (AJAX)
    // ============================================
    function addToCompare(productId, checkbox) {
        fetch('/comparar/agregar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: `product_id=${productId}&csrfmiddlewaretoken=${getCsrfToken()}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                compareList = data.compare_list || [];
                updateUI();
                
                // Animar card
                const $card = checkbox.closest('.product-card');
                if ($card) {
                    $card.classList.add('compare-selected');
                }
                
                Toast.success(
                    '¡Producto agregado!',
                    'Producto agregado a la comparación',
                    { duration: 2000 }
                );
            } else {
                checkbox.checked = false;
                Toast.error('Error', data.message || 'No se pudo agregar', { duration: 3000 });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            checkbox.checked = false;
            Toast.error('Error', 'No se pudo agregar el producto', { duration: 3000 });
        });
    }
    
    // ============================================
    // REMOVER DE COMPARACIÓN (AJAX)
    // ============================================
    function removeFromCompare(productId, checkbox) {
        fetch('/comparar/remover/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: `product_id=${productId}&csrfmiddlewaretoken=${getCsrfToken()}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                compareList = data.compare_list || [];
                updateUI();
                
                // Remover clase de card
                const $card = checkbox.closest('.product-card');
                if ($card) {
                    $card.classList.remove('compare-selected');
                }
                
                Toast.info(
                    'Producto removido',
                    'Producto removido de la comparación',
                    { duration: 2000 }
                );
            } else {
                checkbox.checked = true;
                Toast.error('Error', data.message || 'No se pudo remover', { duration: 3000 });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            checkbox.checked = true;
            Toast.error('Error', 'No se pudo remover el producto', { duration: 3000 });
        });
    }
    
    // ============================================
    // ACTUALIZAR UI
    // ============================================
    function updateUI() {
        const count = compareList.length;
        
        // Actualizar botón flotante
        if ($floatingBtn) {
            if (count > 0) {
                $floatingBtn.style.display = 'flex';
                const $countSpan = $floatingBtn.querySelector('.compare-count');
                if ($countSpan) {
                    $countSpan.textContent = count;
                }
            } else {
                $floatingBtn.style.display = 'none';
            }
        }
        
        // Actualizar checkboxes
        const allCheckboxes = document.querySelectorAll('.compare-checkbox');
        allCheckboxes.forEach(cb => {
            const productId = parseInt(cb.value);
            const isInList = compareList.includes(productId);
            
            cb.checked = isInList;
            
            // Marcar card como seleccionado
            const $card = cb.closest('.product-card');
            if ($card) {
                if (isInList) {
                    $card.classList.add('compare-selected');
                } else {
                    $card.classList.remove('compare-selected');
                }
            }
            
            // Deshabilitar checkboxes si límite alcanzado
            if (count >= config.maxProducts && !isInList) {
                cb.disabled = true;
                if ($card) {
                    $card.classList.add('compare-disabled');
                }
            } else {
                cb.disabled = false;
                if ($card) {
                    $card.classList.remove('compare-disabled');
                }
            }
        });
    }
    
    // ============================================
    // IR A PÁGINA DE COMPARACIÓN
    // ============================================
    function goToComparison() {
        if (compareList.length < 2) {
            Toast.warning(
                'Selección insuficiente',
                'Selecciona al menos 2 productos para comparar',
                { duration: 3000 }
            );
            return;
        }
        
        // Redirigir a vista de comparación
        const ids = compareList.join(',');
        window.location.href = `/comparar/?ids=${ids}`;
    }
    
    // ============================================
    // UTILIDADES
    // ============================================
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
        add: addToCompare,
        remove: removeFromCompare,
        clear: function() {
            fetch('/comparar/limpiar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: `csrfmiddlewaretoken=${getCsrfToken()}`
            })
            .then(() => {
                compareList = [];
                updateUI();
                Toast.success('Comparación limpiada', '', { duration: 2000 });
            });
        },
        goToComparison: goToComparison,
    };
})();

// ============================================
// INICIALIZAR AL CARGAR LA PÁGINA
// ============================================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ProductCompare.init);
} else {
    ProductCompare.init();
}

// Hacer disponible globalmente
window.ProductCompare = ProductCompare;