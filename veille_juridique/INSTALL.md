# 🚀 Guide d'installation - Veille Juridique Flask

Guide complet d'installation de l'application de veille juridique sur le serveur dusselle.fr.

## 📋 Prérequis système

Avant de commencer, assurez-vous que votre serveur dispose de :

- **Python 3.8+** : `python3 --version`
- **pip** : `pip3 --version`
- **venv** : `python3 -m venv --help`
- **Accès SSH** au serveur
- **Minimum 100 Mo d'espace disque libre**

## 🔧 Installation étape par étape

### Étape 1 : Connexion au serveur

```bash
ssh wrbh3411@dusselle.fr
# Entrez votre mot de passe
```

### Étape 2 : Navigation vers le dossier web

```bash
cd /home/wrbh3411/public_html
```

### Étape 3 : Upload des fichiers

**Option A : Via Git (recommandé)**

```bash
git clone <votre-repo-url> veille_juridique
cd veille_juridique
```

**Option B : Via SCP depuis votre machine locale**

```bash
# Sur votre machine locale
scp -r veille_juridique/ wrbh3411@dusselle.fr:/home/wrbh3411/public_html/
```

**Option C : Via FTP**

Utilisez FileZilla ou un autre client FTP pour uploader le dossier `veille_juridique/`.

### Étape 4 : Création de l'environnement virtuel Python

```bash
cd /home/wrbh3411/public_html/veille_juridique

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Vous devriez voir (venv) au début de votre prompt
```

### Étape 5 : Installation des dépendances Python

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

Vous devriez voir :
- Flask
- Flask-SQLAlchemy
- feedparser
- python-dateutil
- Werkzeug
- SQLAlchemy

### Étape 6 : Initialisation de la base de données

```bash
# Initialiser la base de données SQLite
python app.py --init

# Vous devriez voir : "✓ Base de données initialisée avec succès"
```

### Étape 7 : Ajouter des flux RSS de démonstration (optionnel)

```bash
python app.py --sample

# Cela ajoutera 3 flux juridiques français :
# - Legifrance - Actualités
# - Journal Officiel (JORF)
# - Dalloz Actualité
```

### Étape 8 : Tester le serveur de développement

```bash
python app.py --host 0.0.0.0 --port 8000
```

Ouvrez votre navigateur et accédez à : `http://dusselle.fr:8000`

Vous devriez voir l'interface de l'application.

Pour arrêter le serveur : `Ctrl+C`

## 🎯 Installation en production

### Option 1 : Utiliser le script de déploiement automatique

```bash
# Rendre le script exécutable
chmod +x scripts/deploy.sh

# Lancer le déploiement en mode production
./scripts/deploy.sh production
```

### Option 2 : Utiliser Gunicorn (recommandé)

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer avec Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Option 3 : Créer un service systemd

Pour que l'application démarre automatiquement au boot :

```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/veille-juridique.service
```

Copiez ce contenu :

```ini
[Unit]
Description=Veille Juridique Flask Application
After=network.target

[Service]
User=wrbh3411
WorkingDirectory=/home/wrbh3411/public_html/veille_juridique
Environment="PATH=/home/wrbh3411/public_html/veille_juridique/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/home/wrbh3411/public_html/veille_juridique/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activez le service :

```bash
sudo systemctl daemon-reload
sudo systemctl start veille-juridique
sudo systemctl enable veille-juridique
sudo systemctl status veille-juridique
```

Commandes utiles :

```bash
# Voir les logs
sudo journalctl -u veille-juridique -f

# Redémarrer le service
sudo systemctl restart veille-juridique

# Arrêter le service
sudo systemctl stop veille-juridique
```

## 🔄 Configuration de la mise à jour automatique (Cron)

### 1. Éditer le script de mise à jour

```bash
nano scripts/update_feeds.sh
```

Vérifiez que le chemin est correct :

```bash
APP_DIR="/home/wrbh3411/public_html/veille_juridique"
```

### 2. Rendre le script exécutable

```bash
chmod +x scripts/update_feeds.sh
```

### 3. Tester le script manuellement

```bash
./scripts/update_feeds.sh
```

### 4. Ajouter au crontab

```bash
crontab -e
```

Ajoutez cette ligne pour une mise à jour toutes les 6 heures :

```cron
0 */6 * * * /home/wrbh3411/public_html/veille_juridique/scripts/update_feeds.sh
```

Autres exemples de fréquence :

```cron
# Toutes les heures
0 * * * * /home/wrbh3411/public_html/veille_juridique/scripts/update_feeds.sh

