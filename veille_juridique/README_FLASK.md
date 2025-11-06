# 📰 Application de Veille Juridique RSS - Version Flask/Python

Application web moderne de veille juridique basée sur des flux RSS, développée avec Flask et SQLite.

## ✨ Fonctionnalités

- ✅ **Agrégation de flux RSS** : Collecte automatique d'articles depuis plusieurs sources juridiques
- 🔍 **Recherche en temps réel** : Filtrage par mot-clé et catégorie
- 📊 **Interface moderne** : Design responsive type Gmail avec Bootstrap 5
- ⚙️ **Gestion CRUD complète** : API REST pour gérer les flux
- 🔄 **Actualisation automatique** : Mise à jour manuelle et programmée via cron
- 💾 **Base SQLite** : Aucune configuration MySQL nécessaire
- 🚀 **Production-ready** : Déploiement avec Gunicorn

## 📋 Prérequis

- **Python** : 3.8 ou supérieur
- **pip** : Gestionnaire de paquets Python
- **SQLite** : Intégré à Python

## 🚀 Installation rapide (Développement)

```bash
# 1. Cloner ou télécharger le projet
cd veille_juridique/

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser la base de données
python app.py --init

# 4. Ajouter des flux d'exemple
python app.py --sample

# 5. Démarrer le serveur de développement
python app.py

# L'application est accessible sur http://localhost:8000
```

## 🏭 Déploiement en production

### Option 1 : Gunicorn (Recommandé)

```bash
# Démarrer avec le script fourni
chmod +x start.sh
./start.sh

# OU manuellement
gunicorn --config gunicorn_config.py wsgi:application
```

### Option 2 : cPanel/Plesk

Consultez le guide complet : **[DEPLOIEMENT_CPANEL.md](DEPLOIEMENT_CPANEL.md)**

## 📁 Structure du projet

```
veille_juridique/
├── app.py                      # Application Flask principale
├── wsgi.py                     # Point d'entrée WSGI pour production
├── config.py                   # Configuration (dev/prod/test)
├── models.py                   # Modèles SQLAlchemy (Feed, Article)
├── requirements.txt            # Dépendances Python
├── gunicorn_config.py          # Configuration Gunicorn
├── start.sh                    # Script de démarrage
├── database.db                 # Base de données SQLite (créée automatiquement)
├── templates/                  # Templates Jinja2
│   ├── base.html
│   ├── dashboard.html
│   └── feeds.html
└── static/                     # Fichiers statiques
    ├── css/style.css
    └── js/app.js
```

## 🎯 Utilisation

### Interface Web

- **Page d'accueil** : http://localhost:8000/ - Liste des articles
- **Gestion des flux** : http://localhost:8000/feeds - CRUD des flux RSS

### API REST

#### Récupérer les statistiques
```bash
GET /api/stats
```

#### Lister tous les flux
```bash
GET /api/feeds
```

#### Ajouter un flux
```bash
POST /api/feeds
Content-Type: application/json

{
  "name": "Legifrance",
  "url": "https://www.legifrance.gouv.fr/rss/jorf.xml",
  "category": "Législation",
  "is_active": true
}
```

#### Modifier un flux
```bash
PUT /api/feeds/{id}
Content-Type: application/json

{
  "name": "Nouveau nom",
  "is_active": false
}
```

#### Supprimer un flux
```bash
DELETE /api/feeds/{id}
```

#### Actualiser tous les flux
```bash
POST /api/refresh
```

#### Rechercher des articles
```bash
GET /api/search?q=mot-clé
GET /api/search?category=Législation
GET /api/search?feed_id=1
```

### Ligne de commande

```bash
# Initialiser la base de données
python app.py --init

# Ajouter des flux d'exemple
python app.py --sample

# Mettre à jour tous les flux
python app.py --update

# Démarrer le serveur
python app.py --host 0.0.0.0 --port 8000
```

## ⏰ Configuration Cron (Automatisation)

