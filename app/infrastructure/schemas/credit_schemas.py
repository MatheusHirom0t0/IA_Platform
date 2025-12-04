from pydantic import BaseModel


class CreditRequest(BaseModel):
    cpf: str
    message: str


class CreditResponse(BaseModel):
    reply: str