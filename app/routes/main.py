"""Routes principales de l'application (pages web)."""
from flask import Blueprint, render_template, current_app, request
from app.models import Article, Feed
from app.models_collab import Folder, ArticleFolder
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Page d'accueil avec liste des articles."""
    folder_id = request.args.get('folder', type=int)
    search_query = request.args.get('q', '').strip()

    # Récupérer les articles récents
    query = Article.query.join(Feed).filter(Feed.is_active == True)

    # Filtrer par dossier si spécifié
    if folder_id:
        query = query.join(ArticleFolder).filter(ArticleFolder.folder_id == folder_id)

    # Filtrer par recherche si spécifié
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            (Article.title.like(search_pattern)) |
            (Article.description.like(search_pattern))
        )

    # Récupérer tous les articles (pas de limite pour l'instant)
    articles = query.order_by(desc(Article.published_date)).all()

    # Récupérer les statistiques
    total_feeds = Feed.query.filter_by(is_active=True).count()
    total_articles = Article.query.count()

    # Récupérer le nom du dossier si filtré
    folder_name = None
    if folder_id:
        folder = Folder.query.get(folder_id)
        if folder:
            folder_name = folder.name

    return render_template(
        'index_simple.html',
        articles=articles,
        total_feeds=total_feeds,
        total_articles=total_articles,
        folder_name=folder_name
    )


@main_bp.route('/manage-feeds')
def manage_feeds():
    """Page de gestion des flux RSS."""
    feeds = Feed.query.order_by(Feed.category, Feed.name).all()

    # Compter les articles par flux
    feeds_with_counts = []
    for feed in feeds:
        feed_dict = feed.to_dict()
        feeds_with_counts.append(feed_dict)

    return render_template(
        'manage_feeds.html',
        feeds=feeds_with_counts
    )


@main_bp.route('/manage-folders')
def manage_folders():
    """Page de gestion des dossiers."""
    return render_template('manage_folders.html')


@main_bp.route('/about')
def about():
    """Page à propos."""
    return render_template('about.html')
