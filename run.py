"""
Point d'entrée de l'application

Ce script lance le serveur de développement Uvicorn.

Pourquoi un fichier run.py séparé ?
- Plus facile à lancer : python run.py
- Configuration centralisée
- Peut ajouter des options (debug, reload, etc.)

Pour lancer en production, utiliser plutôt :
    uvicorn app.main:app --host 0.0.0.0 --port 8000

Pour le développement avec rechargement automatique :
    python run.py

Ou directement :
    uvicorn app.main:app --reload
"""

import uvicorn

uvicorn.run(
        "app.main:app",  # Module:application
        host="127.0.0.1",  # Accessible depuis le réseau local (téléphone, etc.)
        port=5500
        ,  # Port standard pour le développement
        reload=False,

        log_level="info",  # Niveau de logging
    )