import asyncio
from app.database import AsyncSessionLocal
from app.models import City, get_initial_cities
from sqlalchemy import delete

async def seed():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(City))
        for city_data in get_initial_cities():
            session.add(City(**city_data))
        await session.commit()
        print("Tana neighborhoods seeded!")

asyncio.run(seed())
