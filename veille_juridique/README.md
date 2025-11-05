# 📰 Application de Veille Juridique RSS - Python/Flask

Application web moderne et complète de veille juridique basée sur des flux RSS, développée avec **Python 3** et **Flask**.

## 🌟 Fonctionnalités

- ✅ **Agrégation de flux RSS** : Collecte automatique d'articles depuis plusieurs sources juridiques
- 🔍 **Recherche avancée** : Filtrage en temps réel par mot-clé, catégorie et source
- 📊 **Dashboard moderne** : Interface type Gmail avec design clair et professionnel
- ⚙️ **Gestion CRUD complète** : Ajout, modification et suppression de flux RSS
- 🔄 **Actualisation manuelle et automatique** : Bouton de rafraîchissement + scripts cron
- 📈 **Statistiques en temps réel** : Nombre de flux actifs et d'articles
- 🎨 **Interface responsive** : Compatible mobile, tablette et desktop
- 💾 **Base de données SQLite** : Simple, légère et sans configuration serveur

## 📋 Prérequis

- **Python** : Version 3.8 ou supérieure
- **pip** : Gestionnaire de paquets Python
- **Accès SSH** au serveur (pour configuration cron)
- **Connexion Internet** : Pour récupérer les flux RSS

## 📁 Structure du projet

```
veille_juridique/
├── app.py                      # Application Flask principale
├── config.py                   # Configuration de l'application
├── models.py                   # Modèles de base de données (SQLAlchemy)
├── requirements.txt            # Dépendances Python
├── database.db                 # Base de données SQLite (généré automatiquement)
│
├── static/                     # Fichiers statiques (CSS, JS, images)
│   ├── css/
│   │   └── style.css          # Styles personnalisés
│   ├── js/
│   │   └── app.js             # JavaScript de l'application
│   └── images/                # Images et assets
│
├── templates/                  # Templates HTML (Jinja2)
│   ├── base.html              # Template de base
│   ├── dashboard.html         # Page d'accueil (liste des articles)
│   └── feeds.html             # Gestion des flux RSS
│
├── scripts/                    # Scripts Shell
│   ├── update_feeds.sh        # Mise à jour automatique des flux
│   ├── backup_db.sh           # Sauvegarde de la base de données
│   └── deploy.sh              # Déploiement de l'application
│
├── logs/                       # Logs (créé automatiquement)
└── README.md                   # Cette documentation
```

## 🚀 Installation rapide

### Méthode 1 : Installation automatique (recommandée)

```bash
# Se connecter au serveur
ssh votre-utilisateur@dusselle.fr

# Naviguer vers le dossier web
cd /home/wrbh3411/public_html

# Cloner ou uploader le dossier veille_juridique
# (si vous avez le projet en local, utilisez scp ou git)

# Se déplacer dans le dossier
cd veille_juridique

# Rendre le script de déploiement exécutable
chmod +x scripts/deploy.sh

# Lancer le déploiement (mode développement)
./scripts/deploy.sh development
```

### Méthode 2 : Installation manuelle

```bash
# 1. Créer un environnement virtuel Python
python3 -m venv venv

# 2. Activer l'environnement virtuel
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
python app.py --init

# 5. (Optionnel) Ajouter des flux d'exemple
python app.py --sample

# 6. Lancer l'application
python app.py --host 0.0.0.0 --port 8000
```

## 📖 Utilisation

### Démarrer l'application

```bash
# Mode développement (avec debug)
./scripts/deploy.sh development

# Mode production (sans debug)
./scripts/deploy.sh production
```

L'application sera accessible sur : `http://dusselle.fr:8000`

### Gestion des flux RSS

#### 1. Ajouter un flux RSS

- Accédez à la page **"Flux RSS"** dans le menu latéral
- Cliquez sur **"Ajouter un flux"**
- Remplissez les informations :
  - **Nom** : Nom du flux (ex: "Legifrance - Actualités")
  - **URL** : URL complète du flux RSS (ex: `https://www.legifrance.gouv.fr/rss/actualites.xml`)
  - **Catégorie** : Catégorie du flux (ex: "Législation", "Jurisprudence", "Doctrine")
  - **Actif** : Cochez pour recevoir les mises à jour automatiques
