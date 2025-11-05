"""
Configuration de l'application de veille juridique
"""
import os

class Config:
    """Configuration de base de l'application"""

    # Clé secrète pour les sessions Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Configuration de la base de données SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration de l'application
    APP_NAME = "Veille Juridique RSS"
    APP_VERSION = "1.0.0"

    # Nombre d'articles par page
    ARTICLES_PER_PAGE = 50

    # Durée de conservation des articles (en jours)
    ARTICLE_RETENTION_DAYS = 90

    # Timeout pour la récupération des flux RSS (en secondes)
    RSS_FETCH_TIMEOUT = 30

    # User-Agent pour la récupération des flux
    RSS_USER_AGENT = "Mozilla/5.0 (compatible; VeilleJuridiqueBot/1.0)"


class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False

    # En production, utiliser une vraie clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()


class TestingConfig(Config):
    """Configuration pour les tests"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dictionnaire de configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
