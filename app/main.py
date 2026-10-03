from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
