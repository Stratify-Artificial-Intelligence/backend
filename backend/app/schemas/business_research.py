from pydantic import BaseModel, model_validator

from app.enums import ResearchRequestStatusEnum


class Research(BaseModel):
    research: str


class ResearchExtended(Research):
    response_id: str
    status: ResearchRequestStatusEnum | None = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    citation_tokens: int | None = None
    num_search_queries: int | None = None
    reasoning_tokens: int | None = None


class ResearchParams(BaseModel):
    max_tokens: int
    business_id: int | None = None
    sync_generation: bool | None = False


class ResearchStoreParams(BaseModel):
    business_id: int | None = None
    research_id: str | None = None
    research: str | None = None

    @model_validator(mode='after')
    def validate_research_id_xor_research(self):
        fields = ['research_id', 'research']
        set_fields = [field for field in fields if getattr(self, field) is not None]
        if len(set_fields) != 1:
            raise ValueError('Exactly one of research_id or research must be provided.')
        return self
