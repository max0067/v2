"""
Application Flask de veille juridique RSS
"""
import os
import sys
import argparse
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import feedparser
from sqlalchemy import or_, desc
from models import db, Feed, Article
from config import config

# Initialiser l'application Flask
app = Flask(__name__)

# Charger la configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialiser la base de données
db.init_app(app)


def init_database():
    """Initialiser la base de données"""
    with app.app_context():
        db.create_all()
        print("✓ Base de données initialisée avec succès")


def fetch_feed_articles(feed):
    """
    Récupérer les articles d'un flux RSS

    Args:
        feed: Objet Feed

    Returns:
        int: Nombre d'articles ajoutés
    """
    try:
        # Parser le flux RSS
        parsed = feedparser.parse(
            feed.url,
            agent=app.config['RSS_USER_AGENT']
        )

        if parsed.bozo:
            print(f"⚠ Avertissement lors du parsing de {feed.name}: {parsed.bozo_exception}")

        articles_added = 0

        # Parcourir les entrées du flux
        for entry in parsed.entries:
            # Vérifier si l'article existe déjà (via GUID ou lien)
            guid = entry.get('id', entry.get('link'))
            existing = Article.query.filter(
                (Article.guid == guid) | (Article.link == entry.get('link'))
            ).first()

            if existing:
                continue

            # Parser la date de publication
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except:
                    pass

            # Créer le nouvel article
            article = Article(
                feed_id=feed.id,
                title=entry.get('title', 'Sans titre'),
                link=entry.get('link', ''),
                description=entry.get('summary', entry.get('description', '')),
                pub_date=pub_date,
                guid=guid
            )

            db.session.add(article)
            articles_added += 1

        db.session.commit()
        print(f"✓ {articles_added} nouveaux articles ajoutés depuis {feed.name}")
        return articles_added

    except Exception as e:
        print(f"✗ Erreur lors de la récupération du flux {feed.name}: {str(e)}")
        db.session.rollback()
        return 0


def update_all_feeds():
    """Mettre à jour tous les flux RSS actifs"""
    print("\n" + "="*60)
    print("Mise à jour des flux RSS")
    print("="*60 + "\n")

    feeds = Feed.query.filter_by(is_active=True).all()
    total_articles = 0

    for feed in feeds:
        print(f"Traitement du flux : {feed.name} ({feed.url})")
        total_articles += fetch_feed_articles(feed)

    # Nettoyer les anciens articles
    cleanup_old_articles()

    print(f"\n✓ Mise à jour terminée : {total_articles} nouveaux articles au total\n")
    return total_articles


def cleanup_old_articles():
    """Supprimer les articles plus anciens que la durée de rétention"""
    retention_days = app.config['ARTICLE_RETENTION_DAYS']
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    deleted = Article.query.filter(Article.created_at < cutoff_date).delete()
    db.session.commit()

    if deleted > 0:
        print(f"✓ {deleted} anciens articles supprimés (> {retention_days} jours)")


# ========== ROUTES ==========

@app.route('/')
def index():
    """Page d'accueil - Liste des articles"""
    page = request.args.get('page', 1, type=int)
    per_page = app.config['ARTICLES_PER_PAGE']

    # Récupérer tous les articles, triés par date de publication décroissante
    articles_query = Article.query.order_by(desc(Article.pub_date), desc(Article.created_at))

    # Pagination
    articles_paginated = articles_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Statistiques
    total_feeds = Feed.query.count()
    total_articles = Article.query.count()

    return render_template(
        'dashboard.html',
        articles=articles_paginated.items,
        pagination=articles_paginated,
        total_feeds=total_feeds,
        total_articles=total_articles
    )


@app.route('/feeds')
def feeds():
    """Page de gestion des flux RSS"""
    feeds_list = Feed.query.order_by(Feed.name).all()
    return render_template('feeds.html', feeds=feeds_list)


@app.route('/api/feeds', methods=['GET'])
def api_get_feeds():
    """API : Récupérer tous les flux"""
    feeds_list = Feed.query.all()
    return jsonify([feed.to_dict() for feed in feeds_list])


@app.route('/api/feeds', methods=['POST'])
def api_add_feed():
    """API : Ajouter un nouveau flux"""
    data = request.get_json()

    if not data or not data.get('name') or not data.get('url'):
        return jsonify({'error': 'Nom et URL requis'}), 400

    # Vérifier si l'URL existe déjà
    existing = Feed.query.filter_by(url=data['url']).first()
    if existing:
        return jsonify({'error': 'Ce flux existe déjà'}), 409

    # Créer le nouveau flux
    feed = Feed(
        name=data['name'],
        url=data['url'],
        category=data.get('category', 'Général'),
        is_active=data.get('is_active', True)
    )

    db.session.add(feed)
    db.session.commit()

    return jsonify(feed.to_dict()), 201


@app.route('/api/feeds/<int:feed_id>', methods=['PUT'])
def api_update_feed(feed_id):
    """API : Modifier un flux existant"""
    feed = Feed.query.get_or_404(feed_id)
    data = request.get_json()

    if data.get('name'):
        feed.name = data['name']
    if data.get('url'):
        feed.url = data['url']
    if data.get('category') is not None:
        feed.category = data['category']
    if data.get('is_active') is not None:
        feed.is_active = data['is_active']

    feed.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(feed.to_dict())


