"""Prediction extraction service using LLM."""
import requests
from typing import List, Dict
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


class PredictionService:
    """Handles LLM-based prediction extraction (positive and negative)."""

    def extract_predictions(self, text: str, language: str = 'en') -> Dict[str, List[str]]:
        """Extract positive and negative predictions from text using LLM."""
        if config.LLM_PROVIDER == 'cloudflare':
            return self._extract_with_cloudflare(text, language)
        else:
            return self._extract_with_ollama(text, language)

    def _extract_with_cloudflare(self, text: str, language: str) -> Dict[str, List[str]]:
        """Extract predictions using Cloudflare Workers AI."""
        if not config.CLOUDFLARE_ACCOUNT_ID or not config.CLOUDFLARE_API_TOKEN:
            print("ERROR: Cloudflare credentials not configured")
            return {'positive': [], 'negative': []}

        model = config.CLOUDFLARE_MODEL_EN if language == 'en' else config.CLOUDFLARE_MODEL_PL

        url = f"https://api.cloudflare.com/client/v4/accounts/{config.CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"

        headers = {
            "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        system_message = (
            f"You are an expert analyst for the hypothetical country Atlantis. {ATLANTIS_CONTEXT}\n\n"
            "Extract predictions from the text. Return ONLY predictions related to Atlantis.\n"
            "Format:\n"
            "POSITIVE:\n- prediction 1\n- prediction 2\n\n"
            "NEGATIVE:\n- prediction 1\n- prediction 2" if language == 'en' else
            f"Jesteś ekspertem analitykiem dla hipotetycznego państwa Atlantis. {ATLANTIS_CONTEXT}\n\n"
            "Wyodrębnij predykcje z tekstu. Zwróć TYLKO predykcje związane z Atlantis.\n"
            "Format:\n"
            "POZYTYWNE:\n- predykcja 1\n- predykcja 2\n\n"
            "NEGATYWNE:\n- predykcja 1\n- predykcja 2"
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
                predictions_text = result["result"]["response"]
                return self._parse_predictions(predictions_text, language)
            else:
                print(f"Cloudflare AI error: {result.get('errors')}")
                return {'positive': [], 'negative': []}

        except Exception as e:
            print(f"Cloudflare AI extraction error: {e}")
            return {'positive': [], 'negative': []}

    def _extract_with_ollama(self, text: str, language: str) -> Dict[str, List[str]]:
        """Extract predictions using local Ollama LLM."""
        prompt = self._build_prompt(text, language)

        try:
            response = requests.post(
                f'http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}/api/generate',
                json={'model': config.OLLAMA_MODEL, 'prompt': prompt, 'stream': False},
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                predictions_text = result.get('response', '')
                return self._parse_predictions(predictions_text, language)
            else:
                print(f"Ollama extraction error: Status {response.status_code}, Response: {response.text}")
                return {'positive': [], 'negative': []}

        except Exception as e:
            print(f"Ollama extraction error: {e}")

        return {'positive': [], 'negative': []}

    def _build_prompt(self, text: str, language: str) -> str:
        """Build extraction prompt."""
        if language == 'en':
            return (
                f"Context: You are analyzing information for the hypothetical country Atlantis.\n\n{ATLANTIS_CONTEXT}\n\n"
                f"Extract positive and negative predictions from the following text that are relevant to Atlantis:\n\n{text}\n\n"
                "Format:\nPOSITIVE:\n- prediction 1\n- prediction 2\n\nNEGATIVE:\n- prediction 1\n- prediction 2"
            )
        else:
            return (
                f"Kontekst: Analizujesz informacje dla hipotetycznego państwa Atlantis.\n\n{ATLANTIS_CONTEXT}\n\n"
                f"Wyodrębnij pozytywne i negatywne predykcje z następującego tekstu, które są istotne dla Atlantis:\n\n{text}\n\n"
                "Format:\nPOZYTYWNE:\n- predykcja 1\n- predykcja 2\n\nNEGATYWNE:\n- predykcja 1\n- predykcja 2"
            )

    def _parse_predictions(self, predictions_text: str, language: str) -> Dict[str, List[str]]:
        """Parse predictions from LLM response."""
        lines = predictions_text.split('\n')
        
        positive_markers = ['POSITIVE:', 'POZYTYWNE:']
        negative_markers = ['NEGATIVE:', 'NEGATYWNE:']
        
        positive = []
        negative = []
        current_section = None

        for line in lines:
            line = line.strip()
            
            if any(marker in line.upper() for marker in positive_markers):
                current_section = 'positive'
                continue
            elif any(marker in line.upper() for marker in negative_markers):
                current_section = 'negative'
                continue
            
            if line and (line.startswith('-') or line.startswith('*')):
                cleaned = line.lstrip('-*').strip()
                if cleaned:
                    if current_section == 'positive':
                        positive.append(cleaned)
                    elif current_section == 'negative':
                        negative.append(cleaned)

        return {'positive': positive, 'negative': negative}
