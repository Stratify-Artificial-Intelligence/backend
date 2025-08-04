from pydantic import BaseModel

from app.enums import ResearchRequestStatusEnum


class Research(BaseModel):
    research: str


class ResearchExtended(BaseModel):
    response_id: str
    status: ResearchRequestStatusEnum | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    citation_tokens: int | None = None
    num_search_queries: int | None = None
    reasoning_tokens: int | None = None
    research: str | None = None


class ResearchParams(BaseModel):
    max_tokens: int
    business_id: int | None = None
    sync_generation: bool | None = False
