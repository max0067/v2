#!/bin/bash
# Script d'installation pour dusselle.fr
# À exécuter sur votre serveur (wrbh3411@down)

echo "🚀 Installation de l'application de Veille Juridique"
echo "===================================================="
echo ""

# Se placer dans le répertoire de l'application
cd ~/veille_app || { echo "❌ Erreur: répertoire ~/veille_app introuvable"; exit 1; }

echo "✓ Répertoire: $(pwd)"
echo ""

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    echo "✓ Activation de l'environnement virtuel..."
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé. Créez-le avec: python3 -m venv venv"
    exit 1
fi

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install Flask Flask-SQLAlchemy feedparser python-dateutil gunicorn --quiet
echo "✓ Dépendances installées"
echo ""

# Initialiser la base de données
if [ ! -f "database.db" ]; then
    echo "🗄️  Initialisation de la base de données..."
    python app.py --init
    echo "✓ Base de données créée"
    echo ""

    echo "📰 Ajout de flux RSS d'exemple..."
    python app.py --sample
    echo "✓ Flux ajoutés"
else
    echo "✓ Base de données existante trouvée"
fi

echo ""
echo "✅ Installation terminée!"
echo ""
echo "Prochaines étapes:"
echo "1. Redémarrez l'application dans cPanel (Setup Python App → Restart)"
echo "2. Accédez à https://dusselle.fr/"
echo ""
echo "Pour actualiser les flux RSS:"
echo "  python app.py --update"
echo ""
