# 🚀 Guide de déploiement pour dusselle.fr

Ce guide vous explique comment démarrer l'application de veille juridique RSS sur votre serveur dusselle.fr.

---

## 📋 Prérequis du serveur

Avant de commencer, assurez-vous que votre serveur dispose de :

- ✅ **PHP 8.0+** installé
- ✅ **MySQL 5.7+** ou MariaDB
- ✅ **Apache** avec mod_rewrite activé
- ✅ **Accès SSH** au serveur
- ✅ **Extensions PHP** : pdo_mysql, simplexml, libxml, curl

---

## 🔧 Étape 1 : Connexion au serveur

### Option A : Connexion SSH classique

```bash
# Remplacez "votre-utilisateur" par votre nom d'utilisateur
ssh votre-utilisateur@dusselle.fr

# OU si vous utilisez un port SSH personnalisé
ssh -p 2222 votre-utilisateur@dusselle.fr
```

### Option B : Si vous avez un accès cPanel/FTP

1. Connectez-vous à votre cPanel
2. Utilisez le "Terminal" intégré
3. OU utilisez FileZilla/WinSCP pour transférer les fichiers

---

## 📦 Étape 2 : Préparer l'environnement

### 2.1 Naviguer vers le dossier web

```bash
# Le dossier peut être différent selon votre hébergement :
# - /home/votre-utilisateur/public_html
# - /var/www/html
# - /var/www/dusselle.fr

cd /home/votre-utilisateur/public_html
```

### 2.2 Sauvegarder les fichiers existants (IMPORTANT)

```bash
# Créer une sauvegarde avec horodatage
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz * 2>/dev/null

# Vérifier que la sauvegarde a été créée
ls -lh backup_*.tar.gz
```

---

## 📥 Étape 3 : Installer l'application

### Option A : Via Git (recommandé)

```bash
# Supprimer les anciens fichiers (après la sauvegarde !)
rm -rf * .??*

# Cloner le dépôt
git clone https://github.com/votre-compte/v2.git .

# OU si vous avez déjà cloné localement, utilisez rsync/scp
```

### Option B : Via FTP/SCP

```bash
# Depuis votre machine locale (PAS sur le serveur)
scp -r /chemin/local/v2/* votre-utilisateur@dusselle.fr:/home/votre-utilisateur/public_html/
```

### Option C : Via le script d'installation automatique

```bash
# Si les fichiers sont déjà sur le serveur
chmod +x install.sh
./install.sh
```

---

## 🗄️ Étape 4 : Configurer la base de données MySQL

### 4.1 Créer la base de données

```bash
# Se connecter à MySQL
mysql -u root -p

# Entrez votre mot de passe MySQL quand demandé
```

Puis dans le shell MySQL :

```sql
-- Créer la base de données
CREATE DATABASE IF NOT EXISTS dusselle_rss
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Créer un utilisateur dédié (recommandé pour la sécurité)
CREATE USER 'dusselle_user'@'localhost' IDENTIFIED BY 'MotDePasseSecurise123!';

-- Donner les droits à l'utilisateur
GRANT ALL PRIVILEGES ON dusselle_rss.* TO 'dusselle_user'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Quitter MySQL
EXIT;
```

### 4.2 Importer le schéma SQL

```bash
# Retour dans le terminal SSH
mysql -u root -p dusselle_rss < database/schema.sql

# OU avec l'utilisateur créé
mysql -u dusselle_user -p dusselle_rss < database/schema.sql
```

---

## ⚙️ Étape 5 : Configurer l'application

### 5.1 Créer le fichier de configuration

```bash
# Copier le fichier exemple
cp config/config.example.php config/config.php

# Éditer le fichier avec nano (ou vi)
nano config/config.php
```

### 5.2 Modifier les paramètres de connexion

Dans le fichier `config/config.php`, modifiez ces lignes :

```php
// Configuration de la base de données
define('DB_HOST', 'localhost');
define('DB_NAME', 'dusselle_rss');
define('DB_USER', 'dusselle_user');        // ← Votre utilisateur MySQL
define('DB_PASS', 'MotDePasseSecurise123!'); // ← Votre mot de passe MySQL
define('DB_CHARSET', 'utf8mb4');

// Configuration de l'application
define('APP_NAME', 'Veille Juridique RSS');
define('APP_URL', 'https://dusselle.fr');
define('TIMEZONE', 'Europe/Paris');
```

**Pour la production, désactivez l'affichage des erreurs :**

```php
// Gestion des erreurs (à désactiver en production)
error_reporting(0);
ini_set('display_errors', 0);
```

Sauvegardez le fichier :
- `Ctrl + O` puis `Entrée` pour sauvegarder
- `Ctrl + X` pour quitter nano

---

## 🔐 Étape 6 : Configurer les permissions

```bash
# Donner les bonnes permissions aux fichiers
chmod -R 755 .
chmod 644 config/config.php
chmod +x cron/update-feeds.php
chmod +x install.sh

# Changer le propriétaire pour l'utilisateur web
# (peut être www-data, apache, ou votre utilisateur selon l'hébergement)
chown -R www-data:www-data .

# OU si vous n'avez pas les droits sudo
chown -R $(whoami):$(whoami) .
```

---

## 🌐 Étape 7 : Configurer Apache

