# 🚀 Déploiement rapide sur votre serveur dusselle.fr

## ✅ Ce que vous avez déjà

Vous voyez **"It works! Python v3.8.20"** sur dusselle.fr - parfait !
Cela signifie que l'application Python est configurée dans cPanel.

## 📦 Étape 1 : Récupérer les fichiers de l'application

Vous avez 2 options :

### Option A : Cloner depuis Git (⭐ Recommandé)

Sur votre serveur (wrbh3411@down), dans le terminal :

```bash
# Se placer dans le bon répertoire
cd ~/veille_app  # Ou le répertoire configuré dans cPanel

# Cloner le projet
git clone http://127.0.0.1:41742/git/max0067/v2 temp
cd temp
git checkout claude/legal-rss-monitoring-app-011CUqNqkGBZNE7ayYqntiii

# Copier les fichiers de l'application Flask
cp -r veille_juridique/* ~/veille_app/
cd ~/veille_app

# Nettoyer
rm -rf ~/temp
```

### Option B : Uploader manuellement

1. **Téléchargez l'archive** `veille_juridique.tar.gz` depuis le conteneur
2. **Uploadez via FTP/cPanel** File Manager dans `~/veille_app/`
3. **Décompressez** :
   ```bash
   cd ~/veille_app
   tar -xzf veille_juridique.tar.gz
   rm veille_juridique.tar.gz
   ```

## 🔧 Étape 2 : Installer les dépendances

```bash
cd ~/veille_app

# Activer l'environnement virtuel (déjà fait selon votre prompt)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🗄️ Étape 3 : Initialiser la base de données

```bash
# Initialiser la base de données SQLite
python app.py --init

# Ajouter des flux d'exemple
python app.py --sample

# Vérifier que ça fonctionne
python app.py --update
```

## 📝 Étape 4 : Configurer cPanel Python App

Dans **cPanel** → **Setup Python App** :

### Configuration de l'application

```
Application Root: veille_app (ou le chemin de votre app)
Application URL: /
Application startup file: wsgi.py
Application Entry point: application
Python version: 3.8
```

### Variables d'environnement (optionnel)

```
FLASK_ENV=production
SECRET_KEY=votre_cle_secrete_aleatoire_longue
```

### Redémarrer l'application

Cliquez sur **"Restart"** dans l'interface cPanel Python App.

## ✅ Étape 5 : Tester

Accédez à **https://dusselle.fr/**

Vous devriez voir l'application de veille juridique !

## 🔍 Si ça ne fonctionne pas

### Vérifier les logs

```bash
# Dans cPanel, voir les logs de l'application
tail -f ~/logs/stderr.log
tail -f ~/logs/stdout.log
```

### Vérifier les fichiers

```bash
cd ~/veille_app
ls -la

# Vous devez voir :
# - wsgi.py
# - app.py
# - requirements.txt
# - templates/
# - static/
```

### Tester manuellement

```bash
cd ~/veille_app
source venv/bin/activate
python wsgi.py
```

Si ça affiche des erreurs, corrigez-les.

### Permissions

```bash
cd ~/veille_app
chmod 644 *.py
chmod 755 .
chmod 666 database.db  # Pour permettre l'écriture
```

## 🎯 Commandes rapides

```bash
# Tout en une fois
cd ~/veille_app
source venv/bin/activate
pip install -r requirements.txt
python app.py --init
python app.py --sample

# Redémarrer via cPanel ou :
touch tmp/restart.txt  # Si Passenger est utilisé
```

## 📞 Aide supplémentaire

- Consultez **DEPLOIEMENT_CPANEL.md** pour plus de détails
- Vérifiez les logs dans cPanel
- Testez l'API : `curl https://dusselle.fr/api/stats`

---

**Bonne chance ! 🚀**
