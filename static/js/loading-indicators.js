/**
 * ================================================================
 * SISTEMA DE INDICADORES DE CARGA - JAVASCRIPT
 * ================================================================
 */

const LoadingIndicators = (function() {
    'use strict';
    
    // ============================================
    // CONFIGURACIÓN
    // ============================================
    const config = {
        globalBarSelector: '#globalLoadingBar',
        defaultDelay: 300, // ms antes de mostrar loading
    };
    
    // ============================================
    // BARRA DE PROGRESO GLOBAL
    // ============================================
    const GlobalBar = {
        bar: null,
        progress: null,
        isLoading: false,
        currentProgress: 0,
        
        init() {
            // Crear barra si no existe
            if (!document.querySelector('.global-loading-bar')) {
                const bar = document.createElement('div');
                bar.className = 'global-loading-bar';
                bar.innerHTML = '<div class="loading-bar-progress"></div>';
                document.body.insertBefore(bar, document.body.firstChild);
            }
            
            this.bar = document.querySelector('.global-loading-bar');
            this.progress = this.bar.querySelector('.loading-bar-progress');
        },
        
        start() {
            if (!this.bar) this.init();
            
            this.isLoading = true;
            this.currentProgress = 0;
            this.progress.style.width = '0%';
            this.progress.classList.add('loading');
            
            // Animación progresiva
            this.animate();
        },
        
        animate() {
            if (!this.isLoading) return;
            
            // Incremento logarítmico (rápido al inicio, lento al final)
            const increment = (100 - this.currentProgress) * 0.1;
            this.currentProgress = Math.min(this.currentProgress + increment, 95);
            
            this.progress.style.width = this.currentProgress + '%';
            
            if (this.currentProgress < 95) {
                requestAnimationFrame(() => this.animate());
            }
        },
        
        complete() {
            this.isLoading = false;
            this.currentProgress = 100;
            this.progress.style.width = '100%';
            
            setTimeout(() => {
                this.progress.classList.remove('loading');
                this.progress.style.width = '0%';
            }, 400);
        },
        
        error() {
            this.progress.style.background = '#ef4444';
            this.complete();
            
            setTimeout(() => {
                this.progress.style.background = '';
            }, 1000);
        }
    };
    
    // ============================================
    // OVERLAY DE CARGA
    // ============================================
    function showOverlay(element, options = {}) {
        const defaults = {
            text: 'Cargando...',
            dark: false,
            spinner: 'default',
        };
        
        const opts = { ...defaults, ...options };
        
        // Verificar si el elemento existe
        if (!element) {
            console.error('LoadingIndicators: Elemento no encontrado');
            return null;
        }
        
        // Asegurar posicionamiento relativo
        const position = window.getComputedStyle(element).position;
        if (position === 'static') {
            element.style.position = 'relative';
        }
        
        // Crear overlay
        const overlay = document.createElement('div');
        overlay.className = `loading-overlay ${opts.dark ? 'loading-overlay-dark' : ''}`;
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-overlay-text">${opts.text}</div>
        `;
        
        element.appendChild(overlay);
        
        // Activar con delay para suavizar
        requestAnimationFrame(() => {
            overlay.classList.add('active');
        });
        
        return overlay;
    }
    
    function hideOverlay(element) {
        if (!element) return;
        
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
            setTimeout(() => overlay.remove(), 300);
        }
    }
    
    // ============================================
    // BOTONES CON LOADING
    // ============================================
    function buttonLoading(button, options = {}) {
        const defaults = {
            text: null, // Texto durante carga, o null para solo spinner
        };
        
        const opts = { ...defaults, ...options };
        
        if (!button) return null;
        
        // Guardar estado original
        button.dataset.originalText = button.innerHTML;
        button.dataset.originalDisabled = button.disabled;
        
        // Aplicar estado de carga
        button.disabled = true;
        
        if (opts.text) {
            button.classList.add('btn-loading-text');
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"></span>
                ${opts.text}
            `;
        } else {
            button.classList.add('btn-loading');
        }
        
        return button;
    }
    
    function buttonReset(button) {
        if (!button) return;
        
        button.classList.remove('btn-loading', 'btn-loading-text');
        button.innerHTML = button.dataset.originalText || button.innerHTML;
        button.disabled = button.dataset.originalDisabled === 'true';
        
        delete button.dataset.originalText;
        delete button.dataset.originalDisabled;
    }
    
    // ============================================
    // AUTO-LISTENERS PARA FORMULARIOS
    // ============================================
    function attachFormListeners() {
        // Interceptar envío de formularios
        document.addEventListener('submit', function(e) {
            const form = e.target;
            
            // Ignorar si ya tiene su propio handler
            if (form.dataset.loadingHandled === 'true') return;
            
            // Aplicar loading al botón de submit
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                buttonLoading(submitBtn, { text: 'Enviando...' });
            }
            
            // Mostrar barra global
            GlobalBar.start();
            
            // Auto-resetear después de 10 segundos (fallback)
            setTimeout(() => {
                GlobalBar.complete();
                if (submitBtn) buttonReset(submitBtn);
            }, 10000);
        });
    }
    
    // ============================================
    // AUTO-LISTENERS PARA AJAX CON FETCH
    // ============================================
    function interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = function(...args) {
            // Verificar si la request tiene header AJAX
            const isAjax = args[1]?.headers?.['X-Requested-With'] === 'XMLHttpRequest';
            
            if (isAjax) {
                GlobalBar.start();
            }
            
            return originalFetch.apply(this, args)
                .then(response => {
                    if (isAjax) {
                        GlobalBar.complete();
                    }
                    return response;
                })
                .catch(error => {
                    if (isAjax) {
                        GlobalBar.error();
                    }
                    throw error;
                });
        };
    }
    
    // ============================================
    // AUTO-LISTENERS PARA ENLACES
    // ============================================
    function attachLinkListeners() {
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            
            if (link && link.href && !link.target && !link.download) {
                // Ignorar #, mailto:, tel:, javascript:
                if (link.href.startsWith('#') || 
                    link.href.startsWith('mailto:') ||
                    link.href.startsWith('tel:') ||
                    link.href.startsWith('javascript:')) {
                    return;
                }
                
                // Mostrar barra global
                GlobalBar.start();
                
                // Auto-completar después de navegación
                setTimeout(() => {
                    GlobalBar.complete();
                }, 5000);
            }
        });
    }
    
    // ============================================
    // INICIALIZACIÓN
    // ============================================
    function init() {
        GlobalBar.init();
        attachFormListeners();
        interceptFetch();
        attachLinkListeners();
        
        console.log('✅ LoadingIndicators inicializado');
    }
    
    // ============================================
    // API PÚBLICA
    // ============================================
    return {
        init,
        
        // Barra global
        startGlobal: () => GlobalBar.start(),
        completeGlobal: () => GlobalBar.complete(),
        errorGlobal: () => GlobalBar.error(),
        
        // Overlays
        showOverlay,
        hideOverlay,
        
        // Botones
        buttonLoading,
        buttonReset,
    };
})();

// ============================================
// INICIALIZACIÓN AUTOMÁTICA
// ============================================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', LoadingIndicators.init);
} else {
    LoadingIndicators.init();
}

// Exponer globalmente
window.LoadingIndicators = LoadingIndicators;