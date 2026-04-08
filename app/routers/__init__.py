"""
Package routers - Routes de l'application

Ce package contient tous les routeurs FastAPI.

Structure :
- web.py : Routes pour les pages web (HTML/HTMX)
- api.py : Routes pour l'API REST (JSON) - à créer plus tard
"""

from app.routers.web import router as web_router

# Export des routeurs
__all__ = ["web_router"]