# Toutes les 3 heures
0 */3 * * * /home/wrbh3411/public_html/veille_juridique/scripts/update_feeds.sh

# Tous les jours à 6h du matin
0 6 * * * /home/wrbh3411/public_html/veille_juridique/scripts/update_feeds.sh

# Toutes les 30 minutes
*/30 * * * * /home/wrbh3411/public_html/veille_juridique/scripts/update_feeds.sh
```

### 5. Vérifier que le cron fonctionne

```bash
# Voir les logs de mise à jour
tail -f /home/wrbh3411/public_html/veille_juridique/logs/update_feeds.log
```

## 💾 Configuration de la sauvegarde automatique

```bash
# Rendre le script exécutable
chmod +x scripts/backup_db.sh

# Tester manuellement
./scripts/backup_db.sh

# Ajouter au crontab pour une sauvegarde quotidienne à 2h du matin
crontab -e
```

Ajoutez :

```cron
0 2 * * * /home/wrbh3411/public_html/veille_juridique/scripts/backup_db.sh
```

## 🌐 Configuration avec Nginx (reverse proxy)

Si vous souhaitez utiliser Nginx comme reverse proxy :

### 1. Installer Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Créer la configuration

```bash
sudo nano /etc/nginx/sites-available/veille-juridique
```

Contenu :

```nginx
server {
    listen 80;
    server_name dusselle.fr;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/wrbh3411/public_html/veille_juridique/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Activer la configuration

```bash
sudo ln -s /etc/nginx/sites-available/veille-juridique /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. (Optionnel) Configurer SSL avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dusselle.fr
```

## ✅ Vérification de l'installation

### Test 1 : Vérifier que Python fonctionne

```bash
cd /home/wrbh3411/public_html/veille_juridique
source venv/bin/activate
python --version
```

### Test 2 : Vérifier les dépendances

```bash
pip list | grep -E "(Flask|SQLAlchemy|feedparser)"
```

### Test 3 : Vérifier la base de données

```bash
ls -lh database.db
```

### Test 4 : Lancer une mise à jour manuelle

```bash
python app.py --update
```

### Test 5 : Vérifier l'application web

Accédez à `http://dusselle.fr:8000` dans votre navigateur.

Vous devriez voir :
- La page d'accueil avec les articles
- Le menu latéral avec "Tableau de bord" et "Flux RSS"
- Le bouton "Actualiser les flux"

## 🐛 Résolution des problèmes courants

### Problème : "ModuleNotFoundError: No module named 'flask'"

**Solution** :

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problème : "Permission denied" sur les scripts

**Solution** :

```bash
chmod +x scripts/*.sh
```

### Problème : L'application ne démarre pas

**Solution** :

```bash
# Vérifier les erreurs
python app.py

# Vérifier que le port n'est pas utilisé
lsof -i :8000

# Essayer un autre port
python app.py --port 5000
```

### Problème : Les flux RSS ne se chargent pas

**Solution** :

```bash
# Vérifier la connexion Internet
curl -I https://www.legifrance.gouv.fr

# Tester manuellement
python app.py --update
```

### Problème : Erreur de base de données

**Solution** :

```bash
# Supprimer et recréer la base de données
rm database.db
python app.py --init
python app.py --sample
```

## 📊 Après l'installation

1. **Ajouter vos propres flux RSS** dans l'interface web
2. **Configurer le cron** pour les mises à jour automatiques
3. **Configurer les sauvegardes** automatiques
4. **Personnaliser** l'application selon vos besoins

## 🎉 Installation terminée !

Votre application de veille juridique est maintenant opérationnelle.

Accédez à : `http://dusselle.fr:8000`

Pour toute question, consultez le fichier `README.md`.
