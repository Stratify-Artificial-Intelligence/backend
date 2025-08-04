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
        return ResearchExtended(
            response_id=response_output['id'],
            status=response_output.get('status'),
            prompt_tokens=response_output['usage']['prompt_tokens'],
            completion_tokens=response_output['usage']['completion_tokens'],
            total_tokens=response_output['usage']['total_tokens'],
            citation_tokens=response_output['usage'].get('citation_tokens'),
            num_search_queries=response_output['usage'].get('num_search_queries'),
            reasoning_tokens=response_output['usage'].get('reasoning_tokens'),
            research=response_output['choices'][0]['message']['content'],
        )

    def get_deep_research_async(self, request_id: str) -> ResearchExtended | None:
        response = requests.get(
            settings.API_URL_ASYNC + f'/{request_id}',
            headers=self.headers,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 404:
                return None
            raise e
        response_output = response.json()
        return self._perplexity_async_response_to_research_schema(response_output)

    def do_deep_research_async(self, prompt: str, max_tokens: int) -> ResearchExtended:
        payload = {
            'request': {
                'model': 'sonar-deep-research',
                'messages': [
                    {'role': 'user', 'content': prompt},
                ],
                'max_tokens': max_tokens,
            }
        }
        response = requests.post(
            settings.API_URL_ASYNC,
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        response_output = response.json()
        return self._perplexity_async_response_to_research_schema(response_output)

    @staticmethod
    def _perplexity_async_response_to_research_schema(
        response: dict[str, Any],
    ) -> ResearchExtended:
        """Convert Perplexity API response to ResearchExtended schema."""
        response_info = response.get('response')
        if response_info is None:
            return ResearchExtended(
                response_id=response['id'],
                status=response['status'],
            )
        else:
            return ResearchExtended(
                response_id=response['id'],
                status=response['status'],
                prompt_tokens=response_info['usage']['prompt_tokens'],
                completion_tokens=response_info['usage']['completion_tokens'],
                total_tokens=response_info['usage']['total_tokens'],
                citation_tokens=response_info['usage'].get('citation_tokens'),
                num_search_queries=response_info['usage'].get('num_search_queries'),
                reasoning_tokens=response_info['usage'].get('reasoning_tokens'),
                research=response_info['choices'][0]['message']['content'],
            )
