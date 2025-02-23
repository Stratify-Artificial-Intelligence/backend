from pydantic import BaseModel, Field


class TestBase(BaseModel):
    description: str | None = Field(
        None, description="This is a description for a Test."
    )

    class Config:
        extra = "forbid"


class TestCreate(TestBase):
    name: str


class Test(TestCreate):
    id: int


class TestPartialUpdate(TestBase):
    name: str | None = None
