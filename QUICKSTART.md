# 🚀 Démarrage rapide pour dusselle.fr

Ce guide vous permet de déployer l'application en **moins de 10 minutes**.

---

## 📦 Méthode 1 : Script automatique (RECOMMANDÉ)

### Étape 1 : Connexion au serveur

```bash
# Connectez-vous à votre serveur
ssh votre-utilisateur@dusselle.fr
```

### Étape 2 : Préparation

```bash
# Allez dans votre dossier web
cd /home/votre-utilisateur/public_html

# Sauvegarde de sécurité (IMPORTANT !)
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz * 2>/dev/null
```

### Étape 3 : Installation

```bash
# Si les fichiers sont déjà uploadés
chmod +x deploy-dusselle.sh
./deploy-dusselle.sh
```

**C'est tout ! Le script fait tout automatiquement** :
- ✅ Vérifie les prérequis (PHP, MySQL, extensions)
- ✅ Configure l'application
- ✅ Crée la base de données
- ✅ Importe le schéma SQL
- ✅ Configure les permissions
- ✅ Teste la connexion
- ✅ Configure le CRON (optionnel)

---

## 📝 Méthode 2 : Installation manuelle rapide

### 1️⃣ Connexion SSH

```bash
ssh votre-utilisateur@dusselle.fr
cd /home/votre-utilisateur/public_html
```

### 2️⃣ Configuration

```bash
# Copier la configuration
cp config/config.example.php config/config.php

# Éditer avec vos identifiants MySQL
nano config/config.php
```

Modifiez ces lignes :
```php
define('DB_USER', 'votre_utilisateur');
define('DB_PASS', 'votre_mot_de_passe');
```

### 3️⃣ Base de données

```bash
# Créer la BDD et importer le schéma
mysql -u root -p < database/schema.sql
```

### 4️⃣ Permissions

```bash
chmod -R 755 .
chmod 644 config/config.php
chmod +x cron/update-feeds.php
```

### 5️⃣ Test

```bash
# Tester la connexion
php -r "require 'config/config.php'; require 'src/Database.php'; Database::getInstance(); echo 'OK\n';"

# Tester les flux RSS
php cron/update-feeds.php
```

### 6️⃣ Accès

Ouvrez votre navigateur : **https://dusselle.fr/**

---

## 🔐 Informations importantes

### Identifiants MySQL à préparer

Avant de commencer, ayez sous la main :
- 📌 **Nom de la base de données** : ex. `dusselle_rss`
- 📌 **Utilisateur MySQL** : ex. `root` ou `dusselle_user`
- 📌 **Mot de passe MySQL**
- 📌 **Hôte MySQL** : généralement `localhost`

### Structure de la base de données

Le script créera automatiquement :
- Table **rss_feeds** : Stocke les flux RSS
- Table **articles** : Stocke les articles collectés
- Flux RSS de démonstration : Legifrance, Journal Officiel, Dalloz, Conseil d'État

---

## ⏰ Configuration du CRON (optionnel)

Pour que les flux se mettent à jour automatiquement :

```bash
crontab -e
```

Ajoutez cette ligne :

```bash
0 */6 * * * /usr/bin/php /home/votre-utilisateur/public_html/cron/update-feeds.php >> /var/log/rss-update.log 2>&1
```

Cela mettra à jour les flux **toutes les 6 heures**.

---

## 🌐 Accès à l'application

Une fois installée :

| Page | URL | Description |
|------|-----|-------------|
| **Accueil** | https://dusselle.fr/ | Affiche tous les articles RSS |
| **Gestion des flux** | https://dusselle.fr/manage-feeds.php | Ajouter/modifier/supprimer des flux |

---

## 🎯 Premiers pas après l'installation

### 1. Ajouter un flux RSS

1. Allez sur : https://dusselle.fr/manage-feeds.php
2. Cliquez sur **"Ajouter un flux"**
3. Remplissez :
   - **Nom** : "Legifrance Actualités"
   - **URL** : "https://www.legifrance.gouv.fr/rss/actualites.xml"
   - **Catégorie** : "Législation"
4. Cliquez sur **"Enregistrer"**

### 2. Charger les articles

Sur la page d'accueil, cliquez sur **"Actualiser les flux"**.

### 3. Rechercher des articles

Utilisez la barre de recherche en haut pour filtrer les articles.

---

## 🆘 Problèmes courants

### ❌ Erreur "Connexion à la base de données échouée"

**Solution** :
```bash
# Vérifier MySQL
systemctl status mysql

# Vérifier les identifiants dans config.php
nano config/config.php
```

### ❌ Erreur 500

**Solution** :
```bash
# Vérifier les logs
tail -f /var/log/apache2/error.log

# Vérifier les permissions
chmod 644 config/config.php
```

### ❌ Les flux ne se chargent pas

**Solution** :
```bash
# Tester manuellement
php cron/update-feeds.php

# Vérifier les extensions PHP
php -m | grep -E "(curl|simplexml|libxml)"
```

---

## 📚 Documentation complète

- **Guide complet** : [README.md](README.md)
- **Guide de déploiement détaillé** : [DEPLOY-DUSSELLE.md](DEPLOY-DUSSELLE.md)
- **Documentation API** : [API.md](API.md)
- **Installation complète** : [INSTALL.md](INSTALL.md)

---

## ✅ Checklist de déploiement

Cochez au fur et à mesure :

- [ ] Connexion SSH réussie
- [ ] Sauvegarde des fichiers existants
- [ ] Fichiers de l'application uploadés
- [ ] config.php créé et configuré
- [ ] Base de données créée
- [ ] Schéma SQL importé
- [ ] Permissions configurées
- [ ] Test de connexion réussi
- [ ] Test du script cron réussi
- [ ] Accès à https://dusselle.fr/ fonctionnel
- [ ] HTTPS activé (décommenter dans .htaccess)
- [ ] CRON configuré (optionnel)

---

## 📞 Support

En cas de problème :

1. Consultez d'abord ce guide
2. Vérifiez les logs : `tail -f /var/log/apache2/error.log`
3. Consultez le [guide complet](README.md)
4. Relancez le script d'installation : `./deploy-dusselle.sh`

---

## 🎉 Félicitations !

Votre application de veille juridique RSS est maintenant opérationnelle !

**Version** : 1.0.0
**Application** : Veille Juridique RSS
**Domaine** : dusselle.fr
