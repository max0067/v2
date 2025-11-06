"""Routes pour la gestion des dossiers et collections."""
from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Article
from app.models_collab import User, Folder, ArticleFolder, FolderShare, ActivityLog

folders_bp = Blueprint('folders', __name__)


# ========== HELPER FUNCTIONS ==========

def get_current_user():
    """Récupérer l'utilisateur courant (ou créer un utilisateur par défaut)."""
    user_id = session.get('user_id')
    if not user_id:
        # Créer un utilisateur par défaut si aucun n'existe
        user = User.query.filter_by(email='default@veille.fr').first()
        if not user:
            user = User(
                email='default@veille.fr',
                username='utilisateur',
                full_name='Utilisateur par défaut',
                role='admin'
            )
            user.set_password('changeme')
            db.session.add(user)
            db.session.commit()
        session['user_id'] = user.id
        return user
    return User.query.get(user_id)


def log_activity(user, action, entity_type, entity_id, details=None):
    """Enregistrer une activité dans les logs."""
    log = ActivityLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=request.remote_addr
    )
    db.session.add(log)


# ========== ROUTES DOSSIERS ==========

@folders_bp.route('/folders', methods=['GET'])
def get_folders():
    """Récupérer tous les dossiers de l'utilisateur."""
    try:
        user = get_current_user()

        # Dossiers propres
        own_folders = Folder.query.filter_by(owner_id=user.id).all()

        # Dossiers partagés avec l'utilisateur
        shared_folders_ids = [share.folder_id for share in FolderShare.query.filter_by(shared_with_id=user.id).all()]
        shared_folders = Folder.query.filter(Folder.id.in_(shared_folders_ids)).all() if shared_folders_ids else []

        return jsonify({
            'success': True,
            'own_folders': [f.to_dict() for f in own_folders],
            'shared_folders': [f.to_dict() for f in shared_folders]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@folders_bp.route('/folders', methods=['POST'])
def create_folder():
    """Créer un nouveau dossier."""
    try:
        user = get_current_user()
        data = request.get_json()

        folder = Folder(
            name=data.get('name'),
            description=data.get('description'),
            color=data.get('color', '#0066A1'),
            icon=data.get('icon', 'folder'),
            owner_id=user.id,
            parent_id=data.get('parent_id')
        )

        db.session.add(folder)
        db.session.commit()

        log_activity(user, 'create', 'folder', folder.id, {'name': folder.name})

        return jsonify({
            'success': True,
            'folder': folder.to_dict(),
            'message': 'Dossier créé avec succès'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@folders_bp.route('/folders/<int:folder_id>', methods=['PUT'])
def update_folder(folder_id):
    """Mettre à jour un dossier."""
    try:
        user = get_current_user()
        folder = Folder.query.get_or_404(folder_id)

        # Vérifier les permissions
        if folder.owner_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        data = request.get_json()

        if 'name' in data:
            folder.name = data['name']
        if 'description' in data:
            folder.description = data['description']
        if 'color' in data:
            folder.color = data['color']
        if 'icon' in data:
            folder.icon = data['icon']

        db.session.commit()

        log_activity(user, 'update', 'folder', folder.id, {'name': folder.name})

        return jsonify({
            'success': True,
            'folder': folder.to_dict(),
            'message': 'Dossier mis à jour'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@folders_bp.route('/folders/<int:folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    """Supprimer un dossier."""
    try:
        user = get_current_user()
        folder = Folder.query.get_or_404(folder_id)

        # Vérifier les permissions
        if folder.owner_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        log_activity(user, 'delete', 'folder', folder.id, {'name': folder.name})

        db.session.delete(folder)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Dossier supprimé'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTES ARTICLES DANS DOSSIERS ==========

@folders_bp.route('/folders/<int:folder_id>/articles', methods=['GET'])
def get_folder_articles(folder_id):
    """Récupérer tous les articles d'un dossier."""
    try:
        folder = Folder.query.get_or_404(folder_id)

        articles = [af.article.to_dict() for af in folder.articles.all()]

        return jsonify({
            'success': True,
            'folder': folder.to_dict(),
            'articles': articles
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@folders_bp.route('/folders/<int:folder_id>/articles/<int:article_id>', methods=['POST'])
def add_article_to_folder(folder_id, article_id):
    """Ajouter un article à un dossier."""
    try:
        user = get_current_user()
        folder = Folder.query.get_or_404(folder_id)
        article = Article.query.get_or_404(article_id)

        # Vérifier si l'article est déjà dans le dossier
        existing = ArticleFolder.query.filter_by(
            article_id=article_id,
            folder_id=folder_id
        ).first()

        if existing:
            return jsonify({
                'success': False,
                'error': 'Article déjà dans ce dossier'
            }), 400

        article_folder = ArticleFolder(
            article_id=article_id,
            folder_id=folder_id,
            added_by=user.id
        )

        db.session.add(article_folder)
        db.session.commit()

        log_activity(user, 'add_to_folder', 'article', article_id, {
            'folder_id': folder_id,
            'folder_name': folder.name
        })

        return jsonify({
            'success': True,
            'message': f'Article ajouté au dossier "{folder.name}"'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@folders_bp.route('/folders/<int:folder_id>/articles/<int:article_id>', methods=['DELETE'])
def remove_article_from_folder(folder_id, article_id):
    """Retirer un article d'un dossier."""
    try:
        user = get_current_user()

        article_folder = ArticleFolder.query.filter_by(
            article_id=article_id,
            folder_id=folder_id
        ).first_or_404()

        log_activity(user, 'remove_from_folder', 'article', article_id, {'folder_id': folder_id})

        db.session.delete(article_folder)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Article retiré du dossier'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ROUTES PARTAGE ==========

@folders_bp.route('/folders/<int:folder_id>/share', methods=['POST'])
def share_folder(folder_id):
    """Partager un dossier avec un autre utilisateur."""
    try:
        user = get_current_user()
        folder = Folder.query.get_or_404(folder_id)

        # Vérifier les permissions
        if folder.owner_id != user.id:
            return jsonify({'success': False, 'error': 'Seul le propriétaire peut partager'}), 403

        data = request.get_json()
        shared_with_email = data.get('email')
        permission = data.get('permission', 'read')

        # Trouver l'utilisateur
        shared_user = User.query.filter_by(email=shared_with_email).first()
        if not shared_user:
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 404

        # Vérifier si déjà partagé
        existing = FolderShare.query.filter_by(
            folder_id=folder_id,
            shared_with_id=shared_user.id
        ).first()

        if existing:
            # Mettre à jour la permission
            existing.permission = permission
        else:
            share = FolderShare(
                folder_id=folder_id,
                shared_with_id=shared_user.id,
                permission=permission,
                shared_by=user.id
            )
            db.session.add(share)

        folder.is_shared = True
        db.session.commit()

        log_activity(user, 'share', 'folder', folder_id, {
            'shared_with': shared_user.full_name,
            'permission': permission
        })

        return jsonify({
            'success': True,
            'message': f'Dossier partagé avec {shared_user.full_name}'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@folders_bp.route('/folders/<int:folder_id>/shares', methods=['GET'])
def get_folder_shares(folder_id):
    """Récupérer tous les partages d'un dossier."""
    try:
        folder = Folder.query.get_or_404(folder_id)

        shares = [share.to_dict() for share in folder.shares.all()]

        return jsonify({
            'success': True,
            'shares': shares
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@folders_bp.route('/folders/<int:folder_id>/shares/<int:share_id>', methods=['DELETE'])
def remove_folder_share(folder_id, share_id):
    """Retirer un partage."""
    try:
        user = get_current_user()
        folder = Folder.query.get_or_404(folder_id)

        # Vérifier les permissions
        if folder.owner_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        share = FolderShare.query.get_or_404(share_id)

        log_activity(user, 'unshare', 'folder', folder_id, {
            'removed_user_id': share.shared_with_id
        })

        db.session.delete(share)

        # Si plus de partages, marquer comme non partagé
        if folder.shares.count() == 1:  # 1 car on n'a pas encore commit
            folder.is_shared = False

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Partage retiré'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
