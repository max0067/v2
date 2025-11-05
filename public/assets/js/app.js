/**
 * Application JavaScript pour Veille Juridique RSS
 */

// Utilitaires
const Utils = {
    /**
     * Afficher une notification toast
     */
    showAlert(message, type = 'info', duration = 4000) {
        const container = document.getElementById('alertContainer');
        if (!container) return;

        const alertTypes = {
            success: 'alert-success',
            error: 'alert-danger',
            warning: 'alert-warning',
            info: 'alert-info'
        };

        const icons = {
            success: 'check-circle-fill',
            error: 'exclamation-triangle-fill',
            warning: 'exclamation-circle-fill',
            info: 'info-circle-fill'
        };

        const alert = document.createElement('div');
        alert.className = `alert ${alertTypes[type]} alert-dismissible fade show`;
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            <i class="bi bi-${icons[type]}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(alert);

        // Auto-supprimer après la durée spécifiée
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, duration);
    },

    /**
     * Afficher/masquer l'overlay de chargement
     */
    toggleLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    },

    /**
     * Requête API
     */
    async apiRequest(url, options = {}) {
        try {
            const response = await fetch(url, options);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erreur API:', error);
            throw error;
        }
    }
};

// ===========================================
// PAGE INDEX - Gestion des articles
// ===========================================

if (window.location.pathname.includes('index.php') || window.location.pathname.endsWith('/')) {

    // Recherche d'articles
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            if (query.length === 0) {
                // Réafficher tous les articles
                document.querySelectorAll('.article-card').forEach(card => {
                    card.style.display = 'flex';
                });
                return;
            }

            if (query.length < 2) return;

            // Debounce de 500ms
            searchTimeout = setTimeout(async () => {
                try {
                    const data = await Utils.apiRequest(`api/search.php?q=${encodeURIComponent(query)}`);

                    if (data.success) {
                        displaySearchResults(data.articles);
                    }
                } catch (error) {
                    Utils.showAlert('Erreur lors de la recherche', 'error');
                }
            }, 500);
        });
    }

    /**
     * Afficher les résultats de recherche
     */
    function displaySearchResults(articles) {
        const container = document.getElementById('articlesContainer');
        if (!container) return;

        if (articles.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    Aucun article trouvé pour cette recherche.
                </div>
            `;
            return;
        }

        container.innerHTML = articles.map(article => `
            <div class="article-card" data-category="${escapeHtml(article.category)}">
                <div class="article-header">
                    <span class="badge bg-primary">${escapeHtml(article.category)}</span>
                    <span class="article-date">
                        <i class="bi bi-clock"></i>
                        ${formatDate(article.pub_date || article.created_at)}
                    </span>
                </div>
                <h3 class="article-title">
                    <a href="${escapeHtml(article.link)}" target="_blank">
                        ${escapeHtml(article.title)}
                    </a>
                </h3>
                ${article.description ? `
                    <p class="article-description">
                        ${escapeHtml(stripTags(article.description).substring(0, 200))}...
                    </p>
                ` : ''}
                <div class="article-footer">
                    <span class="article-source">
                        <i class="bi bi-rss"></i>
                        ${escapeHtml(article.feed_name)}
                    </span>
                    <a href="${escapeHtml(article.link)}" target="_blank" class="btn btn-sm btn-outline-primary">
                        Lire l'article <i class="bi bi-arrow-right"></i>
                    </a>
                </div>
            </div>
        `).join('');
    }

    // Actualiser les flux RSS
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            refreshBtn.disabled = true;
            Utils.toggleLoading(true);

            try {
                const data = await Utils.apiRequest('api/fetch-feeds.php');

                if (data.success) {
                    Utils.showAlert(data.message, 'success');

                    // Recharger la page après 1.5s pour afficher les nouveaux articles
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    Utils.showAlert('Erreur lors de la récupération des flux', 'error');
                    refreshBtn.disabled = false;
                    Utils.toggleLoading(false);
                }

                // Afficher les erreurs s'il y en a
                if (data.errors && data.errors.length > 0) {
                    console.warn('Erreurs de flux:', data.errors);
                }

            } catch (error) {
                Utils.showAlert('Erreur de connexion', 'error');
                refreshBtn.disabled = false;
                Utils.toggleLoading(false);
            }
        });
    }
}

// ===========================================
// PAGE MANAGE-FEEDS - Gestion des flux RSS
// ===========================================

if (window.location.pathname.includes('manage-feeds.php')) {

    // Ajouter un flux
    const saveFeedBtn = document.getElementById('saveFeedBtn');
    if (saveFeedBtn) {
        saveFeedBtn.addEventListener('click', async () => {
            const name = document.getElementById('feedName').value.trim();
            const url = document.getElementById('feedUrl').value.trim();
            const category = document.getElementById('feedCategory').value.trim();

            if (!name || !url) {
                Utils.showAlert('Veuillez remplir tous les champs requis', 'warning');
                return;
            }

            saveFeedBtn.disabled = true;

            try {
                const data = await Utils.apiRequest('api/add-feed.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, url, category })
                });

                if (data.success) {
                    Utils.showAlert(data.message, 'success');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    Utils.showAlert(data.error, 'error');
                    saveFeedBtn.disabled = false;
                }
            } catch (error) {
                Utils.showAlert('Erreur de connexion', 'error');
                saveFeedBtn.disabled = false;
            }
        });
    }

    // Modifier un flux
    const editButtons = document.querySelectorAll('.edit-feed');
    editButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const name = btn.dataset.name;
            const url = btn.dataset.url;
            const category = btn.dataset.category;

            document.getElementById('editFeedId').value = id;
            document.getElementById('editFeedName').value = name;
            document.getElementById('editFeedUrl').value = url;
            document.getElementById('editFeedCategory').value = category;

            const modal = new bootstrap.Modal(document.getElementById('editFeedModal'));
            modal.show();
        });
    });

    const updateFeedBtn = document.getElementById('updateFeedBtn');
    if (updateFeedBtn) {
        updateFeedBtn.addEventListener('click', async () => {
            const id = document.getElementById('editFeedId').value;
            const name = document.getElementById('editFeedName').value.trim();
            const url = document.getElementById('editFeedUrl').value.trim();
            const category = document.getElementById('editFeedCategory').value.trim();

            if (!name || !url) {
                Utils.showAlert('Veuillez remplir tous les champs requis', 'warning');
                return;
            }

            updateFeedBtn.disabled = true;

            try {
                const data = await Utils.apiRequest('api/update-feed.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id, name, url, category })
                });

                if (data.success) {
                    Utils.showAlert(data.message, 'success');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    Utils.showAlert(data.error, 'error');
                    updateFeedBtn.disabled = false;
                }
            } catch (error) {
                Utils.showAlert('Erreur de connexion', 'error');
                updateFeedBtn.disabled = false;
            }
        });
    }

    // Supprimer un flux
    const deleteButtons = document.querySelectorAll('.delete-feed');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const name = btn.dataset.name;

            if (!confirm(`Êtes-vous sûr de vouloir supprimer le flux "${name}" ?\n\nTous les articles associés seront également supprimés.`)) {
                return;
            }

            btn.disabled = true;

            try {
                const data = await Utils.apiRequest('api/delete-feed.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id })
                });

                if (data.success) {
                    Utils.showAlert(data.message, 'success');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    Utils.showAlert(data.error, 'error');
                    btn.disabled = false;
                }
            } catch (error) {
                Utils.showAlert('Erreur de connexion', 'error');
                btn.disabled = false;
            }
        });
    });
}

// ===========================================
// FONCTIONS UTILITAIRES
// ===========================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function stripTags(html) {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}
