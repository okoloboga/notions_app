import asyncio
import uvicorn

from database import engine
from models import Base
from api import app

# Создание таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())
    uvicorn.run(app, host="0.0.0.0", port=8000)

