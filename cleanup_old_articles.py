#!/usr/bin/env python3
"""Script de nettoyage des articles anciens.

Ce script supprime les articles de plus de X jours (défini dans .env ou 90 jours par défaut)
SAUF les articles marqués comme favoris qui sont conservés indéfiniment.
"""
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Article


def cleanup_old_articles(dry_run=False, retention_days=None):
    """Nettoyer les articles anciens.

    Args:
        dry_run: Si True, affiche ce qui serait supprimé sans le faire
        retention_days: Nombre de jours de rétention (défaut: variable ARTICLES_RETENTION_DAYS ou 90)
    """
    app = create_app()

    with app.app_context():
        # Obtenir la période de rétention
        if retention_days is None:
            retention_days = int(os.environ.get('ARTICLES_RETENTION_DAYS', 90))

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        print("🧹 Nettoyage des articles anciens")
        print(f"📅 Date limite : {cutoff_date.strftime('%d/%m/%Y %H:%M')}")
        print(f"⏱️  Articles de plus de {retention_days} jours seront supprimés")
        print()

        # Compter les articles à supprimer
        old_articles = Article.query.filter(
            Article.created_at < cutoff_date,
            Article.is_favorite == False  # Ne pas supprimer les favoris
        ).all()

        # Compter les favoris conservés
        old_favorites = Article.query.filter(
            Article.created_at < cutoff_date,
            Article.is_favorite == True
        ).count()

        total_count = len(old_articles)

        if total_count == 0:
            print("✅ Aucun article à supprimer")
            if old_favorites > 0:
                print(f"⭐ {old_favorites} article(s) favori(s) ancien(s) conservé(s)")
            return 0

        print(f"🗑️  {total_count} article(s) à supprimer")
        if old_favorites > 0:
            print(f"⭐ {old_favorites} article(s) favori(s) ancien(s) seront conservés")
        print()

        if dry_run:
            print("🔍 MODE TEST - Aucune suppression effectuée")
            print()
            print("Articles qui seraient supprimés :")
            for i, article in enumerate(old_articles[:10], 1):  # Afficher max 10
                print(f"  {i}. {article.title[:70]}... ({article.created_at.strftime('%d/%m/%Y')})")

            if total_count > 10:
                print(f"  ... et {total_count - 10} autres")
        else:
            # Supprimer les articles
            try:
                for article in old_articles:
                    db.session.delete(article)

                db.session.commit()
                print(f"✅ {total_count} article(s) supprimé(s) avec succès")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erreur lors de la suppression : {e}")
                return 1

        print()

        # Statistiques finales
        remaining_articles = Article.query.count()
        favorites_count = Article.query.filter(Article.is_favorite == True).count()

        print("📊 Statistiques finales :")
        print(f"   - Articles restants : {remaining_articles}")
        print(f"   - Dont favoris : {favorites_count}")
        print()

        return 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Nettoyer les articles anciens')
    parser.add_argument('--dry-run', action='store_true',
                        help='Mode test : afficher ce qui serait supprimé sans le faire')
    parser.add_argument('--days', type=int,
                        help='Nombre de jours de rétention (défaut: 90)')

    args = parser.parse_args()

    sys.exit(cleanup_old_articles(dry_run=args.dry_run, retention_days=args.days))