### Option A : Votre DocumentRoot pointe déjà vers public_html

Si Apache pointe déjà vers `/home/votre-utilisateur/public_html`, vous devez déplacer le contenu de `public/` :

```bash
# Déplacer les fichiers publics à la racine
mv public/* .
mv public/.htaccess . 2>/dev/null
rmdir public

# Ajuster les chemins dans les fichiers PHP
# (Les fichiers sont déjà configurés pour chercher ../config et ../src)
```

### Option B : Configurer un VirtualHost dédié

Si vous avez accès à la configuration Apache :

```bash
sudo nano /etc/apache2/sites-available/dusselle.conf
```

Ajoutez :

```apache
<VirtualHost *:80>
    ServerName dusselle.fr
    ServerAlias www.dusselle.fr
    DocumentRoot /home/votre-utilisateur/public_html/public

    <Directory /home/votre-utilisateur/public_html/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/dusselle_error.log
    CustomLog ${APACHE_LOG_DIR}/dusselle_access.log combined
</VirtualHost>
```

Activez le site :

```bash
sudo a2ensite dusselle
sudo systemctl restart apache2
```

---

## ✅ Étape 8 : Tester l'installation

### 8.1 Tester la connexion à la base de données

```bash
php -r "require 'config/config.php'; require 'src/Database.php'; Database::getInstance(); echo 'Connexion OK\n';"
```

Si vous voyez "Connexion OK", tout est bon !

### 8.2 Tester le script de mise à jour RSS

```bash
php cron/update-feeds.php
```

Vous devriez voir les flux RSS se charger.

### 8.3 Tester via le navigateur

Ouvrez votre navigateur et allez sur :

- **Page d'accueil** : https://dusselle.fr/
- **Gestion des flux** : https://dusselle.fr/manage-feeds.php

---

## ⏰ Étape 9 : Configurer le CRON (mise à jour automatique)

```bash
# Ouvrir la crontab
crontab -e

# Ajouter cette ligne pour une mise à jour toutes les 6 heures
0 */6 * * * /usr/bin/php /home/votre-utilisateur/public_html/cron/update-feeds.php >> /var/log/rss-update.log 2>&1

# OU toutes les heures
0 * * * * /usr/bin/php /home/votre-utilisateur/public_html/cron/update-feeds.php >> /var/log/rss-update.log 2>&1
```

Sauvegarder et quitter.

Vérifier que le cron est bien configuré :

```bash
crontab -l
```

---

## 🔒 Étape 10 : Sécuriser l'application (PRODUCTION)

### 10.1 Activer HTTPS

Éditez le fichier `.htaccess` à la racine :

```bash
nano .htaccess
```

Décommentez ces lignes (retirez le #) :

```apache
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

### 10.2 Désactiver l'affichage des erreurs

Dans `config/config.php` :

```php
error_reporting(0);
ini_set('display_errors', 0);
```

### 10.3 Protéger les fichiers sensibles

Le fichier `.htaccess` protège déjà les dossiers `config/`, `src/`, `database/`, `cron/`.

---

## 🎉 Félicitations !

Votre application de veille juridique RSS est maintenant opérationnelle sur **dusselle.fr** !

---

## 📊 Utilisation quotidienne

### Ajouter un flux RSS

1. Allez sur https://dusselle.fr/manage-feeds.php
2. Cliquez sur "Ajouter un flux"
3. Remplissez le formulaire :
   - **Nom** : ex. "Legifrance Actualités"
   - **URL** : ex. "https://www.legifrance.gouv.fr/rss/actualites.xml"
   - **Catégorie** : ex. "Législation"
4. Cliquez sur "Enregistrer"

### Actualiser les articles

Sur la page d'accueil, cliquez sur le bouton **"Actualiser les flux"**.

### Rechercher des articles

Utilisez la barre de recherche en haut pour filtrer les articles par mot-clé.

---

## 🆘 Dépannage

### Erreur "Connexion à la base de données échouée"

```bash
# Vérifier que MySQL tourne
systemctl status mysql

# Tester la connexion manuellement
mysql -u dusselle_user -p
```

### Erreur 500 Internal Server Error

```bash
# Vérifier les logs Apache
tail -f /var/log/apache2/error.log

# Vérifier les permissions
ls -la config/config.php
chmod 644 config/config.php
```

### Les flux RSS ne se chargent pas

```bash
# Vérifier que curl ou allow_url_fopen est activé
php -i | grep allow_url_fopen
php -m | grep curl

# Tester manuellement un flux
php -r "echo file_get_contents('https://www.legifrance.gouv.fr/rss/jorf.xml');"
```

### Le cron ne fonctionne pas

```bash
# Vérifier les logs
tail -f /var/log/rss-update.log

# Tester manuellement
php cron/update-feeds.php

# Vérifier que le cron est actif
crontab -l
```

---

## 📞 Support

Pour toute question ou problème :

1. Consultez d'abord ce guide
2. Vérifiez les logs : `/var/log/apache2/error.log`
3. Consultez le README.md complet
4. Consultez l'API.md pour l'utilisation de l'API

---

**Version** : 1.0.0
**Dernière mise à jour** : Novembre 2024
**Application** : Veille Juridique RSS pour dusselle.fr
