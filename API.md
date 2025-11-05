# 📡 Documentation API

## Vue d'ensemble

L'API REST de Veille Juridique RSS permet de gérer les flux RSS et les articles.

**Base URL** : `https://dusselle.fr/api/`

---

## 📌 Endpoints disponibles

### 1. Récupérer les articles depuis les flux

Récupère tous les articles depuis tous les flux RSS configurés.

**Endpoint** : `GET /api/fetch-feeds.php`

**Réponse** :
```json
{
  "success": true,
  "feeds_processed": 4,
  "articles_added": 23,
  "message": "4 flux traité(s), 23 nouvel(aux) article(s) ajouté(s)",
  "errors": []
}
```

**Exemple d'erreur** :
```json
{
  "success": true,
  "feeds_processed": 3,
  "articles_added": 15,
  "errors": [
    {
      "feed": "Legifrance",
      "error": "Impossible de récupérer le flux"
    }
  ]
}
```

**Utilisation JavaScript** :
```javascript
fetch('/api/fetch-feeds.php')
  .then(res => res.json())
  .then(data => {
    console.log(data.message);
  });
```

---

### 2. Ajouter un flux RSS

Ajoute un nouveau flux RSS à la base de données.

**Endpoint** : `POST /api/add-feed.php`

**Paramètres (JSON)** :
```json
{
  "name": "Nom du flux",
  "url": "https://exemple.com/rss.xml",
  "category": "Catégorie"
}
```

**Réponse succès** :
```json
{
  "success": true,
  "message": "Flux ajouté avec succès"
}
```

**Réponse erreur** :
```json
{
  "success": false,
  "error": "URL invalide ou erreur lors de l'ajout"
}
```

**Utilisation JavaScript** :
```javascript
fetch('/api/add-feed.php', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Dalloz',
    url: 'https://www.dalloz-actualite.fr/feed',
    category: 'Doctrine'
  })
})
.then(res => res.json())
.then(data => console.log(data.message));
```

---

### 3. Mettre à jour un flux RSS

Met à jour un flux RSS existant.

**Endpoint** : `POST /api/update-feed.php`

**Paramètres (JSON)** :
```json
{
  "id": 1,
  "name": "Nouveau nom",
  "url": "https://exemple.com/rss.xml",
  "category": "Nouvelle catégorie"
}
```

**Réponse succès** :
```json
{
  "success": true,
  "message": "Flux mis à jour avec succès"
}
```

**Réponse erreur** :
```json
{
  "success": false,
  "error": "URL invalide ou erreur lors de la mise à jour"
}
```

**Utilisation JavaScript** :
```javascript
fetch('/api/update-feed.php', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id: 1,
    name: 'Legifrance Actualités',
    url: 'https://www.legifrance.gouv.fr/rss/actualites.xml',
    category: 'Législation'
  })
})
.then(res => res.json())
.then(data => console.log(data.message));
```

---

### 4. Supprimer un flux RSS

Supprime un flux RSS et tous ses articles associés.

**Endpoint** : `POST /api/delete-feed.php`

**Paramètres (JSON)** :
```json
{
  "id": 1
}
```

**Réponse succès** :
```json
{
  "success": true,
  "message": "Flux supprimé avec succès"
}
```

**Réponse erreur** :
```json
{
  "success": false,
  "error": "Erreur lors de la suppression"
}
```

**Utilisation JavaScript** :
```javascript
fetch('/api/delete-feed.php', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id: 1 })
})
.then(res => res.json())
.then(data => console.log(data.message));
```

---

### 5. Rechercher des articles

Recherche des articles par mot-clé dans le titre, la description ou le nom du flux.

**Endpoint** : `GET /api/search.php?q={keyword}`

**Paramètres** :
- `q` (string, requis) : Mot-clé de recherche

**Réponse** :
```json
{
  "success": true,
  "count": 12,
  "articles": [
    {
      "id": 1,
      "title": "Nouvelle loi sur...",
      "link": "https://...",
      "description": "...",
      "pub_date": "2024-11-05 14:30:00",
      "feed_name": "Legifrance",
      "category": "Législation",
      "created_at": "2024-11-05 14:35:00"
    }
  ]
}
```

**Utilisation JavaScript** :
```javascript
const keyword = 'réforme';
fetch(`/api/search.php?q=${encodeURIComponent(keyword)}`)
  .then(res => res.json())
  .then(data => {
    console.log(`${data.count} article(s) trouvé(s)`);
    console.log(data.articles);
  });
```

---

## 🔒 Codes de statut HTTP

| Code | Signification |
|------|---------------|
| 200  | Succès |
| 400  | Requête invalide (paramètres manquants ou invalides) |
| 405  | Méthode HTTP non autorisée |
| 500  | Erreur serveur |

---

## 🛡️ Sécurité

- Toutes les requêtes SQL utilisent des **requêtes préparées** (protection contre injection SQL)
- Les URL de flux RSS sont **validées** avant ajout
- Les données en sortie sont **échappées** pour prévenir les attaques XSS
- Headers de sécurité configurés via `.htaccess`

---

## 📊 Exemple d'intégration complète

```javascript
// Classe API pour simplifier les appels
class RSSAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  async fetchFeeds() {
    const res = await fetch(`${this.baseURL}/fetch-feeds.php`);
    return res.json();
  }

  async addFeed(name, url, category = 'Général') {
    const res = await fetch(`${this.baseURL}/add-feed.php`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, url, category })
    });
    return res.json();
  }

  async updateFeed(id, name, url, category) {
    const res = await fetch(`${this.baseURL}/update-feed.php`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, name, url, category })
    });
    return res.json();
  }

  async deleteFeed(id) {
    const res = await fetch(`${this.baseURL}/delete-feed.php`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id })
    });
    return res.json();
  }

  async search(keyword) {
    const res = await fetch(`${this.baseURL}/search.php?q=${encodeURIComponent(keyword)}`);
    return res.json();
  }
}

// Utilisation
const api = new RSSAPI();

// Actualiser les flux
await api.fetchFeeds();

// Ajouter un flux
await api.addFeed('Dalloz', 'https://www.dalloz-actualite.fr/feed', 'Doctrine');

// Rechercher
const results = await api.search('réforme');
console.log(results.articles);
```

---

## 🧪 Test avec cURL

```bash
# Récupérer les flux
curl https://dusselle.fr/api/fetch-feeds.php

# Ajouter un flux
curl -X POST https://dusselle.fr/api/add-feed.php \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","url":"https://exemple.com/rss.xml","category":"Test"}'

# Rechercher
curl "https://dusselle.fr/api/search.php?q=loi"

# Supprimer un flux
curl -X POST https://dusselle.fr/api/delete-feed.php \
  -H "Content-Type: application/json" \
  -d '{"id":1}'
```

---

Pour toute question, consultez le fichier **README.md** principal.
