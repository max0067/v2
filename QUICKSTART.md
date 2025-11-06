# 🚀 Démarrage rapide - Veille Juridique RSS Flask

Guide de démarrage ultra-rapide pour tester l'application en local.

## Installation rapide (développement)

```bash
# 1. Cloner/télécharger le projet
cd /home/user/v2

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
nano .env  # Modifier les paramètres DB_*

# 5. Créer la base de données
mysql -u root -p < database/schema.sql

# 6. Lancer l'application
python run.py
```

Accédez à : **http://localhost:5000**

## Test rapide des fonctionnalités

### 1. Ajouter un flux RSS

Via l'interface web :
- Cliquez sur "Gérer les flux"
- Cliquez sur "Ajouter un flux"
- Remplissez les informations
- Enregistrez

Ou via l'API :

```bash
curl -X POST http://localhost:5000/api/feeds \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Feed",
    "url": "https://www.legifrance.gouv.fr/rss/jorf.xml",
    "category": "Test"
  }'
```

### 2. Actualiser les flux

Via l'interface :
- Cliquez sur "Actualiser les flux" sur la page d'accueil

Ou via CLI :

```bash
python cli.py refresh
```

### 3. Rechercher

- Utilisez la barre de recherche sur la page d'accueil
- Tapez au moins 2 caractères

## Commandes CLI utiles

```bash
# Actualiser tous les flux
python cli.py refresh

# Nettoyer les articles anciens
python cli.py cleanup 90

# Voir les statistiques
python cli.py stats
```

## Endpoints API principaux

```bash
# Récupérer tous les flux
GET /api/feeds

# Ajouter un flux
POST /api/feeds

# Actualiser tous les flux
POST /api/feeds/refresh

# Rechercher des articles
GET /api/articles/search?q=juridique

# Obtenir les statistiques
GET /api/stats
```

## Dépannage rapide

### Erreur de connexion MySQL

```bash
# Vérifier que MySQL tourne
sudo systemctl status mysql

# Vérifier les identifiants dans .env
cat .env | grep DB_
```

### Port 5000 déjà utilisé

```bash
# Changer le port dans .env
echo "PORT=5001" >> .env

# Ou lancer avec un autre port
PORT=5001 python run.py
```

### Module non trouvé

```bash
# Vérifier que l'environnement virtuel est activé
which python
# Devrait afficher: /home/user/v2/venv/bin/python

# Réactiver si nécessaire
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

---

Pour une installation complète en production, consultez **INSTALL_FLASK.md**.
