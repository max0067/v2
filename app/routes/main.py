"""Routes principales de l'application (pages web)."""
from flask import Blueprint, render_template, current_app
from app.models import Article, Feed
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Page d'accueil avec liste des articles."""
    page = 1
    per_page = current_app.config.get('ITEMS_PER_PAGE', 50)

    # Récupérer les articles récents
    articles = Article.query\
        .join(Feed)\
        .filter(Feed.is_active == True)\
        .order_by(desc(Article.published_date))\
        .limit(per_page)\
        .all()

    # Récupérer les statistiques
    total_feeds = Feed.query.filter_by(is_active=True).count()
    total_articles = Article.query.count()

    return render_template(
        'index.html',
        articles=articles,
        total_feeds=total_feeds,
        total_articles=total_articles
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


@main_bp.route('/about')
def about():
    """Page à propos."""
    return render_template('about.html')
