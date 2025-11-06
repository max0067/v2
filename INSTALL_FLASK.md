# 🚀 Guide d'installation - Veille Juridique RSS Flask

Guide d'installation complet pour déployer l'application Flask de veille juridique sur votre serveur.

## 📋 Prérequis système

Avant de commencer, assurez-vous d'avoir :

- **Accès SSH** au serveur
- **Python 3.8+** installé
- **MySQL 5.7+** ou **MariaDB 10.3+**
- **Droits sudo** (pour certaines opérations)
- **Git** (optionnel, pour cloner le projet)

## 🔍 Vérifier les prérequis

```bash
# Vérifier Python
python3 --version
# Devrait afficher : Python 3.8.x ou supérieur

# Vérifier pip
pip3 --version

# Vérifier MySQL
mysql --version

# Vérifier que virtualenv est disponible
python3 -m venv --help
```

Si certains outils manquent :

```bash
# Installer Python et pip (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Installer MySQL (si nécessaire)
sudo apt install mysql-server

# Sur CentOS/RHEL
sudo yum install python3 python3-pip mysql-server
```

## 📦 Installation complète étape par étape

### Étape 1 : Récupérer le projet

**Option A : Avec Git**

```bash
# Cloner le dépôt
cd /home/user
git clone <url-du-repo> v2
cd v2
```

**Option B : Upload manuel**

```bash
# Créer le répertoire
mkdir -p /home/user/v2
cd /home/user/v2

# Uploader les fichiers via SCP/FTP
# Puis décompresser si nécessaire
tar -xzf veille-rss-flask.tar.gz
```

### Étape 2 : Créer l'environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Vous devriez voir (venv) dans votre prompt
# (venv) user@server:~/v2$

# Mettre à jour pip
pip install --upgrade pip setuptools wheel
```

### Étape 3 : Installer les dépendances Python

```bash
# S'assurer d'être dans le répertoire du projet
cd /home/user/v2

# Installer toutes les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

### Étape 4 : Configurer la base de données MySQL

```bash
# Se connecter à MySQL
mysql -u root -p

# Dans MySQL, créer la base et l'utilisateur
```

```sql
-- Créer la base de données
CREATE DATABASE dusselle_rss CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer un utilisateur dédié (recommandé)
CREATE USER 'rss_user'@'localhost' IDENTIFIED BY 'mot_de_passe_securise';

-- Donner les permissions
GRANT ALL PRIVILEGES ON dusselle_rss.* TO 'rss_user'@'localhost';
FLUSH PRIVILEGES;

-- Quitter MySQL
EXIT;
```

```bash
# Importer le schéma
mysql -u rss_user -p dusselle_rss < database/schema.sql

# Vérifier que les tables sont créées
mysql -u rss_user -p dusselle_rss -e "SHOW TABLES;"
```

### Étape 5 : Configuration de l'application

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec votre éditeur préféré
nano .env
```

**Configuration minimale dans `.env` :**

```bash
# Environnement
FLASK_ENV=production
FLASK_DEBUG=False

# Sécurité - GÉNÉREZ UNE CLÉ ALÉATOIRE !
SECRET_KEY=changez-cette-cle-par-quelque-chose-de-tres-aleatoire-et-long

# Base de données
DB_HOST=localhost
DB_NAME=dusselle_rss
DB_USER=rss_user
DB_PASS=mot_de_passe_securise

# Port (optionnel)
PORT=5000
```

**Générer une clé secrète sécurisée :**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copiez le résultat dans SECRET_KEY
```

### Étape 6 : Sécuriser les fichiers

```bash
# Définir les bonnes permissions
chmod 600 .env                    # Fichier sensible
chmod 755 app/                    # Répertoire accessible
chmod 644 app/*.py                # Fichiers Python en lecture
chmod +x run.py cli.py            # Scripts exécutables

# Si vous utilisez un serveur web (recommandé)
sudo chown -R www-data:www-data /home/user/v2
# Ou pour nginx
sudo chown -R nginx:nginx /home/user/v2
```

### Étape 7 : Test de l'installation

```bash
# Activer l'environnement virtuel (si pas déjà fait)
source venv/bin/activate

# Tester le démarrage
python run.py
```

Vous devriez voir :

```
╔══════════════════════════════════════════════════════╗
║  📰 Veille Juridique RSS - Version 2.0              ║
║  🚀 Serveur de développement Flask                  ║
╚══════════════════════════════════════════════════════╝

🌐 URL: http://localhost:5000
...
```

Ouvrez un navigateur et allez sur : `http://votre-serveur:5000`

**Appuyez sur Ctrl+C pour arrêter le serveur de test.**

## 🌐 Déploiement en production

### Option 1 : Avec Gunicorn + Systemd (Recommandé)

#### A. Créer le service systemd

```bash
sudo nano /etc/systemd/system/veille-rss.service
```

Contenu du fichier :

