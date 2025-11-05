# 📰 Veille Juridique RSS

Application web moderne de veille juridique basée sur des flux RSS, développée en PHP 8+ avec une interface minimaliste et professionnelle.

## 🌟 Fonctionnalités

- ✅ **Agrégation de flux RSS** : Collecte automatique d'articles depuis plusieurs sources juridiques
- 🔍 **Recherche avancée** : Filtrage en temps réel par mot-clé (titre, source, contenu)
- 📊 **Dashboard moderne** : Interface type tableau de bord avec design responsive
- ⚙️ **Gestion CRUD complète** : Ajout, modification et suppression de flux RSS
- 🔄 **Actualisation manuelle** : Bouton pour récupérer les derniers articles
- ⏰ **Mise à jour automatique** : Script cron pour actualisation périodique (toutes les 6h)
- 🔒 **Sécurité renforcée** : Protection contre les injections SQL, validation des URL

## 📋 Prérequis

- **PHP** : Version 8.0 ou supérieure
- **MySQL** : Version 5.7 ou supérieure
- **Extensions PHP** :
  - `pdo_mysql`
  - `simplexml`
  - `libxml`
  - `curl` ou `allow_url_fopen` activé
- **Apache** : Avec `mod_rewrite` activé
- **Accès SSH** au serveur (pour configuration cron)

## 📁 Structure du projet

```
v2/
├── config/
│   └── config.php              # Configuration BDD et paramètres
├── src/                         # Classes PHP (MVC)
│   ├── Database.php
│   ├── RssFeed.php
│   └── Article.php
├── public/                      # Dossier web public
│   ├── index.php                # Page d'accueil
│   ├── manage-feeds.php         # Gestion des flux
│   ├── api/                     # Endpoints API
│   │   ├── fetch-feeds.php
│   │   ├── add-feed.php
│   │   ├── update-feed.php
│   │   ├── delete-feed.php
│   │   └── search.php
│   └── assets/
│       ├── css/style.css
│       └── js/app.js
├── database/
│   └── schema.sql               # Schéma de base de données
├── cron/
│   └── update-feeds.php         # Script cron
└── README.md
```

## 🚀 Installation

### Étape 1 : Connexion SSH et préparation

```bash
# Se connecter au serveur
ssh votre-utilisateur@dusselle.fr

# Naviguer vers le dossier web
cd /path/to/public_html

# Sauvegarder les fichiers existants (IMPORTANT !)
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .

# Supprimer les anciens fichiers (ATTENTION : opération irréversible)
rm -rf * .*
```

### Étape 2 : Upload des fichiers

```bash
# Option 1 : Via Git (recommandé)
git clone <votre-repo> .
cd public

# Option 2 : Via FTP/SCP
# Uploadez tous les fichiers du projet dans /public_html/
```

### Étape 3 : Configuration de la base de données

```bash
# Se connecter à MySQL
mysql -u root -p

# Exécuter le schéma SQL
mysql -u root -p < database/schema.sql

# OU directement dans MySQL :
source /chemin/vers/database/schema.sql
```

### Étape 4 : Configuration de l'application

Éditez le fichier `config/config.php` :

```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'dusselle_rss');
define('DB_USER', 'votre_utilisateur_mysql');
define('DB_PASS', 'votre_mot_de_passe_mysql');
```

### Étape 5 : Configuration des permissions

```bash
# Donner les permissions appropriées
chmod 755 public/
chmod 644 public/*.php
chmod 644 config/config.php
chmod +x cron/update-feeds.php

# Le propriétaire doit être l'utilisateur Apache (www-data, apache, etc.)
chown -R www-data:www-data /path/to/project
```

### Étape 6 : Configuration Apache

Le dossier `public/` doit être la racine documentaire (DocumentRoot).

**Option A : Modifier la configuration Apache**

```apache
<VirtualHost *:80>
    ServerName dusselle.fr
    DocumentRoot /path/to/v2/public

    <Directory /path/to/v2/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/dusselle_error.log
    CustomLog ${APACHE_LOG_DIR}/dusselle_access.log combined
</VirtualHost>
```

**Option B : Déplacer le contenu de `public/` dans `public_html/`**

```bash
# Si vous ne pouvez pas changer le DocumentRoot
mv public/* /path/to/public_html/
mv public/.htaccess /path/to/public_html/
```

### Étape 7 : Redémarrage Apache

```bash
# Sur Ubuntu/Debian
sudo systemctl restart apache2

# Sur CentOS/RHEL
sudo systemctl restart httpd
```

## ⏰ Configuration du CRON (Mise à jour automatique)

```bash
# Ouvrir la crontab
crontab -e

# Ajouter cette ligne (exécution toutes les 6 heures)
0 */6 * * * /usr/bin/php /path/to/v2/cron/update-feeds.php >> /var/log/rss-update.log 2>&1

# Exemples d'autres fréquences :
# Toutes les heures :       0 * * * *
# Toutes les 3 heures :     0 */3 * * *
# Tous les jours à 6h :     0 6 * * *
```

