# Guide Frontend - HTMX et Templates

> Ce document explique comment fonctionne le frontend avec HTMX et Jinja2.

## Philosophie : Hypermedia-Driven Development

### Le problème des SPAs

Les Single Page Applications (React, Vue) ont des inconvénients :
- **Complexité** : Beaucoup de code JavaScript
- **SEO difficile** : Le contenu est généré côté client
- **Bundle lourd** : Temps de chargement élevé
- **État complexe** : Gestion de l'état côté client

### La solution HTMX

HTMX permet de créer des interfaces dynamiques sans JavaScript complexe :

```html
<!-- Un bouton qui charge du contenu sans JavaScript -->
<button hx-get="/api/cars" hx-target="#results">
    Charger les voitures
</button>
```

**Comment ça marche** :
1. L'utilisateur clique sur le bouton
2. HTMX fait une requête GET vers `/api/cars`
3. Le serveur répond avec du HTML (pas du JSON)
4. HTMX insère le HTML dans `#results`

## Templates Jinja2

### Structure de base

```html
<!-- base.html - Le template parent -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Spass Gasy{% endblock %}</title>
</head>
<body>
    <nav>...</nav>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>...</footer>
</body>
</html>
```

```html
<!-- index.html - Le template enfant -->
{% extends "base.html" %}

{% block title %}Accueil{% endblock %}

{% block content %}
<h1>Bienvenue</h1>
{% endblock %}
```

### Variables et filtres

```html
<!-- Afficher une variable -->
<h1>{{ car.brand }}</h1>

<!-- Filtres -->
<p>{{ car.daily_price|round }}</p>          <!-- Arrondir -->
<p>{{ car.description|truncate(50) }}</p>   <!-- Tronquer -->
<p>{{ car.created_at|date("Y-m-d") }}</p>   <!-- Formater date -->
<p>{{ name|default("Anonyme") }}</p>         <!-- Valeur par défaut -->
```

### Boucles et conditions

```html
<!-- Boucle -->
{% for car in cars %}
<div>
    <h3>{{ car.brand }} {{ car.model }}</h3>
    {% if car.is_available %}
        <span class="badge">Disponible</span>
    {% else %}
        <span class="badge">Indisponible</span>
    {% endif %}
</div>
{% endfor %}

<!-- Condition -->
{% if user.is_admin %}
    <a href="/admin">Panneau admin</a>
{% elif user.is_staff %}
    <a href="/staff">Panneau staff</a>
{% else %}
    <p>Connectez-vous</p>
{% endif %}
```

### Inclusions

```html
<!-- Inclure un autre template -->
{% include "partials/_header.html" %}

<!-- Inclure avec des variables -->
{% include "partials/_car_card.html" with car=featured_car %}
```

## HTMX en détail

### Attributs principaux

| Attribut | Description | Exemple |
|----------|-------------|---------|
| `hx-get` | Requête GET | `hx-get="/api/cars"` |
| `hx-post` | Requête POST | `hx-post="/api/booking"` |
| `hx-target` | Où insérer la réponse | `hx-target="#results"` |
| `hx-trigger` | Événement déclencheur | `hx-trigger="click"` |
| `hx-swap` | Comment insérer | `hx-swap="innerHTML"` |

### Exemples concrets

#### Chargement initial

```html
<!-- Charger du contenu au chargement de la page -->
<div hx-get="/api/cars/popular"
     hx-trigger="load"
     hx-indicator="#loading">
    <div id="loading">Chargement...</div>
</div>
```

#### Formulaire de recherche

```html
<!-- Recherche en temps réel -->
<input type="text"
       name="q"
       hx-get="/api/cars/search"
       hx-trigger="input changed delay:500ms"
       hx-target="#results"
       placeholder="Rechercher...">

<div id="results"></div>
```

**Explication** :
- `input` : Déclenché à chaque frappe
- `changed` : Seulement si la valeur a changé
- `delay:500ms` : Attendre 500ms après la dernière frappe

#### Bouton avec confirmation

```html
<button hx-delete="/api/cars/1"
        hx-confirm="Êtes-vous sûr de vouloir supprimer ?"
        hx-target="#car-1"
        hx-swap="outerHTML">
    Supprimer
</button>
```

#### Indicateur de chargement

```html
<button hx-get="/api/cars"
        hx-indicator="#spinner">
    Charger
</button>

<div id="spinner" class="htmx-indicator">
    <div class="spinner"></div>
</div>

<style>
.htmx-indicator {
    display: none;
}
.htmx-request .htmx-indicator {
    display: block;
}
</style>
```

### HX-Boost

Pour activer les transitions de page entières :