Pour actualiser automatiquement les flux :

```bash
# Éditer la crontab
crontab -e

# Ajouter (toutes les 6 heures)
0 */6 * * * cd /chemin/vers/veille_juridique && python app.py --update >> /var/log/rss-update.log 2>&1

# Ou toutes les heures
0 * * * * cd /chemin/vers/veille_juridique && python app.py --update >> /var/log/rss-update.log 2>&1
```

## ⚙️ Configuration

Modifiez `config.py` pour personnaliser :

```python
class Config:
    # Nombre d'articles par page
    ARTICLES_PER_PAGE = 50

    # Durée de conservation des articles (en jours)
    ARTICLE_RETENTION_DAYS = 90

    # Timeout pour la récupération des flux RSS
    RSS_FETCH_TIMEOUT = 30
```

Pour la production :

```bash
# Définir l'environnement
export FLASK_ENV=production
export SECRET_KEY="votre_cle_secrete_aleatoire"
```

## 📊 Sources RSS juridiques recommandées

| Source | URL | Catégorie |
|--------|-----|-----------|
| Legifrance - Actualités | `https://www.legifrance.gouv.fr/rss/actualites.xml` | Législation |
| Journal Officiel (JORF) | `https://www.legifrance.gouv.fr/rss/jorf.xml` | Journal Officiel |
| Dalloz Actualité | `https://www.dalloz-actualite.fr/feed` | Doctrine |

## 🐛 Dépannage

### Erreur "Module not found"

```bash
pip install -r requirements.txt --force-reinstall
```

### Port déjà utilisé

```bash
# Trouver le processus
lsof -i :8000

# Tuer le processus
kill -9 PID
```

### Base de données corrompue

```bash
# Sauvegarder
cp database.db database.db.backup

# Réinitialiser
rm database.db
python app.py --init
python app.py --sample
```

### Problème avec feedparser

Si vous rencontrez une erreur avec `sgmllib` :

```bash
pip install feedparser --no-deps
# Puis installer sgmllib3k manuellement si nécessaire
```

## 🔐 Sécurité

### En production

1. **Désactiver le mode debug** dans `config.py`
2. **Utiliser HTTPS** avec un certificat SSL
3. **Définir une clé secrète forte** :
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```
4. **Limiter l'accès à la base de données** :
   ```bash
   chmod 600 database.db
   ```

## 📈 Performance

### Optimisation Gunicorn

Nombre de workers recommandé :
```
workers = (2 × CPU_cores) + 1
```

Pour 4 CPU :
```bash
gunicorn --workers 9 --bind 0.0.0.0:8000 wsgi:application
```

### Cache et CDN

Les fichiers statiques (CSS, JS) peuvent être servis via un CDN pour améliorer les performances.

## 🛠️ Développement

### Structure MVC

- **Models** : `models.py` - SQLAlchemy ORM
- **Views** : `templates/` - Templates Jinja2
- **Controllers** : `app.py` - Routes Flask

### Ajouter une nouvelle fonctionnalité

1. Créer la route dans `app.py`
2. Créer le template dans `templates/`
3. Ajouter le JavaScript dans `static/js/app.js`
4. Mettre à jour l'API si nécessaire

## 📦 Mise à jour

```bash
# Sauvegarder la base de données
cp database.db database.db.backup

# Mettre à jour le code
git pull  # Si vous utilisez Git

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Redémarrer l'application
pkill gunicorn
./start.sh
```

## 📝 Licence

Ce projet est développé pour un usage personnel/professionnel.

## 🤝 Support

Pour toute question :
- Consultez la documentation : [DEPLOIEMENT_CPANEL.md](DEPLOIEMENT_CPANEL.md)
- Vérifiez les logs : `tail -f /var/log/rss-update.log`

---

**Version** : 1.0.0
**Développé avec** : Flask 3.0, SQLAlchemy 2.0, Bootstrap 5
**Date** : Novembre 2025
