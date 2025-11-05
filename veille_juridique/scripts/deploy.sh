#!/bin/bash

##############################################################################
# Script de déploiement et de lancement de l'application Flask
# Usage: ./deploy.sh [production|development]
##############################################################################

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration par défaut
APP_DIR="/home/wrbh3411/public_html/veille_juridique"
VENV_DIR="${APP_DIR}/venv"
HOST="0.0.0.0"
PORT="8000"
ENV=${1:-development}

# Fonction de logging
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Fonction d'erreur
error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# Fonction de succès
success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Fonction d'avertissement
warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

# Bannière
echo ""
echo "=========================================="
echo "  Déploiement - Veille Juridique Flask"
echo "=========================================="
echo ""

# Vérifier le mode
if [ "$ENV" != "production" ] && [ "$ENV" != "development" ]; then
    error "Mode invalide. Utilisez: production ou development"
    exit 1
fi

log "Mode de déploiement: $ENV"

# Se déplacer dans le dossier de l'application
if [ ! -d "$APP_DIR" ]; then
    error "Le dossier de l'application n'existe pas: $APP_DIR"
    exit 1
fi

cd "$APP_DIR" || exit 1
success "Dossier de l'application: $APP_DIR"

# Vérifier si Python 3 est installé
if ! command -v python3 &> /dev/null; then
    error "Python 3 n'est pas installé"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
success "Python installé: $PYTHON_VERSION"

# Créer ou activer l'environnement virtuel
if [ ! -d "$VENV_DIR" ]; then
    warning "L'environnement virtuel n'existe pas. Création en cours..."
    python3 -m venv venv
    success "Environnement virtuel créé"
fi

log "Activation de l'environnement virtuel..."
source "${VENV_DIR}/bin/activate"

# Installer/Mettre à jour les dépendances
log "Installation des dépendances Python..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
success "Dépendances installées"

# Initialiser la base de données si elle n'existe pas
if [ ! -f "$APP_DIR/database.db" ]; then
    log "Initialisation de la base de données..."
    python app.py --init
    success "Base de données initialisée"

    # Ajouter des flux d'exemple
    warning "Voulez-vous ajouter des flux RSS de démonstration ? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        python app.py --sample
    fi
fi

# Créer les dossiers nécessaires
mkdir -p logs
mkdir -p static/images

# Définir les permissions
chmod 755 static
chmod 755 templates
chmod 644 database.db 2>/dev/null || true

# Définir la variable d'environnement Flask
export FLASK_ENV=$ENV

if [ "$ENV" = "production" ]; then
    export FLASK_DEBUG=0
    warning "IMPORTANT: En production, utilisez un serveur WSGI (gunicorn, uWSGI, etc.)"
    warning "Le serveur Flask intégré n'est PAS recommandé pour la production"

    # Vérifier si gunicorn est installé
    if command -v gunicorn &> /dev/null; then
        log "Démarrage avec Gunicorn (production)..."
        exec gunicorn -w 4 -b ${HOST}:${PORT} app:app
    else
        warning "Gunicorn n'est pas installé. Installation recommandée: pip install gunicorn"
        log "Démarrage avec le serveur Flask (non recommandé pour la production)..."
        exec python app.py --host $HOST --port $PORT
    fi
else
    export FLASK_DEBUG=1
    log "Démarrage du serveur Flask en mode développement..."
    echo ""
    success "Serveur accessible sur: http://${HOST}:${PORT}"
    success "Ctrl+C pour arrêter le serveur"
    echo ""
    exec python app.py --host $HOST --port $PORT
fi
