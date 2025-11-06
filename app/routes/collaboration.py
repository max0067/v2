"""Routes pour les annotations, commentaires et collaboration."""
from flask import Blueprint, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.models import Article
from app.models_collab import (User, ArticleNote, ArticleHighlight, ArticleComment,
                                ArticleAttachment, ArticleAssignment, ActivityLog)

collaboration_bp = Blueprint('collaboration', __name__)

# Configuration uploads
UPLOAD_FOLDER = 'uploads/attachments'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png', 'zip'}


def get_current_user():
    """Récupérer l'utilisateur courant."""
    user_id = session.get('user_id')
    if not user_id:
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


def allowed_file(filename):
    """Vérifier si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def log_activity(user, action, entity_type, entity_id, details=None):
    """Enregistrer une activité."""
    log = ActivityLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=request.remote_addr
    )
    db.session.add(log)


# ========== NOTES PRIVÉES ==========

@collaboration_bp.route('/articles/<int:article_id>/notes', methods=['GET'])
def get_article_notes(article_id):
    """Récupérer toutes les notes d'un article."""
    try:
        user = get_current_user()

        # Notes de l'utilisateur
        notes = ArticleNote.query.filter_by(
            article_id=article_id,
            author_id=user.id
        ).all()

        return jsonify({
            'success': True,
            'notes': [note.to_dict() for note in notes]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/articles/<int:article_id>/notes', methods=['POST'])
def create_article_note(article_id):
    """Créer une note sur un article."""
    try:
        user = get_current_user()
        data = request.get_json()

        note = ArticleNote(
            article_id=article_id,
            author_id=user.id,
            content=data.get('content'),
            is_private=data.get('is_private', True)
        )

        db.session.add(note)
        db.session.commit()

        log_activity(user, 'create', 'note', note.id, {'article_id': article_id})

        return jsonify({
            'success': True,
            'note': note.to_dict(),
            'message': 'Note créée'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Mettre à jour une note."""
    try:
        user = get_current_user()
        note = ArticleNote.query.get_or_404(note_id)

        # Vérifier que c'est bien l'auteur
        if note.author_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        data = request.get_json()
        note.content = data.get('content', note.content)

        db.session.commit()

        log_activity(user, 'update', 'note', note.id)

        return jsonify({
            'success': True,
            'note': note.to_dict(),
            'message': 'Note mise à jour'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Supprimer une note."""
    try:
        user = get_current_user()
        note = ArticleNote.query.get_or_404(note_id)

        if note.author_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        log_activity(user, 'delete', 'note', note.id)

        db.session.delete(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note supprimée'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== SURLIGNAGES ==========

@collaboration_bp.route('/articles/<int:article_id>/highlights', methods=['GET'])
def get_article_highlights(article_id):
    """Récupérer tous les surlignages d'un article."""
    try:
        user = get_current_user()

        highlights = ArticleHighlight.query.filter_by(
            article_id=article_id,
            author_id=user.id
        ).all()

        return jsonify({
            'success': True,
            'highlights': [h.to_dict() for h in highlights]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/articles/<int:article_id>/highlights', methods=['POST'])
def create_highlight(article_id):
    """Créer un surlignage."""
    try:
        user = get_current_user()
        data = request.get_json()

        highlight = ArticleHighlight(
            article_id=article_id,
            author_id=user.id,
            text=data.get('text'),
            color=data.get('color', '#FFFF00'),
            start_offset=data.get('start_offset'),
            end_offset=data.get('end_offset'),
            note=data.get('note')
        )

        db.session.add(highlight)
        db.session.commit()

        log_activity(user, 'create', 'highlight', highlight.id, {'article_id': article_id})

        return jsonify({
            'success': True,
            'highlight': highlight.to_dict(),
            'message': 'Surlignage créé'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/highlights/<int:highlight_id>', methods=['DELETE'])
def delete_highlight(highlight_id):
    """Supprimer un surlignage."""
    try:
        user = get_current_user()
        highlight = ArticleHighlight.query.get_or_404(highlight_id)

        if highlight.author_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        log_activity(user, 'delete', 'highlight', highlight.id)

        db.session.delete(highlight)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Surlignage supprimé'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== COMMENTAIRES COLLABORATIFS ==========

@collaboration_bp.route('/articles/<int:article_id>/comments', methods=['GET'])
def get_article_comments(article_id):
    """Récupérer tous les commentaires d'un article."""
    try:
        # Récupérer seulement les commentaires de premier niveau
        comments = ArticleComment.query.filter_by(
            article_id=article_id,
            parent_id=None
        ).order_by(ArticleComment.created_at.desc()).all()

        return jsonify({
            'success': True,
            'comments': [c.to_dict(include_replies=True) for c in comments]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/articles/<int:article_id>/comments', methods=['POST'])
def create_comment(article_id):
    """Créer un commentaire."""
    try:
        user = get_current_user()
        data = request.get_json()

        comment = ArticleComment(
            article_id=article_id,
            author_id=user.id,
            parent_id=data.get('parent_id'),
            content=data.get('content'),
            mentions=data.get('mentions', [])
        )

        db.session.add(comment)
        db.session.commit()

        log_activity(user, 'create', 'comment', comment.id, {'article_id': article_id})

        return jsonify({
            'success': True,
            'comment': comment.to_dict(),
            'message': 'Commentaire ajouté'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    """Mettre à jour un commentaire."""
    try:
        user = get_current_user()
        comment = ArticleComment.query.get_or_404(comment_id)

        if comment.author_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        data = request.get_json()
        comment.content = data.get('content', comment.content)

        db.session.commit()

        log_activity(user, 'update', 'comment', comment.id)

        return jsonify({
            'success': True,
            'comment': comment.to_dict(),
            'message': 'Commentaire mis à jour'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Supprimer un commentaire."""
    try:
        user = get_current_user()
        comment = ArticleComment.query.get_or_404(comment_id)

        if comment.author_id != user.id and user.role != 'admin':
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        log_activity(user, 'delete', 'comment', comment.id)

        db.session.delete(comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Commentaire supprimé'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== PIÈCES JOINTES ==========

@collaboration_bp.route('/articles/<int:article_id>/attachments', methods=['GET'])
def get_article_attachments(article_id):
    """Récupérer toutes les pièces jointes d'un article."""
    try:
        attachments = ArticleAttachment.query.filter_by(article_id=article_id).all()

        return jsonify({
            'success': True,
            'attachments': [a.to_dict() for a in attachments]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/articles/<int:article_id>/attachments', methods=['POST'])
def upload_attachment(article_id):
    """Uploader une pièce jointe."""
    try:
        user = get_current_user()

        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Type de fichier non autorisé'}), 400

        # Créer le dossier si nécessaire
        upload_path = os.path.join(UPLOAD_FOLDER, str(article_id))
        os.makedirs(upload_path, exist_ok=True)

        # Nom de fichier sécurisé
        original_filename = secure_filename(file.filename)
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{original_filename}"
        file_path = os.path.join(upload_path, filename)

        # Sauvegarder le fichier
        file.save(file_path)

        # Créer l'enregistrement
        attachment = ArticleAttachment(
            article_id=article_id,
            uploaded_by=user.id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.content_type,
            description=request.form.get('description')
        )

        db.session.add(attachment)
        db.session.commit()

        log_activity(user, 'upload', 'attachment', attachment.id, {
            'article_id': article_id,
            'filename': original_filename
        })

        return jsonify({
            'success': True,
            'attachment': attachment.to_dict(),
            'message': 'Fichier uploadé'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/attachments/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(attachment_id):
    """Supprimer une pièce jointe."""
    try:
        user = get_current_user()
        attachment = ArticleAttachment.query.get_or_404(attachment_id)

        if attachment.uploaded_by != user.id and user.role != 'admin':
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        # Supprimer le fichier
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)

        log_activity(user, 'delete', 'attachment', attachment.id)

        db.session.delete(attachment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Pièce jointe supprimée'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== ASSIGNATIONS ==========

@collaboration_bp.route('/articles/<int:article_id>/assign', methods=['POST'])
def assign_article(article_id):
    """Assigner un article à un collègue."""
    try:
        user = get_current_user()
        data = request.get_json()

        assigned_to_email = data.get('email')
        assigned_to = User.query.filter_by(email=assigned_to_email).first()

        if not assigned_to:
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 404

        assignment = ArticleAssignment(
            article_id=article_id,
            assigned_to_id=assigned_to.id,
            assigned_by_id=user.id,
            priority=data.get('priority', 'normal'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            note=data.get('note')
        )

        db.session.add(assignment)
        db.session.commit()

        log_activity(user, 'assign', 'article', article_id, {
            'assigned_to': assigned_to.full_name
        })

        return jsonify({
            'success': True,
            'assignment': assignment.to_dict(),
            'message': f'Article assigné à {assigned_to.full_name}'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/assignments/<int:assignment_id>/status', methods=['PUT'])
def update_assignment_status(assignment_id):
    """Mettre à jour le statut d'une assignation."""
    try:
        user = get_current_user()
        assignment = ArticleAssignment.query.get_or_404(assignment_id)

        # Seul l'assigné ou l'assigneur peut modifier
        if assignment.assigned_to_id != user.id and assignment.assigned_by_id != user.id:
            return jsonify({'success': False, 'error': 'Permission refusée'}), 403

        data = request.get_json()
        assignment.status = data.get('status', assignment.status)

        if assignment.status == 'completed':
            assignment.completed_at = datetime.utcnow()

        db.session.commit()

        log_activity(user, 'update_status', 'assignment', assignment.id, {
            'status': assignment.status
        })

        return jsonify({
            'success': True,
            'assignment': assignment.to_dict(),
            'message': 'Statut mis à jour'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@collaboration_bp.route('/my-assignments', methods=['GET'])
def get_my_assignments():
    """Récupérer mes assignations."""
    try:
        user = get_current_user()

        # Assignations reçues
        received = ArticleAssignment.query.filter_by(
            assigned_to_id=user.id
        ).order_by(ArticleAssignment.due_date.asc()).all()

        # Assignations créées
        created = ArticleAssignment.query.filter_by(
            assigned_by_id=user.id
        ).order_by(ArticleAssignment.assigned_at.desc()).all()

        return jsonify({
            'success': True,
            'received': [a.to_dict() for a in received],
            'created': [a.to_dict() for a in created]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== HISTORIQUE ==========

@collaboration_bp.route('/activity-log', methods=['GET'])
def get_activity_log():
    """Récupérer l'historique des activités."""
    try:
        user = get_current_user()

        # Récupérer les activités des 30 derniers jours
        limit = request.args.get('limit', 50, type=int)

        if user.role == 'admin':
            # Admin voit tout
            logs = ActivityLog.query.order_by(
                ActivityLog.created_at.desc()
            ).limit(limit).all()
        else:
            # Utilisateur voit ses propres activités
            logs = ActivityLog.query.filter_by(
                user_id=user.id
            ).order_by(ActivityLog.created_at.desc()).limit(limit).all()

        return jsonify({
            'success': True,
            'logs': [log.to_dict() for log in logs]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
