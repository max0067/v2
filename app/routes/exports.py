"""Routes pour les exports (PDF, CSV, etc.)."""
from flask import Blueprint, jsonify, request, make_response, render_template
from app import db
from app.models import Article, ExportHistory
from datetime import datetime
import csv
import json
from io import StringIO, BytesIO
import logging

exports_bp = Blueprint('exports', __name__)
logger = logging.getLogger(__name__)


@exports_bp.route('/export/csv', methods=['GET', 'POST'])
def export_csv():
    """Exporter des articles en CSV."""
    # Récupérer les IDs d'articles (query param ou POST)
    if request.method == 'POST':
        data = request.get_json()
        article_ids = data.get('article_ids', [])
    else:
        article_ids = request.args.getlist('ids', type=int)

    # Si pas d'IDs, exporter les favoris ou tous
    if not article_ids:
        filter_type = request.args.get('filter', 'all')
        if filter_type == 'favorites':
            articles = Article.query.filter_by(is_favorite=True).all()
        else:
            articles = Article.query.limit(1000).all()  # Limite pour éviter timeout
    else:
        articles = Article.query.filter(Article.id.in_(article_ids)).all()

    # Créer le CSV
    si = StringIO()
    writer = csv.writer(si)

    # Headers
    writer.writerow([
        'ID',
        'Titre',
        'Source',
        'Catégorie',
        'Auteur',
        'Date de publication',
        'Lien',
        'Description',
        'Favori',
        'Importance',
        'Tags'
    ])

    # Données
    for article in articles:
        writer.writerow([
            article.id,
            article.title,
            article.feed.name if article.feed else '',
            article.feed.category if article.feed else '',
            article.author or '',
            article.published_date.strftime('%Y-%m-%d %H:%M') if article.published_date else '',
            article.link,
            article.description or '',
            'Oui' if article.is_favorite else 'Non',
            article.importance,
            ', '.join([tag.name for tag in article.tags])
        ])

    # Créer la réponse
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"

    # Sauvegarder dans l'historique
    try:
        history = ExportHistory(
            export_type='csv',
            filename=f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            article_ids=json.dumps([a.id for a in articles])
        )
        db.session.add(history)
        db.session.commit()
    except Exception as e:
        logger.error(f"Erreur sauvegarde historique: {str(e)}")

    return output


@exports_bp.route('/export/pdf/<int:article_id>', methods=['GET'])
def export_article_pdf(article_id):
    """Exporter un article en PDF."""
    article = Article.query.get_or_404(article_id)

    try:
        # Importer WeasyPrint (à installer séparément)
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        # Générer le HTML de l'article
        html_content = render_template('exports/article_pdf.html', article=article)

        # Convertir en PDF
        font_config = FontConfiguration()
        pdf = HTML(string=html_content).write_pdf(font_config=font_config)

        # Créer la réponse
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=article_{article.id}_{datetime.now().strftime("%Y%m%d")}.pdf'

        # Sauvegarder dans l'historique
        try:
            history = ExportHistory(
                export_type='pdf',
                filename=f"article_{article.id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                article_ids=json.dumps([article.id])
            )
            db.session.add(history)
            db.session.commit()
        except Exception as e:
            logger.error(f"Erreur sauvegarde historique: {str(e)}")

        return response

    except ImportError:
        # WeasyPrint non installé, utiliser une alternative simple
        return export_article_html_print(article_id)


@exports_bp.route('/export/print/<int:article_id>', methods=['GET'])
def export_article_html_print(article_id):
    """Version imprimable HTML d'un article (alternative au PDF)."""
    article = Article.query.get_or_404(article_id)
    return render_template('exports/article_print.html', article=article)


@exports_bp.route('/export/bibliography', methods=['POST'])
def export_bibliography():
    """Exporter une bibliographie des articles sélectionnés."""
    data = request.get_json()
    article_ids = data.get('article_ids', [])
    style = data.get('style', 'apa')  # apa, mla, chicago

    if not article_ids:
        return jsonify({'success': False, 'error': 'Aucun article sélectionné'}), 400

    articles = Article.query.filter(Article.id.in_(article_ids)).all()

    # Générer les citations selon le style
    citations = []
    for article in articles:
        if style == 'apa':
            citation = format_citation_apa(article)
        elif style == 'mla':
            citation = format_citation_mla(article)
        else:  # chicago
            citation = format_citation_chicago(article)

        citations.append(citation)

    # Trier par auteur/titre
    citations.sort()

    return jsonify({
        'success': True,
        'style': style,
        'citations': citations,
        'count': len(citations)
    })


def format_citation_apa(article):
    """Formater une citation au format APA."""
    author = article.author or article.feed.name
    year = article.published_date.year if article.published_date else datetime.now().year
    title = article.title

    return f"{author}. ({year}). {title}. Récupéré de {article.link}"


def format_citation_mla(article):
    """Formater une citation au format MLA."""
    author = article.author or article.feed.name
    title = article.title
    source = article.feed.name
    date = article.published_date.strftime('%d %b. %Y') if article.published_date else 'n.d.'

    return f'{author}. "{title}." {source}, {date}. Web. {article.link}'


def format_citation_chicago(article):
    """Formater une citation au format Chicago."""
    author = article.author or article.feed.name
    title = article.title
    source = article.feed.name
    date = article.published_date.strftime('%B %d, %Y') if article.published_date else 'n.d.'

    return f'{author}. "{title}." {source}. {date}. {article.link}.'


@exports_bp.route('/export/history', methods=['GET'])
def get_export_history():
    """Récupérer l'historique des exports."""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = ExportHistory.query\
        .order_by(ExportHistory.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'exports': [{
            'id': exp.id,
            'type': exp.export_type,
            'filename': exp.filename,
            'created_at': exp.created_at.isoformat() if exp.created_at else None
        } for exp in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })
