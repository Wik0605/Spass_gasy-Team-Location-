import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models import Car

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Car))
        cars = result.scalars().all()
        for c in cars:
            if c.image_url and ("Gemini.png" in c.image_url):
                c.image_url = "/assets/Gemini.png"
        await session.commit()
        print("Updated database image URLs.")

asyncio.run(main())