@app.route('/api/feeds/<int:feed_id>', methods=['DELETE'])
def api_delete_feed(feed_id):
    """API : Supprimer un flux"""
    feed = Feed.query.get_or_404(feed_id)

    db.session.delete(feed)
    db.session.commit()

    return jsonify({'message': 'Flux supprimé avec succès'}), 200


@app.route('/api/refresh', methods=['POST'])
def api_refresh_feeds():
    """API : Rafraîchir tous les flux RSS"""
    try:
        total_articles = update_all_feeds()
        return jsonify({
            'message': f'{total_articles} nouveaux articles récupérés',
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/search')
def api_search():
    """API : Rechercher des articles"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    feed_id = request.args.get('feed_id', type=int)

    if not query and not category and not feed_id:
        return jsonify([])

    # Construire la requête
    articles_query = Article.query

    # Filtre par mot-clé
    if query:
        search_filter = or_(
            Article.title.ilike(f'%{query}%'),
            Article.description.ilike(f'%{query}%')
        )
        articles_query = articles_query.filter(search_filter)

    # Filtre par catégorie
    if category:
        articles_query = articles_query.join(Feed).filter(Feed.category == category)

    # Filtre par flux
    if feed_id:
        articles_query = articles_query.filter(Article.feed_id == feed_id)

    # Limiter les résultats
    articles = articles_query.order_by(desc(Article.pub_date)).limit(100).all()

    return jsonify([article.to_dict() for article in articles])


@app.route('/api/categories')
def api_get_categories():
    """API : Récupérer toutes les catégories uniques"""
    categories = db.session.query(Feed.category).distinct().filter(
        Feed.category.isnot(None)
    ).all()
    return jsonify([cat[0] for cat in categories if cat[0]])


@app.route('/api/stats')
def api_stats():
    """API : Statistiques de l'application"""
    total_feeds = Feed.query.count()
    active_feeds = Feed.query.filter_by(is_active=True).count()
    total_articles = Article.query.count()

    # Articles de la dernière semaine
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_articles = Article.query.filter(Article.created_at >= week_ago).count()

    return jsonify({
        'total_feeds': total_feeds,
        'active_feeds': active_feeds,
        'total_articles': total_articles,
        'recent_articles': recent_articles
    })


# ========== FILTRES TEMPLATE ==========

@app.template_filter('format_date')
def format_date(date):
    """Formater une date pour l'affichage"""
    if not date:
        return 'Date inconnue'

    # Calculer le temps écoulé
    now = datetime.utcnow()
    delta = now - date

    if delta.days == 0:
        if delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"Il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            hours = delta.seconds // 3600
            return f"Il y a {hours} heure{'s' if hours > 1 else ''}"
    elif delta.days == 1:
        return "Hier"
    elif delta.days < 7:
        return f"Il y a {delta.days} jours"
    else:
        return date.strftime('%d/%m/%Y à %H:%M')


# ========== COMMANDES CLI ==========

def cli_update():
    """Commande CLI pour mettre à jour les flux"""
    with app.app_context():
        update_all_feeds()


def cli_init():
    """Commande CLI pour initialiser la base de données"""
    init_database()


def cli_add_sample_feeds():
    """Ajouter des flux RSS de démonstration"""
    with app.app_context():
        sample_feeds = [
            {
                'name': 'Legifrance - Actualités',
                'url': 'https://www.legifrance.gouv.fr/rss/actualites.xml',
                'category': 'Législation'
            },
            {
                'name': 'Journal Officiel (JORF)',
                'url': 'https://www.legifrance.gouv.fr/rss/jorf.xml',
                'category': 'Journal Officiel'
            },
            {
                'name': 'Dalloz Actualité',
                'url': 'https://www.dalloz-actualite.fr/feed',
                'category': 'Doctrine'
            }
        ]

        for feed_data in sample_feeds:
            existing = Feed.query.filter_by(url=feed_data['url']).first()
            if not existing:
                feed = Feed(**feed_data)
                db.session.add(feed)
                print(f"✓ Flux ajouté : {feed_data['name']}")
            else:
                print(f"⊘ Flux existant : {feed_data['name']}")

        db.session.commit()
        print("\n✓ Flux d'exemple ajoutés avec succès\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Application de veille juridique RSS')
    parser.add_argument('--init', action='store_true', help='Initialiser la base de données')
    parser.add_argument('--update', action='store_true', help='Mettre à jour tous les flux RSS')
    parser.add_argument('--sample', action='store_true', help='Ajouter des flux RSS de démonstration')
    parser.add_argument('--port', type=int, default=8000, help='Port du serveur (défaut: 8000)')
    parser.add_argument('--host', default='0.0.0.0', help='Host du serveur (défaut: 0.0.0.0)')

    args = parser.parse_args()

    if args.init:
        cli_init()
    elif args.update:
        cli_update()
    elif args.sample:
        cli_add_sample_feeds()
    else:
        # Initialiser la base de données si elle n'existe pas
        if not os.path.exists('database.db'):
            cli_init()

        # Lancer le serveur Flask
        print(f"\n🚀 Serveur Flask démarré sur http://{args.host}:{args.port}\n")
        app.run(host=args.host, port=args.port, debug=(env == 'development'))
