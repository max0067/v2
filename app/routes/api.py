"""Routes API de l'application."""
from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import Article, Feed
from app.utils.rss_parser import RSSParser
from datetime import datetime, timedelta
from sqlalchemy import or_, desc
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@api_bp.route('/feeds', methods=['GET'])
def get_feeds():
    """Récupérer tous les flux RSS."""
    feeds = Feed.query.order_by(Feed.category, Feed.name).all()
    return jsonify({
        'success': True,
        'feeds': [feed.to_dict() for feed in feeds]
    })


@api_bp.route('/feeds', methods=['POST'])
def add_feed():
    """Ajouter un nouveau flux RSS."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'Données manquantes'}), 400

    name = data.get('name', '').strip()
    url = data.get('url', '').strip()
    category = data.get('category', '').strip()

    # Validation
    if not name or not url:
        return jsonify({
            'success': False,
            'error': 'Le nom et l\'URL sont requis'
        }), 400

    # Vérifier si l'URL existe déjà
    existing = Feed.query.filter_by(url=url).first()
    if existing:
        return jsonify({
            'success': False,
            'error': 'Ce flux RSS existe déjà'
        }), 409

    # Créer le flux
    feed = Feed(
        name=name,
        url=url,
        category=category if category else 'Général',
        is_active=True
    )

    try:
        db.session.add(feed)
        db.session.commit()
        logger.info(f"Nouveau flux ajouté: {name} ({url})")
        return jsonify({
            'success': True,
            'message': 'Flux ajouté avec succès',
            'feed': feed.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de l'ajout du flux: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de l\'ajout du flux'
        }), 500


@api_bp.route('/feeds/<int:feed_id>', methods=['PUT'])
def update_feed(feed_id):
    """Mettre à jour un flux RSS."""
    feed = Feed.query.get_or_404(feed_id)
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'Données manquantes'}), 400

    # Mise à jour des champs
    if 'name' in data:
        feed.name = data['name'].strip()
    if 'url' in data:
        new_url = data['url'].strip()
        # Vérifier si la nouvelle URL n'existe pas déjà
        existing = Feed.query.filter(Feed.url == new_url, Feed.id != feed_id).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Cette URL est déjà utilisée par un autre flux'
            }), 409
        feed.url = new_url
    if 'category' in data:
        feed.category = data['category'].strip()
    if 'is_active' in data:
        feed.is_active = bool(data['is_active'])

    try:
        db.session.commit()
        logger.info(f"Flux mis à jour: {feed.name}")
        return jsonify({
            'success': True,
            'message': 'Flux mis à jour avec succès',
            'feed': feed.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la mise à jour du flux: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la mise à jour du flux'
        }), 500


@api_bp.route('/feeds/<int:feed_id>', methods=['DELETE'])
def delete_feed(feed_id):
    """Supprimer un flux RSS."""
    feed = Feed.query.get_or_404(feed_id)

    try:
        feed_name = feed.name
        db.session.delete(feed)
        db.session.commit()
        logger.info(f"Flux supprimé: {feed_name}")
        return jsonify({
            'success': True,
            'message': 'Flux supprimé avec succès'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la suppression du flux: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la suppression du flux'
        }), 500


@api_bp.route('/feeds/refresh', methods=['POST'])
def refresh_feeds():
    """Actualiser tous les flux RSS actifs."""
    try:
        feeds = Feed.query.filter_by(is_active=True).all()

        if not feeds:
            return jsonify({
                'success': False,
                'error': 'Aucun flux actif à actualiser'
            }), 404

        parser = RSSParser()
        stats = {
            'total_feeds': len(feeds),
            'success': 0,
            'errors': 0,
            'new_articles': 0
        }

        for feed in feeds:
            try:
                new_count = parser.fetch_and_save(feed)
                stats['new_articles'] += new_count
                stats['success'] += 1
                logger.info(f"Flux actualisé: {feed.name} ({new_count} nouveaux articles)")
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Erreur lors de l'actualisation du flux {feed.name}: {str(e)}")

        return jsonify({
            'success': True,
            'message': f'{stats["new_articles"]} nouveaux articles récupérés',
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Erreur lors de l'actualisation des flux: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de l\'actualisation des flux'
        }), 500


@api_bp.route('/feeds/<int:feed_id>/refresh', methods=['POST'])
def refresh_single_feed(feed_id):
    """Actualiser un flux RSS spécifique."""
    feed = Feed.query.get_or_404(feed_id)

    try:
        parser = RSSParser()
        new_count = parser.fetch_and_save(feed)

        return jsonify({
            'success': True,
            'message': f'{new_count} nouveaux articles récupérés',
            'new_articles': new_count
        })
    except Exception as e:
        logger.error(f"Erreur lors de l'actualisation du flux {feed.name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/articles', methods=['GET'])
def get_articles():
    """Récupérer les articles avec pagination et filtres."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    feed_id = request.args.get('feed_id', type=int)
    category = request.args.get('category')

    # Limite la pagination
    per_page = min(per_page, 100)

    # Construire la requête
    query = Article.query.join(Feed).filter(Feed.is_active == True)

    if feed_id:
        query = query.filter(Article.feed_id == feed_id)
    if category:
        query = query.filter(Feed.category == category)

    # Paginer et trier
    pagination = query.order_by(desc(Article.published_date))\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'articles': [article.to_dict() for article in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })


@api_bp.route('/articles/search', methods=['GET'])
def search_articles():
    """Rechercher des articles."""
    query_text = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    if not query_text or len(query_text) < 2:
        return jsonify({
            'success': False,
            'error': 'La recherche doit contenir au moins 2 caractères'
        }), 400

    # Limite la pagination
    per_page = min(per_page, 100)

    # Recherche dans titre, description et contenu
    search_pattern = f'%{query_text}%'
    query = Article.query.join(Feed)\
        .filter(Feed.is_active == True)\
        .filter(
            or_(
                Article.title.ilike(search_pattern),
                Article.description.ilike(search_pattern),
                Article.content.ilike(search_pattern),
                Feed.name.ilike(search_pattern)
            )
        )

    # Paginer
    pagination = query.order_by(desc(Article.published_date))\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'query': query_text,
        'articles': [article.to_dict() for article in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Récupérer les statistiques."""
    total_feeds = Feed.query.count()
    active_feeds = Feed.query.filter_by(is_active=True).count()
    total_articles = Article.query.count()

    # Articles des 7 derniers jours
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_articles = Article.query\
        .filter(Article.created_at >= week_ago)\
        .count()

    # Dernier article
    last_article = Article.query\
        .order_by(desc(Article.created_at))\
        .first()

    return jsonify({
        'success': True,
        'stats': {
            'total_feeds': total_feeds,
            'active_feeds': active_feeds,
            'total_articles': total_articles,
            'recent_articles': recent_articles,
            'last_update': last_article.created_at.isoformat() if last_article else None
        }
    })
