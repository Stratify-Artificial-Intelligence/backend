from pydantic import BaseModel, ConfigDict


class Test(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
