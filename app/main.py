# backend/app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "LocalHub 백엔드 서버 정상 작동 중!"}