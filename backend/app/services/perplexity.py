import requests
from app.settings import PerplexitySettings


settings = PerplexitySettings()


def deep_research(prompt: str, max_tokens: int) -> str:
    headers = {
        'Authorization': f'Bearer {settings.API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    payload = {
        'model': 'sonar-deep-research',
        'messages': [{'role': 'user', 'content': prompt}, ],
        'max_tokens': max_tokens,
    }
    response = requests.post(settings.API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
