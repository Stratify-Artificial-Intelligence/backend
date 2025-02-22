from pydantic import BaseModel


class Test(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None

    class Config:
        from_attributes = True
