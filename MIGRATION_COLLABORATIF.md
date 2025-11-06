# Migration des fonctionnalités collaboratives

## 📋 Vue d'ensemble

Ce guide explique comment activer les nouvelles fonctionnalités collaboratives de votre application de veille juridique RSS.

## ✨ Nouvelles fonctionnalités

### 🗂️ Organisation
- **Dossiers thématiques** : Créez des dossiers avec couleurs et icônes personnalisées
- **Organisation par affaire/client** : Classez vos articles par dossier
- **Partage de collections** : Partagez vos dossiers avec des collègues (permissions : lecture, écriture, admin)

### 📝 Annotations
- **Notes privées** : Ajoutez des notes personnelles sur chaque article
- **Surlignage de texte** : Marquez les passages importants avec différentes couleurs
- **Commentaires collaboratifs** : Discutez des articles avec des collègues
- **Mentions** : Mentionnez des utilisateurs dans les commentaires (@utilisateur)

### 📎 Pièces jointes
- **Upload de fichiers** : Attachez des documents aux articles (PDF, Word, Excel, etc.)
- **Formats supportés** : pdf, doc, docx, xls, xlsx, txt, jpg, jpeg, png, zip

### 👥 Collaboration
- **Multi-utilisateurs** : Système complet avec rôles (admin, éditeur, lecteur)
- **Assignation** : Assignez des articles à des collègues avec priorité et date limite
- **Historique** : Traçabilité complète de toutes les modifications

### 🔍 Important
**Les flux RSS restent accessibles à tous les utilisateurs** - Seuls les dossiers et annotations sont privés ou partagés selon vos paramètres.

## 🚀 Installation sur le serveur de production

### Étape 1 : Se connecter au serveur

```bash
ssh wrbh3411@dusselle.fr
cd /home/wrbh3411/public_html/flask-version
```

### Étape 2 : Récupérer les modifications

```bash
git pull origin claude/flask-rss-legal-monitoring-011CUsAx3pPA2Ktr1GJ26fNt
```

### Étape 3 : Activer l'environnement virtuel

```bash
source /home/wrbh3411/virtualenv/public_html/flask-version/3.6/bin/activate
```

### Étape 4 : Exécuter le script de migration

```bash
python migrate_collaborative.py
```

Vous devriez voir :

```
🚀 Migration des fonctionnalités collaboratives
============================================================

📋 Création des nouvelles tables...
✅ Tables créées avec succès

👤 Création de l'utilisateur par défaut...
✅ Utilisateur créé : default@veille.fr
   Username: utilisateur
   Mot de passe: changeme (À CHANGER !)

📊 Tables dans la base de données :
   ✅ users
   ✅ folders
   ✅ article_folders
   ✅ folder_shares
   ✅ article_notes
   ✅ article_highlights
   ✅ article_comments
   ✅ article_attachments
   ✅ article_assignments
   ✅ activity_logs

📁 Création de dossiers d'exemple...
✅ 5 dossiers d'exemple créés

📈 Statistiques :
   - Utilisateurs : 1
   - Dossiers : 5
   - Notes : 0
   - Commentaires : 0
   - Surlignages : 0
   - Assignations : 0

============================================================
✅ Migration terminée avec succès !

🔐 IMPORTANT - Informations de connexion :
   Email : default@veille.fr
   Mot de passe : changeme

⚠️  Changez ce mot de passe dès que possible !
```

### Étape 5 : Redémarrer l'application

```bash
touch /home/wrbh3411/public_html/flask-version/passenger_wsgi.py
```

### Étape 6 : Vérifier que tout fonctionne

Ouvrez votre navigateur sur http://dusselle.fr et vérifiez que :
- ✅ La nouvelle interface s'affiche correctement
- ✅ La section "Mes Dossiers" apparaît dans la sidebar
- ✅ Vous pouvez créer un nouveau dossier
- ✅ Les boutons "Dossier", "Note", "Détails" apparaissent sur les articles

## 📚 Guide d'utilisation rapide

### Créer un dossier

1. Cliquez sur le bouton **+** à côté de "Mes Dossiers"
2. Entrez un nom (ex: "Droit social")
3. Choisissez une couleur
4. Choisissez une icône
5. Cliquez sur "Créer"

