#!/bin/bash
# Script d'installation automatique Flask pour dusselle.fr

echo "🚀 Installation automatique de l'application Flask..."

# 1. Configuration des variables
DB_HOST="localhost"
DB_NAME="wrbh3411_rss_legal"
DB_USER="wrbh3411_rss_legal"
DB_PASS="lealealea06"
SECRET_KEY="b65fc872b054c0fa21e9296c8157d5717f4b4321be61b4200c09a01ab56153d8"

# 2. Créer passenger_wsgi.py avec les variables EN DUR (pas de .env)
echo "📝 Création de passenger_wsgi.py..."
cat > ~/public_html/flask-version/passenger_wsgi.py << 'WSGI_EOF'
import sys
import os

# Variables d'environnement EN DUR
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'wrbh3411_rss_legal'
os.environ['DB_USER'] = 'wrbh3411_rss_legal'
os.environ['DB_PASS'] = 'lealealea06'
os.environ['SECRET_KEY'] = 'b65fc872b054c0fa21e9296c8157d5717f4b4321be61b4200c09a01ab56153d8'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Environnement virtuel
INTERP = "/home/wrbh3411/virtualenv/public_html/flask-version/3.6/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Ajouter le chemin
sys.path.insert(0, os.path.dirname(__file__))

# Importer l'application
from run import app as application
WSGI_EOF

echo "✅ passenger_wsgi.py créé"

# 3. Activer l'environnement virtuel et créer les tables
echo "🗄️  Création des tables de la base de données..."
source /home/wrbh3411/virtualenv/public_html/flask-version/3.6/bin/activate
cd /home/wrbh3411/public_html/flask-version

python << 'PYTHON_EOF'
import os

# Définir les variables d'environnement avant d'importer l'app
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'wrbh3411_rss_legal'
os.environ['DB_USER'] = 'wrbh3411_rss_legal'
os.environ['DB_PASS'] = 'lealealea06'
os.environ['SECRET_KEY'] = 'b65fc872b054c0fa21e9296c8157d5717f4b4321be61b4200c09a01ab56153d8'
os.environ['FLASK_ENV'] = 'production'

from app import create_app, db

app = create_app()
with app.app_context():
    try:
        db.create_all()
        print("✅ Tables créées avec succès!")

        # Vérifier la connexion
        from app.models import Feed
        count = Feed.query.count()
        print(f"✅ Connexion DB OK - {count} flux RSS")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
PYTHON_EOF

# 4. Créer .htaccess correct
echo "📝 Configuration .htaccess..."
cat > ~/public_html/.htaccess << 'HTACCESS_EOF'
Options -Indexes
PassengerEnabled On
PassengerPython /home/wrbh3411/virtualenv/public_html/flask-version/3.6/bin/python
PassengerAppRoot /home/wrbh3411/public_html/flask-version

<FilesMatch "\.(env|sql|log|pyc|db)$">
    Require all denied
</FilesMatch>
HTACCESS_EOF

echo "✅ .htaccess configuré"

# 5. Redémarrer Passenger
echo "🔄 Redémarrage de Passenger..."
mkdir -p ~/public_html/tmp
touch ~/public_html/tmp/restart.txt

echo ""
echo "✅ Installation terminée !"
echo ""
echo "🌐 Testez votre application sur: http://dusselle.fr/"
echo ""
echo "⏳ Attendez 10-15 secondes puis rafraîchissez votre navigateur (Ctrl+F5)"
echo ""
echo "📋 Si vous voyez toujours une erreur, consultez les logs:"
echo "   tail -50 ~/logs/error_log"
echo ""
