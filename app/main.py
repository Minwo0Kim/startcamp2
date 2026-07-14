# backend/app/main.py
from fastapi import FastAPI

from .database import engine
from .models import Base
from .routers.roulette import router as roulette_router


app = FastAPI()
app.include_router(roulette_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "LocalHub 백엔드 서버 정상 작동 중!"}