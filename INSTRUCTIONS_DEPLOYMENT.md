# 🚀 Instructions de déploiement pour votre serveur dusselle.fr

## 📍 Vous êtes ici : Serveur wrbh3411@down

Voici exactement ce que vous devez faire sur **VOTRE serveur réel** :

---

## Étape 1️⃣ : Trouver le répertoire de votre application Python

Sur votre serveur, exécutez :

```bash
# Voir où vous êtes
pwd

# Trouver le répertoire de l'app Python
# Cherchez dans cPanel → Setup Python App → voir le "Application Root"
```

**Options possibles** :
- `~/public_html/`
- `~/www/`
- `~/htdocs/`
- `~/veille_app/` (à créer si n'existe pas)
- Un autre chemin spécifié dans cPanel

---

## Étape 2️⃣ : Créer le répertoire si nécessaire

```bash
# Si le répertoire n'existe pas, créez-le
mkdir -p ~/veille_app
cd ~/veille_app
```

---

## Étape 3️⃣ : Uploader l'archive

**Option A : Via cPanel File Manager** (⭐ Le plus simple)

1. Connectez-vous à **cPanel** sur dusselle.fr
2. Allez dans **"File Manager"**
3. Naviguez vers le répertoire de votre application (ex: `veille_app`)
4. Cliquez sur **"Upload"**
5. Uploadez le fichier `veille_juridique.tar.gz`
6. Une fois uploadé, cliquez droit sur le fichier → **"Extract"**

**Option B : Via SCP/SFTP**

```bash
# Sur votre ordinateur local (si vous avez téléchargé l'archive)
scp veille_juridique.tar.gz wrbh3411@dusselle.fr:~/veille_app/
```

**Option C : Via wget (si l'archive est accessible en ligne)**

```bash
cd ~/veille_app
wget <url-de-l-archive>
```

---

## Étape 4️⃣ : Extraire l'archive

Sur votre serveur :

```bash
cd ~/veille_app
tar -xzf veille_juridique.tar.gz
ls -la

# Vous devriez voir :
# app.py, wsgi.py, config.py, models.py, requirements.txt
# templates/, static/
```

---

## Étape 5️⃣ : Installer les dépendances

```bash
cd ~/veille_app

# Activer l'environnement virtuel (si vous en avez un)
source venv/bin/activate

# Installer les dépendances Python
pip install Flask Flask-SQLAlchemy feedparser python-dateutil gunicorn
```

---

## Étape 6️⃣ : Initialiser la base de données

```bash
cd ~/veille_app

# Initialiser la base de données SQLite
python app.py --init

# Ajouter des flux RSS d'exemple
python app.py --sample

# Tester la mise à jour des flux
python app.py --update
```

---

## Étape 7️⃣ : Configurer cPanel Python App

1. **Connectez-vous à cPanel**
2. Allez dans **"Setup Python App"**
3. Si l'application existe déjà, **éditez-la**, sinon **créez-en une nouvelle** :

### Configuration :

```
Application Root: veille_app
Application URL: /
Application startup file: wsgi.py
Application Entry point: application
Python version: 3.8 (ou la version disponible)
```

4. Cliquez sur **"Restart"** ou **"Redémarrer"**

---

## Étape 8️⃣ : Tester l'application

Ouvrez votre navigateur et accédez à :

✅ **https://dusselle.fr/**

Vous devriez voir l'interface de veille juridique !

### Tester l'API :

```bash
curl https://dusselle.fr/api/stats
```

---

## 🔧 Si vous rencontrez des problèmes

### Problème : "Module not found"

```bash
cd ~/veille_app
source venv/bin/activate
pip install -r requirements.txt
```

### Problème : "Permission denied" sur database.db

```bash
chmod 666 ~/veille_app/database.db
```

### Problème : Page blanche ou erreur 500

Vérifiez les logs dans cPanel :
- **Error Log** dans cPanel
- Ou via terminal : `tail -f ~/logs/stderr.log`

### Problème : Le répertoire n'existe toujours pas

```bash
# Créer le répertoire manuellement
mkdir -p ~/veille_app
cd ~/veille_app
pwd  # Vérifier où vous êtes
```

---

## 📁 Vérifier que tous les fichiers sont présents

```bash
cd ~/veille_app
ls -la

# Fichiers essentiels à vérifier :
# ✅ app.py
# ✅ wsgi.py
# ✅ config.py
# ✅ models.py
# ✅ requirements.txt
# ✅ templates/ (dossier)
# ✅ static/ (dossier)
# ✅ database.db (après init)
```

---

## 🎯 Configuration du Cron (optionnel)

Pour mettre à jour automatiquement les flux :

1. Dans cPanel → **Cron Jobs**
2. Ajoutez :

```bash
0 */6 * * * cd ~/veille_app && python app.py --update >> ~/logs/rss-update.log 2>&1
```

Cela actualisera les flux toutes les 6 heures.

---

## ✅ Checklist finale

- [ ] Archive uploadée et extraite dans `~/veille_app/`
- [ ] Dépendances installées (`pip install...`)
- [ ] Base de données initialisée (`python app.py --init`)
- [ ] Flux d'exemple ajoutés (`python app.py --sample`)
- [ ] Application configurée dans cPanel Python App
- [ ] Application redémarrée dans cPanel
- [ ] Test : https://dusselle.fr/ fonctionne
- [ ] Test : https://dusselle.fr/api/stats retourne des données

---

## 🆘 Besoin d'aide ?

Si vous êtes bloqué sur une étape, voici ce qu'il faut vérifier :

1. **Quel est votre répertoire actuel ?**
   ```bash
   pwd
   ```

2. **L'environnement virtuel est-il activé ?**
   ```bash
   which python
   # Devrait montrer quelque chose comme ~/veille_app/venv/bin/python
   ```

3. **Les fichiers sont-ils tous présents ?**
   ```bash
   ls -la ~/veille_app/
   ```

4. **Python fonctionne-t-il ?**
   ```bash
   python --version
   # Devrait afficher Python 3.8.x
   ```

---

**Bonne chance ! 🚀**

Une fois terminé, vous aurez une application de veille juridique complète et fonctionnelle sur https://dusselle.fr/
