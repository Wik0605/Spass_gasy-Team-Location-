"""
Routes Web (HTML/HTMX)

Routes disponibles :
- GET /              : Page d'accueil
- GET /cars          : Liste des voitures
- GET /cars/{id}     : Détail d'une voiture
- GET /car/{id}/itineraire : Calculateur d'itinéraire
- GET /booking       : Page de réservation
- GET /rental-types  : Page des tarifs
- GET /contact       : Page de contact
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import datetime

from app.database import get_db
from app.services import car_service, rental_service, city_service

router = APIRouter(prefix="", tags=["web"])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["current_year"] = lambda: datetime.datetime.now().year


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    rental_types = await rental_service.get_rental_types(db)
    available_cars = await car_service.get_available_cars(db, limit=6)
    cities = await city_service.get_active_cities(db)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "rental_types": rental_types,
        "available_cars": available_cars,
        "cities": cities,
    })


@router.get("/cars", response_class=HTMLResponse)
async def cars_list(request: Request, db: AsyncSession = Depends(get_db)):
    cars = await car_service.get_available_cars(db, order_by_price=True)

    return templates.TemplateResponse("cars.html", {
        "request": request,
        "cars": cars,
    })


@router.get("/cars/{car_id}", response_class=HTMLResponse)
async def car_detail(request: Request, car_id: int, db: AsyncSession = Depends(get_db)):
    car = await car_service.get_car_by_id(db, car_id)

    if not car:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    rental_types = await rental_service.get_rental_types(db)

    return templates.TemplateResponse("car_detail.html", {
        "request": request,
        "car": car,
        "rental_types": rental_types,
    })


@router.get("/car/{car_id}/itineraire", response_class=HTMLResponse)
async def car_itineraire(request: Request, car_id: int, db: AsyncSession = Depends(get_db)):
    car = await car_service.get_car_by_id(db, car_id)

    if not car:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    return templates.TemplateResponse("itineraire.html", {
        "request": request,
        "car": car,
    })


@router.get("/booking", response_class=HTMLResponse)
async def booking_page(request: Request, db: AsyncSession = Depends(get_db)):
    cars = await car_service.get_available_cars(db)
    rental_types = await rental_service.get_rental_types(db)

    return templates.TemplateResponse("booking.html", {
        "request": request,
        "cars": cars,
        "rental_types": rental_types,
    })


@router.get("/rental-types", response_class=HTMLResponse)
async def rental_types_page(request: Request, db: AsyncSession = Depends(get_db)):
    rental_types = await rental_service.get_rental_types(db)

    return templates.TemplateResponse("rental_types.html", {
        "request": request,
        "rental_types": rental_types,
    })


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


# =============================================================================
# PARTIALS HTMX
# =============================================================================

@router.get("/api/cars/search", response_class=HTMLResponse)
async def search_cars(request: Request, db: AsyncSession = Depends(get_db)):
    cars = await car_service.get_available_cars(db, order_by_price=True)
    return templates.TemplateResponse("partials/_car_list.html", {"request": request, "cars": cars})


@router.get("/api/cars/popular", response_class=HTMLResponse)
async def popular_cars(request: Request, db: AsyncSession = Depends(get_db)):
    cars = await car_service.get_available_cars(db, limit=6)
    return templates.TemplateResponse("partials/_car_grid.html", {"request": request, "cars": cars})
