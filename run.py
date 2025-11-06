#!/usr/bin/env python3
"""Point d'entrée pour lancer l'application Flask."""
import os
from app import create_app, db

# Créer l'application
app = create_app()


@app.cli.command()
def init_db():
    """Initialiser la base de données."""
    with app.app_context():
        db.create_all()
        print("✅ Base de données initialisée avec succès!")


@app.cli.command()
def drop_db():
    """Supprimer toutes les tables (ATTENTION: destructif!)."""
    with app.app_context():
        if input("⚠️  Êtes-vous sûr de vouloir supprimer toutes les tables? (yes/no): ") == "yes":
            db.drop_all()
            print("✅ Toutes les tables ont été supprimées!")
        else:
            print("❌ Opération annulée.")


if __name__ == '__main__':
    # Lancer le serveur de développement
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"""
╔══════════════════════════════════════════════════════╗
║  📰 Veille Juridique RSS - Version 2.0              ║
║  🚀 Serveur de développement Flask                  ║
╚══════════════════════════════════════════════════════╝

🌐 URL: http://localhost:{port}
🐛 Debug: {debug}
⚙️  Environnement: {os.environ.get('FLASK_ENV', 'development')}

💡 Commandes utiles:
   flask init-db       - Initialiser la base de données
   flask db init       - Initialiser les migrations
   flask db migrate    - Créer une migration
   flask db upgrade    - Appliquer les migrations

Appuyez sur Ctrl+C pour arrêter le serveur.
""")

    app.run(host='0.0.0.0', port=port, debug=debug)
