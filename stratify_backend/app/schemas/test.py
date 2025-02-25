from pydantic import BaseModel, ConfigDict, Field


class TestBase(BaseModel):
    description: str | None = Field(
        None,
        description='This is a description for a Test.',
    )

    model_config = ConfigDict(extra='forbid')


class TestCreate(TestBase):
    name: str


class Test(TestCreate):
    id: int


class TestPartialUpdate(TestBase):
    name: str | None = None
