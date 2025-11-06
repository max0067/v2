# 📰 Veille Juridique RSS - Version Flask

Application web moderne de veille juridique basée sur des flux RSS, développée avec **Python Flask** et **SQLAlchemy**.

## 🌟 Caractéristiques

- ✅ **Architecture Flask moderne** : Factory pattern, Blueprints, SQLAlchemy ORM
- 🔄 **Agrégation RSS automatique** : Récupération depuis plusieurs sources juridiques
- 🔍 **Recherche en temps réel** : Filtrage instantané par mot-clé
- 📊 **API RESTful** : Endpoints JSON pour toutes les opérations
- 🎨 **Interface responsive** : Design moderne avec Bootstrap 5
- ⚙️ **CRUD complet** : Gestion complète des flux RSS
- ⏰ **Tâches planifiées** : Script CLI pour actualisation automatique via cron
- 🔒 **Sécurité renforcée** : ORM pour éviter les injections SQL, validation des données

## 📋 Prérequis

### Serveur
- **Python** : Version 3.8 ou supérieure
- **MySQL** : Version 5.7 ou supérieure (ou MariaDB 10.3+)
- **pip** : Gestionnaire de packages Python
- **virtualenv** : Pour l'environnement virtuel (recommandé)

### Extensions Python
Toutes les dépendances sont listées dans `requirements.txt` :
- Flask 3.0+
- SQLAlchemy
- PyMySQL
- feedparser
- etc.

## 📁 Structure du projet

```
v2/
├── app/
│   ├── __init__.py              # Factory Flask
│   ├── models.py                # Modèles SQLAlchemy
│   ├── routes/
│   │   ├── main.py              # Routes web
│   │   └── api.py               # Routes API
│   ├── templates/               # Templates Jinja2
│   │   ├── base.html
│   │   ├── index.html
│   │   └── manage_feeds.html
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── utils/
│       └── rss_parser.py        # Parser RSS
├── database/
│   └── schema.sql               # Schéma BDD
├── config.py                    # Configuration
├── run.py                       # Point d'entrée
├── cli.py                       # Script CLI/cron
├── requirements.txt             # Dépendances Python
├── .env.example                 # Exemple de configuration
└── README_FLASK.md
```

## 🚀 Installation

### Étape 1 : Préparer l'environnement

```bash
# Se connecter au serveur
ssh votre-utilisateur@dusselle.fr

# Aller dans le répertoire du projet
cd /home/user/v2

# Créer un environnement virtuel Python
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip
```

### Étape 2 : Installer les dépendances

```bash
# Installer toutes les dépendances
pip install -r requirements.txt
```

### Étape 3 : Configurer l'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env
nano .env
```

Configurez vos paramètres dans `.env` :

```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=votre-cle-secrete-aleatoire-tres-longue
DB_HOST=localhost
DB_NAME=dusselle_rss
DB_USER=votre_utilisateur_mysql
DB_PASS=votre_mot_de_passe_mysql
```

### Étape 4 : Créer la base de données

**Option A : Avec le schéma SQL**

```bash
# Se connecter à MySQL
mysql -u root -p

# Exécuter le schéma
source database/schema.sql

# Ou en une ligne
mysql -u root -p < database/schema.sql
```

**Option B : Avec Flask-Migrate** (recommandé pour le développement)

```bash
# Initialiser les migrations
flask db init

# Créer une migration
flask db migrate -m "Initial migration"

# Appliquer les migrations
flask db upgrade
```

### Étape 5 : Tester l'application

```bash
# Lancer le serveur de développement
python run.py

# Ou avec Flask CLI
flask run --host=0.0.0.0 --port=5000
```

Accédez à : `http://localhost:5000`

## 🔧 Déploiement en production

### Avec Gunicorn (recommandé)

```bash
# Installer Gunicorn (déjà dans requirements.txt)
pip install gunicorn

# Lancer avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Avec logs
gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile /var/log/gunicorn-access.log \
  --error-logfile /var/log/gunicorn-error.log \
  run:app
```

### Service systemd

Créer `/etc/systemd/system/veille-rss.service` :

