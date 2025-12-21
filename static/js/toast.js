/**
 * ================================================================
 * SISTEMA DE NOTIFICACIONES TOAST PROFESIONAL
 * ================================================================
 * 
 * Uso:
 * Toast.success('Título', 'Mensaje')
 * Toast.error('Título', 'Mensaje')
 * Toast.warning('Título', 'Mensaje')
 * Toast.info('Título', 'Mensaje')
 */

const Toast = (function() {
    'use strict';
    
    // Configuración por defecto
    const defaults = {
        duration: 4000,        // Duración en ms
        position: 'top-right', // Posición del contenedor
        closeButton: true,     // Mostrar botón de cerrar
        progressBar: true,     // Mostrar barra de progreso
        pauseOnHover: true,    // Pausar al hacer hover
        sound: false,          // Reproducir sonido (opcional)
        maxToasts: 5,          // Máximo de toasts simultáneos
    };
    
    // Iconos para cada tipo
    const icons = {
        success: '<i class="bi bi-check-circle-fill"></i>',
        error: '<i class="bi bi-x-circle-fill"></i>',
        warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
        info: '<i class="bi bi-info-circle-fill"></i>',
    };
    
    // Contenedor de toasts
    let container = null;
    
    /**
     * Inicializar el contenedor si no existe
     */
    function initContainer() {
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }
    
    /**
     * Crear un toast
     */
    function createToast(type, title, message, options = {}) {
        const config = { ...defaults, ...options };
        const toastContainer = initContainer();
        
        // Limitar número de toasts
        const existingToasts = toastContainer.querySelectorAll('.toast-notification');
        if (existingToasts.length >= config.maxToasts) {
            // Remover el más antiguo
            removeToast(existingToasts[0], true);
        }
        
        // Crear elemento toast
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        
        // Construir HTML
        let html = `
            <div class="toast-icon">
                ${icons[type] || icons.info}
            </div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${escapeHtml(title)}</div>` : ''}
                ${message ? `<div class="toast-message">${escapeHtml(message)}</div>` : ''}
            </div>
        `;
        
        if (config.closeButton) {
            html += `
                <button type="button" class="toast-close" aria-label="Cerrar">
                    <i class="bi bi-x"></i>
                </button>
            `;
        }
        
        if (config.progressBar) {
            html += `<div class="toast-progress"></div>`;
        }
        
        toast.innerHTML = html;
        
        // Agregar al contenedor
        toastContainer.appendChild(toast);
        
        // Event listeners
        if (config.closeButton) {
            const closeBtn = toast.querySelector('.toast-close');
            closeBtn.addEventListener('click', () => removeToast(toast));
        }
        
        // Pausar/reanudar al hacer hover
        if (config.duration <= 0) {
            // Persistente: sin auto-cierre ni barra de progreso
        } else if (config.pauseOnHover) {
            let remainingTime = config.duration;
            let startTime = Date.now();
            let timeoutId;
            
            const progressBar = toast.querySelector('.toast-progress');
            
            function startProgress() {
                if (progressBar) {
                    progressBar.style.width = '100%';
                    progressBar.style.transition = `width ${remainingTime}ms linear`;
                    
                    // Forzar reflow para que la transición funcione
                    void progressBar.offsetWidth;
                    
                    progressBar.style.width = '0%';
                }
                
                timeoutId = setTimeout(() => {
                    removeToast(toast);
                }, remainingTime);
            }
            
            function pauseProgress() {
                clearTimeout(timeoutId);
                const elapsed = Date.now() - startTime;
                remainingTime -= elapsed;
                
                if (progressBar) {
                    const currentWidth = parseFloat(window.getComputedStyle(progressBar).width);
                    const totalWidth = progressBar.parentElement.offsetWidth;
                    const percentage = (currentWidth / totalWidth) * 100;
                    progressBar.style.transition = 'none';
                    progressBar.style.width = `${percentage}%`;
                }
            }
            
            function resumeProgress() {
                startTime = Date.now();
                startProgress();
            }
            
            toast.addEventListener('mouseenter', pauseProgress);
            toast.addEventListener('mouseleave', resumeProgress);
            
            // Iniciar progreso
            startProgress();
        } else if (config.duration > 0) {
            // Sin hover, simplemente timeout
            if (config.progressBar) {
                const progressBar = toast.querySelector('.toast-progress');
                progressBar.style.width = '100%';
                progressBar.style.transition = `width ${config.duration}ms linear`;
                void progressBar.offsetWidth;
                progressBar.style.width = '0%';
            }
            
            setTimeout(() => {
                removeToast(toast);
            }, config.duration);
        } else {
            // Persistente sin hover
        }
        
        // Animación de entrada
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
        
        // Reproducir sonido (opcional)
        if (config.sound) {
            playSound(type);
        }
        
        return toast;
    }
    
    /**
     * Remover un toast
     */
    function removeToast(toast, immediate = false) {
        if (!toast || !toast.parentElement) return;
        
        if (immediate) {
            toast.remove();
        } else {
            toast.classList.remove('show');
            toast.classList.add('hide');
            
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
                
                // Remover contenedor si está vacío
                if (container && container.children.length === 0) {
                    container.remove();
                    container = null;
                }
            }, 300);
        }
    }
    
    /**
     * Escapar HTML para prevenir XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Reproducir sonido (opcional)
     */
    function playSound(type) {
        // Puedes agregar sonidos personalizados aquí
        // const audio = new Audio(`/static/sounds/${type}.mp3`);
        // audio.play().catch(() => {});
    }
    
    /**
     * Limpiar todos los toasts
     */
    function clearAll() {
        if (container) {
            const toasts = container.querySelectorAll('.toast-notification');
            toasts.forEach(toast => removeToast(toast, true));
        }
    }
    
    // API Pública
    return {
        success: (title, message, options) => createToast('success', title, message, options),
        error: (title, message, options) => createToast('error', title, message, options),
        warning: (title, message, options) => createToast('warning', title, message, options),
        info: (title, message, options) => createToast('info', title, message, options),
        clearAll: clearAll,
        
        // Método personalizado
        custom: (type, title, message, options) => createToast(type, title, message, options),
    };
})();

// Hacer disponible globalmente
window.Toast = Toast;
