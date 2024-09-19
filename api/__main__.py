import asyncio
import uvicorn

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request

from database import engine
from models import Base
from api import app


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.middleware
async def rate_limit_middleware(request: Request, call_next):   
    """
    A middleware function that limits the number of requests to the API based on the IP address of the client.

    Parameters:
        request (Request): The incoming request object.
        call_next: The next middleware or application to call.

    Returns:
        Response: The response from the next middleware or application.
    """
    return await limiter.limit_request(request)(call_next)



async def create_tables():
    """
    Create tables in the database.

    This function asynchronously creates tables in the database. It uses the `engine` object to create a connection
    and then executes the `Base.metadata.create_all()` method
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())
    uvicorn.run(app, host="api", port=8000)

