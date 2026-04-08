"""
Modèles de données SQLAlchemy

Ce module définit la structure des tables de la base de données.
Chaque classe représente une table et ses colonnes.

Pourquoi cette structure ?
- Separation of concerns : Les modèles ne contiennent que la définition des données
- Type hints : Permet l'autocomplétion dans l'IDE
- Relations claires : Les foreign keys sont explicites

Tables principales :
- CarType : Types de véhicules (économique, SUV, luxe, etc.)
- Car : Véhicules disponibles à la location
- RentalType : Types de location (journalière, hebdomadaire, mensuelle)
- Location : Locations effectuées par les clients
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CarType(Base):
    """
    Types/Catégories de voitures

    Cette table permet de classer les véhicules par catégorie.
    Exemples : Économique, SUV, Luxe, Utilitaire, Sport

    Pourquoi une table séparée ?
    - Évite la duplication des noms de catégories
    - Permet d'ajouter des attributs aux catégories (description, icône)
    - Facilite la recherche par catégorie
    """
    __tablename__ = "car_types"

    # Clé primaire
    # Mapped[int] indique que c'est un entier
    # mapped_column avec primary_key=True crée une colonne auto-incrémentée
    id: Mapped[int] = mapped_column(primary_key=True)

    # Nom du type de voiture
    # String(50) limite à 50 caractères
    # nullable=False signifie que ce champ est obligatoire
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # Description optionnelle
    # Text permet des descriptions longues
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Icône pour l'affichage (nom de l'icône ou emoji)
    icon: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relation avec les voitures
    # back_populates crée la relation bidirectionnelle
    # Cela permet d'accéder à car_type.cars pour avoir toutes les voitures d'un type
    cars: Mapped[list["Car"]] = relationship(back_populates="car_type")

    def __repr__(self):
        """Représentation textuelle pour le debug"""
        return f"<CarType(id={self.id}, name='{self.name}')>"


class Car(Base):
    """
    Voitures disponibles à la location

    Cette table contient toutes les informations sur chaque véhicule.
    Chaque voiture appartient à un type (Catégorie).

    Attributs importants :
    - brand : Marque (Toyota, Renault, etc.)
    - model : Modèle (Yaris, Clio, etc.)
    - year : Année du modèle
    - daily_price : Prix de base par jour
    - is_available : Disponibilité actuelle
    """
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Informations sur le véhicule
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Immatriculation unique
    plate_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    # Prix de base par jour (en devise locale)
    daily_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Disponibilité
    # Par défaut, une voiture est disponible
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Clé étrangère vers le type de voiture
    # car_type_id référence CarType.id
    car_type_id: Mapped[int] = mapped_column(ForeignKey("car_types.id"), nullable=False)

    # Relation vers le type de voiture
    # Permet d'accéder à car.car_type.name
    car_type: Mapped["CarType"] = relationship(back_populates="cars")

    # Image optionnelle
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Description optionnelle
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Nombre de places
    seats: Mapped[int] = mapped_column(Integer, default=5)

    # Type de transmission (manuelle/automatique)
    transmission: Mapped[str] = mapped_column(String(20), default="manuelle")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relation avec les locations
    rentals: Mapped[list["Rental"]] = relationship(back_populates="car")

    def __repr__(self):
        return f"<Car(id={self.id}, brand='{self.brand}', model='{self.model}')>"

    @property
    def full_name(self) -> str:
        """Retourne le nom complet du véhicule (Marque Modèle)"""
        return f"{self.brand} {self.model}"


class RentalType(Base):
    """
    Types de location

    Définit les différentes durées de location possibles.
    Exemples : Journalière, Hebdomadaire, Mensuelle

    Pourquoi une table séparée ?
    - Permet de définir des tarifs différents selon la durée
    - Facilite l'ajout de nouveaux types de location
    - Stocke le multiplicateur de prix (ex: semaine = 6 jours payés)
    """
    __tablename__ = "rental_types"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # Nombre de jours couverts par ce type
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)

    # Multiplicateur de prix par rapport au tarif journalier
    # Exemple : 6.0 pour une semaine (payer 6 jours au lieu de 7)
    # Exemple : 25.0 pour un mois (payer 25 jours au lieu de 30)
    price_multiplier: Mapped[float] = mapped_column(Float, default=1.0)

    # Description optionnelle
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Remise en pourcentage (ex: 10 pour 10% de remise)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # Relation avec les locations
    rentals: Mapped[list["Rental"]] = relationship(back_populates="rental_type")

    def __repr__(self):
        return f"<RentalType(id={self.id}, name='{self.name}')>"


class Rental(Base):
    """
    Locations effectuées

    Cette table enregistre chaque location de voiture.
    Elle fait le lien entre un client, une voiture et un type de location.

    Champs importants :
    - customer_name : Nom du client
    - customer_phone : Numéro de téléphone
    - start_date : Date de début de location
    - end_date : Date de fin prévue
    - total_price : Prix total calculé
    - status : État de la location (confirmée, en cours, terminée)
    """
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Informations client
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Clé étrangère vers la voiture
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"), nullable=False)

    # Clé étrangère vers le type de location
    rental_type_id: Mapped[int] = mapped_column(ForeignKey("rental_types.id"), nullable=False)

    # Dates de location
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Prix total calculé
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Statut de la location
    # confirmée, en_cours, terminée, annulée
    status: Mapped[str] = mapped_column(String(20), default="confirmée")

    # Notes optionnelles
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relations
    car: Mapped["Car"] = relationship(back_populates="rentals")
    rental_type: Mapped["RentalType"] = relationship(back_populates="rentals")

    def __repr__(self):
        return f"<Rental(id={self.id}, customer='{self.customer_name}', status='{self.status}')>"


# =============================================================================
# DONNÉES INITIALES (à insérer lors de la création de la DB)
# =============================================================================

def get_initial_car_types() -> list[dict]:
    """
    Retourne les types de voitures initiaux

    Ces données seront insérées automatiquement lors de l'initialisation
    de la base de données.
    """
    return [
        {"name": "Économique", "description": "Voitures économiques, parfaites pour la ville", "icon": "🚗"},
        {"name": "Compacte", "description": "Véhicules compacts, bon compromis confort/prix", "icon": "🚙"},
        {"name": "SUV", "description": "Véhicules tout-terrain spacieux", "icon": "🚐"},
        {"name": "Luxe", "description": "Véhicules haut de gamme pour les occasions spéciales", "icon": "🏎️"},
        {"name": "Utilitaire", "description": "Véhicules utilitaires pour le transport", "icon": "🛻"},
    ]


def get_initial_rental_types() -> list[dict]:
    """
    Retourne les types de location initiaux
    """
    return [
        {"name": "Journalière", "duration_days": 1, "price_multiplier": 1.0, "discount_percent": 0},
        {"name": "Hebdomadaire", "duration_days": 7, "price_multiplier": 6.0, "discount_percent": 5},
        {"name": "Mensuelle", "duration_days": 30, "price_multiplier": 25.0, "discount_percent": 10},
        {"name": "Week-end", "duration_days": 3, "price_multiplier": 2.5, "discount_percent": 0},
    ]


def get_initial_cars() -> list[dict]:
    """
    Retourne quelques voitures initiales pour démonstration
    """
    return [
        {
            "brand": "Toyota",
            "model": "Yaris",
            "year": 2023,
            "plate_number": "1234 TANA",
            "daily_price": 25000.0,  # En Ariary (devise malgache)
            "car_type_id": 1,  # Économique
            "seats": 5,
            "transmission": "manuelle",
            "description": "Parfaite pour la ville, économique et fiable."
        },
        {
            "brand": "Renault",
            "model": "Duster",
            "year": 2022,
            "plate_number": "5678 TANA",
            "daily_price": 45000.0,
            "car_type_id": 3,  # SUV
            "seats": 5,
            "transmission": "manuelle",
            "description": "SUV compact idéal pour les routes malgaches."
        },
        {
            "brand": "Mercedes",
            "model": "Classe E",
            "year": 2023,
            "plate_number": "9999 TANA",
            "daily_price": 120000.0,
            "car_type_id": 4,  # Luxe
            "seats": 5,
            "transmission": "automatique",
            "description": "Confort et élégance pour vos occasions spéciales."
        },
    ]