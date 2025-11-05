# 🚀 Guide d'installation rapide

## ⚡ Installation en 5 minutes

### 1️⃣ Préparer le serveur

```bash
# Connexion SSH
ssh votre-utilisateur@dusselle.fr

# Sauvegarder les fichiers existants
cd /path/to/public_html
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .

# ⚠️ ATTENTION : Suppression des fichiers existants
rm -rf * .*
```

### 2️⃣ Cloner le projet

```bash
# Cloner depuis Git
git clone <votre-repo> .
cd public
```

### 3️⃣ Créer la base de données

```bash
# Se connecter à MySQL
mysql -u root -p

# Exécuter le schéma
mysql -u root -p < database/schema.sql
```

### 4️⃣ Configurer l'application

```bash
# Copier le fichier de configuration
cp config/config.example.php config/config.php

# Éditer les identifiants MySQL
nano config/config.php
```

Modifier ces lignes :
```php
define('DB_USER', 'votre_utilisateur');
define('DB_PASS', 'votre_mot_de_passe');
```

### 5️⃣ Configurer les permissions

```bash
chmod -R 755 .
chmod +x cron/update-feeds.php
chown -R www-data:www-data .
```

### 6️⃣ Redémarrer Apache

```bash
sudo systemctl restart apache2
```

### 7️⃣ Tester l'installation

```bash
# Test de connexion BDD
php -r "require 'config/config.php'; require 'src/Database.php'; Database::getInstance(); echo 'OK';"

# Test du script cron
php cron/update-feeds.php
```

### 8️⃣ Accéder à l'application

🌐 **Page d'accueil** : https://dusselle.fr/
⚙️ **Gestion des flux** : https://dusselle.fr/manage-feeds.php

---

## ⏰ Configuration CRON (optionnel)

```bash
crontab -e

# Ajouter cette ligne (mise à jour toutes les 6h)
0 */6 * * * /usr/bin/php /path/to/v2/cron/update-feeds.php >> /var/log/rss-update.log 2>&1
```

---

## 🔐 Sécurité (IMPORTANT pour la production)

### Désactiver l'affichage des erreurs

Éditer `config/config.php` :

```php
error_reporting(0);
ini_set('display_errors', 0);
```

### Activer HTTPS

Éditer `public/.htaccess`, décommenter :

```apache
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

---

## ✅ Checklist finale

- [ ] Base de données créée et accessible
- [ ] Fichier config.php configuré avec les bons identifiants
- [ ] Permissions correctes (755 pour dossiers, 644 pour fichiers)
- [ ] Apache redémarré
- [ ] Test de connexion réussi
- [ ] Page d'accueil accessible
- [ ] Erreurs désactivées en production
- [ ] HTTPS activé
- [ ] CRON configuré (optionnel)

---

## 🆘 Aide rapide

### Erreur de connexion MySQL
```bash
sudo systemctl status mysql
mysql -u root -p  # Tester la connexion
```

### Erreur de permissions
```bash
sudo chown -R www-data:www-data /path/to/project
sudo chmod -R 755 /path/to/project
```

### Logs Apache
```bash
tail -f /var/log/apache2/error.log
```

Pour plus de détails, consultez le fichier **README.md** complet.
