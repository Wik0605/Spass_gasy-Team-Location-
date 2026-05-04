from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models import Rental, RentalType, Car

async def get_rental_types(db: AsyncSession) -> List[RentalType]:
    """Récupère tous les types de location disponibles."""
    result = await db.execute(select(RentalType).order_by(RentalType.duration_days))
    return result.scalars().all()

async def get_rental_by_tracking(db: AsyncSession, query_str: str) -> Optional[Rental]:
    """
    Recherche une réservation par son ID ou le numéro de téléphone du client.
    """
    query = select(Rental).options(
        selectinload(Rental.car),
        selectinload(Rental.rental_type)
    )
    
    if query_str.isdigit():
        query = query.where(or_(Rental.id == int(query_str), Rental.customer_phone == query_str))
    else:
        query = query.where(Rental.customer_phone == query_str)
        
    result = await db.execute(query)
    return result.scalar_one_or_none()