- Cliquez sur **"Enregistrer"**

#### 2. Modifier un flux RSS

- Dans la page **"Flux RSS"**, cliquez sur l'icône **crayon** (✏️) à côté du flux
- Modifiez les informations souhaitées
- Cliquez sur **"Enregistrer les modifications"**

#### 3. Supprimer un flux RSS

- Dans la page **"Flux RSS"**, cliquez sur l'icône **poubelle** (🗑️) à côté du flux
- Confirmez la suppression
- ⚠️ **Attention** : Tous les articles associés seront également supprimés

### Actualiser les flux

#### Manuellement

- Cliquez sur le bouton **"Actualiser les flux"** en haut de la page
- L'application récupèrera les nouveaux articles de tous les flux actifs

#### Automatiquement (Cron)

Voir la section [Configuration du Cron](#-configuration-du-cron-mise-à-jour-automatique)

### Rechercher des articles

- Utilisez la **barre de recherche** en haut de la page d'accueil
- Tapez un mot-clé (minimum 2 caractères)
- Les résultats s'affichent en temps réel
- Vous pouvez également filtrer par **catégorie** avec le menu déroulant

## 🔧 Commandes CLI

L'application propose plusieurs commandes en ligne de commande :

```bash
# Initialiser la base de données
python app.py --init

# Mettre à jour tous les flux RSS
python app.py --update

# Ajouter des flux RSS de démonstration
python app.py --sample

# Lancer le serveur sur un port spécifique
python app.py --host 0.0.0.0 --port 5000
```

## ⏰ Configuration du Cron (Mise à jour automatique)

### 1. Rendre le script exécutable

```bash
chmod +x /home/wrbh3411/public_html/veille_juridique/scripts/update_feeds.sh
```

### 2. Éditer le script si nécessaire

Ouvrez `scripts/update_feeds.sh` et vérifiez/modifiez le chemin de l'application :

```bash
APP_DIR="/home/wrbh3411/public_html/veille_juridique"
```

### 3. Configurer le crontab

```bash
# Ouvrir la crontab
crontab -e

# Ajouter cette ligne pour une mise à jour toutes les 6 heures
0 */6 * * * /home/wrbh3411/public_html/veille_juridique/scripts/update_feeds.sh

# Exemples d'autres fréquences :
# Toutes les heures :      0 * * * *
# Toutes les 3 heures :    0 */3 * * *
# Tous les jours à 6h :    0 6 * * *
# Toutes les 30 minutes :  */30 * * * *
```

### 4. Vérifier les logs

```bash
tail -f /home/wrbh3411/public_html/veille_juridique/logs/update_feeds.log
```

## 💾 Sauvegarde de la base de données

### Sauvegarde manuelle

```bash
# Lancer le script de sauvegarde
./scripts/backup_db.sh

# Les sauvegardes sont stockées dans :
# /home/wrbh3411/backups/veille_juridique/
```

### Sauvegarde automatique (Cron)

```bash
# Ouvrir la crontab
crontab -e

# Ajouter cette ligne pour une sauvegarde quotidienne à 2h du matin
0 2 * * * /home/wrbh3411/public_html/veille_juridique/scripts/backup_db.sh
```

Les sauvegardes de plus de 30 jours sont automatiquement supprimées.

## 🔌 API REST

L'application expose une API REST pour interagir avec les données :

### Flux RSS

```bash
# Récupérer tous les flux
GET /api/feeds

# Ajouter un nouveau flux
POST /api/feeds
Content-Type: application/json
{
  "name": "Nom du flux",
  "url": "https://exemple.com/rss.xml",
  "category": "Catégorie",
  "is_active": true
}

# Modifier un flux
PUT /api/feeds/<feed_id>
Content-Type: application/json
{
  "name": "Nouveau nom",
  "category": "Nouvelle catégorie"
}

# Supprimer un flux
DELETE /api/feeds/<feed_id>
```

### Articles

```bash
# Rechercher des articles
GET /api/search?q=mot-clé
GET /api/search?category=Législation
GET /api/search?feed_id=1

# Récupérer les catégories
GET /api/categories

# Récupérer les statistiques
GET /api/stats

# Rafraîchir tous les flux
POST /api/refresh
```

## 🌐 Déploiement en production

### Option 1 : Gunicorn (recommandé)

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Ou utiliser le script de déploiement
./scripts/deploy.sh production
```

### Option 2 : Nginx + Gunicorn

1. **Installer Nginx** :
```bash
sudo apt install nginx
```

2. **Créer un fichier de configuration Nginx** :
```bash
sudo nano /etc/nginx/sites-available/veille-juridique
```

3. **Contenu du fichier** :
```nginx
server {
    listen 80;
    server_name dusselle.fr;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/wrbh3411/public_html/veille_juridique/static;
    }
}
```

4. **Activer la configuration** :
```bash
sudo ln -s /etc/nginx/sites-available/veille-juridique /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3 : Service systemd

