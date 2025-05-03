from pydantic import BaseModel


class BusinessResearchParams(BaseModel):
    max_tokens: int


class BusinessResearch(BaseModel):
    id: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    citation_tokens: int
    num_search_queries: int
    reasoning_tokens: int
    research: str
