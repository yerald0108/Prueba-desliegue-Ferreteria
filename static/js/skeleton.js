/**
 * ================================================================
 * SISTEMA DE SKELETON SCREENS - JAVASCRIPT
 * ================================================================
 * 
 * Gestiona la visualización y reemplazo de skeleton screens
 * para mejorar la percepción de velocidad de carga.
 */

const SkeletonLoader = (function() {
    'use strict';
    
    // ============================================
    // CONFIGURACIÓN
    // ============================================
    const config = {
        fadeOutDuration: 300,  // ms
        fadeInDuration: 300,   // ms
        minDisplayTime: 500,   // ms mínimo que se muestra el skeleton
    };
    
    // Templates de skeletons almacenados
    const templates = new Map();
    
    // ============================================
    // INICIALIZACIÓN
    // ============================================
    function init() {
        // Cargar templates desde el DOM
        loadTemplates();
        
        console.log('✅ SkeletonLoader inicializado');
        console.log('📦 Templates cargados:', templates.size);
    }
    
    // ============================================
    // CARGAR TEMPLATES
    // ============================================
    function loadTemplates() {
        const templateElements = document.querySelectorAll('script[type="text/template"]');
        
        templateElements.forEach(template => {
            const id = template.id.replace('-template', '');
            templates.set(id, template.innerHTML);
        });
    }
    
    // ============================================
    // MOSTRAR SKELETON
    // ============================================
    /**
     * Muestra un skeleton en el contenedor especificado
     * 
     * @param {HTMLElement|string} container - Elemento o selector
     * @param {string} templateId - ID del template a usar
     * @param {number} count - Número de skeletons a mostrar
     * @param {Object} options - Opciones adicionales
     * @returns {Object} - Objeto con métodos para controlar el skeleton
     */
    function show(container, templateId, count = 1, options = {}) {
        const $container = typeof container === 'string' 
            ? document.querySelector(container)
            : container;
        
        if (!$container) {
            console.error('❌ Contenedor no encontrado:', container);
            return null;
        }
        
        const template = templates.get(templateId);
        if (!template) {
            console.error('❌ Template no encontrado:', templateId);
            return null;
        }
        
        // Timestamp de inicio
        const startTime = Date.now();
        
        // Crear wrapper para skeletons
        const wrapper = document.createElement('div');
        wrapper.className = 'skeleton-wrapper';
        wrapper.dataset.skeletonId = generateId();
        
        // Agregar skeletons según count
        for (let i = 0; i < count; i++) {
            wrapper.innerHTML += template;
        }
        
        // Limpiar contenedor y agregar skeletons
        $container.innerHTML = '';
        $container.appendChild(wrapper);
        
        // Objeto de control
        const controller = {
            id: wrapper.dataset.skeletonId,
            startTime,
            
            /**
             * Oculta el skeleton y muestra el contenido real
             * @param {string|HTMLElement} content - Contenido HTML o elemento
             */
            hide: function(content) {
                const elapsedTime = Date.now() - startTime;
                const remainingTime = Math.max(0, config.minDisplayTime - elapsedTime);
                
                setTimeout(() => {
                    hideWithTransition(wrapper, content, $container);
                }, remainingTime);
            },
            
            /**
             * Oculta inmediatamente sin transición
             */
            hideImmediately: function() {
                if (wrapper.parentElement) {
                    wrapper.remove();
                }
            },
            
            /**
             * Actualiza el contenido mientras se muestra el skeleton
             * @param {string|HTMLElement} content - Nuevo contenido
             */
            update: function(content) {
                this.hide(content);
            }
        };
        
        return controller;
    }
    
    // ============================================
    // OCULTAR CON TRANSICIÓN
    // ============================================
    function hideWithTransition(wrapper, content, container) {
        // Fase 1: Fade out del skeleton
        wrapper.classList.add('fade-out-skeleton');
        
        setTimeout(() => {
            // Crear contenedor para nuevo contenido
            const contentWrapper = document.createElement('div');
            contentWrapper.className = 'fade-in-content';
            
            if (typeof content === 'string') {
                contentWrapper.innerHTML = content;
            } else {
                contentWrapper.appendChild(content);
            }
            
            // Reemplazar skeleton con contenido
            wrapper.replaceWith(contentWrapper);
            
            // Forzar reflow para activar transición
            void contentWrapper.offsetWidth;
            
            // Fade in del contenido
            requestAnimationFrame(() => {
                contentWrapper.style.opacity = '1';
            });
            
        }, config.fadeOutDuration);
    }
    
    // ============================================
    // HELPERS ESPECÍFICOS
    // ============================================
    
    /**
     * Muestra skeletons para product cards
     */
    function showProductCards(container, count = 3) {
        return show(container, 'skeleton-product-card', count);
    }
    
    /**
     * Muestra skeletons para cart items
     */
    function showCartItems(container, count = 2) {
        return show(container, 'skeleton-cart-item', count);
    }
    
    /**
     * Muestra skeletons para order items
     */
    function showOrderItems(container, count = 5) {
        return show(container, 'skeleton-order-item', count);
    }
    
    /**
     * Muestra skeletons para stat cards (admin)
     */
    function showStatCards(container, count = 4) {
        return show(container, 'skeleton-stat-card', count);
    }
    
    /**
     * Muestra skeletons para reviews
     */
    function showReviews(container, count = 3) {
        return show(container, 'skeleton-review', count);
    }
    
    /**
     * Muestra skeleton para comparación
     */
    function showCompare(container) {
        return show(container, 'skeleton-compare', 1);
    }
    
    // ============================================
    // INTEGRACIÓN CON FETCH
    // ============================================
    /**
     * Wrapper para fetch que muestra skeleton automáticamente
     * 
     * @param {string} url - URL a fetchear
     * @param {HTMLElement|string} container - Contenedor para skeleton
     * @param {string} templateId - Template de skeleton
     * @param {number} count - Cantidad de skeletons
     * @returns {Promise}
     */
    function fetchWithSkeleton(url, container, templateId, count = 1) {
        // Mostrar skeleton
        const skeleton = show(container, templateId, count);
        
        // Realizar fetch
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                // Ocultar skeleton y mostrar contenido
                if (skeleton) {
                    skeleton.hide(html);
                }
                return html;
            })
            .catch(error => {
                console.error('❌ Error en fetch:', error);
                
                // Ocultar skeleton y mostrar error
                if (skeleton) {
                    const errorHtml = `
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle"></i>
                            Error al cargar contenido. Por favor intenta nuevamente.
                        </div>
                    `;
                    skeleton.hide(errorHtml);
                }
                
                throw error;
            });
    }
    
    // ============================================
    // INTEGRACIÓN CON AJAX (jQuery)
    // ============================================
    /**
     * Wrapper para $.ajax que muestra skeleton
     */
    function ajaxWithSkeleton(options, container, templateId, count = 1) {
        if (typeof $ === 'undefined') {
            console.error('❌ jQuery no está disponible');
            return null;
        }
        
        // Mostrar skeleton
        const skeleton = show(container, templateId, count);
        
        // Realizar AJAX
        const ajaxOptions = {
            ...options,
            success: function(response) {
                // Ocultar skeleton y mostrar contenido
                if (skeleton) {
                    skeleton.hide(response);
                }
                
                // Llamar callback original si existe
                if (options.success) {
                    options.success.call(this, response);
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ Error en AJAX:', error);
                
                // Ocultar skeleton y mostrar error
                if (skeleton) {
                    const errorHtml = `
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle"></i>
                            Error al cargar contenido.
                        </div>
                    `;
                    skeleton.hide(errorHtml);
                }
                
                // Llamar callback original si existe
                if (options.error) {
                    options.error.call(this, xhr, status, error);
                }
            }
        };
        
        return $.ajax(ajaxOptions);
    }
    
    // ============================================
    // UTILIDADES
    // ============================================
    function generateId() {
        return 'skeleton-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }
    
    // ============================================
    // API PÚBLICA
    // ============================================
    return {
        init,
        
        // Métodos generales
        show,
        
        // Métodos específicos
        showProductCards,
        showCartItems,
        showOrderItems,
        showStatCards,
        showReviews,
        showCompare,
        
        // Integraciones
        fetchWithSkeleton,
        ajaxWithSkeleton,
        
        // Utilidades
        templates,
    };
})();

// ============================================
// INICIALIZACIÓN AUTOMÁTICA
// ============================================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', SkeletonLoader.init);
} else {
    SkeletonLoader.init();
}

// Exponer globalmente
window.SkeletonLoader = SkeletonLoader;