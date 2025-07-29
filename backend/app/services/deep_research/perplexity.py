from typing import Any

import requests

from app.schemas import ResearchExtended
from app.services.deep_research.base import DeepResearchProvider
from app.settings import PerplexitySettings


settings = PerplexitySettings()


class DeepResearchPerplexity(DeepResearchProvider):
    """Implementation of DeepResearchProvider using Perplexity AI."""

    headers = {
        'Authorization': f'Bearer {settings.API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def do_deep_research(self, prompt: str, max_tokens: int) -> ResearchExtended:
        payload = {
            'model': 'sonar-deep-research',
            'messages': [
                {'role': 'user', 'content': prompt},
            ],
            'max_tokens': max_tokens,
        }
        response = requests.post(settings.API_URL, headers=self.headers, json=payload)
        response.raise_for_status()
        response_output = response.json()
        return self._perplexity_response_to_research_schema(response_output)

    def get_deep_research_async(self, request_id: str) -> ResearchExtended:
        response = requests.get(
            settings.API_URL_ASYNC + f'/{request_id}',
            headers=self.headers,
        )
        response.raise_for_status()
        response_output = response.json()
        return self._perplexity_response_to_research_schema(response_output['response'])

    def do_deep_research_async(self, prompt: str, max_tokens: int) -> ResearchExtended:
        payload = {
            'model': 'sonar-deep-research',
            'messages': [
                {'role': 'user', 'content': prompt},
            ],
            'max_tokens': max_tokens,
        }
        response = requests.post(
            settings.API_URL_ASYNC,
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        response_output = response.json()
        return self._perplexity_response_to_research_schema(response_output['response'])

    @staticmethod
    def _perplexity_response_to_research_schema(
        response: dict[str, Any],
    ) -> ResearchExtended:
        """Convert Perplexity API response to ResearchExtended schema."""
        return ResearchExtended(
            response_id=response['id'],
            status=response.get('status'),
            prompt_tokens=response['usage']['prompt_tokens'],
            completion_tokens=response['usage']['completion_tokens'],
            total_tokens=response['usage']['total_tokens'],
            citation_tokens=response['usage'].get('citation_tokens'),
            num_search_queries=response['usage'].get('num_search_queries'),
            reasoning_tokens=response['usage'].get('reasoning_tokens'),
            research=response['choices'][0]['message']['content'],
        )