Créer un service systemd pour démarrer automatiquement l'application :

```bash
sudo nano /etc/systemd/system/veille-juridique.service
```

Contenu :
```ini
[Unit]
Description=Veille Juridique Flask Application
After=network.target

[Service]
User=wrbh3411
WorkingDirectory=/home/wrbh3411/public_html/veille_juridique
Environment="PATH=/home/wrbh3411/public_html/veille_juridique/venv/bin"
ExecStart=/home/wrbh3411/public_html/veille_juridique/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer le service :
```bash
sudo systemctl daemon-reload
sudo systemctl start veille-juridique
sudo systemctl enable veille-juridique
sudo systemctl status veille-juridique
```

## 📊 Sources RSS juridiques recommandées

| Source | URL | Catégorie |
|--------|-----|-----------|
| Legifrance - Actualités | `https://www.legifrance.gouv.fr/rss/actualites.xml` | Législation |
| Journal Officiel (JORF) | `https://www.legifrance.gouv.fr/rss/jorf.xml` | Journal Officiel |
| Dalloz Actualité | `https://www.dalloz-actualite.fr/feed` | Doctrine |
| Village de la Justice | `https://www.village-justice.com/articles/backend.php` | Actualités juridiques |
| Doctrine.fr | `https://www.doctrine.fr/rss` | Jurisprudence |

## 🐛 Dépannage

### Erreur "ModuleNotFoundError"

```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur "Permission denied" pour les scripts

```bash
# Rendre tous les scripts exécutables
chmod +x scripts/*.sh
```

### Les flux ne se chargent pas

```bash
# Tester manuellement la mise à jour
python app.py --update

# Vérifier les logs
tail -f logs/update_feeds.log
```

### L'application ne démarre pas

```bash
# Vérifier que le port n'est pas déjà utilisé
lsof -i :8000

# Utiliser un autre port
python app.py --port 5000
```

### Base de données corrompue

```bash
# Restaurer depuis une sauvegarde
cp /home/wrbh3411/backups/veille_juridique/database_YYYYMMDD_HHMMSS.db.gz .
gunzip database_YYYYMMDD_HHMMSS.db.gz
mv database_YYYYMMDD_HHMMSS.db database.db

# Ou réinitialiser complètement
rm database.db
python app.py --init
python app.py --sample
```

## 🔒 Sécurité

### Bonnes pratiques implémentées

✅ **Requêtes préparées SQLAlchemy** : Protection contre les injections SQL
✅ **Validation des entrées** : Vérification des URL et des données
✅ **Clé secrète Flask** : Pour la sécurité des sessions
✅ **CORS** : Contrôle d'accès aux API

### Recommandations pour la production

1. **Changer la clé secrète** :
```bash
export SECRET_KEY=$(python -c 'import os; print(os.urandom(24).hex())')
```

2. **Utiliser HTTPS** avec un certificat SSL (Let's Encrypt)

3. **Limiter les accès** avec un firewall :
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

4. **Désactiver le mode debug** en production (déjà fait dans `config.py`)

## 📝 Licence

Ce projet est développé pour un usage personnel/professionnel.

## 👨‍💻 Support et Contact

Pour toute question ou problème :
- Consultez la section **Dépannage** ci-dessus
- Vérifiez les logs : `/logs/update_feeds.log`
- Testez les commandes CLI manuellement

---

**Version** : 1.0.0
**Date** : Novembre 2024
**Développé avec** : Python 3, Flask, SQLAlchemy, Bootstrap 5
**Hébergement** : dusselle.fr
