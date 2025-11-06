# Configuration du Cron pour actualisation automatique

## 🎯 Objectif

Actualiser automatiquement tous les flux RSS **tous les jours** sans intervention manuelle.

## 📝 Instructions

### Étape 1 : Tester le script manuellement

D'abord, testez que le script fonctionne correctement :

```bash
cd /home/wrbh3411/public_html/flask-version
python auto_refresh_feeds.py
```

Vous devriez voir :
```
🔄 Actualisation automatique des flux RSS - 06/11/2024 22:30:15

📡 6 flux à actualiser

  📥 Legifrance... ✅ 3 nouveau(x) article(s)
  📥 Journal Officiel... ✅ 1 nouveau(x) article(s)
  ...

📊 Résumé de l'actualisation :
   - Flux actualisés : 6/6
   - Erreurs : 0
   - Nouveaux articles : 12

✅ Actualisation terminée avec succès !
```

### Étape 2 : Configurer le cron job

Une fois le test réussi, configurez l'actualisation automatique quotidienne :

```bash
# Ouvrir l'éditeur cron
crontab -e
```

**Ajoutez cette ligne** (actualisation tous les jours à **2h du matin**) :

```cron
0 2 * * * cd /home/wrbh3411/public_html/flask-version && /home/wrbh3411/virtualenv/public_html/flask-version/3.6/bin/python auto_refresh_feeds.py >> /home/wrbh3411/logs/rss_refresh.log 2>&1
```

### Étape 3 : Créer le dossier de logs

```bash
# Créer le dossier pour les logs
mkdir -p /home/wrbh3411/logs
```

### Étape 4 : Sauvegarder et vérifier

Après avoir ajouté la ligne cron :

1. **Sauvegarder** : `Ctrl+X` puis `Y` puis `Entrée` (si nano)
2. **Vérifier** que le cron est bien configuré :

```bash
crontab -l
```

Vous devriez voir votre ligne de cron.

## 🕐 Horaires possibles

Vous pouvez choisir un autre horaire selon vos besoins :

| Horaire | Ligne cron |
|---------|------------|
| **2h du matin** (recommandé) | `0 2 * * *` |
| 6h du matin | `0 6 * * *` |
| Midi | `0 12 * * *` |
| Minuit | `0 0 * * *` |
| Toutes les 12h (2h et 14h) | `0 2,14 * * *` |
| Toutes les 6h | `0 */6 * * *` |

## 📊 Consulter les logs

Pour voir les résultats des actualisations automatiques :

```bash
# Voir les dernières actualisations
tail -50 /home/wrbh3411/logs/rss_refresh.log

# Suivre en temps réel (si vous lancez manuellement)
tail -f /home/wrbh3411/logs/rss_refresh.log
```

## 🧪 Tester manuellement l'actualisation

Vous pouvez toujours lancer l'actualisation manuellement quand vous voulez :

```bash
cd /home/wrbh3411/public_html/flask-version
python auto_refresh_feeds.py
```

## 🔧 Dépannage

### Le cron ne s'exécute pas ?

1. **Vérifier que le cron est bien configuré** :
   ```bash
   crontab -l
   ```

2. **Vérifier les logs du système** :
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

3. **Tester le chemin complet** :
   ```bash
   /home/wrbh3411/virtualenv/public_html/flask-version/3.6/bin/python --version
   ```

### Pas de nouveaux articles ?

C'est normal si :
- Les flux n'ont pas publié de nouveaux articles depuis la dernière actualisation
- Le script a déjà récupéré tous les articles disponibles

### Erreurs dans les logs ?

```bash
# Voir les erreurs récentes
tail -100 /home/wrbh3411/logs/rss_refresh.log | grep "❌"
```

## ✅ Résumé

Une fois configuré, votre application va :

- ✅ **Actualiser automatiquement** tous les flux RSS tous les jours à 2h du matin
- ✅ **Garder tous les articles à vie** (pas de suppression)
- ✅ **Logger toutes les actualisations** dans `/home/wrbh3411/logs/rss_refresh.log`
- ✅ **Continuer même en cas d'erreur** sur un flux (les autres seront actualisés)

---

**Date de création** : 06 novembre 2024
**Configuration** : Actualisation quotidienne à 2h du matin
**Rétention** : Articles conservés à vie