```ini
[Unit]
Description=Veille Juridique RSS Flask Application
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/home/user/v2
Environment="PATH=/home/user/v2/venv/bin"
ExecStart=/home/user/v2/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/veille-rss-access.log \
    --error-logfile /var/log/veille-rss-error.log \
    run:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### B. Activer et démarrer le service

```bash
# Créer les fichiers de logs
sudo touch /var/log/veille-rss-access.log
sudo touch /var/log/veille-rss-error.log
sudo chown www-data:www-data /var/log/veille-rss-*.log

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable veille-rss

# Démarrer le service
sudo systemctl start veille-rss

# Vérifier le statut
sudo systemctl status veille-rss

# Voir les logs en temps réel
sudo journalctl -u veille-rss -f
```

### Option 2 : Avec Nginx en reverse proxy

#### A. Installer Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### B. Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/veille-rss
```

Configuration :

```nginx
server {
    listen 80;
    server_name dusselle.fr www.dusselle.fr;

    # Logs
    access_log /var/log/nginx/veille-rss-access.log;
    error_log /var/log/nginx/veille-rss-error.log;

    # Proxy vers Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Fichiers statiques (performance)
    location /static {
        alias /home/user/v2/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

#### C. Activer la configuration

```bash
# Créer le lien symbolique
sudo ln -s /etc/nginx/sites-available/veille-rss /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

### Option 3 : Activer HTTPS avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d dusselle.fr -d www.dusselle.fr

# Le renouvellement automatique est configuré par défaut
# Tester le renouvellement
sudo certbot renew --dry-run
```

## ⏰ Configuration des tâches automatiques (Cron)

### Créer les fichiers de logs

```bash
sudo touch /var/log/rss-update.log
sudo touch /var/log/rss-cleanup.log
sudo chown www-data:www-data /var/log/rss-*.log
```

### Configurer le cron

```bash
# Éditer la crontab de l'utilisateur www-data
sudo crontab -u www-data -e
```

Ajouter ces lignes :

```cron
# Actualiser les flux RSS toutes les 6 heures
0 */6 * * * cd /home/user/v2 && /home/user/v2/venv/bin/python cli.py refresh >> /var/log/rss-update.log 2>&1

# Nettoyer les anciens articles tous les jours à 3h du matin
0 3 * * * cd /home/user/v2 && /home/user/v2/venv/bin/python cli.py cleanup 90 >> /var/log/rss-cleanup.log 2>&1

# Afficher les stats tous les lundis à 9h (optionnel)
0 9 * * 1 cd /home/user/v2 && /home/user/v2/venv/bin/python cli.py stats >> /var/log/rss-stats.log 2>&1
```

### Tester les commandes manuellement

```bash
# Tester la mise à jour
sudo -u www-data /home/user/v2/venv/bin/python /home/user/v2/cli.py refresh

# Tester le nettoyage
sudo -u www-data /home/user/v2/venv/bin/python /home/user/v2/cli.py cleanup 90

# Voir les stats
sudo -u www-data /home/user/v2/venv/bin/python /home/user/v2/cli.py stats
```

## ✅ Vérification finale

### Checklist de déploiement

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Toutes les dépendances installées
- [ ] Base de données MySQL créée et configurée
- [ ] Fichier `.env` configuré avec des valeurs sécurisées
- [ ] Permissions des fichiers correctes
- [ ] Service systemd configuré et démarré
- [ ] Nginx configuré (si utilisé)
- [ ] HTTPS activé (recommandé)
- [ ] Tâches cron configurées
- [ ] Application accessible depuis un navigateur

### Commandes utiles pour le monitoring

```bash
# Statut du service
sudo systemctl status veille-rss

# Logs en temps réel
sudo journalctl -u veille-rss -f

# Logs Nginx
sudo tail -f /var/log/nginx/veille-rss-error.log

# Logs de l'application
sudo tail -f /var/log/veille-rss-error.log

# Logs des cron
sudo tail -f /var/log/rss-update.log
```

## 🔄 Mise à jour de l'application

```bash
# Se connecter au serveur
ssh user@dusselle.fr

# Aller dans le répertoire
cd /home/user/v2

# Activer l'environnement virtuel
source venv/bin/activate

# Récupérer les mises à jour (si Git)
git pull

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Appliquer les migrations (si nécessaire)
flask db upgrade

# Redémarrer le service
sudo systemctl restart veille-rss
```

## 🐛 Dépannage

### Le service ne démarre pas

```bash
# Voir les logs détaillés
sudo journalctl -u veille-rss -n 50

# Vérifier la syntaxe du fichier service
sudo systemctl daemon-reload
sudo systemctl status veille-rss
```

### Erreur de connexion MySQL

```bash
# Tester la connexion
mysql -u rss_user -p dusselle_rss

# Vérifier les variables dans .env
cat .env | grep DB_
```

### Nginx renvoie une erreur 502

```bash
# Vérifier que Gunicorn tourne
sudo systemctl status veille-rss

# Vérifier que le port 5000 est bien écouté
sudo netstat -tulpn | grep 5000

# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/veille-rss-error.log
```

---

**🎉 Félicitations ! Votre application de veille juridique est maintenant déployée.**

Pour toute question ou problème, consultez les logs ou la documentation complète dans `README_FLASK.md`.
