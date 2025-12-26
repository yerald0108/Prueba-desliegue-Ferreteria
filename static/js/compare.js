/**
 * ================================================================
 * SISTEMA DE COMPARACIÓN DE PRODUCTOS - VERSIÓN CORREGIDA
 * ================================================================
 * 
 * Funcionalidades:
 * - Selección de productos (hasta 4)
 * - Sincronización con sesión del servidor
 * - Botón flotante con contador
 * - Persistencia correcta al recargar
 */

const ProductCompare = (function() {
    'use strict';
    
    // ============================================
    // CONFIGURACIÓN
    // ============================================
    const config = {
        maxProducts: 4,
        floatingBtnId: 'compareFloatingButton',
    };
    
    // ============================================
    // ESTADO
    // ============================================
    let compareList = [];
    let $floatingBtn = null;
    let isInitialized = false;
    
    // ============================================
    // INICIALIZACIÓN
    // ============================================
    function init() {
        if (isInitialized) return;
        
        $floatingBtn = document.getElementById(config.floatingBtnId);
        
        // ✅ CRUCIAL: Cargar lista desde servidor PRIMERO
        loadCompareListFromServer()
            .then(() => {
                // Después de cargar, configurar event listeners
                attachEventListeners();
                
                // Actualizar UI inicial
                updateUI();
                
                isInitialized = true;
                
                console.log('✅ ProductCompare inicializado. Lista actual:', compareList);
            })
            .catch(error => {
                console.error('❌ Error inicializando comparador:', error);
                // Incluso con error, intentar inicializar con lista vacía
                compareList = [];
                attachEventListeners();
                updateUI();
                isInitialized = true;
            });
    }
    
    // ============================================
    // CARGAR LISTA DESDE SERVIDOR (AJAX)
    // ============================================
    function loadCompareListFromServer() {
        return fetch('/comparar/obtener/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                compareList = data.compare_list || [];
                console.log('📥 Lista cargada desde servidor:', compareList);
            } else {
                console.warn('⚠️ Respuesta no exitosa del servidor');
                compareList = [];
            }
        })
        .catch(error => {
            console.error('❌ Error cargando lista desde servidor:', error);
            // En caso de error, intentar con localStorage como fallback
            const stored = localStorage.getItem('compare_list_backup');
            if (stored) {
                try {
                    compareList = JSON.parse(stored);
                    console.log('💾 Lista restaurada desde localStorage:', compareList);
                } catch (e) {
                    compareList = [];
                }
            } else {
                compareList = [];
            }
        });
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
        
        console.log('🔄 Checkbox cambiado:', { productId, isChecked });
        
        if (isChecked) {
            // Intentar agregar
            if (compareList.includes(productId)) {
                console.warn('⚠️ Producto ya está en la lista:', productId);
                Toast.warning(
                    'Ya seleccionado',
                    'Este producto ya está en la comparación',
                    { duration: 2000 }
                );
                return;
            }
            
            if (compareList.length >= config.maxProducts) {
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
        // Optimistic update
        const optimisticList = [...compareList, productId];
        
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
                // Actualizar con respuesta del servidor
                compareList = data.compare_list || optimisticList;
                
                // Backup en localStorage
                localStorage.setItem('compare_list_backup', JSON.stringify(compareList));
                
                console.log('✅ Producto agregado. Lista actualizada:', compareList);
                
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
                // Revertir cambio optimista
                checkbox.checked = false;
                Toast.error('Error', data.message || 'No se pudo agregar', { duration: 3000 });
            }
        })
        .catch(error => {
            console.error('❌ Error agregando producto:', error);
            // Revertir cambio optimista
            checkbox.checked = false;
            Toast.error('Error', 'No se pudo agregar el producto', { duration: 3000 });
        });
    }
    
    // ============================================
    // REMOVER DE COMPARACIÓN (AJAX)
    // ============================================
    function removeFromCompare(productId, checkbox) {
        // Optimistic update
        const optimisticList = compareList.filter(id => id !== productId);
        
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
                // Actualizar con respuesta del servidor
                compareList = data.compare_list || optimisticList;
                
                // Backup en localStorage
                localStorage.setItem('compare_list_backup', JSON.stringify(compareList));
                
                console.log('✅ Producto removido. Lista actualizada:', compareList);
                
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
                // Revertir cambio optimista
                checkbox.checked = true;
                Toast.error('Error', data.message || 'No se pudo remover', { duration: 3000 });
            }
        })
        .catch(error => {
            console.error('❌ Error removiendo producto:', error);
            // Revertir cambio optimista
            checkbox.checked = true;
            Toast.error('Error', 'No se pudo remover el producto', { duration: 3000 });
        });
    }
    
    // ============================================
    // ACTUALIZAR UI
    // ============================================
    function updateUI() {
        const count = compareList.length;
        
        console.log('🎨 Actualizando UI. Productos en lista:', count, compareList);
        
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
            
            // Actualizar estado del checkbox
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
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    compareList = [];
                    localStorage.removeItem('compare_list_backup');
                    updateUI();
                    Toast.success('Comparación limpiada', '', { duration: 2000 });
                }
            })
            .catch(error => {
                console.error('Error limpiando:', error);
                Toast.error('Error', 'No se pudo limpiar la comparación');
            });
        },
        goToComparison: goToComparison,
        getList: function() { return [...compareList]; }, // Para debugging
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