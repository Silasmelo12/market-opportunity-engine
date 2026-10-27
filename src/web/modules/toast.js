// Módulo de notificações (toast) e feedback de carregamento (loading)
// Extraído de src/web/app.js (Etapa 3 da Modularização - Spec 022)

function showToastNotification(message, isSuccess = true, onUndo = null) {
  const toast = document.getElementById('toast-notification');
  const msgEl = document.getElementById('toast-message');
  const iconEl = document.getElementById('toast-icon');
  const undoBtn = document.getElementById('toast-action-btn');
  if (!toast || !msgEl) return;

  msgEl.textContent = message;
  if (iconEl) iconEl.innerHTML = isSuccess
    ? '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'
    : '<svg class="icon" aria-hidden="true"><use href="#icon-warning"></use></svg>';

  toast.className = `fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-2xl border text-xs font-medium transition-all duration-300 transform translate-y-0 opacity-100 pointer-events-auto ${
    isSuccess
      ? 'bg-fintech-surface border-emerald-500/50 text-white'
      : 'bg-fintech-surface border-amber-500/50 text-white'
  }`;

  if (undoBtn) {
    if (typeof onUndo === 'function') {
      undoBtn.classList.remove('hidden');
      undoBtn.onclick = () => {
        onUndo();
        hideToastNotification();
      };
    } else {
      undoBtn.classList.add('hidden');
    }
  }

  if (window._toastTimeout) clearTimeout(window._toastTimeout);
  window._toastTimeout = setTimeout(() => {
    hideToastNotification();
  }, 6000);
}

function hideToastNotification() {
  const toast = document.getElementById('toast-notification');
  if (toast) {
    toast.className = 'fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-2xl border text-xs font-medium transition-all duration-300 transform translate-y-16 opacity-0 pointer-events-none';
  }
}

function showLoading(msg = 'Carregando...') {
  const loadingText = (typeof elements !== 'undefined' && elements && elements.loadingText)
    ? elements.loadingText
    : document.getElementById('loading-text');
  const loadingOverlay = (typeof elements !== 'undefined' && elements && elements.loadingOverlay)
    ? elements.loadingOverlay
    : document.getElementById('loading-spinner');

  if (loadingText) loadingText.textContent = msg;
  if (loadingOverlay) loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
  const loadingOverlay = (typeof elements !== 'undefined' && elements && elements.loadingOverlay)
    ? elements.loadingOverlay
    : document.getElementById('loading-spinner');

  if (loadingOverlay) loadingOverlay.classList.add('hidden');
}

// Exposição compatível para navegador (window) e Node.js (module.exports)
if (typeof window !== 'undefined') {
  window.showToastNotification = showToastNotification;
  window.hideToastNotification = hideToastNotification;
  window.showLoading = showLoading;
  window.hideLoading = hideLoading;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    showToastNotification,
    hideToastNotification,
    showLoading,
    hideLoading
  };
}
