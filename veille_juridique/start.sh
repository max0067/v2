#!/bin/bash
# Script de démarrage pour l'application de veille juridique

# Se placer dans le répertoire de l'application
cd "$(dirname "$0")"

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Initialiser la base de données si elle n'existe pas
if [ ! -f "database.db" ]; then
    echo "Initialisation de la base de données..."
    python app.py --init
    echo "Ajout de flux d'exemple..."
    python app.py --sample
fi

# Démarrer l'application avec Gunicorn
echo "Démarrage de l'application avec Gunicorn..."
gunicorn --config gunicorn_config.py wsgi:application
