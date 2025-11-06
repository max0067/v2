"""Modèles pour le système collaboratif et de gestion de dossiers."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


# ========== UTILISATEURS ET ROLES ==========

class User(db.Model):
    """Modèle pour les utilisateurs."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(db.String(20), default='reader')  # admin, editor, reader
    is_active = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relations
    folders = db.relationship('Folder', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('ArticleNote', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('ArticleComment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    highlights = db.relationship('ArticleHighlight', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    assigned_articles = db.relationship('ArticleAssignment', foreign_keys='ArticleAssignment.assigned_to_id', backref='assignee', lazy='dynamic')

    def set_password(self, password):
        """Hasher le mot de passe."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifier le mot de passe."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


# ========== DOSSIERS ET COLLECTIONS ==========

class Folder(db.Model):
    """Modèle pour les dossiers thématiques."""

    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#0066A1')  # Couleur hex
    icon = db.Column(db.String(50), default='folder')  # Icône Bootstrap

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'))  # Sous-dossiers

    is_shared = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    articles = db.relationship('ArticleFolder', backref='folder', lazy='dynamic', cascade='all, delete-orphan')
    children = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    shares = db.relationship('FolderShare', backref='folder', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_articles=False):
        """Convertir en dictionnaire."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'parent_id': self.parent_id,
            'is_shared': self.is_shared,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'article_count': self.articles.count()
        }

        if include_articles:
            data['articles'] = [af.article.to_dict() for af in self.articles.all()]

        return data

    def __repr__(self):
        return f'<Folder {self.name}>'


class ArticleFolder(db.Model):
    """Association entre articles et dossiers."""

    __tablename__ = 'article_folders'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('article_id', 'folder_id', name='unique_article_folder'),
    )

    def __repr__(self):
        return f'<ArticleFolder article={self.article_id} folder={self.folder_id}>'


class FolderShare(db.Model):
    """Partage de dossiers avec d'autres utilisateurs."""

    __tablename__ = 'folder_shares'

    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission = db.Column(db.String(20), default='read')  # read, write, admin
    shared_at = db.Column(db.DateTime, default=datetime.utcnow)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = (
        db.UniqueConstraint('folder_id', 'shared_with_id', name='unique_folder_share'),
    )

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'folder_id': self.folder_id,
            'shared_with_id': self.shared_with_id,
            'shared_with_name': User.query.get(self.shared_with_id).full_name if self.shared_with_id else None,
            'permission': self.permission,
            'shared_at': self.shared_at.isoformat() if self.shared_at else None
        }


# ========== NOTES ET ANNOTATIONS ==========

class ArticleNote(db.Model):
    """Notes privées sur les articles."""

    __tablename__ = 'article_notes'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)
    is_private = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else None,
            'content': self.content,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<ArticleNote {self.id}>'


class ArticleHighlight(db.Model):
    """Surlignages de texte dans les articles."""

    __tablename__ = 'article_highlights'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    text = db.Column(db.Text, nullable=False)  # Texte surligné
    color = db.Column(db.String(7), default='#FFFF00')  # Couleur du surlignage
    start_offset = db.Column(db.Integer)  # Position de début dans le texte
    end_offset = db.Column(db.Integer)  # Position de fin

    note = db.Column(db.Text)  # Note optionnelle sur le surlignage

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else None,
            'text': self.text,
            'color': self.color,
            'start_offset': self.start_offset,
            'end_offset': self.end_offset,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ArticleHighlight {self.id}>'


class ArticleComment(db.Model):
    """Commentaires collaboratifs sur les articles."""

    __tablename__ = 'article_comments'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('article_comments.id'))  # Pour les réponses

    content = db.Column(db.Text, nullable=False)
    mentions = db.Column(db.JSON)  # Liste des user_id mentionnés

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    replies = db.relationship('ArticleComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self, include_replies=False):
        """Convertir en dictionnaire."""
        data = {
            'id': self.id,
            'article_id': self.article_id,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else None,
            'author_avatar': self.author.avatar if self.author else None,
            'parent_id': self.parent_id,
            'content': self.content,
            'mentions': self.mentions or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_replies:
            data['replies'] = [reply.to_dict() for reply in self.replies.all()]

        return data

    def __repr__(self):
        return f'<ArticleComment {self.id}>'


# ========== PIÈCES JOINTES ==========

class ArticleAttachment(db.Model):
    """Pièces jointes liées aux articles."""

    __tablename__ = 'article_attachments'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Taille en octets
    mime_type = db.Column(db.String(100))

    description = db.Column(db.Text)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'uploaded_by': self.uploaded_by,
            'uploader_name': User.query.get(self.uploaded_by).full_name if self.uploaded_by else None,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'description': self.description,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

    def __repr__(self):
        return f'<ArticleAttachment {self.filename}>'


# ========== ASSIGNATION ET COLLABORATION ==========

class ArticleAssignment(db.Model):
    """Assignation d'articles à des collègues."""

    __tablename__ = 'article_assignments'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    due_date = db.Column(db.DateTime)

    note = db.Column(db.Text)  # Note d'assignation

    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'assigned_to_id': self.assigned_to_id,
            'assigned_to_name': User.query.get(self.assigned_to_id).full_name if self.assigned_to_id else None,
            'assigned_by_id': self.assigned_by_id,
            'assigned_by_name': User.query.get(self.assigned_by_id).full_name if self.assigned_by_id else None,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'note': self.note,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f'<ArticleAssignment {self.id}>'


# ========== HISTORIQUE ==========

class ActivityLog(db.Model):
    """Historique des modifications et actions."""

    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    action = db.Column(db.String(50), nullable=False)  # create, update, delete, share, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # article, folder, note, etc.
    entity_id = db.Column(db.Integer, nullable=False)

    details = db.Column(db.JSON)  # Détails de l'action
    ip_address = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convertir en dictionnaire."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': User.query.get(self.user_id).full_name if self.user_id else 'Système',
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ActivityLog {self.action} {self.entity_type}>'
