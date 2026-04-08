"""
Routes Web (HTML/HTMX)

Ce module contient toutes les routes qui servent des pages HTML.
Ces routes utilisent Jinja2 pour le templating et HTMX pour les interactions.

Pourquoi séparer les routes web de l'API ?
- Séparation des préoccupations (HTML vs JSON)
- Templates différents
- Middlewares différents possibles (sessions, CSRF, etc.)
- Plus facile à maintenir et tester

Architecture des routes :
- GET / : Page d'accueil
- GET /cars : Liste des voitures
- GET /cars/{id} : Détail d'une voiture
- GET /booking : Page de réservation
- GET /contact : Page de contact
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db
from app.models import CarType, Car, RentalType

# Création du routeur
# prefix="" : Pas de préfixe pour les routes web
# tags=["web"] : Pour la documentation OpenAPI
router = APIRouter(prefix="", tags=["web"])

# Configuration des templates Jinja2
# Le dossier templates est à la racine du package app
templates = Jinja2Templates(directory="app/templates")

# Filtre personnalisé pour Jinja2
# Permet d'obtenir l'année actuelle dans les templates
import datetime
templates.env.filters["current_year"] = lambda: datetime.datetime.now().year


# =============================================================================
# PAGE D'ACCUEIL
# =============================================================================

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Page d'accueil de l'application

    Affiche :
    - Les types de voitures disponibles
    - Les types de location (tarifs)
    - Une sélection de voitures populaires
    - Formulaire de recherche rapide

    Args:
        request: Objet Request de FastAPI (pour le contexte du template)
        db: Session de base de données (injectée par dépendance)

    Returns:
        Template HTML index.html avec les données
    """
    # Récupérer tous les types de voitures
    # select(CarType) crée une requête SQLAlchemy
    # order_by(CarType.name) trie par nom
    car_types_result = await db.execute(
        select(CarType).order_by(CarType.name)
    )
    car_types = car_types_result.scalars().all()

    # Récupérer tous les types de location
    rental_types_result = await db.execute(
        select(RentalType).order_by(RentalType.duration_days)
    )
    rental_types = rental_types_result.scalars().all()

    # Récupérer quelques voitures disponibles (limit 6)
    # where(Car.is_available == True) filtre les voitures disponibles
    available_cars_result = await db.execute(
        select(Car)
        .where(Car.is_available == True)
        .order_by(Car.created_at.desc())
        .limit(6)
    )
    available_cars = available_cars_result.scalars().all()

    # Contexte passé au template
    # request est obligatoire pour que les urls fonctionnent
    context = {
        "request": request,
        "car_types": car_types,
        "rental_types": rental_types,
        "available_cars": available_cars,
        "current_year": datetime.datetime.now().year,
    }

    # Rendu du template avec le contexte
    return templates.TemplateResponse("index.html", context)


# =============================================================================
# PAGE LISTE DES VOITURES
# =============================================================================

@router.get("/cars", response_class=HTMLResponse)
async def cars_list(
    request: Request,
    type: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Liste des voitures avec filtres optionnels

    Args:
        request: Objet Request
        type: ID du type de voiture (filtre optionnel)
        db: Session de base de données

    Returns:
        Template HTML avec la liste filtrée
    """
    # Requête de base avec chargement du type de voiture
    query = select(Car).options(selectinload(Car.car_type)).where(Car.is_available == True)

    # Appliquer le filtre si type est spécifié
    if type:
        query = query.where(Car.car_type_id == type)

    # Exécuter la requête
    result = await db.execute(query.order_by(Car.daily_price))
    cars = result.scalars().all()

    # Récupérer les types pour le filtre
    car_types_result = await db.execute(select(CarType))
    car_types = car_types_result.scalars().all()

    context = {
        "request": request,
        "cars": cars,
        "car_types": car_types,
        "selected_type": type,
        "current_year": datetime.datetime.now().year,
    }

    return templates.TemplateResponse("cars.html", context)


# =============================================================================
# PAGE DÉTAIL D'UNE VOITURE
# =============================================================================

@router.get("/cars/{car_id}", response_class=HTMLResponse)
async def car_detail(
    request: Request,
    car_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Détail d'une voiture spécifique

    Args:
        request: Objet Request
        car_id: ID de la voiture
        db: Session de base de données

    Returns:
        Template HTML avec le détail de la voiture
    """
    # Récupérer la voiture par ID avec son type
    result = await db.execute(
        select(Car)
        .options(selectinload(Car.car_type))
        .where(Car.id == car_id)
    )
    car = result.scalar_one_or_none()

    if not car:
        # Retourner une page 404 si la voiture n'existe pas
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404
        )

    # Récupérer les types de location pour le formulaire de réservation
    rental_types_result = await db.execute(select(RentalType))
    rental_types = rental_types_result.scalars().all()

    context = {
        "request": request,
        "car": car,
        "rental_types": rental_types,
        "current_year": datetime.datetime.now().year,
    }

    return templates.TemplateResponse("car_detail.html", context)


