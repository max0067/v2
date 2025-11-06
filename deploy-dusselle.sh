#!/bin/bash
#######################################################
# Script de déploiement automatique pour dusselle.fr
# Application : Veille Juridique RSS
# Version : 1.0.0
#######################################################

set -e  # Arrêter le script en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions d'affichage
print_header() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Vérifier qu'on est dans le bon dossier
check_directory() {
    if [ ! -f "config/config.example.php" ]; then
        print_error "Erreur : Ce script doit être exécuté depuis la racine du projet"
        echo "Usage : cd /home/votre-utilisateur/public_html && bash deploy-dusselle.sh"
        exit 1
    fi
}

# Vérifier les prérequis système
check_requirements() {
    print_header "Vérification des prérequis"

    # Vérifier PHP
    if command -v php &> /dev/null; then
        PHP_VERSION=$(php -v | head -n 1 | cut -d " " -f 2 | cut -d "." -f 1,2)
        print_success "PHP $PHP_VERSION détecté"

        # Vérifier la version de PHP
        if (( $(echo "$PHP_VERSION < 8.0" | bc -l) )); then
            print_error "PHP 8.0 ou supérieur est requis (version actuelle : $PHP_VERSION)"
            exit 1
        fi
    else
        print_error "PHP n'est pas installé"
        exit 1
    fi

    # Vérifier MySQL
    if command -v mysql &> /dev/null; then
        print_success "MySQL/MariaDB détecté"
    else
        print_warning "MySQL n'a pas été détecté. Assurez-vous qu'il est installé."
    fi

    # Vérifier les extensions PHP requises
    print_info "Vérification des extensions PHP..."

    REQUIRED_EXTENSIONS=("pdo_mysql" "simplexml" "libxml")
    MISSING_EXTENSIONS=()

    for ext in "${REQUIRED_EXTENSIONS[@]}"; do
        if php -m | grep -q "$ext"; then
            print_success "Extension $ext : OK"
        else
            MISSING_EXTENSIONS+=("$ext")
            print_error "Extension $ext : MANQUANTE"
        fi
    done

    if [ ${#MISSING_EXTENSIONS[@]} -ne 0 ]; then
        print_error "Extensions manquantes : ${MISSING_EXTENSIONS[*]}"
        echo "Installez-les avec : sudo apt install php-${MISSING_EXTENSIONS[0]} ..."
        exit 1
    fi
}

# Configuration de l'application
configure_app() {
    print_header "Configuration de l'application"

    if [ ! -f "config/config.php" ]; then
        cp config/config.example.php config/config.php
        print_success "Fichier config.php créé"

        # Demander les informations MySQL
        echo ""
        print_info "Configuration de la base de données MySQL"
        echo ""

        read -p "Nom de la base de données [dusselle_rss] : " DB_NAME
        DB_NAME=${DB_NAME:-dusselle_rss}

        read -p "Utilisateur MySQL [root] : " DB_USER
        DB_USER=${DB_USER:-root}

        read -sp "Mot de passe MySQL : " DB_PASS
        echo ""

        read -p "Hôte MySQL [localhost] : " DB_HOST
        DB_HOST=${DB_HOST:-localhost}

        # Mettre à jour le fichier de configuration
        sed -i "s/define('DB_NAME', 'dusselle_rss');/define('DB_NAME', '$DB_NAME');/" config/config.php
        sed -i "s/define('DB_USER', 'votre_utilisateur');/define('DB_USER', '$DB_USER');/" config/config.php
        sed -i "s/define('DB_PASS', 'votre_mot_de_passe');/define('DB_PASS', '$DB_PASS');/" config/config.php
        sed -i "s/define('DB_HOST', 'localhost');/define('DB_HOST', '$DB_HOST');/" config/config.php

        # Désactiver l'affichage des erreurs pour la production
        sed -i "s/error_reporting(E_ALL);/error_reporting(0);/" config/config.php
        sed -i "s/ini_set('display_errors', 1);/ini_set('display_errors', 0);/" config/config.php

        print_success "Configuration MySQL mise à jour"

        # Stocker les identifiants pour l'étape suivante
        echo "$DB_NAME" > /tmp/db_name.tmp
        echo "$DB_USER" > /tmp/db_user.tmp
        echo "$DB_PASS" > /tmp/db_pass.tmp
        echo "$DB_HOST" > /tmp/db_host.tmp
    else
        print_success "config.php existe déjà"
    fi
}

# Configuration des permissions
set_permissions() {
    print_header "Configuration des permissions"

    chmod -R 755 . 2>/dev/null || true
    chmod 644 config/config.php 2>/dev/null || true
    chmod +x cron/update-feeds.php 2>/dev/null || true
    chmod +x deploy-dusselle.sh 2>/dev/null || true
    chmod +x install.sh 2>/dev/null || true

    print_success "Permissions configurées"
}

# Configuration de la base de données
setup_database() {
    print_header "Configuration de la base de données"

    # Récupérer les identifiants stockés
    if [ -f /tmp/db_name.tmp ]; then
        DB_NAME=$(cat /tmp/db_name.tmp)
        DB_USER=$(cat /tmp/db_user.tmp)
        DB_PASS=$(cat /tmp/db_pass.tmp)
        DB_HOST=$(cat /tmp/db_host.tmp)

        # Nettoyer les fichiers temporaires
        rm -f /tmp/db_*.tmp
    else
        # Demander les identifiants si pas déjà configuré
        read -p "Nom de la base de données : " DB_NAME
        read -p "Utilisateur MySQL : " DB_USER
        read -sp "Mot de passe MySQL : " DB_PASS
        echo ""
        read -p "Hôte MySQL [localhost] : " DB_HOST
        DB_HOST=${DB_HOST:-localhost}
    fi

    print_info "Création de la base de données..."

    # Créer la base de données
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || {
        print_error "Impossible de créer la base de données"
        print_info "Essayez de la créer manuellement avec :"
        echo "mysql -u $DB_USER -p -e \"CREATE DATABASE $DB_NAME;\""
        exit 1
    }

    print_success "Base de données créée : $DB_NAME"

    # Importer le schéma
    print_info "Import du schéma SQL..."
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < database/schema.sql 2>/dev/null || {
        print_error "Impossible d'importer le schéma"
        exit 1
    }

    print_success "Schéma importé avec succès"
}

# Test de connexion
test_connection() {
    print_header "Test de connexion à la base de données"

    php -r "
    require 'config/config.php';
    require 'src/Database.php';
    try {
        Database::getInstance();
        echo 'OK';
    } catch (Exception \$e) {
        echo 'ERROR: ' . \$e->getMessage();
        exit(1);
    }
    " > /tmp/db_test.tmp 2>&1

    RESULT=$(cat /tmp/db_test.tmp)
    rm -f /tmp/db_test.tmp

    if [ "$RESULT" == "OK" ]; then
        print_success "Connexion à la base de données réussie"
    else
        print_error "Échec de connexion : $RESULT"
        exit 1
    fi
}

# Test du script cron
test_cron_script() {
    print_header "Test du script de mise à jour RSS"

    print_info "Exécution de la mise à jour des flux..."
    php cron/update-feeds.php 2>&1 | tail -n 5

    print_success "Script de mise à jour testé avec succès"
}

# Déplacer les fichiers publics si nécessaire
move_public_files() {
    print_header "Configuration de la structure web"

    CURRENT_DIR=$(pwd)

    if [[ "$CURRENT_DIR" == */public ]]; then
        print_success "Vous êtes déjà dans le bon dossier (public/)"
    elif [ -d "public" ]; then
        print_warning "Le dossier 'public/' existe"
        echo ""
        read -p "Voulez-vous déplacer le contenu de public/ à la racine ? (o/n) " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[OoYy]$ ]]; then
            mv public/* . 2>/dev/null || true
            mv public/.htaccess . 2>/dev/null || true
            rmdir public 2>/dev/null || true
            print_success "Fichiers déplacés vers la racine"
        fi
    fi
}

# Configurer le CRON
setup_cron() {
    print_header "Configuration du CRON (optionnel)"

    CURRENT_DIR=$(pwd)

    echo ""
    print_info "Pour activer la mise à jour automatique des flux RSS :"
    echo ""
    echo "1. Ouvrez la crontab :"
    echo "   crontab -e"
    echo ""
    echo "2. Ajoutez cette ligne (mise à jour toutes les 6 heures) :"
    echo -e "${GREEN}0 */6 * * * /usr/bin/php $CURRENT_DIR/cron/update-feeds.php >> /var/log/rss-update.log 2>&1${NC}"
    echo ""
    echo "3. Sauvegardez et quittez"
    echo ""

    read -p "Voulez-vous que je configure le cron automatiquement ? (o/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[OoYy]$ ]]; then
        # Créer le dossier de logs s'il n'existe pas
        sudo mkdir -p /var/log 2>/dev/null || mkdir -p ~/logs

        # Ajouter le cron job
        (crontab -l 2>/dev/null; echo "0 */6 * * * /usr/bin/php $CURRENT_DIR/cron/update-feeds.php >> /var/log/rss-update.log 2>&1") | crontab -

        print_success "CRON configuré avec succès"
        print_info "Vérifiez avec : crontab -l"
    else
        print_info "Configuration du CRON ignorée (vous pouvez le faire plus tard)"
    fi
}

