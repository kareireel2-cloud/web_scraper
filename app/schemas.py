from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be empty")
        if not (1 <= len(value) <= 200):
            raise ValueError("title length must be between 1 and 200 characters")
        return value


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
