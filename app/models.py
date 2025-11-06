"""Modèles SQLAlchemy pour l'application."""
from datetime import datetime
from app import db


class Feed(db.Model):
    """Modèle pour les flux RSS."""

    __tablename__ = 'rss_feeds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_fetch = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation avec les articles
    articles = db.relationship('Article', backref='feed', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Feed {self.name}>'

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'category': self.category,
            'is_active': self.is_active,
            'last_fetch': self.last_fetch.isoformat() if self.last_fetch else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'articles_count': self.articles.count()
        }


class Article(db.Model):
    """Modèle pour les articles."""

    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('rss_feeds.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    published_date = db.Column(db.DateTime)
    guid = db.Column(db.String(500), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Index pour améliorer les performances
    __table_args__ = (
        db.Index('idx_feed_published', 'feed_id', 'published_date'),
        db.Index('idx_guid', 'guid'),
        db.Index('idx_created', 'created_at'),
    )

    def __repr__(self):
        return f'<Article {self.title[:50]}>'

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'feed_id': self.feed_id,
            'feed_name': self.feed.name if self.feed else None,
            'feed_category': self.feed.category if self.feed else None,
            'title': self.title,
            'link': self.link,
            'description': self.description,
            'content': self.content,
            'author': self.author,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
