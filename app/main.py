# app/main.py
from fastapi import FastAPI
from app.api.auth import auth_router
from app.db import database, init_db
from contextlib import asynccontextmanager

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    init_db()  
    await database.connect()
    
    yield  

    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth")
