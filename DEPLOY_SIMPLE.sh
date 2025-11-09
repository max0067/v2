#!/bin/bash
# Script de déploiement simple - À exécuter sur le serveur

echo "🚀 Déploiement des fonctionnalités collaboratives"
echo "=================================================="
echo ""

# Se positionner dans le bon répertoire
cd /home/wrbh3411/public_html/flask-version || exit 1

echo "📥 Récupération des dernières modifications..."
git fetch origin claude/flask-rss-legal-monitoring-011CUsAx3pPA2Ktr1GJ26fNt

# Forcer le reset pour écraser les modifications locales
echo "🔄 Reset des fichiers modifiés localement..."
git reset --hard origin/claude/flask-rss-legal-monitoring-011CUsAx3pPA2Ktr1GJ26fNt

echo "✅ Fichiers mis à jour"
echo ""

# Vérifier les fichiers critiques
echo "🔍 Vérification des fichiers critiques..."
echo ""

echo "1. Template utilisé :"
grep -A1 "index_lexis" app/routes/main.py | grep "index"
echo ""

echo "2. Chargement de app.js :"
grep "app.js" app/templates/base_lexis.html
echo ""

echo "3. Chargement de lexis_collab.js :"
grep "lexis_collab.js" app/templates/index_lexis_collab.html
echo ""

echo "4. Fonction openArticle existe dans app.js :"
grep -c "function openArticle" app/static/js/app.js
echo ""

# Redémarrer l'application
echo "🔄 Redémarrage de l'application..."
touch passenger_wsgi.py

echo ""
echo "=================================================="
echo "✅ Déploiement terminé !"
echo ""
echo "📌 Prochaines étapes :"
echo "1. Attendre 10 secondes"
echo "2. Ouvrir une FENÊTRE DE NAVIGATION PRIVÉE"
echo "3. Aller sur http://dusselle.fr"
echo "4. Vérifier :"
echo "   - Les dossiers apparaissent dans la sidebar"
echo "   - Les articles sont cliquables"
echo ""
