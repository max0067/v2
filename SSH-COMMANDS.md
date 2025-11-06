# 🔐 Commandes SSH pour dusselle.fr

Ce fichier contient toutes les commandes SSH essentielles pour déployer et gérer l'application.

---

## 🔌 Connexion au serveur

### Connexion standard

```bash
ssh votre-utilisateur@dusselle.fr
```

### Connexion avec port personnalisé

```bash
ssh -p 2222 votre-utilisateur@dusselle.fr
```

### Connexion avec clé SSH

```bash
ssh -i ~/.ssh/id_rsa votre-utilisateur@dusselle.fr
```

### Se souvenir du mot de passe (éviter de le retaper)

```bash
ssh-copy-id votre-utilisateur@dusselle.fr
```

---

## 📂 Navigation et préparation

### Aller dans le dossier web

```bash
# Dossier standard
cd /home/votre-utilisateur/public_html

# OU selon l'hébergement
cd /var/www/html
cd /var/www/dusselle.fr
cd ~/public_html
```

### Vérifier où vous êtes

```bash
pwd
```

### Lister les fichiers

```bash
ls -la
```

---

## 💾 Sauvegarde

### Créer une sauvegarde complète

```bash
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz * 2>/dev/null
```

### Vérifier la sauvegarde

```bash
ls -lh backup_*.tar.gz
```

### Restaurer une sauvegarde

```bash
tar -xzf backup_20241106_143000.tar.gz
```

---

## 🚀 Déploiement rapide (RECOMMANDÉ)

### Méthode automatique

```bash
# Une seule commande pour tout installer !
chmod +x deploy-dusselle.sh && ./deploy-dusselle.sh
```

---

## ⚙️ Configuration manuelle

### Copier le fichier de configuration

```bash
cp config/config.example.php config/config.php
```

### Éditer la configuration

```bash
nano config/config.php
# OU
vi config/config.php
```

**Dans nano :**
- `Ctrl + O` puis `Entrée` : Sauvegarder
- `Ctrl + X` : Quitter

**Dans vi :**
- Appuyez sur `i` : Mode insertion
- `Esc` puis `:wq` : Sauvegarder et quitter
- `Esc` puis `:q!` : Quitter sans sauvegarder

---

## 🗄️ Commandes MySQL

### Se connecter à MySQL

```bash
mysql -u root -p
```

### Créer la base de données

```sql
CREATE DATABASE IF NOT EXISTS dusselle_rss
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER 'dusselle_user'@'localhost' IDENTIFIED BY 'MotDePasseSecurise123!';
GRANT ALL PRIVILEGES ON dusselle_rss.* TO 'dusselle_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Importer le schéma SQL

```bash
mysql -u root -p dusselle_rss < database/schema.sql
```

### Vérifier les tables créées

```bash
mysql -u root -p -e "USE dusselle_rss; SHOW TABLES;"
```

### Voir les flux RSS dans la BDD

```bash
mysql -u root -p -e "USE dusselle_rss; SELECT * FROM rss_feeds;"
```

### Voir les articles

```bash
mysql -u root -p -e "USE dusselle_rss; SELECT COUNT(*) as total FROM articles;"
```

---

## 🔒 Permissions

### Configurer les permissions

```bash
chmod -R 755 .
chmod 644 config/config.php
chmod +x cron/update-feeds.php
chmod +x deploy-dusselle.sh
chmod +x install.sh
```

### Changer le propriétaire (si nécessaire)

```bash
# Si vous avez les droits sudo
sudo chown -R www-data:www-data .

# OU
sudo chown -R apache:apache .

# OU pour votre utilisateur
chown -R $(whoami):$(whoami) .
```

---

## 🧪 Tests

### Tester la connexion à la base de données

```bash
php -r "require 'config/config.php'; require 'src/Database.php'; Database::getInstance(); echo 'Connexion OK\n';"
```

### Tester le script de mise à jour RSS

```bash
php cron/update-feeds.php
```

### Tester un flux RSS spécifique

```bash
php -r "echo file_get_contents('https://www.legifrance.gouv.fr/rss/jorf.xml');" | head -50
```

### Vérifier la version de PHP

```bash
php -v
```

### Vérifier les extensions PHP

```bash
php -m | grep -E "(pdo_mysql|simplexml|libxml|curl)"
```

### Vérifier allow_url_fopen

```bash
php -i | grep allow_url_fopen
```

---

## ⏰ Configuration CRON

### Ouvrir la crontab

```bash
crontab -e
```

### Ajouter la ligne de mise à jour (toutes les 6 heures)

```bash
0 */6 * * * /usr/bin/php /home/votre-utilisateur/public_html/cron/update-feeds.php >> /var/log/rss-update.log 2>&1
```

### Autres fréquences possibles

```bash
# Toutes les heures
0 * * * * /usr/bin/php /chemin/vers/cron/update-feeds.php >> /var/log/rss-update.log 2>&1

# Toutes les 3 heures
0 */3 * * * /usr/bin/php /chemin/vers/cron/update-feeds.php >> /var/log/rss-update.log 2>&1

# Tous les jours à 6h du matin
0 6 * * * /usr/bin/php /chemin/vers/cron/update-feeds.php >> /var/log/rss-update.log 2>&1

# Toutes les 30 minutes
*/30 * * * * /usr/bin/php /chemin/vers/cron/update-feeds.php >> /var/log/rss-update.log 2>&1
```

### Lister les cron jobs actifs

```bash
crontab -l
```

### Supprimer tous les cron jobs

```bash
crontab -r
```

---

## 📊 Logs et surveillance

### Voir les logs Apache

```bash
# Erreurs
tail -f /var/log/apache2/error.log

