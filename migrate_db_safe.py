#!/usr/bin/env python3
"""Script de migration sécurisé pour ajouter les nouvelles fonctionnalités.

Ce script :
1. Charge automatiquement le fichier .env
2. Ajoute les nouvelles colonnes à la table articles
3. Crée les nouvelles tables
"""
import sys
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from sqlalchemy import text


def migrate_database():
    """Exécuter la migration de la base de données."""
    app = create_app()

    with app.app_context():
        print("🔄 Migration de la base de données...")
        print()

        try:
            # Étape 1: Ajouter les nouvelles colonnes à la table articles
            print("📋 Ajout des nouvelles colonnes à la table 'articles'...")

            columns_to_add = [
                ("is_favorite", "BOOLEAN DEFAULT FALSE"),
                ("is_read", "BOOLEAN DEFAULT FALSE"),
                ("notes", "TEXT"),
                ("importance", "INTEGER DEFAULT 0"),
            ]

            for column_name, column_def in columns_to_add:
                try:
                    # Vérifier si la colonne existe déjà
                    result = db.session.execute(text(
                        f"SHOW COLUMNS FROM articles LIKE '{column_name}'"
                    ))
                    if result.fetchone() is None:
                        # La colonne n'existe pas, on l'ajoute
                        db.session.execute(text(
                            f"ALTER TABLE articles ADD COLUMN {column_name} {column_def}"
                        ))
                        db.session.commit()
                        print(f"   ✅ Colonne '{column_name}' ajoutée")
                    else:
                        print(f"   ⏭️  Colonne '{column_name}' existe déjà")
                except Exception as e:
                    print(f"   ⚠️  Erreur pour '{column_name}': {e}")
                    db.session.rollback()

            print()

            # Étape 2: Créer les nouvelles tables
            print("📋 Création des nouvelles tables...")
            db.create_all()
            print("   ✅ Tables créées avec succès")
            print()

            # Étape 3: Vérifier les tables créées
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            print("📊 Tables dans la base de données :")
            for table in sorted(tables):
                print(f"   - {table}")
            print()

            # Étape 4: Vérifier les colonnes de la table articles
            print("🔍 Colonnes de la table 'articles' :")
            columns = inspector.get_columns('articles')
            for col in columns:
                print(f"   - {col['name']} ({col['type']})")
            print()

            # Étape 5: Statistiques
            from app.models import Feed, Article, Tag

            feeds_count = Feed.query.count()
            articles_count = Article.query.count()
            tags_count = Tag.query.count()

            print("📈 Statistiques :")
            print(f"   - Flux RSS : {feeds_count}")
            print(f"   - Articles : {articles_count}")
            print(f"   - Tags : {tags_count}")
            print()

            print("✅ Migration terminée avec succès !")
            print()
            print("🔄 Redémarrez l'application avec :")
            print("   touch passenger_wsgi.py")

        except Exception as e:
            print(f"❌ Erreur lors de la migration : {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

    return True


if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
