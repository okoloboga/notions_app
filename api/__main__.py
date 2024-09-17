import asyncio
import uvicorn

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request

from database import engine
from models import Base
from api import app


limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter

@app.middleware
async def rate_limit_middleware(request: Request, call_next):
    return await limiter.limit_request(request)(call_next)

# Создание таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())
    uvicorn.run(app, host="0.0.0.0", port=8000)