# =============================================================================
# PAGE RÉSERVATION
# =============================================================================

@router.get("/booking", response_class=HTMLResponse)
async def booking_page(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Page de réservation

    Permet de créer une nouvelle location.
    """
    # Récupérer toutes les voitures disponibles avec leur type
    cars_result = await db.execute(
        select(Car)
        .options(selectinload(Car.car_type))
        .where(Car.is_available == True)
    )
    cars = cars_result.scalars().all()

    # Récupérer les types de location
    rental_types_result = await db.execute(select(RentalType))
    rental_types = rental_types_result.scalars().all()

    context = {
        "request": request,
        "cars": cars,
        "rental_types": rental_types,
        "current_year": datetime.datetime.now().year,
    }

    return templates.TemplateResponse("booking.html", context)


# =============================================================================
# PAGE TARIFS
# =============================================================================

@router.get("/rental-types", response_class=HTMLResponse)
async def rental_types_page(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Page des tarifs de location

    Affiche tous les types de location disponibles.
    """
    rental_types_result = await db.execute(select(RentalType))
    rental_types = rental_types_result.scalars().all()

    context = {
        "request": request,
        "rental_types": rental_types,
        "current_year": datetime.datetime.now().year,
    }

    return templates.TemplateResponse("rental_types.html", context)


# =============================================================================
# PAGE CONTACT
# =============================================================================

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """
    Page de contact
    """
    context = {
        "request": request,
        "current_year": datetime.datetime.now().year,
    }

    return templates.TemplateResponse("contact.html", context)


# =============================================================================
# API ENDPOINTS POUR HTMX
# =============================================================================

@router.get("/api/cars/search", response_class=HTMLResponse)
async def search_cars(
    request: Request,
    car_type: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    API de recherche de voitures (utilisée par HTMX)

    Cette route est appelée dynamiquement par HTMX quand l'utilisateur
    filtre les voitures sur la page d'accueil.

    Retourne un fragment HTML (pas une page complète).
    """
    query = select(Car).where(Car.is_available == True)

    if car_type:
        query = query.where(Car.car_type_id == car_type)

    result = await db.execute(query.order_by(Car.daily_price))
    cars = result.scalars().all()

    # Retourne un fragment HTML pour HTMX
    return templates.TemplateResponse(
        "partials/_car_list.html",
        {
            "request": request,
            "cars": cars
        }
    )


@router.get("/api/cars/popular", response_class=HTMLResponse)
async def popular_cars(request: Request, db: AsyncSession = Depends(get_db)):
    """
    API pour les voitures populaires (utilisée par HTMX sur la page d'accueil)

    Retourne un fragment HTML avec les voitures les plus récentes.
    """
    result = await db.execute(
        select(Car)
        .where(Car.is_available == True)
        .options(selectinload(Car.car_type))
        .order_by(Car.created_at.desc())
        .limit(6)
    )
    cars = result.scalars().all()

    return templates.TemplateResponse(
        "partials/_car_grid.html",
        {
            "request": request,
            "cars": cars
        }
    )