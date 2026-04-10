"""
Application principale FastAPI

C'est le point d'entrée de l'application.
Ce fichier configure :
1. L'application FastAPI
2. La connexion à la base de données
3. Les routeurs (web et API)
4. Le middleware (CORS, sessions, etc.)
5. Les événements de démarrage/arrêt

Architecture :
- L'application est créée avec FastAPI
- Les routeurs sont inclus pour séparer les préoccupations
- La base de données est initialisée au démarrage
- Les fichiers statiques sont configurés

Pourquoi cette structure ?
- Le code est organisé et maintenable
- Chaque partie a une responsabilité unique
- Facile d'ajouter de nouvelles fonctionnalités
- Prêt pour la production avec une configuration adaptée
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.database import init_db, engine
from app.routers.web import router as web_router

# Chemin vers les fichiers statiques
# Path(__file__).parent.parent remonte au dossier racine du projet
STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application

    Ce contexte asynchrone gère le démarrage et l'arrêt de l'application.

    Au démarrage :
    - Initialise la base de données (crée les tables si nécessaires)
    - Charge les données initiales (types de voitures, types de location)

    À l'arrêt :
    - Ferme proprement les connexions

    Pourquoi utiliser lifespan ?
    - Remplace les événements on_startup/on_shutdown (dépréciés)
    - Plus propre pour gérer les ressources asynchrones
    - Garantit que tout est prêt avant de servir les requêtes
    """
    # ===== DÉMARRAGE =====
    print("🚀 Démarrage de Spass Gasy...")

    # Initialiser la base de données
    # Cela crée les tables si elles n'existent pas
    await init_db()

    # Charger les données initiales
    await seed_initial_data()

    print("✅ Application prête !")

    # Yield : l'application est maintenant active
    yield

    # ===== ARRÊT =====
    print("🛑 Arrêt de Spass Gasy...")
    await engine.dispose()
    print("👋 Au revoir !")


async def seed_initial_data():
    """
    Insère les données initiales dans la base de données

    Cette fonction vérifie si les données existent déjà
    avant de les insérer (évite les doublons).

    Données insérées :
    - Types de voitures (Économique, SUV, Luxe, etc.)
    - Types de location (Journalière, Hebdomadaire, etc.)
    - Quelques voitures de démonstration
    """
    from datetime import datetime
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.database import AsyncSessionLocal
    from app.models import CarType, RentalType, Car, Rental, get_initial_car_types, get_initial_rental_types, get_initial_cars

    async with AsyncSessionLocal() as session:
        # Vérifier si les données existent déjà
        existing_types = await session.execute(select(CarType))
        if existing_types.scalars().first():
            print("📊 Données déjà présentes, pas besoin de seed.")
            return

        print("📝 Insertion des données initiales...")

        # Insérer les types de voitures
        for car_type_data in get_initial_car_types():
            car_type = CarType(**car_type_data)
            session.add(car_type)

        # Insérer les types de location
        for rental_type_data in get_initial_rental_types():
            rental_type = RentalType(**rental_type_data)
            session.add(rental_type)

        # Commit avant d'insérer les voitures (pour avoir les IDs)
        await session.commit()

        # Insérer les voitures de démonstration
        for car_data in get_initial_cars():
            car = Car(**car_data)
            session.add(car)

        await session.commit()

        # Ajouter une location de démonstration pour le tracking
        demo_rental = Rental(
            customer_name="Client Test",
            customer_phone="0340000000",
            car_id=1,
            rental_type_id=1,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow(),
            total_price=25000.0,
            status="en_cours"
        )
        session.add(demo_rental)
        await session.commit()

        print("✅ Données initiales insérées avec succès !")


# =============================================================================
# CRÉATION DE L'APPLICATION
# =============================================================================

app = FastAPI(
    title="Spass Gasy",
    description="""
    Application de location de voitures à Madagascar.

    ## Fonctionnalités

    * Consultation des véhicules disponibles
    * Réservation en ligne
    * Gestion des locations
    * Tarification flexible

    ## Technologies

    * FastAPI pour l'API
    * HTMX pour les interactions dynamiques
    * SQLite pour la base de données
    * Tailwind CSS pour le style
    """,
    version="0.1.0",
    lifespan=lifespan,  # Gestion du cycle de vie
    docs_url="/docs",  # Documentation Swagger
    redoc_url="/redoc",  # Documentation ReDoc
)

# =============================================================================
# CONFIGURATION DU MIDDLEWARE
# =============================================================================

# CORS (Cross-Origin Resource Sharing)
# Permet les requêtes depuis d'autres domaines (utile pour le développement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# FICHIERS STATIQUES
# =============================================================================

# Servir les fichiers statiques (CSS, JS, images)
# Le premier argument est le chemin URL, le second le dossier
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Servir aussi le dossier assets s'il existe
ASSETS_DIR = Path(__file__).parent / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# =============================================================================
# INCLUSION DES ROUTEURS
# =============================================================================

# Routeur pour les pages web (HTML/HTMX)
app.include_router(web_router)

# TODO: Ajouter le routeur API quand il sera créé
# from app.routers.api import router as api_router
# app.include_router(api_router, prefix="/api")


# =============================================================================
# ROUTE DE SANTÉ
# =============================================================================

@app.get("/health")
async def health_check():
    """
    Route de vérification de santé de l'application

    Utilisée par :
    - Les outils de monitoring
    - Les load balancers
    - Les tests d'intégration

    Returns:
        dict: Statut de l'application
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "message": "Spass Gasy est opérationnel !"
    }