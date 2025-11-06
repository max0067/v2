#!/usr/bin/env python3
"""Script d'actualisation automatique des flux RSS.

Ce script actualise tous les flux RSS actifs et peut être lancé via cron.
"""
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Feed
from app.utils.rss_parser import RSSParser


def refresh_all_feeds():
    """Actualiser tous les flux RSS actifs."""
    app = create_app()

    with app.app_context():
        print(f"🔄 Actualisation automatique des flux RSS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()

        # Récupérer tous les flux actifs
        feeds = Feed.query.filter_by(is_active=True).all()

        if not feeds:
            print("⚠️  Aucun flux actif trouvé")
            return 0

        print(f"📡 {len(feeds)} flux à actualiser")
        print()

        parser = RSSParser()
        total_new_articles = 0
        success_count = 0
        error_count = 0

        for feed in feeds:
            try:
                print(f"  📥 {feed.name}...", end=" ", flush=True)

                # Parser le flux
                new_articles = parser.parse_feed(feed.url, feed.id)

                # Mettre à jour la date de dernière récupération
                feed.last_fetch = datetime.utcnow()
                db.session.commit()

                total_new_articles += new_articles
                success_count += 1

                print(f"✅ {new_articles} nouveau(x) article(s)")

            except Exception as e:
                error_count += 1
                print(f"❌ Erreur: {str(e)[:50]}")
                db.session.rollback()

        print()
        print("📊 Résumé de l'actualisation :")
        print(f"   - Flux actualisés : {success_count}/{len(feeds)}")
        print(f"   - Erreurs : {error_count}")
        print(f"   - Nouveaux articles : {total_new_articles}")
        print()

        if error_count == 0:
            print("✅ Actualisation terminée avec succès !")
        else:
            print(f"⚠️  Actualisation terminée avec {error_count} erreur(s)")

        return 0 if error_count == 0 else 1


if __name__ == '__main__':
    try:
        sys.exit(refresh_all_feeds())
    except Exception as e:
        print(f"❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
