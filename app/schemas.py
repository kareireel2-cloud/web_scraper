from pydantic import BaseModel, Field, AnyHttpUrl

class ItemBase(BaseModel):
    url : AnyHttpUrl
    title: str = Field(min_length=1, max_length=200)
    max_concurency : int 