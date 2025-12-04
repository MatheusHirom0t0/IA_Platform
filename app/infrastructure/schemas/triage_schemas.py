# app/schemas/triage_schemas.py
from pydantic import BaseModel


class TriageRequest(BaseModel):
    message: str


class TriageResponse(BaseModel):
    reply: str
