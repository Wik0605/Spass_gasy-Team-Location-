from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models import Car, CarImage


async def get_available_cars(
    db: AsyncSession,
    limit: Optional[int] = None,
    order_by_price: bool = False
) -> List[Car]:
    """Récupère les voitures disponibles avec leurs images."""
    query = select(Car).where(Car.is_available == True).options(selectinload(Car.images))

    if order_by_price:
        query = query.order_by(Car.daily_price)
    else:
        query = query.order_by(Car.created_at.desc())

    if limit is not None:
        query = query.limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_car_by_id(db: AsyncSession, car_id: int) -> Optional[Car]:
    """Récupère une voiture avec toutes ses photos (pour le carousel)."""
    result = await db.execute(
        select(Car)
        .where(Car.id == car_id)
        .options(selectinload(Car.images))
    )
    return result.scalar_one_or_none()
