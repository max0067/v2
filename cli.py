#!/usr/bin/env python3
"""Script CLI pour les tâches cron et maintenance."""
import sys
import logging
from datetime import datetime
from app import create_app, db
from app.models import Feed, Article
from app.utils.rss_parser import RSSParser

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/rss-update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def refresh_all_feeds():
    """Actualiser tous les flux RSS actifs."""
    logger.info("=" * 60)
    logger.info("Début de l'actualisation des flux RSS")
    logger.info("=" * 60)

    app = create_app()

    with app.app_context():
        try:
            # Récupérer tous les flux actifs
            feeds = Feed.query.filter_by(is_active=True).all()

            if not feeds:
                logger.warning("Aucun flux actif trouvé")
                return

            logger.info(f"Flux actifs trouvés: {len(feeds)}")

            parser = RSSParser()
            total_new_articles = 0
            success_count = 0
            error_count = 0

            for feed in feeds:
                try:
                    logger.info(f"Traitement du flux: {feed.name} ({feed.url})")
                    new_count = parser.fetch_and_save(feed)
                    total_new_articles += new_count
                    success_count += 1
                    logger.info(f"✅ {feed.name}: {new_count} nouveaux articles")

                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Erreur pour {feed.name}: {str(e)}", exc_info=True)

            # Résumé
            logger.info("=" * 60)
            logger.info("Résumé de l'actualisation:")
            logger.info(f"  - Flux traités: {len(feeds)}")
            logger.info(f"  - Succès: {success_count}")
            logger.info(f"  - Erreurs: {error_count}")
            logger.info(f"  - Nouveaux articles: {total_new_articles}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Erreur critique lors de l'actualisation: {str(e)}", exc_info=True)
            sys.exit(1)


def cleanup_old_articles(days=90):
    """Supprimer les articles de plus de X jours.

    Args:
        days: Nombre de jours de rétention (défaut: 90)
    """
    logger.info("=" * 60)
    logger.info(f"Nettoyage des articles de plus de {days} jours")
    logger.info("=" * 60)

    app = create_app()

    with app.app_context():
        try:
            parser = RSSParser()
            deleted_count = parser.cleanup_old_articles(days)

            logger.info(f"✅ {deleted_count} articles supprimés")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {str(e)}", exc_info=True)
            sys.exit(1)


def show_stats():
    """Afficher les statistiques."""
    app = create_app()

    with app.app_context():
        try:
            total_feeds = Feed.query.count()
            active_feeds = Feed.query.filter_by(is_active=True).count()
            total_articles = Article.query.count()

            print("\n" + "=" * 60)
            print("📊 STATISTIQUES")
            print("=" * 60)
            print(f"Flux RSS:")
            print(f"  - Total: {total_feeds}")
            print(f"  - Actifs: {active_feeds}")
            print(f"  - Inactifs: {total_feeds - active_feeds}")
            print(f"\nArticles:")
            print(f"  - Total: {total_articles}")

            if total_articles > 0:
                latest = Article.query.order_by(Article.created_at.desc()).first()
                print(f"  - Dernier ajout: {latest.created_at.strftime('%d/%m/%Y %H:%M')}")

            print("=" * 60 + "\n")

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {str(e)}")
            sys.exit(1)


def main():
    """Point d'entrée principal du CLI."""
    if len(sys.argv) < 2:
        print("""
Usage: python cli.py <command> [options]

Commandes disponibles:
  refresh              Actualiser tous les flux RSS actifs
  cleanup [days]       Supprimer les articles anciens (défaut: 90 jours)
  stats                Afficher les statistiques

Exemples:
  python cli.py refresh
  python cli.py cleanup 60
  python cli.py stats
        """)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'refresh':
        refresh_all_feeds()

    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        cleanup_old_articles(days)

    elif command == 'stats':
        show_stats()

    else:
        print(f"❌ Commande inconnue: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
