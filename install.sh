#!/bin/bash
#######################################################
# Script d'installation automatique
# Veille Juridique RSS pour dusselle.fr
#######################################################

echo "=========================================="
echo "Installation de Veille Juridique RSS"
echo "=========================================="
echo ""

# Vérifier si on est dans le bon dossier
if [ ! -f "config/config.example.php" ]; then
    echo "❌ Erreur: Vous devez exécuter ce script depuis la racine du projet"
    echo "   cd /home/wrbh3411/public_html && bash install.sh"
    exit 1
fi

# 1. Créer le fichier de configuration
echo "1️⃣  Configuration de l'application..."
if [ ! -f "config/config.php" ]; then
    cp config/config.example.php config/config.php
    echo "✅ Fichier config.php créé"
    echo ""
    echo "⚠️  IMPORTANT : Éditez config/config.php avec vos identifiants MySQL"
    echo "   nano config/config.php"
    echo ""
    read -p "Appuyez sur Entrée après avoir configuré config.php..."
else
    echo "✅ config.php existe déjà"
fi

# 2. Vérifier les permissions
echo ""
echo "2️⃣  Configuration des permissions..."
chmod -R 755 .
chmod +x cron/update-feeds.php
chmod 644 config/config.php
echo "✅ Permissions configurées"

# 3. Tester la connexion à la base de données
echo ""
echo "3️⃣  Test de connexion à la base de données..."
php -r "
require 'config/config.php';
require 'src/Database.php';
try {
    Database::getInstance();
    echo '✅ Connexion à la base de données réussie\n';
} catch (Exception \$e) {
    echo '❌ Erreur de connexion : ' . \$e->getMessage() . '\n';
    echo 'Vérifiez vos identifiants dans config/config.php\n';
    exit(1);
}
"

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Corrigez la configuration et relancez le script"
    exit 1
fi

# 4. Proposer d'importer le schéma
echo ""
read -p "4️⃣  Voulez-vous importer le schéma de base de données ? (o/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[OoYy]$ ]]; then
    read -p "Nom d'utilisateur MySQL: " DB_USER
    read -sp "Mot de passe MySQL: " DB_PASS
    echo ""
    read -p "Nom de la base de données: " DB_NAME

    echo "Création de la base de données..."
    mysql -u "$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

    echo "Import du schéma..."
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < database/schema.sql

    if [ $? -eq 0 ]; then
        echo "✅ Base de données importée avec succès"
    else
        echo "❌ Erreur lors de l'import"
        exit 1
    fi
fi

# 5. Test du script cron
echo ""
echo "5️⃣  Test du script de mise à jour..."
php cron/update-feeds.php

# 6. Vérifier la structure web
echo ""
echo "6️⃣  Vérification de la structure web..."
CURRENT_DIR=$(pwd)
if [[ "$CURRENT_DIR" == */public ]]; then
    echo "✅ Vous êtes dans le bon dossier (public/)"
elif [ -d "public" ]; then
    echo "⚠️  ATTENTION : Vous devez déplacer le contenu de public/ à la racine"
    echo ""
    read -p "Voulez-vous que je le fasse automatiquement ? (o/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[OoYy]$ ]]; then
        mv public/* .
        mv public/.htaccess . 2>/dev/null
        rmdir public
        echo "✅ Fichiers déplacés"
    fi
fi

# 7. Récapitulatif
echo ""
echo "=========================================="
echo "✅ Installation terminée !"
echo "=========================================="
echo ""
echo "📍 Prochaines étapes :"
echo ""
echo "1. Vérifiez que Apache pointe vers ce dossier"
echo "2. Accédez à votre site : https://dusselle.fr/"
echo "3. Gestion des flux : https://dusselle.fr/manage-feeds.php"
echo ""
echo "⏰ Pour configurer la mise à jour automatique (cron) :"
echo "   crontab -e"
echo "   Ajoutez : 0 */6 * * * /usr/bin/php $(pwd)/cron/update-feeds.php >> /var/log/rss-update.log 2>&1"
echo ""
echo "📚 Documentation complète : README.md"
echo ""