# Afficher le récapitulatif final
show_summary() {
    print_header "✅ Installation terminée avec succès !"

    echo ""
    print_success "Votre application est maintenant opérationnelle sur dusselle.fr"
    echo ""

    print_info "Accès à l'application :"
    echo "  🌐 Page d'accueil : https://dusselle.fr/"
    echo "  ⚙️  Gestion des flux : https://dusselle.fr/manage-feeds.php"
    echo ""

    print_info "Prochaines étapes :"
    echo "  1. Accédez à votre site dans un navigateur"
    echo "  2. Ajoutez vos flux RSS depuis la page de gestion"
    echo "  3. Cliquez sur 'Actualiser les flux' pour charger les articles"
    echo ""

    print_info "Documentation :"
    echo "  📖 Guide complet : README.md"
    echo "  🚀 Guide de déploiement : DEPLOY-DUSSELLE.md"
    echo "  📡 Documentation API : API.md"
    echo ""

    print_info "Maintenance :"
    echo "  🔄 Mise à jour manuelle : php cron/update-feeds.php"
    echo "  📊 Logs du cron : tail -f /var/log/rss-update.log"
    echo "  🔒 Logs Apache : tail -f /var/log/apache2/error.log"
    echo ""

    print_warning "N'oubliez pas de :"
    echo "  • Activer HTTPS dans .htaccess"
    echo "  • Configurer le CRON pour les mises à jour automatiques"
    echo "  • Faire des sauvegardes régulières de la base de données"
    echo ""
}

# Script principal
main() {
    print_header "🚀 Déploiement de Veille Juridique RSS sur dusselle.fr"

    check_directory
    check_requirements
    configure_app
    set_permissions
    setup_database
    test_connection
    test_cron_script
    move_public_files
    setup_cron
    show_summary

    print_success "Déploiement terminé ! 🎉"
}

# Exécuter le script
main
