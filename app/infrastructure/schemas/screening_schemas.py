"""Pydantic schemas for screening chat messages."""

from pydantic import BaseModel


class ScreeningRequest(BaseModel):
    """Incoming message sent by the user to the screening agent."""

    message: str


class ScreeningResponse(BaseModel):
    """Response returned by the screening agent."""

    reply: str
