"""TODO"""
from pydantic import BaseModel


class CreditInterviewRequest(BaseModel):
    """TODO"""
    cpf: str
    renda_mensal: float
    despesas_mensais: float
    tipo_emprego: str
    numero_dependentes: int
    tem_dividas: bool


class CreditInterviewResponse(BaseModel):
    """TODO"""
    score: float
    reply: str
