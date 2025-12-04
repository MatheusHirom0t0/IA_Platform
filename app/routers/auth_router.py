"""TODO"""
from fastapi import APIRouter
from app.controllers.auth_controller import AuthController

router = APIRouter(prefix="/login", tags=["auth"])

controller = AuthController()


@router.get("")
def login(cpf: str, birth_date: str):
    """TODO"""
    return controller.login(cpf, birth_date)
