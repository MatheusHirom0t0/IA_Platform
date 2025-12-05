from fastapi import FastAPI
from app.routers.screening_router import router as screening_router
from app.routers.auth_router import router as auth_router
from app.routers.credit_router import router as credit_router
from app.routers.forex_router import router as forex_router
from app.routers.interview_router import router as interview_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(screening_router)
app.include_router(credit_router)
app.include_router(forex_router)
app.include_router(interview_router)