```ini
[Unit]
Description=Veille Juridique RSS Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/user/v2
Environment="PATH=/home/user/v2/venv/bin"
ExecStart=/home/user/v2/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

Puis :

```bash
sudo systemctl daemon-reload
sudo systemctl enable veille-rss
sudo systemctl start veille-rss
sudo systemctl status veille-rss
```

### Configuration Nginx

```nginx
server {
    listen 80;
    server_name dusselle.fr;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/user/v2/app/static;
        expires 30d;
    }
}
```

## ⏰ Configuration des tâches automatiques (Cron)

```bash
# Éditer la crontab
crontab -e

# Actualiser les flux toutes les 6 heures
0 */6 * * * cd /home/user/v2 && /home/user/v2/venv/bin/python cli.py refresh >> /var/log/rss-update.log 2>&1

# Nettoyer les anciens articles tous les jours à 3h
0 3 * * * cd /home/user/v2 && /home/user/v2/venv/bin/python cli.py cleanup 90 >> /var/log/rss-cleanup.log 2>&1
```

### Commandes CLI disponibles

```bash
# Actualiser tous les flux
python cli.py refresh

# Nettoyer les articles de plus de 90 jours
python cli.py cleanup 90

# Afficher les statistiques
python cli.py stats
```

## 📖 Utilisation de l'API

### Récupérer les flux

```bash
curl http://localhost:5000/api/feeds
```

### Ajouter un flux

```bash
curl -X POST http://localhost:5000/api/feeds \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouveau flux",
    "url": "https://example.com/feed.xml",
    "category": "Législation"
  }'
```

### Actualiser tous les flux

```bash
curl -X POST http://localhost:5000/api/feeds/refresh
```

### Rechercher des articles

```bash
curl http://localhost:5000/api/articles/search?q=juridique
```

Pour plus de détails, consultez `API.md`.

## 🔒 Sécurité

### Recommandations pour la production

1. **Changez la clé secrète** dans `.env`
2. **Désactivez le mode debug** : `FLASK_DEBUG=False`
3. **Utilisez HTTPS** avec Let's Encrypt
4. **Limitez les permissions** des fichiers :

```bash
chmod 600 .env
chmod 755 app/
chmod 644 app/*.py
```

5. **Configurez un firewall** (UFW, iptables)
6. **Sauvegardez régulièrement** la base de données

## 🛠️ Développement

### Lancer en mode développement

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### Tests

```bash
# Installer pytest (si nécessaire)
pip install pytest pytest-cov

# Lancer les tests
pytest

# Avec couverture
pytest --cov=app tests/
```

### Migrations de base de données

```bash
# Créer une nouvelle migration
flask db migrate -m "Description du changement"

# Appliquer les migrations
flask db upgrade

# Revenir en arrière
flask db downgrade
```

## 📊 Sources RSS recommandées

| Source | URL | Catégorie |
|--------|-----|-----------|
| Legifrance - Actualités | https://www.legifrance.gouv.fr/rss/actualites.xml | Législation |
| Journal Officiel (JORF) | https://www.legifrance.gouv.fr/rss/jorf.xml | Journal Officiel |
| Dalloz Actualité | https://www.dalloz-actualite.fr/feed | Doctrine |
| Conseil d'État | https://www.conseil-etat.fr/rss | Jurisprudence |

## 🐛 Dépannage

### Erreur de connexion à la base de données

```bash
# Vérifier les identifiants dans .env
cat .env | grep DB_

# Tester la connexion MySQL
mysql -u $DB_USER -p$DB_PASS -h $DB_HOST $DB_NAME
```

### Erreur "Module not found"

```bash
# Vérifier que l'environnement virtuel est activé
which python
# Devrait afficher: /home/user/v2/venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Les flux ne se mettent pas à jour

```bash
# Tester manuellement
python cli.py refresh

# Vérifier les logs
tail -f /var/log/rss-update.log
```

## 📝 Licence

Ce projet est développé pour un usage personnel/professionnel.

## 👨‍💻 Support

Pour toute question :
- Consultez la documentation
- Vérifiez les logs : `/var/log/rss-*.log`
- Testez en mode debug

---

**Version** : 2.0.0 (Flask)
**Date** : Novembre 2024
**Technologies** : Python 3.8+, Flask 3.0, SQLAlchemy, MySQL, Bootstrap 5
