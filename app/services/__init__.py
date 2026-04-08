"""
Package services - Logique métier

Ce package contient la logique métier de l'application.
Les services encapsulent les opérations complexes qui impliquent
plusieurs modèles ou nécessitent des calculs.

Pourquoi séparer les services des routes ?
- Réutilisabilité : Un service peut être utilisé par plusieurs routes
- Testabilité : Les services sont plus faciles à tester isolément
- Séparation des préoccupations : Les routes gèrent HTTP, les services gèrent la logique

Structure recommandée :
- services/car_service.py : Gestion des voitures
- services/rental_service.py : Gestion des locations
- services/pricing_service.py : Calcul des prix
"""

# TODO: Ajouter les services au fur et à mesure que l'application grandit
# Exemple : from app.services.car_service import CarService