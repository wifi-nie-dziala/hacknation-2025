"""Fact extraction service using LLM."""
import requests
from typing import List
import config


ATLANTIS_CONTEXT = """
Nazwa państwa: Atlantis
Istotne cechy położenia geograficznego: dostęp do Morza Bałtyckiego, kilka dużych żeglownych rzek, ograniczone zasoby wody pitnej
Liczba ludności: 28 mln
Klimat: umiarkowany
Silne strony gospodarki: przemysł ciężki, motoryzacyjny, spożywczy, chemiczny, ICT, ambicje odgrywania istotnej roli w zakresie OZE, przetwarzania surowców krytycznych oraz budowy ponadnarodowej infrastruktury AI (m.in. big data centers, giga fabryki AI, komputery kwantowe)
Liczebność armii: 150 tys. zawodowych żołnierzy
Stopnień cyfryzacji społeczeństwa: powyżej średniej europejskiej
Waluta: inna niż euro
Kluczowe relacje dwustronne: Niemcy, Francja, Finlandia, Ukraina, USA, Japonia
Potencjalne zagrożenia polityczne i gospodarcze: niestabilność w UE, rozpad UE na grupy „różnych prędkości" pod względem tempa rozwoju oraz zainteresowania głębszą integracją; negatywna kampania wizerunkowa ze strony kilku aktorów państwowych wymierzona przeciw rządowi lub społeczeństwu Atlantis; zakłócenia w dostawach paliw węglowodorowych z USA, Skandynawii, Zatoki Perskiej (wynikające z potencjalnych zmian w polityce wewnętrznej krajów eksporterów lub problemów w transporcie, np. ataki Hutich na gazowce na Morzu Czerwonym); narażenie na spowolnienie rozwoju sektora ICT z powodu embarga na wysokozaawansowane procesory
Potencjalne zagrożenie militarne: zagrożenie atakiem zbrojnym jednego z sąsiadów; trwające od wielu lat ataki hybrydowe co najmniej jednego sąsiada, w tym w obszarze infrastruktury krytycznej i cyberprzestrzeni
Kamienie milowe w rozwoju politycznym i gospodarczym: demokracja parlamentarna od 130 lat; okres stagnacji gospodarczej w latach 1930-1950 oraz 1980-1990; członkostwo w UE i NATO od roku 1997; 25. gospodarka świata wg PKB
"""


class FactExtractionService:
    """Handles LLM-based fact extraction."""

    def extract_facts(self, text: str, language: str = 'en') -> List[str]:
        """Extract facts from text using LLM."""
        print(f"[FACT_EXTRACTION] Calling LLM ({config.LLM_PROVIDER}) for fact extraction...", flush=True)
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
            f"You are an expert analyst for the hypothetical country Atlantis. {ATLANTIS_CONTEXT}\n\n"
            "Extract key facts from text that are relevant to Atlantis. "
            "Return only the facts, one per line." if language == 'en' else
            f"Jesteś ekspertem analitykiem dla hipotetycznego państwa Atlantis. {ATLANTIS_CONTEXT}\n\n"
            "Wyodrębnij kluczowe fakty z tekstu, które są istotne dla Atlantis. "
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
            return (
                f'Extract key facts from the following text. Return ONLY the facts, one per line.\n'
                f'Do NOT include any titles, headers, or phrases like "Here are the extracted facts:", "Extracted facts:", etc.\n'
                f'Just output the raw facts directly.\n\n{text}'
            )
        else:
            return (
                f'Wyodrębnij kluczowe fakty z następującego tekstu. Zwróć TYLKO fakty, jeden na linię.\n'
                f'NIE dodawaj żadnych tytułów, nagłówków ani fraz takich jak "Oto fakty:", "Wyodrębnione fakty:", itp.\n'
                f'Po prostu wypisz same fakty.\n\n{text}'
            )

    def _parse_facts(self, facts_text: str) -> List[str]:
        """Parse facts from LLM response."""
        skip_phrases = [
            'here are the extracted facts',
            'extracted facts:',
            'here are the facts',
            'poniżej znajdują się fakty',
            'wyodrębnione fakty:',
            'oto fakty',
        ]
        facts = []
        for f in facts_text.split('\n'):
            line = f.strip()
            if not line:
                continue
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                line = line.lstrip('-*•').strip()
            lower = line.lower()
            if any(skip in lower for skip in skip_phrases):
                continue
            if len(line) > 10:
                facts.append(line)
        return facts

