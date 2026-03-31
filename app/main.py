from fastapi import FastAPI, Depends
from .routers.auth import router as auth_router
from .database import engine, Base
from .models import user

app = FastAPI()

app.include_router(auth_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

