# Guide de la base de données

> Ce document explique la structure de la base de données et comment l'utiliser.

## Tables

### CarType (Types de voitures)

Les catégories de véhicules disponibles.

```python
class CarType:
    id: int           # Clé primaire
    name: str         # Nom (ex: "Économique", "SUV")
    description: str  # Description
    icon: str         # Emoji ou nom d'icône
```

**Utilisation** :
```python
# Créer un type
car_type = CarType(
    name="Économique",
    description="Voitures économiques pour la ville",
    icon="🚗"
)
await session.add(car_type)

# Récupérer tous les types
result = await session.execute(select(CarType))
types = result.scalars().all()
```

### Car (Voitures)

Les véhicules disponibles à la location.

```python
class Car:
    id: int              # Clé primaire
    brand: str           # Marque (Toyota, Renault...)
    model: str           # Modèle (Yaris, Duster...)
    year: int            # Année
    plate_number: str    # Immatriculation
    daily_price: float   # Prix par jour (Ariary)
    is_available: bool   # Disponibilité
    car_type_id: int     # Clé étrangère vers CarType
    seats: int            # Nombre de places
    transmission: str    # "manuelle" ou "automatique" 
    description: str     # Description
    image_url: str       # URL de l'image
```

**Utilisation** :
```python
# Récupérer les voitures disponibles
result = await session.execute(
    select(Car)
    .where(Car.is_available == True)
    .order_by(Car.daily_price)
)
cars = result.scalars().all()

# Récupérer une voiture avec son type (eager loading)
result = await session.execute(
    select(Car)
    .where(Car.id == car_id)
    .options(selectinload(Car.car_type))
)
car = result.scalar_one()
```

### RentalType (Types de location)

Les durées de location proposées.

```python
class RentalType:
    id: int                # Clé primaire
    name: str              # Nom (Journalière, Hebdomadaire...)
    duration_days: int     # Durée en jours
    price_multiplier: float # Multiplicateur de prix
    discount_percent: float # Remise en %
    description: str       # Description
```

**Calcul du prix** :
```python
def calculate_total_price(daily_price: float, rental_type: RentalType):
    base_price = daily_price * rental_type.price_multiplier
    discount = base_price * (rental_type.discount_percent / 100)
    return base_price - discount

# Exemple : 7 jours avec 5% de remise
# daily_price = 25000 Ar
# price_multiplier = 6.0 (payer 6 jours)
# discount = 5%
# total = 25000 * 6 * 0.95 = 142500 Ar
```

### Rental (Locations)

Les locations effectuées par les clients.

```python
class Rental:
    id: int              # Clé primaire
    customer_name: str   # Nom du client
    customer_phone: str  # Téléphone
    customer_email: str  # Email (optionnel)
    car_id: int          # Voiture louée
    rental_type_id: int  # Type de location
    start_date: datetime # Date de début
    end_date: datetime   # Date de fin
    total_price: float   # Prix total calculé
    status: str           # "confirmée", "en_cours", "terminée", "annulée"
    notes: str           # Notes (optionnel)
```

**Utilisation** :
```python
# Créer une location
rental = Rental(
    customer_name="Jean Dupont",
    customer_phone="+26134000000",
    car_id=1,
    rental_type_id=2,
    start_date=datetime(2024, 1, 15),
    end_date=datetime(2024, 1, 22),
    total_price=142500,
    status="confirmée"
)
await session.add(rental)
await session.commit()
```

## Relations

### Accéder aux données liées

```python
# Depuis une voiture, obtenir son type
car = await session.get(Car, 1)
car_type = car.car_type  # Relation automatique

# Depuis un type, obtenir toutes ses voitures
car_type = await session.get(CarType, 1)
cars = car_type.cars  # Relation automatique

# Depuis une location, obtenir la voiture et le type
rental = await session.get(Rental, 1)
car = rental.car
rental_type = rental.rental_type
```

### Chargement optimisé (Eager Loading)

Pour éviter les requêtes N+1, utilisez `selectinload` :

```python
from sqlalchemy.orm import selectinload

# Charger les voitures avec leur type en une seule requête
result = await session.execute(
    select(Car)
    .options(selectinload(Car.car_type))
    .where(Car.is_available == True)
)
cars = result.scalars().all()

# Maintenant car.car_type est déjà chargé
for car in cars:
    print(f"{car.brand} {car.model} - {car.car_type.name}")
```

## Migrations

### Pourquoi Alembic ?

Alembic permet de gérer les modifications de schéma de base de données de manière versionnée.

### Commandes utiles

```bash
# Initialiser Alembic
alembic init migrations

# Créer une migration automatique
alembic revision --autogenerate -m "Description de la modification"

# Appliquer les migrations
alembic upgrade head

# Revenir à la version précédente
alembic downgrade -1
```

### Exemple de migration

```python
# Ajouter une colonne "color" à la table "cars"
def upgrade():
    op.add_column('cars', sa.Column('color', sa.String(50), nullable=True))

def downgrade():
    op.drop_column('cars', 'color')
```

## Bonnes pratiques

### 1. Toujours utiliser async avec la DB

```python
# ✅ Correct
async with AsyncSessionLocal() as session:
    result = await session.execute(select(Car))
    cars = result.scalars().all()

# ❌ Incorrect (bloque l'event loop)
with Session() as session:  # Sync, pas async
    cars = session.query(Car).all()
```

### 2. Utiliser les transactions

```python
# ✅ Transaction automatique
async with AsyncSessionLocal() as session:
    car = Car(brand="Toyota", ...)
    session.add(car)
    await session.commit()  # Valide la transaction

# ✅ Gestion d'erreur avec rollback
async with AsyncSessionLocal() as session:
    try:
        car = Car(brand="Toyota", ...)
        session.add(car)
        await session.commit()
    except Exception:
        await session.rollback()  # Annule en cas d'erreur
        raise
```

### 3. Index pour les performances

```python
# Dans models.py
class Car(Base):
    # ...
    plate_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True  # Crée un index pour les recherches
    )
```

## Questions fréquentes

### Comment ajouter une nouvelle table ?

1. Créer le modèle dans `models.py`
2. Hériter de `Base`
3. Relancer l'application (les tables sont créées automatiquement)

### Comment faire une recherche ?

```python
# Recherche par texte
result = await session.execute(
    select(Car)
    .where(Car.brand.ilike("%toyota%"))  # Insensible à la casse
)
```

### Comment paginer les résultats ?

```python
# Page 1, 10 éléments par page
result = await session.execute(
    select(Car)
    .offset(0)   # Commencer à 0
    .limit(10)    # 10 éléments
)
```