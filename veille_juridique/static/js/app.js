/**
 * JavaScript pour l'application de veille juridique
 */

// ========== Initialisation ==========

document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar sur mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar-wrapper');
            sidebar.classList.toggle('show');
        });
    }

    // Charger les statistiques
    loadStats();

    // Rafraîchir les stats toutes les 30 secondes
    setInterval(loadStats, 30000);
});

// ========== Fonctions utilitaires ==========

/**
 * Afficher un toast de notification
 * @param {string} message - Le message à afficher
 * @param {string} type - Type de notification (success, error, info, warning)
 */
function showToast(message, type = 'info') {
    const toastElement = document.getElementById('notificationToast');
    const toastBody = document.getElementById('toastMessage');
    const toastHeader = toastElement.querySelector('.toast-header');

    // Définir le message
    toastBody.textContent = message;

    // Définir la couleur selon le type
    toastHeader.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');

    switch (type) {
        case 'success':
            toastHeader.classList.add('bg-success', 'text-white');
            break;
        case 'error':
            toastHeader.classList.add('bg-danger', 'text-white');
            break;
        case 'warning':
            toastHeader.classList.add('bg-warning', 'text-dark');
            break;
        default:
            toastHeader.classList.add('bg-info', 'text-white');
    }

    // Afficher le toast
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    toast.show();
}

/**
 * Charger les statistiques de l'application
 */
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            // Mettre à jour les statistiques dans la sidebar
            const feedsElement = document.getElementById('stat-feeds');
            const articlesElement = document.getElementById('stat-articles');

            if (feedsElement) {
                feedsElement.textContent = stats.active_feeds + ' / ' + stats.total_feeds;
            }

            if (articlesElement) {
                articlesElement.textContent = stats.total_articles.toLocaleString('fr-FR');
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des statistiques:', error);
        });
}

/**
 * Rafraîchir tous les flux RSS
 */
function refreshFeeds() {
    const button = document.getElementById('refreshBtn');
    const originalContent = button.innerHTML;

    // Désactiver le bouton et afficher un spinner
    button.disabled = true;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        Actualisation en cours...
    `;

    fetch('/api/refresh', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');

            // Recharger la page après un court délai pour afficher les nouveaux articles
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showToast(data.error || 'Erreur lors de l\'actualisation', 'error');
            button.disabled = false;
            button.innerHTML = originalContent;
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showToast('Erreur lors de l\'actualisation des flux', 'error');
        button.disabled = false;
        button.innerHTML = originalContent;
    });
}

/**
 * Recherche avec debounce pour éviter trop de requêtes
 */
let searchTimeout = null;

function searchArticlesDebounced(query) {
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    searchTimeout = setTimeout(() => {
        performSearch(query);
    }, 300);
}

function performSearch(query) {
    if (query.length < 2) {
        return;
    }

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(articles => {
            displaySearchResults(articles);
        })
        .catch(error => {
            console.error('Erreur lors de la recherche:', error);
            showToast('Erreur lors de la recherche', 'error');
        });
}

/**
 * Formater une date de manière relative (il y a X minutes/heures/jours)
 * @param {string} dateString - Date au format ISO
 * @returns {string} Date formatée
 */
function formatRelativeDate(dateString) {
    if (!dateString) {
        return 'Date inconnue';
    }

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffMin < 1) {
        return 'À l\'instant';
    } else if (diffMin < 60) {
        return `Il y a ${diffMin} minute${diffMin > 1 ? 's' : ''}`;
    } else if (diffHour < 24) {
        return `Il y a ${diffHour} heure${diffHour > 1 ? 's' : ''}`;
    } else if (diffDay === 1) {
        return 'Hier';
    } else if (diffDay < 7) {
        return `Il y a ${diffDay} jours`;
    } else {
        const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
        return date.toLocaleDateString('fr-FR', options);
    }
}

/**
 * Valider une URL
 * @param {string} url - URL à valider
 * @returns {boolean}
 */
function isValidUrl(url) {
    try {
        const urlObject = new URL(url);
        return urlObject.protocol === 'http:' || urlObject.protocol === 'https:';
    } catch (e) {
        return false;
    }
}

/**
 * Tronquer un texte
 * @param {string} text - Texte à tronquer
 * @param {number} maxLength - Longueur maximale
 * @returns {string}
 */
function truncate(text, maxLength = 100) {
    if (!text) {
        return '';
    }
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

/**
 * Extraire le texte brut d'un HTML
 * @param {string} html - HTML
 * @returns {string}
 */
function stripHtml(html) {
    if (!html) {
        return '';
    }
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || '';
}

/**
 * Gérer les erreurs réseau
 * @param {Response} response - Réponse fetch
 * @returns {Promise}
 */
async function handleResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
        throw new Error(error.error || `Erreur HTTP ${response.status}`);
    }
    return response.json();
}

/**
 * Copier du texte dans le presse-papiers
 * @param {string} text - Texte à copier
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            showToast('Copié dans le presse-papiers', 'success');
        })
        .catch(err => {
            console.error('Erreur lors de la copie:', err);
            showToast('Erreur lors de la copie', 'error');
        });
}

/**
 * Confirmer une action destructive
 * @param {string} message - Message de confirmation
 * @returns {boolean}
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Charger les ressources de manière asynchrone
 * @param {string} url - URL de la ressource
 * @returns {Promise}
 */
async function loadResource(url) {
    try {
        const response = await fetch(url);
        return await handleResponse(response);
    } catch (error) {
        console.error(`Erreur lors du chargement de ${url}:`, error);
        throw error;
    }
}

/**
 * Debounce - limite le nombre d'appels à une fonction
 * @param {Function} func - Fonction à appeler
 * @param {number} wait - Délai d'attente en ms
 * @returns {Function}
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle - limite la fréquence d'appel d'une fonction
 * @param {Function} func - Fonction à appeler
 * @param {number} limit - Intervalle minimum en ms
 * @returns {Function}
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ========== Export des fonctions globales ==========

// Les fonctions suivantes sont disponibles globalement
window.showToast = showToast;
window.refreshFeeds = refreshFeeds;
window.loadStats = loadStats;
window.formatRelativeDate = formatRelativeDate;
window.isValidUrl = isValidUrl;
window.truncate = truncate;
window.stripHtml = stripHtml;
window.copyToClipboard = copyToClipboard;
window.confirmAction = confirmAction;
window.debounce = debounce;
window.throttle = throttle;
