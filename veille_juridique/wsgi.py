"""
Point d'entrée WSGI pour l'application de veille juridique
Utilisé par Gunicorn, uWSGI, et autres serveurs WSGI
"""
import os
import sys

# Ajouter le répertoire de l'application au path Python
sys.path.insert(0, os.path.dirname(__file__))

# Importer l'application Flask
from app import app as application

if __name__ == "__main__":
    application.run()
