from fastapi import FastAPI
from contextlib import asynccontextmanager

from api import main

from db import init_db,get_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    get_session()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(main.router)
