# 🚀 Guide de déploiement sur votre serveur

## 📍 Localiser votre projet

Connectez-vous à votre serveur et trouvez où se trouve le projet v2 :

```bash
# Afficher votre répertoire home
echo $HOME
# Résultat probable: /home/wrbh3411

# Trouver le projet v2
find ~ -name "v2" -type d 2>/dev/null

# Ou chercher des fichiers spécifiques du projet
find ~ -name "README.md" -path "*/v2/*" 2>/dev/null
```

## 📦 Options de déploiement

### Option 1 : Projet déjà sur le serveur (via Git)

Si le projet est déjà sur votre serveur :

```bash
# Aller dans le répertoire du projet
cd ~/v2
# Ou cd /home/wrbh3411/v2
# Ou cd /var/www/v2

# Vérifier que les fichiers Flask sont là
ls -la app/ requirements.txt run.py
```

### Option 2 : Cloner depuis Git

Si le projet est sur GitHub :

```bash
# Aller dans votre répertoire home
cd ~

# Cloner le projet
git clone https://github.com/max0067/v2.git
cd v2

# Ou sur la branche Flask
git checkout claude/flask-rss-legal-monitoring-011CUsAx3pPA2Ktr1GJ26fNt
```

### Option 3 : Uploader les fichiers

Si vous devez transférer les fichiers :

```bash
# Depuis votre machine locale (pas sur le serveur)
scp -r /chemin/local/v2 wrbh3411@down:/home/wrbh3411/

# Ou avec rsync
rsync -avz --progress /chemin/local/v2/ wrbh3411@down:/home/wrbh3411/v2/
```

## 🔧 Installation rapide une fois dans le bon répertoire

```bash
# 1. Vérifier Python
python3 --version
# Doit être >= 3.8

# 2. Créer l'environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer
cp .env.example .env
nano .env
```

## ⚙️ Configuration de .env

Modifiez selon votre serveur :

```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=votre-cle-tres-longue-et-aleatoire-generee
DB_HOST=localhost
DB_NAME=dusselle_rss
DB_USER=wrbh3411_rss
DB_PASS=votre_mot_de_passe
```

## 🗄️ Créer la base de données

```bash
# Se connecter à MySQL
mysql -u root -p

# Dans MySQL :
CREATE DATABASE dusselle_rss CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wrbh3411_rss'@'localhost' IDENTIFIED BY 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON dusselle_rss.* TO 'wrbh3411_rss'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Importer le schéma
mysql -u root -p dusselle_rss < database/schema.sql
```

## 🧪 Tester l'application

```bash
# Activer l'environnement (si pas déjà fait)
source venv/bin/activate

# Lancer le serveur de test
python run.py

# L'application sera accessible sur:
# http://votre-serveur:5000
```

## 🌐 Trouver l'adresse de votre serveur

```bash
# IP locale
ip addr show | grep inet

# Nom d'hôte
hostname -f

# Tester avec curl
curl http://localhost:5000
```

## 📊 Structure attendue

Votre répertoire v2 doit contenir :

```
v2/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── utils/
├── config.py
├── run.py
├── cli.py
├── requirements.txt
├── .env.example
└── database/
    └── schema.sql
```

## 🔍 Dépannage

### Erreur "No such file or directory"

```bash
# Vérifier où vous êtes
pwd

# Lister les répertoires dans votre home
ls -la ~

# Chercher le projet
find ~ -name "requirements.txt" 2>/dev/null
```

### Permissions refusées

```bash
# Si fichiers appartiennent à root
sudo chown -R wrbh3411:wrbh3411 ~/v2

# Ou avec votre utilisateur web
sudo chown -R www-data:www-data ~/v2
```

### Python ou pip non trouvé

```bash
# Installer Python et pip
sudo yum install python3 python3-pip python3-devel

# Ou sur Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## 💡 Commandes de diagnostic

```bash
# Version Python
python3 --version

# Version MySQL
mysql --version

# Espace disque
df -h

# Processus en cours
ps aux | grep python

# Ports en écoute
netstat -tulpn | grep :5000
```

## 📞 Besoin d'aide ?

1. Vérifiez que vous êtes dans le bon répertoire : `pwd`
2. Listez les fichiers : `ls -la`
3. Vérifiez les logs : `tail -f /var/log/rss-*.log`
4. Consultez la documentation : `cat README_FLASK.md`

---

Une fois localisé, suivez le guide **QUICKSTART.md** pour un démarrage rapide.
