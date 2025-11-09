#!/usr/bin/env python3
"""Script de test pour vérifier le nombre d'articles."""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Article, Feed
from sqlalchemy import desc

app = create_app()

with app.app_context():
    # Test 1: Compter tous les articles
    total = Article.query.count()
    print(f"✅ Total articles dans la base: {total}")

    # Test 2: Articles avec feeds actifs
    active_feeds = Feed.query.filter_by(is_active=True).count()
    print(f"✅ Feeds actifs: {active_feeds}")

    # Test 3: Articles des feeds actifs (comme dans la route)
    query = Article.query.join(Feed).filter(Feed.is_active == True)
    articles_from_active_feeds = query.count()
    print(f"✅ Articles des feeds actifs: {articles_from_active_feeds}")

    # Test 4: Articles retournés par la query complète
    articles = query.order_by(desc(Article.published_date)).all()
    print(f"✅ Articles retournés par la query: {len(articles)}")

    # Test 5: Afficher les 10 premiers
    print("\n📰 10 premiers articles:")
    for i, article in enumerate(articles[:10], 1):
        print(f"{i}. {article.title[:60]}... ({article.feed.name})")

    print(f"\n🎯 Conclusion: Vous devriez voir {len(articles)} articles sur la page d'accueil")
