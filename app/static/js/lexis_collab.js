/**
 * Lexis Collaborative Features
 * Gestion des dossiers, notes, commentaires, surlignages et pièces jointes
 */

// État global
const state = {
    currentArticleId: null,
    currentFolderId: 'all',
    folders: [],
    selectedColor: '#0066A1',
    selectedIcon: 'folder'
};

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initializeCollaborativeFeatures();
    loadFolders();
    setupEventListeners();
});

/**
 * Initialisation des fonctionnalités collaboratives
 */
function initializeCollaborativeFeatures() {
    console.log('🚀 Initialisation des fonctionnalités collaboratives');

    // Charger les compteurs
    updateFolderCounts();
}

/**
 * Configuration des écouteurs d'événements
 */
function setupEventListeners() {
    // Bouton créer dossier
    const btnAddFolder = document.getElementById('btnAddFolder');
    if (btnAddFolder) {
        btnAddFolder.addEventListener('click', () => openModal('modalCreateFolder'));
    }

    // Bouton confirmer création dossier
    const btnConfirmCreateFolder = document.getElementById('btnConfirmCreateFolder');
    if (btnConfirmCreateFolder) {
        btnConfirmCreateFolder.addEventListener('click', createFolder);
    }

    // Color picker
    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
            state.selectedColor = this.dataset.color;
            document.getElementById('folderColor').value = this.dataset.color;
        });
    });

    // Icon picker
    document.querySelectorAll('.icon-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.icon-option').forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
            state.selectedIcon = this.dataset.icon;
            document.getElementById('folderIcon').value = this.dataset.icon;
        });
    });

    // Panel tabs
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchPanelTab(tabName);
        });
    });

    // Fermer le panel
    const btnClosePanel = document.getElementById('btnClosePanel');
    if (btnClosePanel) {
        btnClosePanel.addEventListener('click', closeArticlePanel);
    }

    const panelOverlay = document.getElementById('panelOverlay');
    if (panelOverlay) {
        panelOverlay.addEventListener('click', closeArticlePanel);
    }

    // Boutons collaboratifs sur les cartes
    document.addEventListener('click', function(e) {
        // Bouton ajouter à dossier
        if (e.target.closest('.btn-folder')) {
            const articleId = e.target.closest('.btn-folder').dataset.id;
            showAddToFolderModal(articleId);
        }

        // Bouton note rapide
        if (e.target.closest('.btn-note')) {
            const articleId = e.target.closest('.btn-note').dataset.id;
            openArticlePanel(articleId, 'notes');
        }

        // Bouton détails
        if (e.target.closest('.btn-details')) {
            const articleId = e.target.closest('.btn-details').dataset.id;
            openArticlePanel(articleId, 'notes');
        }

        // Clic sur un dossier
        if (e.target.closest('.folder-item')) {
            const folderId = e.target.closest('.folder-item').dataset.folderId;
            filterByFolder(folderId);
        }
    });

    // Bouton confirmer ajout à dossier
    const btnConfirmAddToFolder = document.getElementById('btnConfirmAddToFolder');
    if (btnConfirmAddToFolder) {
        btnConfirmAddToFolder.addEventListener('click', confirmAddToFolder);
    }

    // Bouton sauvegarder note
    const btnSaveNote = document.getElementById('btnSaveNote');
    if (btnSaveNote) {
        btnSaveNote.addEventListener('click', saveNote);
    }

    // Bouton sauvegarder commentaire
    const btnSaveComment = document.getElementById('btnSaveComment');
    if (btnSaveComment) {
        btnSaveComment.addEventListener('click', saveComment);
    }

    // Bouton upload pièce jointe
    const btnUploadAttachment = document.getElementById('btnUploadAttachment');
    if (btnUploadAttachment) {
        btnUploadAttachment.addEventListener('click', () => {
            document.getElementById('attachmentFile').click();
        });
    }

    const attachmentFile = document.getElementById('attachmentFile');
    if (attachmentFile) {
        attachmentFile.addEventListener('change', uploadAttachment);
    }

    // Empêcher la propagation des clics dans les articles
    document.addEventListener('click', function(e) {
        const articleContent = e.target.closest('.article-content');
        if (articleContent && !e.target.closest('.collab-btn')) {
            const url = articleContent.dataset.articleUrl;
            const articleId = articleContent.dataset.articleId;
            if (url) {
                openArticle(url, articleId);
            }
        }
    });
}

/**
 * Charger les dossiers depuis l'API
 */
async function loadFolders() {
    try {
        const response = await fetch('/api/folders');
        const data = await response.json();

        if (data.success) {
            state.folders = [...data.own_folders, ...data.shared_folders];
            renderFolders();
            updateFolderSelect();
        }
    } catch (error) {
        console.error('Erreur lors du chargement des dossiers:', error);
    }
}

