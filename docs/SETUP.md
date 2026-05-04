# Guide d'installation et de configuration

> Ce document explique comment installer et configurer le projet.

## Prérequis

- **Python 3.11+** : Le projet utilise les dernières fonctionnalités de Python
- **pip** : Gestionnaire de packages Python
- **Un éditeur de code** : VS Code recommandé avec l'extension Python
- **Connexion internet** : Obligatoire pour Leaflet, BRouter et Nominatim (APIs externes)

## Installation

### 1. Cloner le projet

```bash
cd /chemin/vers/votre/dossier
git clone <url-du-repo>
cd Spass_gasy
```

### 2. Créer un environnement virtuel

**Pourquoi un environnement virtuel ?**
- Isole les dépendances du projet
- Évite les conflits avec d'autres projets
- Permet de reproduire l'environnement de production

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Sur macOS/Linux :
source venv/bin/activate

# Sur Windows :
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

**Contenu de requirements.txt expliqué :**

| Package | Version | Utilité |
|---------|---------|---------|
| fastapi | >=0.109.0 | Framework web |
| uvicorn | >=0.27.0 | Serveur ASGI |
| jinja2 | >=3.1.0 | Templates HTML |
| sqlalchemy | >=2.0.0 | ORM base de données |
| aiosqlite | >=0.0.19 | Driver SQLite async |
| pydantic | >=2.5.0 | Validation des données |
| alembic | >=1.13.0 | Migrations base de données |

**Librairies front chargées via CDN (aucune installation) :**

| Librairie | CDN | Utilité |
|-----------|-----|---------|
| Leaflet.js 1.9.4 | unpkg.com | Carte interactive |
| Tailwind CSS | cdn.tailwindcss.com | Styles utilitaires |
| HTMX 1.9.10 | unpkg.com | Interactions dynamiques |
| Alpine.js 3.x | jsdelivr.net | Micro-interactions JS |

> **Important** : Leaflet, BRouter et Nominatim nécessitent une connexion internet. La carte ne fonctionnera pas hors ligne.

### 4. Lancer l'application

```bash
# Méthode 1 : Avec le script run.py
python run.py

# Méthode 2 : Avec uvicorn directement
uvicorn app.main:app --reload

# Méthode 3 : Préciser l'hôte et le port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Accéder à l'application

Ouvrez votre navigateur et allez à :
- **Application** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc

## Structure des fichiers

```
Spass_gasy/
├── app/                    # Code de l'application
│   ├── main.py            # Point d'entrée
│   ├── models.py          # Modèles DB
│   ├── schemas.py         # Validation API
│   ├── database.py        # Configuration DB
│   ├── routers/           # Routes
│   │   └── web.py
│   ├── services/          # Logique métier
│   └── templates/         # Templates HTML
├── static/                 # Fichiers statiques
│   └── css/style.css
├── data/                   # Base de données
│   └── spass_gasy.db       # Créé automatiquement
├── docs/                   # Documentation
├── run.py                  # Script de lancement
└── requirements.txt        # Dépendances
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Environnement
ENVIRONMENT=development

# Base de données
DATABASE_URL=sqlite+aiosqlite:///./data/spass_gasy.db

# Pour PostgreSQL en production :
# DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Secret pour les sessions (à changer en production)
SECRET_KEY=votre-cle-secrete-tres-longue-et-complexe

# Debug
DEBUG=true
```

### Configurer Pydantic Settings

Créez `app/config.py` :

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./data/spass_gasy.db"
    secret_key: str = "dev-secret-key"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
```

Utilisez ensuite `settings.database_url` au lieu de la constante.

## Développement

### Workflow recommandé

1. **Créer une branche** pour chaque fonctionnalité
2. **Développer** localement
3. **Tester** manuellement
4. **Commiter** avec des messages clairs
5. **Pousser** sur le repository

### Commandes utiles

```bash
# Formater le code (si installé)
black app/

# Vérifier les types
mypy app/

# Lancer les tests
pytest tests/

# Créer une migration Alembic
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir à la migration précédente
alembic downgrade -1
```

### Important : Formateur HTML et templates Jinja2

Le formateur automatique HTML de VS Code casse les expressions Jinja2 comme `{{ car.daily_price }}` en les découpant sur plusieurs lignes, ce qui plante l'app.

Le fichier `.vscode/settings.json` est déjà configuré pour désactiver ce comportement :

```json
{
  "[html]": {
    "editor.formatOnSave": false
  }
}
```

Ne pas supprimer ce fichier.

### Débogage

Pour déboguer, ajoutez des logs :

```python
import logging

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Utiliser
logger.debug("Message de debug")
logger.info("Message d'info")
logger.error("Message d'erreur")
```

## Production

### Checklist avant déploiement

- [ ] Changer `DEBUG = False`
- [ ] Générer une `SECRET_KEY` sécurisée
- [ ] Configurer PostgreSQL
- [ ] Configurer HTTPS
- [ ] Configurer les sauvegardes de DB
- [ ] Configurer le monitoring

### Déploiement avec Gunicorn

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer avec Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Déploiement sur un VPS

```bash
# Installer les dépendances système
sudo apt update
sudo apt install python3-pip nginx

# Cloner et configurer
git clone <url-du-repo>
cd Spass_gasy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer Nginx
sudo nano /etc/nginx/sites-available/spassgasy

# Contenu du fichier :
server {
    listen 80;
    server_name spassgasy.mg;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/Spass_gasy/static;
    }
}

# Activer le site
sudo ln -s /etc/nginx/sites-available/spassgasy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Lancer avec systemd
sudo nano /etc/systemd/system/spassgasy.service
```

### Service systemd

```ini
[Unit]
Description=Spass Gasy Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/Spass_gasy
ExecStart=/path/to/Spass_gasy/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer
sudo systemctl enable spassgasy
sudo systemctl start spassgasy
```

## Dépannage

### Erreur : "Module not found"

```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur : "Database is locked"

SQLite ne supporte qu'une connexion à la fois en écriture.

```python
# Solution : Augmenter le timeout
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)
```

### Erreur : "Address already in use"

Le port 8000 est déjà utilisé.

```bash
# Trouver le processus
lsof -i :8000

# Tuer le processus
kill -9 <PID>

# Ou utiliser un autre port
uvicorn app.main:app --port 8001
```

## Questions fréquentes

### Puis-je utiliser PostgreSQL en développement ?

Oui, mais SQLite est plus simple. Pour PostgreSQL en développement :

1. Installer PostgreSQL
2. Créer une base de données
3. Changer `DATABASE_URL`

```bash
# DATABASE_URL pour PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost/spassgasy
```

### Comment réinitialiser la base de données ?

```bash
# Supprimer le fichier SQLite
rm data/spass_gasy.db

# Relancer l'application (les tables seront recréées)
python run.py
```

### Comment ajouter une nouvelle dépendance ?

```bash
# Installer le package
pip install package_name

# Mettre à jour requirements.txt
pip freeze > requirements.txt
```