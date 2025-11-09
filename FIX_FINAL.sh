#!/bin/bash
# Script final de réparation - NE FAIT QUE DES CHOSES QUI FONCTIONNENT

echo "=========================================="
echo "FIX FINAL - Version simple et fonctionnelle"
echo "=========================================="
echo ""

cd /home/wrbh3411/public_html/flask-version || exit 1

echo "1. Récupération de la dernière version..."
git fetch origin claude/flask-rss-legal-monitoring-011CUsAx3pPA2Ktr1GJ26fNt

echo "2. Écrasement de TOUS les fichiers locaux modifiés..."
git reset --hard origin/claude/flask-rss-legal-monitoring-011CUsAx3pPA2Ktr1GJ26fNt

echo "3. Vérification du template utilisé..."
grep "index_lexis.html" app/routes/main.py && echo "✅ Template: index_lexis.html" || echo "❌ ERREUR Template"

echo "4. Vérification de la section dossiers..."
grep "Mes Dossiers" app/templates/index_lexis.html && echo "✅ Section dossiers présente" || echo "❌ ERREUR Dossiers"

echo "5. Vérification du JavaScript app.js..."
grep "function openArticle" app/static/js/app.js && echo "✅ Fonction openArticle présente" || echo "❌ ERREUR openArticle"

echo "6. Redémarrage de l'application..."
touch passenger_wsgi.py

echo ""
echo "=========================================="
echo "✅ TERMINÉ !"
echo "=========================================="
echo ""
echo "INSTRUCTIONS IMPORTANTES :"
echo ""
echo "1. Attends 15 secondes"
echo "2. Sur ton ordinateur :"
echo "   - FERME COMPLÈTEMENT ton navigateur (toutes les fenêtres)"
echo "   - ROUVRE-le"
echo "   - Va sur http://dusselle.fr"
echo ""
echo "Tu DOIS voir :"
echo "  ✅ '📁 Mes Dossiers' en haut de la sidebar gauche"
echo "  ✅ Les dossiers listés en dessous"
echo "  ✅ Le bouton 'Actualiser les flux' fonctionne"
echo "  ✅ Tu peux cliquer sur les articles"
echo ""
echo "Si tu ne vois PAS les dossiers :"
echo "  → Ouvre une fenêtre NAVIGATION PRIVÉE (Ctrl+Shift+N)"
echo "  → Va sur http://dusselle.fr dans cette fenêtre"
echo ""
