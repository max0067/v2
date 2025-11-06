"""Factory pour l'application Flask."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """Factory pour créer l'application Flask.

    Args:
        config_name: Nom de la configuration ('development', 'production', 'testing')

    Returns:
        Application Flask configurée
    """
    app = Flask(__name__)

    # Configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    from config import config
    app.config.from_object(config.get(config_name, config['default']))

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Importer les modèles (nécessaire pour les migrations)
    from app import models, models_collab

    # Enregistrer les blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.favorites import favorites_bp
    from app.routes.tags import tags_bp
    from app.routes.exports import exports_bp
    from app.routes.folders import folders_bp
    from app.routes.collaboration import collaboration_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(favorites_bp, url_prefix='/api')
    app.register_blueprint(tags_bp, url_prefix='/api')
    app.register_blueprint(exports_bp, url_prefix='/api')
    app.register_blueprint(folders_bp, url_prefix='/api')
    app.register_blueprint(collaboration_bp, url_prefix='/api')

    # Context processor pour les templates
    @app.context_processor
    def inject_globals():
        """Injecter des variables globales dans tous les templates."""
        return {
            'app_name': 'Veille Juridique RSS',
            'app_version': '2.0.0'
        }

    # Gestionnaire d'erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        """Gérer les erreurs 404."""
        from flask import render_template, request
        if request.path.startswith('/api/'):
            from flask import jsonify
            return jsonify({'error': 'Ressource non trouvée'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Gérer les erreurs 500."""
        from flask import render_template, request, jsonify
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Erreur interne du serveur'}), 500
        return render_template('500.html'), 500

    return app
