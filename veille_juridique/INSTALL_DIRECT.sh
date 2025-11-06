#!/bin/bash
# Script d'installation directe pour le serveur dusselle.fr
# Crée tous les fichiers de l'application dans /home/wrbh3411/veille_juridique/

echo "🚀 Installation de l'application de Veille Juridique"
echo "===================================================="
echo ""

# Se placer dans le bon répertoire
cd /home/wrbh3411/veille_juridique || exit 1

echo "📍 Répertoire: $(pwd)"
echo ""

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p templates static/css static/js
echo "✓ Dossiers créés"
echo ""

# Créer requirements.txt
echo "📝 Création de requirements.txt..."
cat > requirements.txt << 'EOF'
Flask>=3.0.0
Flask-SQLAlchemy>=3.1.1
feedparser>=6.0.11
python-dateutil>=2.8.2
Werkzeug>=3.0.1
SQLAlchemy>=2.0.23
gunicorn>=23.0.0
EOF
echo "✓ requirements.txt créé"

echo ""
echo "✅ Installation terminée!"
echo ""
echo "Prochaines étapes sur votre serveur:"
echo "1. Exécutez ce script: bash INSTALL_DIRECT.sh"
echo "2. Les autres fichiers seront créés via des commandes cat"
echo ""
