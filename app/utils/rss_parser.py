"""Parser RSS pour récupérer les articles."""
import feedparser
import logging
from datetime import datetime
from app import db
from app.models import Article, Feed
import time
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)


class RSSParser:
    """Classe pour parser les flux RSS et sauvegarder les articles."""

    def __init__(self, timeout=30):
        """Initialiser le parser.

        Args:
            timeout: Timeout pour les requêtes HTTP (secondes)
        """
        self.timeout = timeout
        feedparser.USER_AGENT = 'Veille Juridique RSS Bot/2.0 (+https://dusselle.fr)'

    def fetch_and_save(self, feed):
        """Récupérer et sauvegarder les articles d'un flux.

        Args:
            feed: Instance du modèle Feed

        Returns:
            Nombre de nouveaux articles ajoutés
        """
        try:
            logger.info(f"Récupération du flux: {feed.name} ({feed.url})")

            # Parser le flux RSS
            parsed_feed = feedparser.parse(feed.url)

            # Vérifier les erreurs
            if parsed_feed.bozo:
                logger.warning(f"Avertissement lors du parsing de {feed.name}: {parsed_feed.bozo_exception}")

            if not parsed_feed.entries:
                logger.warning(f"Aucune entrée trouvée pour {feed.name}")
                feed.last_fetch = datetime.utcnow()
                db.session.commit()
                return 0

            new_articles_count = 0

            # Traiter chaque entrée
            for entry in parsed_feed.entries:
                try:
                    # Créer un GUID unique
                    guid = entry.get('id') or entry.get('link') or entry.get('title')

                    if not guid:
                        logger.warning(f"Entrée sans identifiant dans {feed.name}, ignorée")
                        continue

                    # Vérifier si l'article existe déjà
                    existing = Article.query.filter_by(guid=guid).first()
                    if existing:
                        continue

                    # Extraire les données
                    title = entry.get('title', 'Sans titre')
                    link = entry.get('link', '')
                    description = entry.get('summary', '') or entry.get('description', '')
                    content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                    author = entry.get('author', '') or entry.get('dc_creator', '')

                    # Parser la date de publication
                    published_date = self._parse_date(entry)

                    # Créer l'article
                    article = Article(
                        feed_id=feed.id,
                        title=title[:500],  # Limite à 500 caractères
                        link=link[:1000],
                        description=description,
                        content=content,
                        author=author[:255] if author else None,
                        published_date=published_date,
                        guid=guid[:500]
                    )

                    db.session.add(article)
                    new_articles_count += 1

                except Exception as e:
                    logger.error(f"Erreur lors du traitement d'une entrée de {feed.name}: {str(e)}")
                    continue

            # Mettre à jour la date de dernière récupération
            feed.last_fetch = datetime.utcnow()
            db.session.commit()

            logger.info(f"Flux {feed.name}: {new_articles_count} nouveaux articles ajoutés")
            return new_articles_count

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la récupération du flux {feed.name}: {str(e)}")
            raise

    def _parse_date(self, entry):
        """Parser la date de publication d'une entrée.

        Args:
            entry: Entrée du flux RSS

        Returns:
            datetime object ou None
        """
        # Essayer différents champs de date
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']

        for field in date_fields:
            if field in entry and entry[field]:
                try:
                    return datetime(*entry[field][:6])
                except (TypeError, ValueError):
                    continue

        # Essayer de parser les chaînes de date
        date_string_fields = ['published', 'updated', 'created']
        for field in date_string_fields:
            if field in entry and entry[field]:
                try:
                    return parsedate_to_datetime(entry[field])
                except Exception:
                    continue

        # Par défaut, retourner la date actuelle
        return datetime.utcnow()

    def cleanup_old_articles(self, days=90):
        """Supprimer les articles de plus de X jours.

        Args:
            days: Nombre de jours de rétention

        Returns:
            Nombre d'articles supprimés
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            deleted = Article.query.filter(Article.created_at < cutoff_date).delete()
            db.session.commit()

            logger.info(f"{deleted} articles de plus de {days} jours supprimés")
            return deleted

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors du nettoyage des anciens articles: {str(e)}")
            raise
