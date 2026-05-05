"""
Point d'entrée de l'application Spass Gasy.

Ce fichier configure :
- L'application FastAPI
- Le middleware CORS
- Les fichiers statiques
- Le démarrage / arrêt (lifespan)
- Les données initiales (seed)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.database import init_db, engine
from app.routers.web import router as web_router
from app.routers.admin import router as admin_router

STATIC_DIR = Path(__file__).parent.parent / "static"
ASSETS_DIR = Path(__file__).parent / "assets"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Cycle de vie de l'application.

    'async with' et 'yield' : tout ce qui est AVANT yield s'exécute au démarrage,
    tout ce qui est APRÈS yield s'exécute à l'arrêt.
    """
    print("Démarrage de Spass Gasy...")
    await init_db()
    await seed_initial_data()
    print("Application prête !")
    yield
    print("Arrêt de Spass Gasy...")
    await engine.dispose()


async def seed_initial_data():
    """
    Insère les données initiales si la DB est vide.
    Guard : on vérifie RentalType — s'il en existe déjà, on ne réinsère rien.
    """
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import RentalType, Car, City, get_initial_rental_types, get_initial_cars, get_initial_cities

    async with AsyncSessionLocal() as session:
        # Insérer les villes si absentes
        existing_cities = await session.execute(select(City))
        if not existing_cities.scalars().first():
            print("Insertion des villes initiales...")
            for city_data in get_initial_cities():
                session.add(City(**city_data))
            await session.commit()

        # Si des RentalTypes existent déjà, les données sont déjà là
        existing_rental_types = await session.execute(select(RentalType))
        if existing_rental_types.scalars().first():
            return

        print("Insertion des types de location et voitures...")

        for rental_type_data in get_initial_rental_types():
            session.add(RentalType(**rental_type_data))
        await session.commit()

        for car_data in get_initial_cars():
            session.add(Car(**car_data))
        await session.commit()

        print("Données initiales insérées !")


app = FastAPI(
    title="Spass Gasy",
    description="Application de location de voitures à Madagascar.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

app.include_router(web_router)
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
