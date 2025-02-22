from typing import Optional

from pydantic import BaseModel, Field


class Test(BaseModel):
    id: int
    name: str
    description: Optional[str] = Field(
        None,
        description='This is a description for a Test.',
    )

    class Config:
        extra = 'forbid'
