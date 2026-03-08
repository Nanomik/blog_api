from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    title: str
    content: str

    @field_validator("title", "content")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Поле не может быть пустым")
        return v


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    @field_validator("title", "content")
    @classmethod
    def not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Поле не может быть пустым")
        return v


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
