#!/usr/bin/env python3
"""Script de migration pour ajouter les fonctionnalités collaboratives.

Ce script ajoute :
- Système d'utilisateurs avec rôles
- Dossiers et collections
- Notes privées et annotations
- Surlignages de texte
- Commentaires collaboratifs
- Pièces jointes
- Assignations d'articles
- Historique des modifications
"""
import sys
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models_collab import (User, Folder, ArticleFolder, FolderShare,
                                ArticleNote, ArticleHighlight, ArticleComment,
                                ArticleAttachment, ArticleAssignment, ActivityLog)


def migrate_collaborative_features():
    """Ajouter les fonctionnalités collaboratives."""
    app = create_app()

    with app.app_context():
        print("🚀 Migration des fonctionnalités collaboratives")
        print("=" * 60)
        print()

        try:
            print("📋 Création des nouvelles tables...")
            db.create_all()
            print("✅ Tables créées avec succès")
            print()

            # Créer un utilisateur par défaut si aucun n'existe
            default_user = User.query.filter_by(email='default@veille.fr').first()
            if not default_user:
                print("👤 Création de l'utilisateur par défaut...")
                default_user = User(
                    email='default@veille.fr',
                    username='utilisateur',
                    full_name='Utilisateur par défaut',
                    role='admin'
                )
                default_user.set_password('changeme')
                db.session.add(default_user)
                db.session.commit()
                print(f"✅ Utilisateur créé : {default_user.email}")
                print(f"   Username: {default_user.username}")
                print(f"   Mot de passe: changeme (À CHANGER !)")
                print()

            # Vérifier les tables créées
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            print("📊 Tables dans la base de données :")
            collaborative_tables = [
                'users', 'folders', 'article_folders', 'folder_shares',
                'article_notes', 'article_highlights', 'article_comments',
                'article_attachments', 'article_assignments', 'activity_logs'
            ]

            for table in collaborative_tables:
                status = "✅" if table in tables else "❌"
                print(f"   {status} {table}")
            print()

            # Créer quelques dossiers d'exemple
            if Folder.query.count() == 0:
                print("📁 Création de dossiers d'exemple...")

                dossiers_exemples = [
                    {'name': 'Droit social', 'color': '#0066A1', 'icon': 'people'},
                    {'name': 'Droit fiscal', 'color': '#00A651', 'icon': 'cash'},
                    {'name': 'Droit des contrats', 'color': '#FF6B00', 'icon': 'file-text'},
                    {'name': 'Jurisprudence', 'color': '#EA4335', 'icon': 'book'},
                    {'name': 'À traiter', 'color': '#FBBC04', 'icon': 'clock'},
                ]

                for folder_data in dossiers_exemples:
                    folder = Folder(
                        name=folder_data['name'],
                        color=folder_data['color'],
                        icon=folder_data['icon'],
                        owner_id=default_user.id
                    )
                    db.session.add(folder)

                db.session.commit()
                print(f"✅ {len(dossiers_exemples)} dossiers d'exemple créés")
                print()

            # Statistiques
            print("📈 Statistiques :")
            print(f"   - Utilisateurs : {User.query.count()}")
            print(f"   - Dossiers : {Folder.query.count()}")
            print(f"   - Notes : {ArticleNote.query.count()}")
            print(f"   - Commentaires : {ArticleComment.query.count()}")
            print(f"   - Surlignages : {ArticleHighlight.query.count()}")
            print(f"   - Assignations : {ArticleAssignment.query.count()}")
            print()

            print("=" * 60)
            print("✅ Migration terminée avec succès !")
            print()
            print("🔐 IMPORTANT - Informations de connexion :")
            print(f"   Email : default@veille.fr")
            print(f"   Mot de passe : changeme")
            print()
            print("⚠️  Changez ce mot de passe dès que possible !")
            print()

            return True

        except Exception as e:
            print(f"❌ Erreur lors de la migration : {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = migrate_collaborative_features()
    sys.exit(0 if success else 1)