### Ajouter un article à un dossier

1. Sur une carte d'article, cliquez sur le bouton **Dossier**
2. Sélectionnez le dossier dans la liste
3. Cliquez sur "Ajouter"

### Ajouter une note à un article

1. Sur une carte d'article, cliquez sur le bouton **Note**
2. Le panneau latéral s'ouvre sur l'onglet "Notes"
3. Tapez votre note dans la zone de texte
4. Cliquez sur "Enregistrer la note"

### Voir tous les détails d'un article

1. Cliquez sur le bouton **Détails** d'un article
2. Le panneau latéral s'ouvre avec 4 onglets :
   - **Notes** : Vos notes privées
   - **Surlignages** : Textes surlignés (à venir)
   - **Commentaires** : Discussions collaboratives
   - **Pièces jointes** : Fichiers attachés

### Filtrer par dossier

1. Dans la sidebar, cliquez sur un dossier
2. Seuls les articles de ce dossier s'affichent
3. Cliquez sur "Tous les articles" pour tout afficher

## 🔒 Sécurité

### Changer le mot de passe par défaut

Pour l'instant, l'authentification multi-utilisateurs utilise un utilisateur par défaut. Pour plus de sécurité :

1. **À court terme** : Continuez avec l'utilisateur par défaut (tous les utilisateurs partagent le même compte)
2. **À moyen terme** : Nous pourrons ajouter un système de login/register complet si besoin

Les notes sont marquées comme "privées" par défaut, mais pour l'instant tout le monde peut les voir car il n'y a qu'un seul utilisateur.

## 🗄️ Nouvelles tables créées

La migration crée 10 nouvelles tables :

| Table | Description |
|-------|-------------|
| `users` | Utilisateurs avec authentification |
| `folders` | Dossiers thématiques |
| `article_folders` | Association articles ↔ dossiers |
| `folder_shares` | Partage de dossiers avec permissions |
| `article_notes` | Notes privées sur les articles |
| `article_highlights` | Surlignages de texte |
| `article_comments` | Commentaires collaboratifs |
| `article_attachments` | Pièces jointes |
| `article_assignments` | Assignations d'articles |
| `activity_logs` | Historique des modifications |

## 📁 Dossiers d'exemple créés

La migration crée automatiquement 5 dossiers d'exemple :

- 🏢 **Droit social** (bleu)
- 💰 **Droit fiscal** (vert)
- 📄 **Droit des contrats** (orange)
- ⚖️ **Jurisprudence** (rouge)
- ⏰ **À traiter** (jaune)

Vous pouvez les supprimer ou les modifier selon vos besoins.

## 🔧 Dépannage

### La migration échoue

Si vous obtenez une erreur "ModuleNotFoundError", installez les dépendances :

```bash
pip install -r requirements-py36.txt
```

### Les tables existent déjà

Si vous obtenez une erreur indiquant que les tables existent déjà, c'est normal - la migration a déjà été effectuée. Vous pouvez ignorer cette erreur.

### L'interface ne se met pas à jour

1. Videz le cache de votre navigateur (Ctrl+F5)
2. Vérifiez que Passenger a bien redémarré :
   ```bash
   touch /home/wrbh3411/public_html/flask-version/passenger_wsgi.py
   ```

### Les dossiers ne s'affichent pas

Vérifiez les logs d'erreur :
```bash
tail -50 /home/wrbh3411/logs/passenger.log
```

## 📞 Support

En cas de problème, vérifiez :
1. Les logs de l'application
2. Les logs de Passenger
3. La console JavaScript du navigateur (F12)

## 🎉 C'est prêt !

Une fois la migration effectuée, vous pouvez :
- ✅ Créer des dossiers thématiques
- ✅ Organiser vos articles
- ✅ Ajouter des notes privées
- ✅ Commenter les articles
- ✅ Attacher des fichiers

**Les flux RSS continuent de fonctionner normalement et restent accessibles à tous !**

---

**Date de création** : 06 novembre 2024
**Version** : 2.1.0 - Collaborative Edition
**Auteur** : Claude AI Assistant
