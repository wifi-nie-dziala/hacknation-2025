"""Unknown information extraction service using LLM."""
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


class UnknownService:
    """Handles LLM-based unknown/missing information extraction."""

    def extract_unknowns(self, text: str, language: str = 'en') -> List[str]:
        """Extract missing information from text using LLM."""
        if config.LLM_PROVIDER == 'cloudflare':
            return self._extract_with_cloudflare(text, language)
        else:
            return self._extract_with_ollama(text, language)

    def _extract_with_cloudflare(self, text: str, language: str) -> List[str]:
        """Extract unknowns using Cloudflare Workers AI."""
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
            "Identify missing information or unknowns that would be important for Atlantis. "
            "Return only the missing information items, one per line." if language == 'en' else
            f"Jesteś ekspertem analitykiem dla hipotetycznego państwa Atlantis. {ATLANTIS_CONTEXT}\n\n"
            "Zidentyfikuj brakujące informacje lub niewiadome, które byłyby ważne dla Atlantis. "
            "Zwróć tylko brakujące informacje, jedną na linię."
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
                unknowns_text = result["result"]["response"]
                return self._parse_unknowns(unknowns_text)
            else:
                print(f"Cloudflare AI error: {result.get('errors')}")
                return []

        except Exception as e:
            print(f"Cloudflare AI extraction error: {e}")
            return []

    def _extract_with_ollama(self, text: str, language: str) -> List[str]:
        """Extract unknowns using local Ollama LLM."""
        prompt = self._build_prompt(text, language)

        try:
            response = requests.post(
                f'http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}/api/generate',
                json={'model': config.OLLAMA_MODEL, 'prompt': prompt, 'stream': False},
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                unknowns_text = result.get('response', '')
                return self._parse_unknowns(unknowns_text)
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
                f"Context: You are analyzing information for the hypothetical country Atlantis.\n\n{ATLANTIS_CONTEXT}\n\n"
                f"Based on the following text, identify what information is missing or unknown that would be important for Atlantis:\n\n{text}\n\n"
                "Missing information:"
            )
        else:
            return (
                f"Kontekst: Analizujesz informacje dla hipotetycznego państwa Atlantis.\n\n{ATLANTIS_CONTEXT}\n\n"
                f"Na podstawie następującego tekstu zidentyfikuj, jakie informacje brakują lub są nieznane, a które byłyby ważne dla Atlantis:\n\n{text}\n\n"
                "Brakujące informacje:"
            )

    def _parse_unknowns(self, unknowns_text: str) -> List[str]:
        """Parse unknowns from LLM response."""
        unknowns = [
            u.strip()
            for u in unknowns_text.split('\n')
            if u.strip() and not u.strip().startswith('-') and not u.strip().startswith('*')
        ]
        return unknowns
