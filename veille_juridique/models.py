"""
Modèles de base de données pour l'application de veille juridique
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Feed(db.Model):
    """Modèle pour les flux RSS"""
    __tablename__ = 'feeds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relation avec les articles
    articles = db.relationship('Article', backref='feed', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Feed {self.name}>'

    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'article_count': self.articles.count()
        }


class Article(db.Model):
    """Modèle pour les articles RSS"""
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feeds.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.Text, nullable=True)
    pub_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    guid = db.Column(db.String(500), nullable=True)  # Pour éviter les doublons

    # Index pour améliorer les performances
    __table_args__ = (
        db.Index('idx_feed_id', 'feed_id'),
        db.Index('idx_pub_date', 'pub_date'),
        db.Index('idx_guid', 'guid'),
    )

    def __repr__(self):
        return f'<Article {self.title[:50]}>'

    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'feed_id': self.feed_id,
            'feed_name': self.feed.name if self.feed else None,
            'feed_category': self.feed.category if self.feed else None,
            'title': self.title,
            'link': self.link,
            'description': self.description,
            'pub_date': self.pub_date.isoformat() if self.pub_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
