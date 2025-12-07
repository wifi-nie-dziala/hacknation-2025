"""Fact extraction service using LLM."""
import requests
from typing import List
import config


class FactExtractionService:
    """Handles LLM-based fact extraction."""

    def extract_facts(self, text: str, language: str = 'en') -> List[str]:
        """Extract facts from text using LLM."""
        if config.LLM_PROVIDER == 'cloudflare':
            return self._extract_with_cloudflare(text, language)
        else:
            return self._extract_with_ollama(text, language)

    def _extract_with_cloudflare(self, text: str, language: str) -> List[str]:
        """Extract facts using Cloudflare Workers AI."""
        if not config.CLOUDFLARE_ACCOUNT_ID or not config.CLOUDFLARE_API_TOKEN:
            print("ERROR: Cloudflare credentials not configured")
            return []

        model = config.CLOUDFLARE_MODEL_EN if language == 'en' else config.CLOUDFLARE_MODEL_PL

        url = f"https://api.cloudflare.com/client/v4/accounts/{config.CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"

        headers = {
            "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        system_message = (
            "You are a helpful assistant that extracts key facts from text. "
            "Return only the facts, one per line." if language == 'en' else
            "Jesteś pomocnym asystentem, który wyodrębnia kluczowe fakty z tekstu. "
            "Zwróć tylko fakty, jeden na linię."
        )

        prompt = self._build_prompt(text, language)

        payload = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            if result.get("success"):
                facts_text = result["result"]["response"]
                return self._parse_facts(facts_text)
            else:
                print(f"Cloudflare AI error: {result.get('errors')}")
                return []

        except Exception as e:
            print(f"Cloudflare AI extraction error: {e}")
            return []

    def _extract_with_ollama(self, text: str, language: str) -> List[str]:
        """Extract facts using local Ollama LLM."""
        prompt = self._build_prompt(text, language)

        try:
            response = requests.post(
                f'http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}/api/generate',
                json={'model': config.OLLAMA_MODEL, 'prompt': prompt, 'stream': False},
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                facts_text = result.get('response', '')
                return self._parse_facts(facts_text)
            else:
                print(f"Ollama extraction error: Status {response.status_code}, Response: {response.text}")
                return []

        except Exception as e:
            print(f"Ollama extraction error: {e}")

        return []

    def _build_prompt(self, text: str, language: str) -> str:
        """Build extraction prompt."""
        if language == 'en':
            return f'Extract key facts from the following text. Return only the facts, one per line:\n\n{text}\n\nFacts:'
        else:
            return f'Wyodrębnij kluczowe fakty z następującego tekstu. Zwróć tylko fakty, jeden na linię:\n\n{text}\n\nFakty:'

    def _parse_facts(self, facts_text: str) -> List[str]:
        """Parse facts from LLM response."""
        facts = [
            f.strip()
            for f in facts_text.split('\n')
            if f.strip() and not f.strip().startswith('-') and not f.strip().startswith('*')
        ]
        return facts

