"""
Schémas Pydantic pour la validation des données

Ce module définit les schémas de validation pour l'API.
Pydantic permet de :
- Valider automatiquement les données entrantes
- Sérialiser les données sortantes (JSON)
- Générer automatiquement la documentation OpenAPI

Pourquoi séparer les schémas des modèles ?
- Séparation des préoccupations : modèles = DB, schémas = API
- Sécurité : on peut exclure certains champs (ex: mots de passe)
- Flexibilité : différents schémas pour création, lecture, mise à jour
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal


# =============================================================================
# SCHÉMAS POUR LES TYPES DE VOITURES (CarType)
# =============================================================================

class CarTypeBase(BaseModel):
    """
    Schéma de base pour CarType

    Contient les champs communs à toutes les opérations.
    Les classes qui héritent peuvent ajouter ou modifier des champs.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nom du type de voiture",
        examples=["Économique", "SUV"]
    )
    description: Optional[str] = Field(
        None,
        description="Description optionnelle du type",
        examples=["Voitures économiques parfaites pour la ville"]
    )
    icon: Optional[str] = Field(
        None,
        max_length=20,
        description="Emoji ou nom d'icône pour l'affichage",
        examples=["🚗", "car-icon"]
    )


class CarTypeCreate(CarTypeBase):
    """
    Schéma pour créer un nouveau type de voiture

    Hérite de CarTypeBase sans ajouter de champs.
    Utilisé lors de la création (POST).
    """
    pass


class CarTypeResponse(CarTypeBase):
    """
    Schéma pour la réponse API d'un type de voiture

    Ajoute l'ID qui est généré automatiquement par la base de données.
    """
    id: int

    # Configuration pour SQLAlchemy
    # from_attributes=True permet de convertir les objets SQLAlchemy en dicts
    model_config = {"from_attributes": True}


# =============================================================================
# SCHÉMAS POUR LES VOITURES (Car)
# =============================================================================

class CarBase(BaseModel):
    """Schéma de base pour les voitures"""
    brand: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Marque de la voiture",
        examples=["Toyota", "Renault"]
    )
    model: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Modèle de la voiture",
        examples=["Yaris", "Duster"]
    )
    year: int = Field(
        ...,
        ge=2000,
        le=2025,
        description="Année du modèle"
    )
    plate_number: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Numéro d'immatriculation",
        examples=["1234 TANA"]
    )
    daily_price: float = Field(
        ...,
        gt=0,
        description="Prix journalier de base (en Ariary)"
    )
    car_type_id: int = Field(
        ...,
        description="ID du type de voiture"
    )
    seats: int = Field(
        default=5,
        ge=1,
        le=9,
        description="Nombre de places"
    )
    transmission: str = Field(
        default="manuelle",
        description="Type de transmission",
        examples=["manuelle", "automatique"]
    )
    description: Optional[str] = Field(
        None,
        description="Description optionnelle"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL de l'image"
    )


class CarCreate(CarBase):
    """Schéma pour créer une nouvelle voiture"""
    pass


class CarUpdate(BaseModel):
    """
    Schéma pour mettre à jour une voiture

    Tous les champs sont optionnels car on peut vouloir
    mettre à jour seulement certains champs.
    """
    brand: Optional[str] = Field(None, min_length=2, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=2000, le=2025)
    plate_number: Optional[str] = Field(None, min_length=4, max_length=20)
    daily_price: Optional[float] = Field(None, gt=0)
    car_type_id: Optional[int] = None
    seats: Optional[int] = Field(None, ge=1, le=9)
    transmission: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None


class CarResponse(CarBase):
    """Schéma pour la réponse API d'une voiture"""
    id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime

    # Inclure les informations du type de voiture
    # car_type est une relation SQLAlchemy, on peut l'inclure directement
    # si le schéma a from_attributes=True
    car_type: Optional[CarTypeResponse] = None

    model_config = {"from_attributes": True}

    @property
    def full_name(self) -> str:
        """Retourne le nom complet du véhicule"""
        return f"{self.brand} {self.model}"


class CarListResponse(BaseModel):
    """Schéma pour une liste de voitures avec pagination"""
    cars: list[CarResponse]
    total: int
    page: int
    per_page: int
    has_next: bool


# =============================================================================
# SCHÉMAS POUR LES TYPES DE LOCATION (RentalType)
# =============================================================================

class RentalTypeBase(BaseModel):
    """Schéma de base pour les types de location"""
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nom du type de location",
        examples=["Journalière", "Hebdomadaire"]
    )
    duration_days: int = Field(
        ...,
        gt=0,
        description="Nombre de jours couverts"
    )
    price_multiplier: float = Field(
        default=1.0,
        ge=0,
        description="Multiplicateur de prix"
    )
    discount_percent: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Pourcentage de remise"
    )
    description: Optional[str] = Field(
        None,
        description="Description optionnelle"
    )


class RentalTypeCreate(RentalTypeBase):
    """Schéma pour créer un type de location"""
    pass


class RentalTypeResponse(RentalTypeBase):
    """Schéma pour la réponse API d'un type de location"""
    id: int

    model_config = {"from_attributes": True}


# =============================================================================
# SCHÉMAS POUR LES LOCATIONS (Rental)
# =============================================================================

class RentalBase(BaseModel):
    """Schéma de base pour les locations"""
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nom complet du client"
    )
    customer_phone: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Numéro de téléphone"
    )
    customer_email: Optional[str] = Field(
        None,
        description="Adresse email (optionnelle)"
    )
    car_id: int = Field(..., description="ID de la voiture")
    rental_type_id: int = Field(..., description="ID du type de location")
    start_date: datetime = Field(..., description="Date de début")
    end_date: datetime = Field(..., description="Date de fin")
    notes: Optional[str] = Field(None, description="Notes additionnelles")


class RentalCreate(RentalBase):
    """Schéma pour créer une nouvelle location"""

    def calculate_total_price(self, daily_price: float, rental_type: RentalTypeResponse) -> float:
        """
        Calcule le prix total de la location

        Formule : prix_journalier * multiplicateur * (1 - remise%)
        """
        base_price = daily_price * rental_type.price_multiplier
        discount = base_price * (rental_type.discount_percent / 100)
        return base_price - discount


class RentalResponse(RentalBase):
    """Schéma pour la réponse API d'une location"""
    id: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime

    # Relations
    car: Optional[CarResponse] = None
    rental_type: Optional[RentalTypeResponse] = None

    model_config = {"from_attributes": True}


class RentalListResponse(BaseModel):
    """Schéma pour une liste de locations"""
    rentals: list[RentalResponse]
    total: int
    page: int
    per_page: int