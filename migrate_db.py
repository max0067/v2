#!/usr/bin/env python3
"""Script de migration de la base de données pour ajouter les nouvelles fonctionnalités.

Ce script ajoute les nouvelles tables et colonnes pour :
- Tags et catégorisation
- Favoris et statut de lecture
- Annotations
- Échéances juridiques
- Historique des exports
"""
import sys
import os

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Feed, Article, Tag, Annotation, LegalDeadline, ExportHistory


def migrate_database():
    """Exécuter la migration de la base de données."""
    app = create_app()

    with app.app_context():
        print("🔄 Migration de la base de données...")
        print()

        # Créer toutes les nouvelles tables
        # (SQLAlchemy créera uniquement les tables qui n'existent pas)
        try:
            print("📋 Création des nouvelles tables...")
            db.create_all()
            print("✅ Tables créées avec succès")
            print()

            # Vérifier les tables créées
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            print("📊 Tables dans la base de données :")
            for table in sorted(tables):
                print(f"   - {table}")
            print()

            # Statistiques
            feeds_count = Feed.query.count()
            articles_count = Article.query.count()
            tags_count = Tag.query.count()

            print("📈 Statistiques :")
            print(f"   - Flux RSS : {feeds_count}")
            print(f"   - Articles : {articles_count}")
            print(f"   - Tags : {tags_count}")
            print()

            print("✅ Migration terminée avec succès !")

        except Exception as e:
            print(f"❌ Erreur lors de la migration : {e}")
            import traceback
            traceback.print_exc()
            return False

    return True


if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
