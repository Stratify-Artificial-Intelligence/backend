from pydantic import BaseModel, Field


class TestCreate(BaseModel):
    name: str
    description: str | None = Field(
        None,
        description='This is a description for a Test.',
    )

    class Config:
        extra = 'forbid'


class Test(TestCreate):
    id: int

    class Config:
        extra = 'forbid'
