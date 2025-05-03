from pydantic import BaseModel


class BusinessResearchParams(BaseModel):
    max_tokens: int


class BusinessResearch(BaseModel):
    research: str