/**
 * Afficher les dossiers dans la sidebar
 */
function renderFolders() {
    const foldersList = document.getElementById('foldersList');
    if (!foldersList) return;

    // Garder le dossier "Tous les articles"
    const allFolder = foldersList.querySelector('[data-folder-id="all"]');
    foldersList.innerHTML = '';
    if (allFolder) {
        foldersList.appendChild(allFolder);
    }

    // Ajouter les dossiers
    state.folders.forEach(folder => {
        const folderItem = document.createElement('div');
        folderItem.className = 'folder-item';
        folderItem.dataset.folderId = folder.id;

        folderItem.innerHTML = `
            <i class="bi bi-${folder.icon} folder-icon" style="color: ${folder.color};"></i>
            <span class="folder-name">${folder.name}</span>
            <span class="folder-count">${folder.article_count || 0}</span>
            <div class="folder-actions">
                <button class="folder-action-btn" onclick="editFolder(${folder.id})" title="Modifier">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="folder-action-btn" onclick="deleteFolder(${folder.id})" title="Supprimer">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;

        foldersList.appendChild(folderItem);
    });
}

/**
 * Mettre à jour le select des dossiers dans le modal
 */
function updateFolderSelect() {
    const selectFolder = document.getElementById('selectFolder');
    if (!selectFolder) return;

    selectFolder.innerHTML = '<option value="">Choisir...</option>';

    state.folders.forEach(folder => {
        const option = document.createElement('option');
        option.value = folder.id;
        option.textContent = folder.name;
        selectFolder.appendChild(option);
    });
}

/**
 * Créer un nouveau dossier
 */
async function createFolder() {
    const name = document.getElementById('folderName').value.trim();
    const color = state.selectedColor;
    const icon = state.selectedIcon;

    if (!name) {
        alert('Veuillez entrer un nom pour le dossier');
        return;
    }

    try {
        const response = await fetch('/api/folders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, color, icon })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Dossier créé avec succès', 'success');
            closeModal('modalCreateFolder');

            // Réinitialiser le formulaire
            document.getElementById('folderName').value = '';
            state.selectedColor = '#0066A1';
            state.selectedIcon = 'folder';

            // Recharger les dossiers
            await loadFolders();
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de la création du dossier', 'error');
    }
}

/**
 * Afficher le modal d'ajout à un dossier
 */
function showAddToFolderModal(articleId) {
    state.currentArticleId = articleId;
    openModal('modalAddToFolder');
}

/**
 * Confirmer l'ajout d'un article à un dossier
 */
async function confirmAddToFolder() {
    const folderId = document.getElementById('selectFolder').value;

    if (!folderId) {
        alert('Veuillez sélectionner un dossier');
        return;
    }

    try {
        const response = await fetch(`/api/folders/${folderId}/articles/${state.currentArticleId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Article ajouté au dossier', 'success');
            closeModal('modalAddToFolder');
            await loadFolders(); // Recharger pour mettre à jour les compteurs
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de l\'ajout au dossier', 'error');
    }
}

/**
 * Filtrer les articles par dossier
 */
function filterByFolder(folderId) {
    state.currentFolderId = folderId;

    // Mettre à jour l'UI
    document.querySelectorAll('.folder-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-folder-id="${folderId}"]`)?.classList.add('active');

    // Filtrer les articles
    const articles = document.querySelectorAll('.article-card');

    if (folderId === 'all') {
        articles.forEach(article => article.style.display = '');
    } else {
        // TODO: Implémenter le filtrage réel basé sur les dossiers
        // Pour l'instant, on affiche tous les articles
        articles.forEach(article => article.style.display = '');
    }
}

/**
 * Ouvrir le panel de détails d'un article
 */
async function openArticlePanel(articleId, tab = 'notes') {
    state.currentArticleId = articleId;

    const panel = document.getElementById('articleDetailPanel');
    const overlay = document.getElementById('panelOverlay');

    panel.classList.add('open');
    overlay.classList.add('show');

    switchPanelTab(tab);

    // Charger les données
    await loadArticleNotes(articleId);
    await loadArticleComments(articleId);
    await loadArticleHighlights(articleId);
    await loadArticleAttachments(articleId);
}

/**
 * Fermer le panel de détails
 */
function closeArticlePanel() {
    const panel = document.getElementById('articleDetailPanel');
    const overlay = document.getElementById('panelOverlay');

    panel.classList.remove('open');
    overlay.classList.remove('show');

    state.currentArticleId = null;
}

/**
 * Changer d'onglet dans le panel
 */
function switchPanelTab(tabName) {
    // Mettre à jour les onglets
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

    // Mettre à jour les panneaux
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(`tab${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`)?.classList.add('active');
}

/**
 * Charger les notes d'un article
 */
async function loadArticleNotes(articleId) {
    try {
        const response = await fetch(`/api/articles/${articleId}/notes`);
        const data = await response.json();

        if (data.success) {
            renderNotes(data.notes);
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Afficher les notes
 */
function renderNotes(notes) {
    const notesList = document.getElementById('notesList');
    if (!notesList) return;

    if (notes.length === 0) {
        notesList.innerHTML = '<p style="color: var(--lexis-gray-600);">Aucune note pour cet article.</p>';
        return;
    }

    notesList.innerHTML = notes.map(note => `
        <div class="note-item">
            <div class="note-header">
                <span class="note-meta">
                    ${new Date(note.created_at).toLocaleDateString('fr-FR')}
                </span>
                <div class="note-actions">
                    <button class="folder-action-btn" onclick="editNote(${note.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="folder-action-btn" onclick="deleteNote(${note.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="note-text">${escapeHtml(note.content)}</div>
        </div>
    `).join('');
}

/**
 * Sauvegarder une note
 */
async function saveNote() {
    const content = document.getElementById('noteTextarea').value.trim();

    if (!content) {
        alert('Veuillez entrer une note');
        return;
    }

    try {
        const response = await fetch(`/api/articles/${state.currentArticleId}/notes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content, is_private: true })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Note enregistrée', 'success');
            document.getElementById('noteTextarea').value = '';
            await loadArticleNotes(state.currentArticleId);
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de l\'enregistrement', 'error');
    }
}

/**
 * Supprimer une note
 */
async function deleteNote(noteId) {
    if (!confirm('Voulez-vous vraiment supprimer cette note ?')) return;

    try {
        const response = await fetch(`/api/articles/notes/${noteId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Note supprimée', 'success');
            await loadArticleNotes(state.currentArticleId);
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de la suppression', 'error');
    }
}

/**
 * Charger les commentaires d'un article
 */
async function loadArticleComments(articleId) {
    try {
        const response = await fetch(`/api/articles/${articleId}/comments`);
        const data = await response.json();

        if (data.success) {
            renderComments(data.comments);
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Afficher les commentaires
 */
function renderComments(comments) {
    const commentsList = document.getElementById('commentsList');
    if (!commentsList) return;

    if (comments.length === 0) {
        commentsList.innerHTML = '<p style="color: var(--lexis-gray-600);">Aucun commentaire pour cet article.</p>';
        return;
    }

    commentsList.innerHTML = comments.map(comment => {
        const initials = comment.author?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U';
        return `
            <div class="comment-item">
                <div class="comment-header">
                    <div class="comment-avatar">${initials}</div>
                    <div>
                        <div class="comment-author">${comment.author || 'Utilisateur'}</div>
                        <div class="comment-time">${new Date(comment.created_at).toLocaleString('fr-FR')}</div>
                    </div>
                </div>
                <div class="comment-text">${escapeHtml(comment.content)}</div>
                <div class="comment-actions">
                    <span class="comment-action" onclick="replyToComment(${comment.id})">Répondre</span>
                    <span class="comment-action" onclick="deleteComment(${comment.id})">Supprimer</span>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Sauvegarder un commentaire
 */
async function saveComment() {
    const content = document.getElementById('commentTextarea').value.trim();

    if (!content) {
        alert('Veuillez entrer un commentaire');
        return;
    }

    try {
        const response = await fetch(`/api/articles/${state.currentArticleId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Commentaire publié', 'success');
            document.getElementById('commentTextarea').value = '';
            await loadArticleComments(state.currentArticleId);
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de la publication', 'error');
    }
}

/**
 * Charger les surlignages d'un article
 */
async function loadArticleHighlights(articleId) {
    try {
        const response = await fetch(`/api/articles/${articleId}/highlights`);
        const data = await response.json();

        if (data.success) {
            renderHighlights(data.highlights);
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Afficher les surlignages
 */
function renderHighlights(highlights) {
    const highlightsList = document.getElementById('highlightsList');
    if (!highlightsList) return;

    if (highlights.length === 0) {
        highlightsList.innerHTML = '<p style="color: var(--lexis-gray-600);">Aucun surlignage pour cet article.</p>';
        return;
    }

    highlightsList.innerHTML = highlights.map(highlight => `
        <div class="highlight-item">
            <span class="highlight-color" style="background: ${highlight.color};"></span>
            <span class="highlight-text" style="background: ${highlight.color};">${escapeHtml(highlight.text)}</span>
            <button class="folder-action-btn" onclick="deleteHighlight(${highlight.id})" style="float: right;">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `).join('');
}

/**
 * Charger les pièces jointes d'un article
 */
async function loadArticleAttachments(articleId) {
    try {
        const response = await fetch(`/api/articles/${articleId}/attachments`);
        const data = await response.json();

        if (data.success) {
            renderAttachments(data.attachments);
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Afficher les pièces jointes
 */
function renderAttachments(attachments) {
    const attachmentsList = document.getElementById('attachmentsList');
    if (!attachmentsList) return;

    if (attachments.length === 0) {
        attachmentsList.innerHTML = '<p style="color: var(--lexis-gray-600);">Aucune pièce jointe pour cet article.</p>';
        return;
    }

    attachmentsList.innerHTML = attachments.map(attachment => {
        const icon = getFileIcon(attachment.filename);
        const size = formatFileSize(attachment.file_size);

        return `
            <div class="attachment-item">
                <div class="attachment-icon">
                    <i class="bi bi-${icon}"></i>
                </div>
                <div class="attachment-info">
                    <div class="attachment-name">${escapeHtml(attachment.filename)}</div>
                    <div class="attachment-size">${size} • ${new Date(attachment.uploaded_at).toLocaleDateString('fr-FR')}</div>
                </div>
                <button class="folder-action-btn" onclick="deleteAttachment(${attachment.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
    }).join('');
}

/**
 * Upload une pièce jointe
 */
async function uploadAttachment() {
    const fileInput = document.getElementById('attachmentFile');
    const file = fileInput.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`/api/articles/${state.currentArticleId}/attachments`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Fichier téléchargé', 'success');
            fileInput.value = '';
            await loadArticleAttachments(state.currentArticleId);
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors du téléchargement', 'error');
    }
}

/**
 * Mettre à jour les compteurs de dossiers
 */
async function updateFolderCounts() {
    // Cette fonction sera appelée après chaque modification
    await loadFolders();
}

/**
 * Ouvrir un modal
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

/**
 * Fermer un modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

/**
 * Afficher un toast de notification
 */
function showToast(message, type = 'info') {
    // Simple alert pour l'instant, on peut améliorer avec un vrai toast
    console.log(`[${type}] ${message}`);
    alert(message);
}

/**
 * Ouvrir un article dans un nouvel onglet
 */
function openArticle(url, articleId) {
    // Marquer comme lu
    markAsRead(articleId);

    // Ouvrir l'article
    window.open(url, '_blank');
}

/**
 * Marquer un article comme lu
 */
async function markAsRead(articleId) {
    try {
        await fetch(`/api/articles/${articleId}/read`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Utilitaires
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        'pdf': 'file-pdf',
        'doc': 'file-word',
        'docx': 'file-word',
        'xls': 'file-excel',
        'xlsx': 'file-excel',
        'zip': 'file-zip',
        'jpg': 'file-image',
        'jpeg': 'file-image',
        'png': 'file-image',
        'txt': 'file-text'
    };
    return icons[ext] || 'file-earmark';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Modifier un dossier
 */
async function editFolder(folderId) {
    showToast('⚠️ Fonctionnalité en développement', 'info');
    // TODO: Implémenter la modification de dossier
}

/**
 * Supprimer un dossier
 */
async function deleteFolder(folderId) {
    if (!confirm('Voulez-vous vraiment supprimer ce dossier ?')) return;

    try {
        const response = await fetch(`/api/folders/${folderId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Dossier supprimé', 'success');
            await loadFolders();
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de la suppression', 'error');
    }
}

/**
 * Modifier une note
 */
async function editNote(noteId) {
    showToast('⚠️ Fonctionnalité en développement', 'info');
    // TODO: Implémenter la modification de note
}

/**
 * Répondre à un commentaire
 */
async function replyToComment(commentId) {
    showToast('⚠️ Fonctionnalité en développement', 'info');
    // TODO: Implémenter la réponse aux commentaires
}

/**
 * Supprimer un commentaire
 */
async function deleteComment(commentId) {
    if (!confirm('Voulez-vous vraiment supprimer ce commentaire ?')) return;

    try {
        const response = await fetch(`/api/articles/comments/${commentId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Commentaire supprimé', 'success');
            await loadArticleComments(state.currentArticleId);
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de la suppression', 'error');
    }
}

/**
 * Supprimer un surlignage
 */
async function deleteHighlight(highlightId) {
    if (!confirm('Voulez-vous vraiment supprimer ce surlignage ?')) return;

    try {
        const response = await fetch(`/api/articles/highlights/${highlightId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Surlignage supprimé', 'success');
            await loadArticleHighlights(state.currentArticleId);
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de la suppression', 'error');
    }
}

/**
 * Supprimer une pièce jointe
 */
async function deleteAttachment(attachmentId) {
    if (!confirm('Voulez-vous vraiment supprimer cette pièce jointe ?')) return;

    try {
        const response = await fetch(`/api/articles/attachments/${attachmentId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Pièce jointe supprimée', 'success');
            await loadArticleAttachments(state.currentArticleId);
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showToast('❌ Erreur lors de la suppression', 'error');
    }
}
