import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models import Car

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Car))
        cars = result.scalars().all()
        for c in cars:
            print(f"Car: {c.brand} {c.model}, Image: {c.image_url}")

asyncio.run(main())
