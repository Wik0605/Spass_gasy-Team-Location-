from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models import RentalType


async def get_rental_types(db: AsyncSession) -> List[RentalType]:
    result = await db.execute(select(RentalType).order_by(RentalType.duration_days))
    return result.scalars().all()
