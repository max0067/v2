#!/bin/bash

##############################################################################
# Script de sauvegarde de la base de données SQLite
# Usage: ./backup_db.sh
# Peut être ajouté au crontab pour sauvegarde automatique quotidienne
##############################################################################

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/wrbh3411/public_html/veille_juridique"
DB_FILE="${APP_DIR}/database.db"
BACKUP_DIR="/home/wrbh3411/backups/veille_juridique"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/database_${DATE}.db"
LOG_FILE="${APP_DIR}/logs/backup.log"

# Nombre de jours de rétention des sauvegardes
RETENTION_DAYS=30

# Créer les dossiers s'ils n'existent pas
mkdir -p "$BACKUP_DIR"
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

# Démarrage
log "=========================================="
log "Début de la sauvegarde de la base de données"
log "=========================================="

# Vérifier si la base de données existe
if [ ! -f "$DB_FILE" ]; then
    error "La base de données n'existe pas: $DB_FILE"
    exit 1
fi

# Taille de la base de données
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
log "Taille de la base de données: $DB_SIZE"

# Copier la base de données
log "Copie de la base de données en cours..."
if cp "$DB_FILE" "$BACKUP_FILE"; then
    success "Base de données sauvegardée: $BACKUP_FILE"
else
    error "Erreur lors de la copie de la base de données"
    exit 1
fi

# Compresser la sauvegarde
log "Compression de la sauvegarde en cours..."
if gzip "$BACKUP_FILE"; then
    BACKUP_FILE="${BACKUP_FILE}.gz"
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    success "Sauvegarde compressée: $BACKUP_FILE ($BACKUP_SIZE)"
else
    error "Erreur lors de la compression"
    exit 1
fi

# Nettoyer les anciennes sauvegardes
log "Nettoyage des sauvegardes de plus de $RETENTION_DAYS jours..."
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "database_*.db.gz" -type f -mtime +$RETENTION_DAYS)

if [ -n "$OLD_BACKUPS" ]; then
    echo "$OLD_BACKUPS" | while read -r old_backup; do
        if rm "$old_backup"; then
            log "Sauvegarde supprimée: $old_backup"
        else
            error "Erreur lors de la suppression de: $old_backup"
        fi
    done
else
    log "Aucune ancienne sauvegarde à supprimer"
fi

# Nombre total de sauvegardes
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "database_*.db.gz" -type f | wc -l)
log "Nombre total de sauvegardes: $TOTAL_BACKUPS"

# Espace disque utilisé par les sauvegardes
BACKUP_DIR_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Espace total utilisé par les sauvegardes: $BACKUP_DIR_SIZE"

log "=========================================="
log "Sauvegarde terminée avec succès"
log "=========================================="

exit 0