```html
<body hx-boost="true">
    <!-- Tous les liens et formulaires utilisent HTMX -->
    <a href="/cars">Voitures</a>  <!-- Navigation via HTMX -->
</body>
```

## Tailwind CSS

### Classes utilitaires

```html
<!-- Padding -->
<p class="p-4">...</p>      <!-- padding: 1rem -->
<p class="px-6 py-2">...</p> <!-- padding-x: 1.5rem, padding-y: 0.5rem -->

<!-- Margin -->
<p class="m-4">...</p>     <!-- margin: 1rem -->
<p class="mt-8">...</p>    <!-- margin-top: 2rem -->

<!-- Flex -->
<div class="flex items-center justify-between">
    ...
</div>

<!-- Grid -->
<div class="grid grid-cols-3 gap-4">
    ...
</div>

<!-- Responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
    <!-- 1 colonne sur mobile, 2 sur tablette, 3 sur desktop -->
</div>
```

### Classes personnalisées

Dans `static/css/style.css`, ajoutez vos classes :

```css
.btn-primary {
    background-color: #4f46e5;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
}
```

Utilisation :

```html
<button class="btn-primary">Cliquez</button>
```

## Navigation mobile

### Barre inférieure

```html
<nav class="fixed bottom-0 left-0 right-0 bg-white border-t">
    <div class="flex justify-around">
        <a href="/" class="flex flex-col items-center">
            <svg>...</svg>
            <span>Accueil</span>
        </a>
        <!-- ... autres liens -->
    </div>
</nav>
```

### Safe Area (iOS)

```html
<style>
nav {
    padding-bottom: env(safe-area-inset-bottom);
}
</style>
```

## Bonnes pratiques

### 1. Templating

```html
<!-- ✅ Bon : Template clair et organisé -->
{% for car in cars %}
<div class="car-card">
    <h3>{{ car.brand }} {{ car.model }}</h3>
    <p>{{ car.daily_price|format_price }}</p>
</div>
{% endfor %}

<!-- ❌ Mauvais : Logique dans le template -->
{% for car in cars %}
<div class="car-card">
    <h3>{{ car.brand }} {{ car.model }}</h3>
    <p>
        {% if car.daily_price > 50000 %}
            {{ car.daily_price * 0.9 }}
        {% else %}
            {{ car.daily_price }}
        {% endif %}
    </p>
</div>
{% endfor %}
```

**Solution** : Créer un filtre personnalisé

```python
# Dans main.py
from jinja2 import Environment

def format_price(value):
    return f"{value:,.0f} Ar"

templates.env.filters['format_price'] = format_price
```

### 2. HTMX

```html
<!-- ✅ Bon : Indicateur de chargement -->
<button hx-get="/api/cars"
        hx-indicator="#loading">
    Charger
</button>
<span id="loading" class="htmx-indicator">Chargement...</span>

<!-- ❌ Mauvais : Pas de feedback -->
<button hx-get="/api/cars">
    Charger
</button>
```

### 3. Accessibilité

```html
<!-- ✅ Bon : Labels et aria -->
<button aria-label="Fermer le menu">
    <svg aria-hidden="true">...</svg>
</button>

<!-- ❌ Mauvais : Pas d'accessibilité -->
<button>
    <svg>...</svg>
</button>
```

## Débogage

### Voir les requêtes HTMX

Ajoutez cet attribut pour voir les en-têtes :

```html
<body hx-ext="debug">
```

### Console du navigateur

```javascript
// Voir les événements HTMX
document.body.addEventListener('htmx:beforeRequest', (e) => {
    console.log('Request:', e.detail.pathInfo.requestPath);
});
```

## Questions fréquentes

### Comment gérer les erreurs HTMX ?

```python
# Côté serveur, retourner un code d'erreur
@app.get("/api/cars")
async def get_cars():
    try:
        cars = await get_all_cars()
        return templates.TemplateResponse("partials/_cars.html", {"cars": cars})
    except Exception:
        # Retourner une erreur 500 avec un message
        return HTMLResponse("Erreur lors du chargement", status_code=500)
```

```html
<!-- Côté client, gérer l'erreur -->
<div hx-get="/api/cars"
     hx-target="#results"
     hx-on="htmx:beforeSwap:if(event.detail.xhr.status === 500) {
         alert('Erreur serveur');
     }">
</div>
```

### Comment pré-charger du contenu ?

```html
<!-- Pré-charger au survol -->
<a href="/cars/1"
   hx-get="/api/cars/1/preview"
   hx-trigger="mouseenter"
   hx-target="#preview">
    Voiture 1
</a>
```

### Comment ajouter des animations ?

```html
<style>
.fade-in {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>

<div hx-get="/api/cars"
     hx-swap="innerHTML transition:0.3s"
     class="fade-in">
</div>
```