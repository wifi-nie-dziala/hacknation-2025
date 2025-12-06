import json
import requests
from typing import List, Dict, Optional, Any
from repositories.node_repository import NodeRepository
import config


class ScenarioService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.node_repo = NodeRepository(db_connection)
    
    def generate_scenarios(self, job_uuid: str) -> Dict[str, Any]:
        nodes = self.node_repo.get_nodes_by_job(job_uuid)
        
        if not nodes:
            return {
                'summary': 'No data to analyze',
                'scenarios': []
            }
        
        facts = [n for n in nodes if n['type'] == 'fact']
        predictions = [n for n in nodes if n['type'] == 'prediction']
        missing_info = [n for n in nodes if n['type'] == 'missing_information']
        
        context = self._build_context(facts, predictions, missing_info)
        
        scenarios = []
        for timeframe in ['12_months', '36_months']:
            for sentiment in ['positive', 'negative']:
                scenario = self._generate_scenario(context, timeframe, sentiment)
                if scenario:
                    scenarios.append(scenario)
        
        summary = self._generate_summary(context)
        
        return {
            'summary': summary,
            'scenarios': scenarios
        }
    
    def _build_context(self, facts: List[Dict], predictions: List[Dict], missing_info: List[Dict]) -> str:
        parts = []
        
        if facts:
            parts.append("FACTS:")
            for f in facts:
                parts.append(f"- {f['value']}")
        
        if predictions:
            parts.append("\nPREDICTIONS:")
            for p in predictions:
                parts.append(f"- {p['value']}")
        
        if missing_info:
            parts.append("\nMISSING INFORMATION:")
            for m in missing_info:
                parts.append(f"- {m['value']}")
        
        return "\n".join(parts)
    
    def _generate_scenario(self, context: str, timeframe: str, sentiment: str) -> Optional[Dict]:
        prompt = f"""Based on the following analysis, generate a {sentiment} scenario for {timeframe.replace('_', ' ')}.

{context}

Create a strategic scenario with:
1. Description of what could happen
2. Concept map showing causal relationships

Respond with JSON:
{{
  "timeframe": "{timeframe}",
  "sentiment": "{sentiment}",
  "description": "scenario description",
  "concept_map": {{
    "nodes": [
      {{"id": "n1", "label": "node label", "type": "action|effect|outcome|trigger|reaction|risk"}}
    ],
    "edges": [
      {{"source": "n1", "target": "n2", "relation": "relation description"}}
    ]
  }}
}}
"""
        
        try:
            response = requests.post(
                f'http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}/api/generate',
                json={
                    'model': config.OLLAMA_MODEL,
                    'prompt': prompt,
                    'stream': False,
                    'format': 'json'
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                try:
                    scenario = json.loads(response_text)
                    return scenario
                except json.JSONDecodeError:
                    return None
            
            return None
        except Exception as e:
            print(f"Scenario generation error: {e}")
            return None
    
    def _generate_summary(self, context: str) -> str:
        prompt = f"""Based on the following strategic analysis, provide a concise summary (2-3 sentences) of the overall situation:

{context}

Summary:"""
        
        try:
            response = requests.post(
                f'http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}/api/generate',
                json={
                    'model': config.OLLAMA_MODEL,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            
            return 'Analysis summary unavailable'
        except Exception as e:
            print(f"Summary generation error: {e}")
            return 'Analysis summary unavailable'
