"""FastAPI entry point:  uvicorn app.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.routers import api
from app.services.recommender import Recommender

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.recommender = Recommender()   # loads catalogue + trains/loads FastText once
    yield


app = FastAPI(title="Acme Retail Enterprises - Product Recommendations", lifespan=lifespan)
app.include_router(api.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
