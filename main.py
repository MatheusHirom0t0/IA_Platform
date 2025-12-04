from fastapi import FastAPI
from app.routers.screening_router import router as screening_router
from app.routers.auth_router import router as auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(screening_router)
