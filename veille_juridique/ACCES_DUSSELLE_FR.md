# 🌐 Comment accéder à l'application sur dusselle.fr

## 📊 Situation actuelle

✅ **Application fonctionnelle** : L'application Flask tourne correctement en local sur le port 80
❌ **Accès externe bloqué** : dusselle.fr retourne un **403 Forbidden**

## 🔍 Diagnostic

Le problème vient de l'infrastructure réseau :
- L'application tourne dans un **conteneur gVisor (runsc)** isolé
- Il y a un **reverse proxy / load balancer** qui bloque l'accès externe
- Les ports ne sont pas exposés au niveau de l'infrastructure cloud

## 💡 Solutions pour rendre l'application accessible

### Option 1 : Configuration via cPanel (⭐ Recommandé)

Si vous avez accès à **cPanel** sur dusselle.fr :

1. **Connectez-vous à cPanel** (https://dusselle.fr:2083)

2. **Option A : Python App Selector**
   - Allez dans **"Setup Python App"**
   - Créez une nouvelle application
   - Uploadez les fichiers de `veille_juridique/`
   - Suivez le guide : [DEPLOIEMENT_CPANEL.md](DEPLOIEMENT_CPANEL.md)

3. **Option B : Utiliser Passenger (Phusion Passenger)**
   - Uploadez les fichiers dans `public_html/veille_juridique/`
   - Créez `passenger_wsgi.py` à la racine web
   - Configurez `.htaccess` pour router vers l'app
   - Voir détails dans [DEPLOIEMENT_CPANEL.md](DEPLOIEMENT_CPANEL.md)

### Option 2 : Déploiement sur le serveur principal

Si vous avez un accès SSH au serveur principal dusselle.fr :

```bash
# 1. Se connecter au serveur
ssh votre-user@dusselle.fr

# 2. Créer le répertoire de l'application
mkdir -p ~/veille_juridique
cd ~/veille_juridique

# 3. Télécharger/cloner l'application
git clone <votre-repo> .
# OU uploader via FTP/SCP

# 4. Installer les dépendances
pip3 install --user -r requirements.txt

# 5. Initialiser la base de données
python3 app.py --init
python3 app.py --sample

# 6. Démarrer avec Gunicorn
chmod +x start.sh
./start.sh

# 7. Configurer le reverse proxy (voir ci-dessous)
```

### Option 3 : Configuration du reverse proxy

Si vous gérez l'infrastructure cloud :

#### Pour Apache

Créer/modifier `/etc/apache2/sites-available/dusselle.fr.conf` :

```apache
<VirtualHost *:80>
    ServerName dusselle.fr
    ServerAlias www.dusselle.fr

    # Reverse proxy vers l'application Flask
    ProxyPreserveHost On
    ProxyPass / http://21.0.0.146:80/
    ProxyPassReverse / http://21.0.0.146:80/

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/dusselle_error.log
    CustomLog ${APACHE_LOG_DIR}/dusselle_access.log combined
</VirtualHost>
```

Puis :
```bash
sudo a2enmod proxy proxy_http
sudo systemctl restart apache2
```

#### Pour Nginx

Créer/modifier `/etc/nginx/sites-available/dusselle.fr` :

```nginx
server {
    listen 80;
    server_name dusselle.fr www.dusselle.fr;

    location / {
        proxy_pass http://21.0.0.146:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Puis :
```bash
sudo ln -s /etc/nginx/sites-available/dusselle.fr /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Option 4 : Exposer les ports dans Docker/Kubernetes

Si l'application tourne dans un conteneur Docker/K8s :

#### Docker

```bash
# Arrêter le conteneur actuel
docker stop <container-id>

# Redémarrer en exposant le port
docker run -p 80:80 -p 443:443 <image-name>
```

#### Kubernetes

Créer un Service de type LoadBalancer :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: veille-juridique
spec:
  type: LoadBalancer
  selector:
    app: veille-juridique
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
```

### Option 5 : Utiliser un tunnel (Solution temporaire)

Pour tester rapidement :

#### Avec Ngrok

```bash
# Installer ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz

# Créer un tunnel
./ngrok http 80

# Vous obtenez une URL publique : https://xyz.ngrok.io
```

#### Avec Cloudflare Tunnel

```bash
# Installer cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64

# Créer un tunnel
./cloudflared-linux-amd64 tunnel --url http://localhost:80
```

## 🎯 Méthode recommandée pour vous

Étant donné que vous avez mentionné avoir accès à un **panel de contrôle (cPanel)** :

### 📝 **Étapes à suivre** :

1. **Téléchargez tous les fichiers** du dossier `veille_juridique/` sur votre ordinateur

2. **Connectez-vous à cPanel** sur dusselle.fr

3. **Suivez le guide de déploiement** : [DEPLOIEMENT_CPANEL.md](DEPLOIEMENT_CPANEL.md)

4. **Uploadez les fichiers** via File Manager ou FTP

5. **Configurez l'application Python** dans cPanel

6. **Testez** en accédant à https://dusselle.fr/

## ✅ Checklist de vérification

Avant de déployer, assurez-vous d'avoir :

- [ ] Accès cPanel/SSH à dusselle.fr
- [ ] Tous les fichiers de `veille_juridique/` téléchargés
- [ ] Python 3.8+ disponible sur le serveur
- [ ] Permissions d'écriture dans le répertoire web
- [ ] Accès aux logs pour débogage

## 📞 Que faire si ça ne fonctionne toujours pas ?

1. **Vérifiez les logs Apache/Nginx** :
   ```bash
   tail -f /var/log/apache2/error.log
   # ou
   tail -f /var/log/nginx/error.log
   ```

2. **Vérifiez que l'app tourne** :
   ```bash
   ps aux | grep gunicorn
   curl http://localhost/api/stats
   ```

3. **Vérifiez les permissions** :
   ```bash
   ls -la ~/veille_juridique/
   chmod 755 ~/veille_juridique/
   ```

4. **Contactez votre hébergeur** pour :
   - Activer Python Apps dans cPanel
   - Exposer les ports nécessaires
   - Configurer le reverse proxy

## 🚀 Alternative : Hébergement sur une autre plateforme

Si dusselle.fr ne supporte pas Python, vous pouvez héberger l'application sur :

- **Heroku** (gratuit pour petits projets)
- **PythonAnywhere** (gratuit avec limitations)
- **Render** (gratuit avec limitations)
- **DigitalOcean App Platform** (5$/mois)
- **AWS Lightsail** (3.50$/mois)

Puis configurer un sous-domaine de dusselle.fr (ex: veille.dusselle.fr) pour pointer vers cette plateforme.

---

## 📄 Fichiers importants

- `DEPLOIEMENT_CPANEL.md` - Guide complet de déploiement cPanel
- `README_FLASK.md` - Documentation de l'application
- `start.sh` - Script de démarrage automatique
- `wsgi.py` - Point d'entrée WSGI

---

**N'hésitez pas à me contacter si vous rencontrez des difficultés !**