# Accès
tail -f /var/log/apache2/access.log
```

### Voir les logs du cron RSS

```bash
tail -f /var/log/rss-update.log
```

### Voir les logs MySQL

```bash
sudo tail -f /var/log/mysql/error.log
```

### Surveiller l'utilisation du disque

```bash
df -h
```

### Surveiller l'utilisation de la RAM

```bash
free -h
```

---

## 🌐 Apache / Serveur Web

### Redémarrer Apache

```bash
# Ubuntu/Debian
sudo systemctl restart apache2

# CentOS/RHEL
sudo systemctl restart httpd
```

### Vérifier le statut d'Apache

```bash
sudo systemctl status apache2
```

### Tester la configuration Apache

```bash
sudo apache2ctl configtest
```

### Activer mod_rewrite (si nécessaire)

```bash
sudo a2enmod rewrite
sudo systemctl restart apache2
```

---

## 🔄 Mise à jour de l'application

### Mettre à jour depuis Git

```bash
# Sauvegarder la config actuelle
cp config/config.php /tmp/config.php.backup

# Tirer les dernières modifications
git pull origin main

# Restaurer la config
cp /tmp/config.php.backup config/config.php

# Mettre à jour la BDD si nécessaire
mysql -u root -p dusselle_rss < database/schema.sql
```

### Mise à jour manuelle des flux

```bash
php cron/update-feeds.php
```

---

## 🧹 Maintenance

### Nettoyer les anciens articles (90+ jours)

Le script cron le fait automatiquement, mais pour forcer :

```bash
mysql -u root -p -e "USE dusselle_rss; DELETE FROM articles WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);"
```

### Optimiser les tables MySQL

```bash
mysql -u root -p -e "USE dusselle_rss; OPTIMIZE TABLE articles, rss_feeds;"
```

### Sauvegarder la base de données

```bash
# Sauvegarde complète
mysqldump -u root -p dusselle_rss > backup_rss_$(date +%Y%m%d).sql

# Sauvegarde avec compression
mysqldump -u root -p dusselle_rss | gzip > backup_rss_$(date +%Y%m%d).sql.gz
```

### Restaurer une sauvegarde de BDD

```bash
mysql -u root -p dusselle_rss < backup_rss_20241106.sql

# OU avec compression
gunzip < backup_rss_20241106.sql.gz | mysql -u root -p dusselle_rss
```

---

## 🐛 Dépannage

### Vérifier si MySQL tourne

```bash
sudo systemctl status mysql
# OU
sudo systemctl status mariadb
```

### Redémarrer MySQL

```bash
sudo systemctl restart mysql
```

### Vérifier si Apache tourne

```bash
sudo systemctl status apache2
```

### Voir les processus PHP

```bash
ps aux | grep php
```

### Tuer un processus PHP bloqué

```bash
# Trouver le PID
ps aux | grep php

# Tuer le processus
kill -9 PID
```

### Vider le cache DNS (si le site ne charge pas)

```bash
# Sur votre machine locale (pas sur le serveur)
# Windows
ipconfig /flushdns

# macOS
sudo dscacheutil -flushcache

# Linux
sudo systemd-resolve --flush-caches
```

---

## 📤 Transfert de fichiers

### Uploader un fichier depuis votre machine locale

```bash
scp /chemin/local/fichier.php votre-utilisateur@dusselle.fr:/home/votre-utilisateur/public_html/
```

### Uploader un dossier entier

```bash
scp -r /chemin/local/dossier votre-utilisateur@dusselle.fr:/home/votre-utilisateur/public_html/
```

### Télécharger un fichier du serveur

```bash
scp votre-utilisateur@dusselle.fr:/home/votre-utilisateur/public_html/config/config.php /chemin/local/
```

### Synchroniser avec rsync

```bash
rsync -avz /chemin/local/ votre-utilisateur@dusselle.fr:/home/votre-utilisateur/public_html/
```

---

## ✅ Checklist de vérification rapide

```bash
# Exécutez ces commandes pour vérifier que tout fonctionne

echo "1. Test PHP"
php -v

echo "2. Test MySQL"
mysql -u root -p -e "SELECT 1;"

echo "3. Test connexion BDD"
php -r "require 'config/config.php'; require 'src/Database.php'; Database::getInstance(); echo 'OK\n';"

echo "4. Test script cron"
php cron/update-feeds.php

echo "5. Vérifier les permissions"
ls -la config/config.php

echo "6. Vérifier Apache"
systemctl status apache2

echo "✅ Tous les tests passés !"
```

---

## 🔗 Liens utiles

- **Application** : https://dusselle.fr/
- **Gestion des flux** : https://dusselle.fr/manage-feeds.php
- **Documentation complète** : README.md
- **Guide de déploiement** : DEPLOY-DUSSELLE.md
- **Démarrage rapide** : QUICKSTART.md

---

## 💡 Astuces

### Créer un alias SSH

Dans votre fichier `~/.ssh/config` (sur votre machine locale) :

```
Host dusselle
    HostName dusselle.fr
    User votre-utilisateur
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

Puis connectez-vous simplement avec :

```bash
ssh dusselle
```

### Utiliser tmux pour les longues opérations

```bash
# Créer une session
tmux new -s deploy

# Détacher : Ctrl+B puis D
# Réattacher
tmux attach -t deploy
```

---

**Version** : 1.0.0
**Application** : Veille Juridique RSS
**Domaine** : dusselle.fr
