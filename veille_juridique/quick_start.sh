#!/bin/bash

##############################################################################
# Script de démarrage rapide - Veille Juridique Flask
# Ce script configure automatiquement l'application
##############################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions
print_header() {
    echo ""
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Bannière
clear
echo ""
echo "┌─────────────────────────────────────────────┐"
echo "│  🚀 Veille Juridique Flask - Quick Start   │"
echo "│  Installation et configuration automatique  │"
echo "└─────────────────────────────────────────────┘"
echo ""

# Vérifications préalables
print_header "Vérification des prérequis"

# Vérifier Python 3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installé: $PYTHON_VERSION"
else
    print_error "Python 3 n'est pas installé"
    echo "Installez Python 3.8+ et relancez ce script"
    exit 1
fi

# Vérifier pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 est disponible"
else
    print_error "pip3 n'est pas installé"
    echo "Installez pip3 et relancez ce script"
    exit 1
fi

# Créer l'environnement virtuel
print_header "Configuration de l'environnement Python"

if [ -d "venv" ]; then
    print_warning "L'environnement virtuel existe déjà"
    read -p "Voulez-vous le recréer ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_info "Ancien environnement supprimé"
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Création de l'environnement virtuel..."
    python3 -m venv venv
    print_success "Environnement virtuel créé"
fi

# Activer l'environnement virtuel
print_info "Activation de l'environnement virtuel..."
source venv/bin/activate
print_success "Environnement virtuel activé"

# Mettre à jour pip
print_info "Mise à jour de pip..."
pip install --upgrade pip --quiet
print_success "pip mis à jour"

# Installer les dépendances
print_header "Installation des dépendances Python"

print_info "Installation en cours (cela peut prendre quelques minutes)..."
pip install -r requirements.txt --quiet
print_success "Toutes les dépendances sont installées"

# Afficher les packages installés
echo ""
print_info "Packages installés:"
pip list | grep -E "(Flask|SQLAlchemy|feedparser|Werkzeug)"

# Initialiser la base de données
print_header "Initialisation de la base de données"

if [ -f "database.db" ]; then
    print_warning "La base de données existe déjà"
    read -p "Voulez-vous la réinitialiser ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm database.db
        print_info "Base de données supprimée"
    else
        print_info "Conservation de la base de données existante"
    fi
fi

if [ ! -f "database.db" ]; then
    print_info "Création de la base de données..."
    python app.py --init
    print_success "Base de données initialisée"

    # Proposer d'ajouter des flux d'exemple
    echo ""
    read -p "Voulez-vous ajouter des flux RSS de démonstration ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python app.py --sample
        print_success "Flux d'exemple ajoutés"

        # Récupérer les articles des flux
        echo ""
        read -p "Voulez-vous récupérer les articles maintenant ? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Récupération des articles en cours..."
            python app.py --update
            print_success "Articles récupérés"
        fi
    fi
fi

# Créer les dossiers nécessaires
print_header "Création des dossiers"

mkdir -p logs
mkdir -p static/images
print_success "Dossiers créés"

# Rendre les scripts exécutables
print_info "Configuration des scripts shell..."
chmod +x scripts/*.sh
print_success "Scripts shell configurés"

# Résumé
print_header "Installation terminée !"

echo -e "${GREEN}✓ L'application est prête à être utilisée${NC}"
echo ""
echo "Pour démarrer l'application :"
echo ""
echo -e "  ${BLUE}1. Mode développement${NC} (avec debug):"
echo -e "     ${YELLOW}./scripts/deploy.sh development${NC}"
echo ""
echo -e "  ${BLUE}2. Mode production${NC} (sans debug):"
echo -e "     ${YELLOW}./scripts/deploy.sh production${NC}"
echo ""
echo -e "  ${BLUE}3. Manuellement${NC}:"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo -e "     ${YELLOW}python app.py --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "L'application sera accessible sur : ${GREEN}http://localhost:8000${NC}"
echo ""
echo "Documentation complète : ${BLUE}README.md${NC}"
echo "Guide d'installation : ${BLUE}INSTALL.md${NC}"
echo ""

# Proposer de démarrer l'application
read -p "Voulez-vous démarrer l'application maintenant ? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Démarrage de l'application..."
    echo ""
    print_success "Serveur Flask démarré sur http://0.0.0.0:8000"
    print_warning "Appuyez sur Ctrl+C pour arrêter le serveur"
    echo ""
    python app.py --host 0.0.0.0 --port 8000
fi

echo ""
print_success "Merci d'utiliser Veille Juridique Flask !"
echo ""
