"""Routes pour la gestion des favoris."""
from flask import Blueprint, jsonify, request
from app import db
from app.models import Article
import logging

favorites_bp = Blueprint('favorites', __name__)
logger = logging.getLogger(__name__)


@favorites_bp.route('/articles/<int:article_id>/favorite', methods=['POST'])
def toggle_favorite(article_id):
    """Ajouter/retirer un article des favoris."""
    article = Article.query.get_or_404(article_id)

    article.is_favorite = not article.is_favorite

    try:
        db.session.commit()
        logger.info(f"Article {article_id} favori: {article.is_favorite}")
        return jsonify({
            'success': True,
            'is_favorite': article.is_favorite,
            'message': 'Ajouté aux favoris' if article.is_favorite else 'Retiré des favoris'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur toggle favorite: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@favorites_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """Récupérer tous les articles favoris."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    pagination = Article.query\
        .filter_by(is_favorite=True)\
        .order_by(Article.published_date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'favorites': [article.to_dict() for article in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@favorites_bp.route('/articles/<int:article_id>/read', methods=['POST'])
def mark_as_read(article_id):
    """Marquer un article comme lu/non lu."""
    article = Article.query.get_or_404(article_id)

    data = request.get_json() or {}
    article.is_read = data.get('is_read', True)

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'is_read': article.is_read
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@favorites_bp.route('/articles/<int:article_id>/importance', methods=['POST'])
def set_importance(article_id):
    """Définir le niveau d'importance d'un article."""
    article = Article.query.get_or_404(article_id)

    data = request.get_json()
    importance = data.get('importance', 0)

    if importance not in [0, 1, 2]:
        return jsonify({'success': False, 'error': 'Importance invalide (0, 1 ou 2)'}), 400

    article.importance = importance

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'importance': article.importance
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@favorites_bp.route('/articles/<int:article_id>/notes', methods=['POST', 'PUT'])
def update_notes(article_id):
    """Ajouter/modifier des notes personnelles sur un article."""
    article = Article.query.get_or_404(article_id)

    data = request.get_json()
    notes = data.get('notes', '')

    article.notes = notes

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'notes': article.notes
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@favorites_bp.route('/articles/<int:article_id>/notes', methods=['GET'])
def get_notes(article_id):
    """Récupérer les notes d'un article."""
    article = Article.query.get_or_404(article_id)

    return jsonify({
        'success': True,
        'notes': article.notes
    })
