import requests

from app.schemas import BusinessResearch
from app.settings import PerplexitySettings


# ToDo (pduran): Refactor this into the ServiceFactory


settings = PerplexitySettings()


def deep_research(prompt: str, max_tokens: int) -> BusinessResearch:
    headers = {
        'Authorization': f'Bearer {settings.API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    payload = {
        'model': 'sonar-deep-research',
        'messages': [
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': max_tokens,
    }
    response = requests.post(settings.API_URL, headers=headers, json=payload)
    response.raise_for_status()
    response_output = response.json()
    return BusinessResearch(
        id=response_output['id'],
        prompt_tokens=response_output['usage']['prompt_tokens'],
        completion_tokens=response_output['usage']['completion_tokens'],
        total_tokens=response_output['usage']['total_tokens'],
        citation_tokens=response_output['usage']['citation_tokens'],
        num_search_queries=response_output['usage']['num_search_queries'],
        reasoning_tokens=response_output['usage']['reasoning_tokens'],
        research=response_output['choices'][0]['message']['content'],
    )