Vérifier les logs :

```bash
tail -f /var/log/rss-update.log
```

## 🧪 Test de l'installation

1. **Vérifier la connexion BDD** :
   ```bash
   php -r "require 'config/config.php'; require 'src/Database.php'; Database::getInstance(); echo 'OK';"
   ```

2. **Tester manuellement le script cron** :
   ```bash
   php cron/update-feeds.php
   ```

3. **Accéder à l'application** :
   - Page d'accueil : `https://dusselle.fr/`
   - Gestion des flux : `https://dusselle.fr/manage-feeds.php`

## 📖 Utilisation

### Ajouter un flux RSS

1. Cliquez sur "Gérer les flux" dans le menu
2. Cliquez sur "Ajouter un flux"
3. Remplissez les informations :
   - **Nom** : Nom du flux (ex: "Legifrance")
   - **URL** : URL complète du flux RSS (ex: `https://www.legifrance.gouv.fr/rss/jorf.xml`)
   - **Catégorie** : Catégorie du flux (ex: "Législation")
4. Cliquez sur "Enregistrer"

### Actualiser les articles

- Cliquez sur le bouton **"Actualiser les flux"** sur la page d'accueil
- Les nouveaux articles seront récupérés depuis tous les flux actifs

### Rechercher des articles

- Utilisez la barre de recherche en haut de la page
- Tapez un mot-clé (minimum 2 caractères)
- Les résultats s'affichent en temps réel

## 🔒 Sécurité

### Bonnes pratiques implémentées

✅ **Requêtes préparées** : Protection contre les injections SQL
✅ **Validation des URL** : Vérification des URL de flux RSS
✅ **Protection .htaccess** : Blocage de l'accès aux fichiers sensibles
✅ **Headers de sécurité** : X-Frame-Options, X-XSS-Protection, etc.
✅ **Désactivation des index** : Empêche le listing des répertoires

### Recommandations pour la production

```php
// Dans config/config.php, désactiver l'affichage des erreurs :
error_reporting(0);
ini_set('display_errors', 0);
```

Activer HTTPS dans `.htaccess` :

```apache
# Décommenter ces lignes :
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

## 🛠️ Maintenance

### Nettoyage des anciens articles

Le script cron supprime automatiquement les articles de plus de 90 jours.

Pour changer cette durée, modifiez `cron/update-feeds.php` :

```php
// Supprime les articles de plus de 30 jours
$articleModel->deleteOldArticles(30);
```

### Sauvegarde de la base de données

```bash
# Sauvegarde quotidienne
mysqldump -u root -p dusselle_rss > backup_rss_$(date +%Y%m%d).sql

# Ajouter dans crontab pour sauvegarde automatique (tous les jours à 2h)
0 2 * * * mysqldump -u root -p'VOTRE_PASSWORD' dusselle_rss > /backups/rss_$(date +\%Y\%m\%d).sql
```

### Vider le cache

```bash
# Si nécessaire, vider le cache d'Apache
sudo systemctl reload apache2
```

## 🐛 Dépannage

### Erreur "Connexion à la base de données échouée"

- Vérifiez les identifiants dans `config/config.php`
- Vérifiez que MySQL est démarré : `sudo systemctl status mysql`

### Erreur "Permission denied"

```bash
sudo chown -R www-data:www-data /path/to/project
sudo chmod -R 755 /path/to/project
```

### Les flux RSS ne se chargent pas

- Vérifiez que `allow_url_fopen` est activé : `php -i | grep allow_url_fopen`
- Vérifiez les extensions : `php -m | grep -E "(curl|simplexml|libxml)"`

### Le cron ne fonctionne pas

- Vérifiez les logs : `tail -f /var/log/rss-update.log`
- Testez manuellement : `php cron/update-feeds.php`
- Vérifiez la crontab : `crontab -l`

## 📊 Sources RSS juridiques recommandées

| Source | URL | Catégorie |
|--------|-----|-----------|
| Legifrance - Actualités | `https://www.legifrance.gouv.fr/rss/actualites.xml` | Législation |
| Journal Officiel (JORF) | `https://www.legifrance.gouv.fr/rss/jorf.xml` | Journal Officiel |
| Dalloz Actualité | `https://www.dalloz-actualite.fr/feed` | Doctrine |
| Conseil d'État | `https://www.conseil-etat.fr/rss` | Jurisprudence |
| Cour de cassation | `https://www.courdecassation.fr/rss` | Jurisprudence |

## 📝 Licence

Ce projet est développé pour un usage personnel/professionnel.

## 👨‍💻 Support

Pour toute question ou problème :
- Vérifiez d'abord la section **Dépannage**
- Consultez les logs Apache : `/var/log/apache2/error.log`
- Consultez les logs de l'application

---

**Version** : 1.0.0
**Date** : Novembre 2024
**Développé avec** : PHP 8+, MySQL, Bootstrap 5
