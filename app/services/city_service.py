from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models import City

async def get_active_cities(db: AsyncSession) -> List[City]:
    """Récupère toutes les villes actives triées par nom."""
    result = await db.execute(select(City).where(City.is_active == True).order_by(City.name))
    return result.scalars().all()
