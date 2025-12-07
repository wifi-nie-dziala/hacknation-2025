"""Report generation service - creates final analysis report."""
import requests
import json
from typing import List, Dict
import config
from .prediction_service import ATLANTIS_CONTEXT


class ReportGenerationService:
    """Generates structured JSON report."""

    def generate_report(self, facts: List[Dict], predictions: List[Dict],
                        unknowns: List[Dict], relations: List[Dict],
                        language: str = 'pl') -> Dict:
        """Generate complete analysis report as structured JSON."""
        print(f"[REPORT] Generating report with {len(facts)} facts, {len(predictions)} predictions, {len(unknowns)} unknowns", flush=True)

        if config.LLM_PROVIDER == 'cloudflare':
            return self._generate_with_cloudflare(facts, predictions, unknowns, relations, language)
        else:
            return self._generate_with_ollama(facts, predictions, unknowns, relations, language)

    def _build_full_prompt(self, facts: List[Dict], predictions: List[Dict],
                           unknowns: List[Dict], relations: List[Dict],
                           language: str) -> str:
        facts_str = "\n".join([f"- {f.get('fact', f.get('value', ''))}" for f in facts[:50]])
        predictions_str = "\n".join([f"- {p.get('value', p.get('prediction', ''))}" for p in predictions[:30]])
        unknowns_str = "\n".join([f"- {u.get('value', u.get('unknown', ''))}" for u in unknowns[:20]])

        relations_str = ""
        for r in relations[:30]:
            rel_type = r.get('relation_type', 'related')
            from_val = str(r.get('from_value', ''))[:50]
            to_val = str(r.get('to_value', ''))[:50]
            relations_str += f"- [{rel_type}] {from_val}... -> {to_val}...\n"

        if language == 'pl':
            return f"""KONTEKST ATLANTIS:
{ATLANTIS_CONTEXT}

ZEBRANE FAKTY:
{facts_str}

PREDYKCJE/PROGNOZY:
{predictions_str}

BRAKUJĄCE INFORMACJE:
{unknowns_str}

POWIĄZANIA MIĘDZY ELEMENTAMI:
{relations_str}

Na podstawie powyższych danych wygeneruj raport analityczny w formacie JSON z następującą strukturą:
{{
  "summary": "Streszczenie danych (max 150 słów) - przejrzyste, user-friendly",
  "positive_scenario": "Scenariusz pozytywny dla Atlantis z wyjaśnieniem korelacji (200-300 słów)",
  "negative_scenario": "Scenariusz negatywny dla Atlantis z wyjaśnieniem korelacji (200-300 słów)",
  "recommendations": "Rekomendacje: jakie decyzje pomogą uniknąć scenariuszy negatywnych (200-300 słów)"
}}

WAŻNE: Odpowiedz TYLKO poprawnym JSON-em, bez żadnego dodatkowego tekstu."""
        else:
            return f"""ATLANTIS CONTEXT:
{ATLANTIS_CONTEXT}

COLLECTED FACTS:
{facts_str}

PREDICTIONS/FORECASTS:
{predictions_str}

MISSING INFORMATION:
{unknowns_str}

RELATIONSHIPS:
{relations_str}

Based on the above data, generate an analytical report in JSON format with this structure:
{{
  "summary": "Data summary (max 150 words) - clear, user-friendly",
  "positive_scenario": "Positive scenario for Atlantis with correlations and cause-effect explanations (200-300 words)",
  "negative_scenario": "Negative scenario for Atlantis with correlations and cause-effect explanations (200-300 words)",
  "recommendations": "Recommendations: decisions to avoid negative scenarios (200-300 words)"
}}

IMPORTANT: Reply with ONLY valid JSON, no additional text."""

    def _generate_with_cloudflare(self, facts: List[Dict], predictions: List[Dict],
                                   unknowns: List[Dict], relations: List[Dict],
                                   language: str) -> Dict:
        if not config.CLOUDFLARE_ACCOUNT_ID or not config.CLOUDFLARE_API_TOKEN:
            return {'error': 'Cloudflare not configured'}

        model = config.CLOUDFLARE_MODEL_PL if language == 'pl' else config.CLOUDFLARE_MODEL_EN
        url = f"https://api.cloudflare.com/client/v4/accounts/{config.CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"

        headers = {
            "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        prompt = self._build_full_prompt(facts, predictions, unknowns, relations, language)

        payload = {
            "messages": [
                {"role": "system", "content": "You are a strategic analyst. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096
        }

        print(f"[REPORT] Calling Cloudflare model: {model}", flush=True)

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            print(f"[REPORT] Cloudflare response status: {response.status_code}", flush=True)
            if response.status_code != 200:
                print(f"[REPORT] Cloudflare error: {response.text[:500]}", flush=True)
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                raw = result["result"]["response"]
                print(f"[REPORT] Got response of {len(raw)} chars", flush=True)
                return self._parse_json_response(raw, facts, predictions, unknowns, relations)
            else:
                print(f"[REPORT] Cloudflare API returned success=false: {result.get('errors', [])}", flush=True)
        except Exception as e:
            print(f"[REPORT] Cloudflare exception: {e}", flush=True)

        return self._fallback_response(facts, predictions, unknowns, relations)

    def _generate_with_ollama(self, facts: List[Dict], predictions: List[Dict],
                               unknowns: List[Dict], relations: List[Dict],
                               language: str) -> Dict:
        prompt = self._build_full_prompt(facts, predictions, unknowns, relations, language)
        ollama_url = f'http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}/api/generate'
        print(f"[REPORT] Calling Ollama at {ollama_url} with model {config.OLLAMA_MODEL}", flush=True)

        try:
            response = requests.post(
                ollama_url,
                json={'model': config.OLLAMA_MODEL, 'prompt': prompt, 'stream': False},
                timeout=300
            )
            print(f"[REPORT] Ollama response status: {response.status_code}", flush=True)
            if response.status_code == 200:
                result = response.json()
                raw = result.get('response', '')
                print(f"[REPORT] Got response of {len(raw)} chars", flush=True)
                return self._parse_json_response(raw, facts, predictions, unknowns, relations)
            else:
                print(f"[REPORT] Ollama error response: {response.text[:500]}", flush=True)
        except Exception as e:
            print(f"[REPORT] Ollama exception: {e}", flush=True)

        return self._fallback_response(facts, predictions, unknowns, relations)

    def _parse_json_response(self, raw: str, facts: List[Dict], predictions: List[Dict],
                              unknowns: List[Dict], relations: List[Dict]) -> Dict:
        import re
        print(f"[REPORT_PARSE] Raw response preview: {raw[:500]}", flush=True)

        cleaned = raw.strip()
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned = '\n'.join(lines)

        try:
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = cleaned[start:end]
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
                parsed = json.loads(json_str)
                if all(k in parsed for k in ['summary', 'positive_scenario', 'negative_scenario', 'recommendations']):
                    parsed['metadata'] = {
                        'facts_count': len(facts),
                        'predictions_count': len(predictions),
                        'unknowns_count': len(unknowns),
                        'relations_count': len(relations)
                    }
                    print(f"[REPORT_PARSE] Successfully parsed JSON report", flush=True)
                    return parsed
                else:
                    print(f"[REPORT_PARSE] JSON missing required keys: {list(parsed.keys())}", flush=True)
        except json.JSONDecodeError as e:
            print(f"[REPORT_PARSE] JSON parse error: {e}", flush=True)
            try:
                start = cleaned.find('{')
                if start >= 0:
                    json_str = cleaned[start:]
                    if not json_str.rstrip().endswith('}'):
                        json_str = json_str.rstrip() + '"}'
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
                    parsed = json.loads(json_str)
                    parsed['metadata'] = {
                        'facts_count': len(facts),
                        'predictions_count': len(predictions),
                        'unknowns_count': len(unknowns),
                        'relations_count': len(relations)
                    }
                    print(f"[REPORT_PARSE] Successfully parsed JSON with repair", flush=True)
                    return parsed
            except:
                pass

        print(f"[REPORT_PARSE] All parsing failed, using fallback", flush=True)
        return self._fallback_response(facts, predictions, unknowns, relations)

    def _fallback_response(self, facts: List[Dict], predictions: List[Dict],
                           unknowns: List[Dict], relations: List[Dict]) -> Dict:
        facts_summary = "; ".join([f.get('fact', f.get('value', ''))[:100] for f in facts[:5]]) if facts else "No facts available"
        predictions_summary = "; ".join([p.get('value', p.get('prediction', ''))[:100] for p in predictions[:3]]) if predictions else "No predictions available"

        return {
            'summary': f'Automatic summary: Analyzed {len(facts)} facts, {len(predictions)} predictions, {len(unknowns)} unknowns. Key facts: {facts_summary[:300]}',
            'positive_scenario': f'Based on current data ({len(facts)} facts), positive developments could include stability in key areas mentioned. Predictions: {predictions_summary[:500]}',
            'negative_scenario': f'Risk factors identified from {len(unknowns)} unknown variables. Monitoring recommended for: {"; ".join([u.get("value", u.get("unknown", ""))[:100] for u in unknowns[:3]]) if unknowns else "unidentified risks"}',
            'recommendations': f'Continue monitoring {len(facts)} identified facts. Address {len(unknowns)} unknown factors. Review {len(predictions)} predictions for actionable insights.',
            'metadata': {
                'facts_count': len(facts),
                'predictions_count': len(predictions),
                'unknowns_count': len(unknowns),
                'relations_count': len(relations),
                'error': False,
                'fallback': True
            }
        }

