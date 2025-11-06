/**
 * Application JavaScript pour Veille Juridique RSS
 */

// Utilitaires
const utils = {
    /**
     * Formater une date ISO en format français
     */
    formatDate: function(isoString) {
        if (!isoString) return 'N/A';
        const date = new Date(isoString);
        return date.toLocaleString('fr-FR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Tronquer un texte
     */
    truncate: function(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    /**
     * Échapper le HTML
     */
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Afficher une notification toast
     */
    showToast: function(message, type = 'info') {
        // Pour l'instant, on utilise alert
        // On pourrait implémenter un système de toast plus sophistiqué
        if (type === 'error') {
            alert('Erreur: ' + message);
        } else {
            alert(message);
        }
    }
};

// API Client
const api = {
    /**
     * Effectuer une requête API
     */
    request: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Une erreur est survenue');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Récupérer tous les flux
     */
    getFeeds: async function() {
        return await this.request('/api/feeds');
    },

    /**
     * Ajouter un flux
     */
    addFeed: async function(feedData) {
        return await this.request('/api/feeds', {
            method: 'POST',
            body: JSON.stringify(feedData)
        });
    },

    /**
     * Mettre à jour un flux
     */
    updateFeed: async function(feedId, feedData) {
        return await this.request(`/api/feeds/${feedId}`, {
            method: 'PUT',
            body: JSON.stringify(feedData)
        });
    },

    /**
     * Supprimer un flux
     */
    deleteFeed: async function(feedId) {
        return await this.request(`/api/feeds/${feedId}`, {
            method: 'DELETE'
        });
    },

    /**
     * Actualiser tous les flux
     */
    refreshFeeds: async function() {
        return await this.request('/api/feeds/refresh', {
            method: 'POST'
        });
    },

    /**
     * Actualiser un flux spécifique
     */
    refreshFeed: async function(feedId) {
        return await this.request(`/api/feeds/${feedId}/refresh`, {
            method: 'POST'
        });
    },

    /**
     * Rechercher des articles
     */
    searchArticles: async function(query, page = 1) {
        return await this.request(`/api/articles/search?q=${encodeURIComponent(query)}&page=${page}`);
    },

    /**
     * Récupérer les articles
     */
    getArticles: async function(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/api/articles?${queryString}`);
    },

    /**
     * Récupérer les statistiques
     */
    getStats: async function() {
        return await this.request('/api/stats');
    }
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Veille Juridique RSS - Application chargée');

    // Gestion des formulaires avec validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-hide des alerts après 5 secondes
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Gestion du focus sur les modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input:not([type="hidden"])');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Réinitialiser les formulaires à la fermeture des modals
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
            }
        });
    });
});

// Exporter les utilitaires pour utilisation globale
window.appUtils = utils;
window.appApi = api;
