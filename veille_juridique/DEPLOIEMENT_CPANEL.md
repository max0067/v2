# 🚀 Guide de déploiement - Application Veille Juridique Flask

## 📋 Prérequis

- Accès cPanel à votre serveur dusselle.fr
- Python 3.8+ installé sur le serveur
- Accès SSH (optionnel mais recommandé)

---

## 🔧 Option 1 : Déploiement via cPanel Python App

### Étape 1 : Configurer l'application Python dans cPanel

1. **Connectez-vous à cPanel** sur dusselle.fr
2. Allez dans **"Setup Python App"** ou **"Python Selector"**
3. Cliquez sur **"Create Application"**

### Étape 2 : Configuration de l'application

Remplissez les champs suivants :

```
Python version: 3.8 ou supérieur
Application root: veille_juridique
Application URL: / (ou /veille si vous voulez un sous-répertoire)
Application startup file: wsgi.py
Application Entry point: application
```

### Étape 3 : Télécharger les fichiers

1. Via **File Manager** dans cPanel :
   - Uploadez tous les fichiers du dossier `veille_juridique/` dans le répertoire de l'application

2. OU via **FTP/SFTP** :
   - Connectez-vous à votre serveur
   - Téléversez les fichiers dans le bon répertoire

### Étape 4 : Installer les dépendances

Dans cPanel, section **"Python App"** :

1. Cliquez sur votre application
2. Cliquez sur **"Run pip install"**
3. Entrez : `Flask Flask-SQLAlchemy feedparser python-dateutil gunicorn`
4. OU uploadez le fichier `requirements.txt` et cliquez sur **"Install dependencies"**

### Étape 5 : Initialiser la base de données

Via **Terminal** dans cPanel (ou SSH) :

```bash
cd ~/veille_juridique
python app.py --init
python app.py --sample
```

### Étape 6 : Démarrer l'application

Dans cPanel **"Python App"** :
- Cliquez sur **"Restart"** ou **"Start"**
- L'application devrait maintenant être accessible sur dusselle.fr

---

## 🔧 Option 2 : Déploiement via Passenger (Phusion Passenger)

Si votre hébergement utilise Passenger (commun avec cPanel) :

### Créer passenger_wsgi.py à la racine web

```bash
cd ~/public_html
nano passenger_wsgi.py
```

Contenu :

```python
import sys
import os

# Ajouter le chemin de l'application
INTERP = "/home/VOTRE_USER/virtualenv/veille_juridique/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, '/home/VOTRE_USER/veille_juridique')

from wsgi import application
```

### Configurer .htaccess

```apache
# .htaccess dans public_html/
PassengerEnabled On
PassengerAppRoot /home/VOTRE_USER/veille_juridique
```

---

## 🔧 Option 3 : Déploiement manuel via Gunicorn + Nginx/Apache Reverse Proxy

### Étape 1 : Installation des dépendances

```bash
cd ~/veille_juridique
pip3 install --user -r requirements.txt
```

### Étape 2 : Initialiser la base de données

```bash
python3 app.py --init
python3 app.py --sample
```

### Étape 3 : Démarrer avec Gunicorn

```bash
chmod +x start.sh
./start.sh
```

OU manuellement :

```bash
gunicorn --config gunicorn_config.py wsgi:application
```

### Étape 4 : Configurer le reverse proxy

**Pour Apache** (créer un fichier .htaccess dans public_html/) :

```apache
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/veille
RewriteRule ^(.*)$ http://localhost:8000/$1 [P,L]
```

**Pour Nginx** (dans la config du site) :

```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## ⚙️ Configuration du CRON (Mise à jour automatique)

Dans cPanel, section **"Cron Jobs"** :

```bash
# Actualiser les flux toutes les 6 heures
0 */6 * * * cd ~/veille_juridique && python3 app.py --update >> ~/logs/rss-update.log 2>&1

# OU toutes les heures
0 * * * * cd ~/veille_juridique && python3 app.py --update >> ~/logs/rss-update.log 2>&1
```

---

## 🔐 Sécurité pour la production

### 1. Configurer une clé secrète forte

Modifiez `config.py` :

```python
import os
import secrets

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
```

### 2. Définir la variable d'environnement

```bash
export FLASK_ENV=production
export SECRET_KEY="votre_cle_secrete_tres_longue_et_aleatoire"
```

### 3. Désactiver le mode debug

Dans `app.py`, s'assurer que :

```python
app.run(debug=False)  # En production
```

---

## 🔍 Dépannage

### L'application ne démarre pas

```bash
# Vérifier les logs
tail -f ~/logs/rss-update.log

# Vérifier si Gunicorn tourne
ps aux | grep gunicorn

# Vérifier les permissions
chmod 755 ~/veille_juridique
chmod 644 ~/veille_juridique/*.py
```

### Erreur "Module not found"

```bash
# Réinstaller les dépendances
pip3 install --user -r requirements.txt --force-reinstall
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
python3 app.py --init
python3 app.py --sample
```

---

## 📊 Maintenance

### Sauvegarde de la base de données

```bash
# Sauvegarde manuelle
cp ~/veille_juridique/database.db ~/backups/database_$(date +%Y%m%d).db

# Automatique via cron (tous les jours à 2h)
0 2 * * * cp ~/veille_juridique/database.db ~/backups/database_$(date +\%Y\%m\%d).db
```

### Mise à jour de l'application

```bash
cd ~/veille_juridique
git pull  # Si vous utilisez Git
pip3 install --user -r requirements.txt --upgrade
pkill gunicorn
./start.sh
```

---

## 📞 Support

**URLs importantes** :
- Application : https://dusselle.fr/
- Gestion des flux : https://dusselle.fr/feeds
- API : https://dusselle.fr/api/stats

**Fichiers de logs** :
- Application : `~/logs/rss-update.log`
- Gunicorn : Voir stdout/stderr
- Apache : `/var/log/apache2/error.log`

---

## ✅ Checklist de déploiement

- [ ] Python 3.8+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Base de données initialisée (`python app.py --init`)
- [ ] Flux d'exemple ajoutés (`python app.py --sample`)
- [ ] Application démarrée (Gunicorn ou cPanel)
- [ ] Reverse proxy configuré (si nécessaire)
- [ ] Cron configuré pour mise à jour automatique
- [ ] Variables d'environnement configurées (FLASK_ENV, SECRET_KEY)
- [ ] Tests effectués (accès web, API, actualisation)
- [ ] Sauvegarde configurée

---

**Version** : 1.0.0
**Dernière mise à jour** : Novembre 2025
