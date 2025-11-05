#!/bin/bash

##############################################################################
# Script de mise à jour automatique des flux RSS
# Usage: ./update_feeds.sh
# Peut être ajouté au crontab pour exécution automatique
##############################################################################

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/wrbh3411/public_html/veille_juridique"
VENV_DIR="${APP_DIR}/venv"
PYTHON="${VENV_DIR}/bin/python"
LOG_FILE="${APP_DIR}/logs/update_feeds.log"

# Créer le dossier de logs s'il n'existe pas
mkdir -p "${APP_DIR}/logs"

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Fonction d'erreur
error() {
    echo -e "${RED}[ERREUR]${NC} $1" | tee -a "$LOG_FILE"
}

# Fonction de succès
success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

# Fonction d'avertissement
warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1" | tee -a "$LOG_FILE"
}

# Démarrage
log "=========================================="
log "Début de la mise à jour des flux RSS"
log "=========================================="

# Vérifier si le dossier de l'application existe
if [ ! -d "$APP_DIR" ]; then
    error "Le dossier de l'application n'existe pas: $APP_DIR"
    exit 1
fi

# Se déplacer dans le dossier de l'application
cd "$APP_DIR" || exit 1

# Vérifier si l'environnement virtuel existe
if [ ! -d "$VENV_DIR" ]; then
    warning "L'environnement virtuel n'existe pas. Création en cours..."
    python3 -m venv venv
    source "${VENV_DIR}/bin/activate"
    pip install -r requirements.txt
    success "Environnement virtuel créé"
else
    # Activer l'environnement virtuel
    source "${VENV_DIR}/bin/activate"
    log "Environnement virtuel activé"
fi

# Mettre à jour les flux RSS
log "Mise à jour des flux RSS en cours..."
if $PYTHON app.py --update >> "$LOG_FILE" 2>&1; then
    success "Flux RSS mis à jour avec succès"
else
    error "Erreur lors de la mise à jour des flux RSS"
    exit 1
fi

# Désactiver l'environnement virtuel
deactivate

log "=========================================="
log "Mise à jour terminée"
log "=========================================="

exit 0
