"""Configuration de l'application Flask."""
import os
from datetime import timedelta


class Config:
    """Configuration de base."""

    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Base de données
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'dusselle_rss')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASS', '')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }

    # Application
    ITEMS_PER_PAGE = 50
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

    # RSS Feed settings
    RSS_TIMEOUT = 30  # secondes
    RSS_USER_AGENT = 'Veille Juridique RSS Bot/1.0'
    ARTICLES_RETENTION_DAYS = 90  # Conservation des articles


class DevelopmentConfig(Config):
    """Configuration de développement."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuration de production."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
