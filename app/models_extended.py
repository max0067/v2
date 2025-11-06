"""Modèles SQLAlchemy étendus pour les fonctionnalités avancées."""
from datetime import datetime
from app import db


# Table d'association many-to-many pour les tags
article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


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

    # Relations
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
    """Modèle pour les articles avec favoris et tags."""

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

    # Nouveaux champs
    is_favorite = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)  # Notes personnelles
    importance = db.Column(db.Integer, default=0)  # 0=normal, 1=important, 2=urgent

    # Relations
    tags = db.relationship('Tag', secondary=article_tags, lazy='subquery',
                          backref=db.backref('articles', lazy=True))
    annotations = db.relationship('Annotation', backref='article', lazy='dynamic', cascade='all, delete-orphan')

    # Index
    __table_args__ = (
        db.Index('idx_feed_published', 'feed_id', 'published_date'),
        db.Index('idx_guid', 'guid'),
        db.Index('idx_created', 'created_at'),
        db.Index('idx_favorite', 'is_favorite'),
        db.Index('idx_importance', 'importance'),
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_favorite': self.is_favorite,
            'is_read': self.is_read,
            'notes': self.notes,
            'importance': self.importance,
            'tags': [tag.to_dict() for tag in self.tags],
            'annotations_count': self.annotations.count()
        }


class Tag(db.Model):
    """Modèle pour les tags."""

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#6c757d')  # Couleur hex
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tag {self.name}>'

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'articles_count': len(self.articles)
        }


class Annotation(db.Model):
    """Modèle pour les annotations d'articles."""

    __tablename__ = 'annotations'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    highlight_text = db.Column(db.Text)  # Texte surligné
    position = db.Column(db.Integer)  # Position dans l'article
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Annotation {self.id} for Article {self.article_id}>'

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'content': self.content,
            'highlight_text': self.highlight_text,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class LegalDeadline(db.Model):
    """Modèle pour les échéances légales."""

    __tablename__ = 'legal_deadlines'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    deadline_date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(100))  # Type d'échéance
    status = db.Column(db.String(50), default='pending')  # pending, completed, cancelled
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))  # Article source
    notification_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Index
    __table_args__ = (
        db.Index('idx_deadline_date', 'deadline_date'),
        db.Index('idx_status', 'status'),
    )

    def __repr__(self):
        return f'<LegalDeadline {self.title}>'

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline_date': self.deadline_date.isoformat() if self.deadline_date else None,
            'category': self.category,
            'status': self.status,
            'article_id': self.article_id,
            'notification_sent': self.notification_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExportHistory(db.Model):
    """Historique des exports."""

    __tablename__ = 'export_history'

    id = db.Column(db.Integer, primary_key=True)
    export_type = db.Column(db.String(50), nullable=False)  # pdf, csv, docx, bibliography
    filename = db.Column(db.String(500))
    article_ids = db.Column(db.Text)  # JSON liste des IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Export {self.export_type} - {self.filename}>'
