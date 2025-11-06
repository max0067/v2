"""Routes pour la gestion des tags."""
from flask import Blueprint, jsonify, request
from app import db
from app.models import Article, Tag
from sqlalchemy import func
import logging

tags_bp = Blueprint('tags', __name__)
logger = logging.getLogger(__name__)


@tags_bp.route('/tags', methods=['GET'])
def get_tags():
    """Récupérer tous les tags avec le nombre d'articles."""
    tags = Tag.query.all()

    tags_list = []
    for tag in tags:
        tag_dict = tag.to_dict()
        tags_list.append(tag_dict)

    return jsonify({
        'success': True,
        'tags': tags_list
    })


@tags_bp.route('/tags', methods=['POST'])
def create_tag():
    """Créer un nouveau tag."""
    data = request.get_json()

    name = data.get('name', '').strip()
    color = data.get('color', '#6c757d')
    description = data.get('description', '')

    if not name:
        return jsonify({'success': False, 'error': 'Le nom du tag est requis'}), 400

    # Vérifier si le tag existe déjà
    existing = Tag.query.filter_by(name=name).first()
    if existing:
        return jsonify({'success': False, 'error': 'Ce tag existe déjà'}), 409

    tag = Tag(name=name, color=color, description=description)

    try:
        db.session.add(tag)
        db.session.commit()
        logger.info(f"Tag créé: {name}")
        return jsonify({
            'success': True,
            'tag': tag.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur création tag: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tags_bp.route('/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """Modifier un tag."""
    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json()

    if 'name' in data:
        tag.name = data['name'].strip()
    if 'color' in data:
        tag.color = data['color']
    if 'description' in data:
        tag.description = data['description']

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'tag': tag.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@tags_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """Supprimer un tag."""
    tag = Tag.query.get_or_404(tag_id)

    try:
        db.session.delete(tag)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Tag supprimé'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@tags_bp.route('/articles/<int:article_id>/tags', methods=['POST'])
def add_tag_to_article(article_id):
    """Ajouter un tag à un article."""
    article = Article.query.get_or_404(article_id)
    data = request.get_json()

    tag_id = data.get('tag_id')
    tag_name = data.get('tag_name')

    # Chercher le tag par ID ou nom
    if tag_id:
        tag = Tag.query.get(tag_id)
    elif tag_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        # Créer le tag s'il n'existe pas
        if not tag:
            tag = Tag(name=tag_name, color=data.get('color', '#6c757d'))
            db.session.add(tag)
    else:
        return jsonify({'success': False, 'error': 'tag_id ou tag_name requis'}), 400

    if not tag:
        return jsonify({'success': False, 'error': 'Tag non trouvé'}), 404

    # Ajouter le tag si pas déjà présent
    if tag not in article.tags:
        article.tags.append(tag)

        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Tag ajouté',
                'tag': tag.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({
            'success': False,
            'error': 'Tag déjà présent sur cet article'
        }), 400


@tags_bp.route('/articles/<int:article_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_tag_from_article(article_id, tag_id):
    """Retirer un tag d'un article."""
    article = Article.query.get_or_404(article_id)
    tag = Tag.query.get_or_404(tag_id)

    if tag in article.tags:
        article.tags.remove(tag)

        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Tag retiré'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'Tag non présent sur cet article'}), 400


@tags_bp.route('/articles/by-tag/<int:tag_id>', methods=['GET'])
def get_articles_by_tag(tag_id):
    """Récupérer tous les articles avec un tag spécifique."""
    tag = Tag.query.get_or_404(tag_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    articles = tag.articles
    total = len(articles)

    # Pagination manuelle
    start = (page - 1) * per_page
    end = start + per_page
    articles_page = articles[start:end]

    return jsonify({
        'success': True,
        'tag': tag.to_dict(),
        'articles': [article.to_dict() for article in articles_page],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })


@tags_bp.route('/tags/cloud', methods=['GET'])
def get_tag_cloud():
    """Récupérer le nuage de tags (tags avec leur fréquence)."""
    # Compter les articles par tag
    tags = Tag.query.all()

    cloud = []
    for tag in tags:
        count = len(tag.articles)
        if count > 0:  # Seulement les tags utilisés
            cloud.append({
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'count': count
            })

    # Trier par fréquence
    cloud.sort(key=lambda x: x['count'], reverse=True)

    return jsonify({
        'success': True,
        'cloud': cloud
    })
