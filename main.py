"""TODO"""
from fastapi import FastAPI

from app.routers.auth_router import router as auth_router
from app.routers.triage_router import router as triage_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(triage_router)
