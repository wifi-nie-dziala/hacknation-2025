import json
import requests
from typing import List, Dict, Optional, Any
from repositories.node_repository import NodeRepository
from repositories.fact_repository import FactRepository
import config


class ReasoningService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.node_repo = NodeRepository(db_connection)
        self.fact_repo = FactRepository(db_connection)
    
    def analyze_facts_for_job(self, job_uuid: str) -> Dict[str, Any]:
        facts = self.fact_repo.get_facts_by_job_uuid(job_uuid)
        
        if not facts:
            return {
                'status': 'completed',
                'nodes_created': 0,
                'relations_created': 0,
                'message': 'No facts to analyze'
            }
        
        system_prompt = self._get_system_prompt()
        tools = self._get_tools()
        
        facts_text = "\n".join([f"- {f['fact']}" for f in facts])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze these facts extracted for government strategic analysis:\n\n{facts_text}\n\nIdentify important facts, create predictions, identify missing information, and build relations between them."}
        ]
        
        nodes_created = 0
        relations_created = 0
        max_iterations = 20
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            response = self._call_llm(messages, tools)
            
            if not response:
                break
            
            assistant_message = response['choices'][0]['message']
            messages.append(assistant_message)
            
            finish_reason = response['choices'][0]['finish_reason']
            
            if finish_reason == 'tool_calls':
                tool_calls = assistant_message.get('tool_calls', [])
                
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])
                    
                    result = self._execute_tool(function_name, arguments, job_uuid)
                    
                    if result.get('success'):
                        if 'node_id' in result:
                            nodes_created += 1
                        if 'relation_id' in result:
                            relations_created += 1
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": json.dumps(result)
                    })
            
            elif finish_reason == 'stop':
                break
        
        return {
            'status': 'completed',
            'nodes_created': nodes_created,
            'relations_created': relations_created,
            'iterations': iteration
        }
    
    def _call_llm(self, messages: List[Dict], tools: List[Dict]) -> Optional[Dict]:
        try:
            formatted_prompt = self._format_messages_for_ollama(messages, tools)
            
            print("\n" + "="*80)
            print("OLLAMA REQUEST:")
            print("="*80)
            print(formatted_prompt[:500] + "..." if len(formatted_prompt) > 500 else formatted_prompt)
            print("="*80 + "\n")
            
            response = requests.post(
                f'http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}/api/generate',
                json={
                    'model': config.OLLAMA_MODEL, 
                    'prompt': formatted_prompt, 
                    'stream': False,
                    'format': 'json'
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print("\n" + "="*80)
                print("OLLAMA RESPONSE:")
                print("="*80)
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                print("="*80 + "\n")
                
                try:
                    parsed = json.loads(response_text)
                    return self._convert_ollama_to_openai_format(parsed)
                except json.JSONDecodeError:
                    print(f"ERROR: Failed to parse JSON response")
                    return None
            
            return None
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None
    
    def _format_messages_for_ollama(self, messages: List[Dict], tools: List[Dict]) -> str:
        prompt_parts = []
        
        for msg in messages:
            if msg['role'] == 'system':
                prompt_parts.append(f"SYSTEM: {msg['content']}\n")
            elif msg['role'] == 'user':
                prompt_parts.append(f"USER: {msg['content']}\n")
            elif msg['role'] == 'assistant':
                if 'content' in msg and msg['content']:
                    prompt_parts.append(f"ASSISTANT: {msg['content']}\n")
            elif msg['role'] == 'tool':
                prompt_parts.append(f"TOOL RESULT: {msg['content']}\n")
        
        tools_desc = "\n\nAVAILABLE TOOLS:\n"
        for tool in tools:
            func = tool['function']
            tools_desc += f"- {func['name']}: {func['description']}\n"
            tools_desc += f"  Parameters: {json.dumps(func['parameters'], indent=2)}\n"
        
        prompt_parts.append(tools_desc)
        prompt_parts.append("\nRespond with JSON in format: {\"action\": \"tool_call\" or \"finish\", \"tool_calls\": [{\"name\": \"tool_name\", \"arguments\": {...}}]}\n")
        
        return "".join(prompt_parts)
    
    def _convert_ollama_to_openai_format(self, parsed: Dict) -> Dict:
        if parsed.get('action') == 'finish':
            return {
                'choices': [{
                    'message': {'role': 'assistant', 'content': parsed.get('message', 'Analysis complete')},
                    'finish_reason': 'stop'
                }]
            }
        
        tool_calls = []
        for idx, tc in enumerate(parsed.get('tool_calls', [])):
            tool_calls.append({
                'id': f'call_{idx}',
                'type': 'function',
                'function': {
                    'name': tc['name'],
                    'arguments': json.dumps(tc['arguments'])
                }
            })
        
        if tool_calls:
            return {
                'choices': [{
                    'message': {
                        'role': 'assistant',
                        'content': None,
                        'tool_calls': tool_calls
                    },
                    'finish_reason': 'tool_calls'
                }]
            }
        
        return {
            'choices': [{
                'message': {'role': 'assistant', 'content': 'No action'},
                'finish_reason': 'stop'
            }]
        }
    
    def _execute_tool(self, function_name: str, arguments: Dict, job_uuid: str) -> Dict:
        try:
            if function_name == 'create_fact_node':
                return self._create_fact_node(arguments, job_uuid)
            elif function_name == 'create_prediction_node':
                return self._create_prediction_node(arguments, job_uuid)
            elif function_name == 'create_missing_info_node':
                return self._create_missing_info_node(arguments, job_uuid)
            elif function_name == 'create_relation':
                return self._create_relation(arguments)
            elif function_name == 'finish_analysis':
                return {'success': True, 'finished': True, 'summary': arguments.get('summary', '')}
            else:
                return {'success': False, 'error': 'Unknown tool'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_fact_node(self, args: Dict, job_uuid: str) -> Dict:
        value = args['value']
        metadata = args.get('metadata', {})
        metadata['importance'] = args.get('importance', 'medium')
        
        node_id = self.node_repo.create_node('fact', value, job_uuid, metadata)
        return {'success': True, 'node_id': node_id, 'type': 'fact'}
    
    def _create_prediction_node(self, args: Dict, job_uuid: str) -> Dict:
        value = args['value']
        metadata = args.get('metadata', {})
        metadata['confidence_level'] = args.get('confidence_level', 'medium')
        metadata['timeframe'] = args.get('timeframe')
        
        node_id = self.node_repo.create_node('prediction', value, job_uuid, metadata)
        return {'success': True, 'node_id': node_id, 'type': 'prediction'}
    
    def _create_missing_info_node(self, args: Dict, job_uuid: str) -> Dict:
        value = args['value']
        metadata = args.get('metadata', {})
        metadata['priority'] = args.get('priority', 'medium')
        metadata['needed_for'] = args.get('needed_for', '')
        
        node_id = self.node_repo.create_node('missing_information', value, job_uuid, metadata)
        return {'success': True, 'node_id': node_id, 'type': 'missing_information'}
    
    def _create_relation(self, args: Dict) -> Dict:
        source_node_id = args['source_node_id']
        target_node_id = args['target_node_id']
        relation_type = args['relation_type']
        confidence = args.get('confidence', 1.0)
        metadata = args.get('metadata', {})
        metadata['reasoning'] = args.get('reasoning', '')
        
        relation_id = self.node_repo.create_relation(
            source_node_id, target_node_id, relation_type, confidence, metadata
        )
        return {'success': True, 'relation_id': relation_id, 'relation_type': relation_type}
    
    def _get_system_prompt(self) -> str:
        return """You are a strategic analysis AI for government decision-making.

Your task is to analyze extracted facts and build a knowledge graph by:
1. Identifying relevant facts for government strategic analysis
2. Creating predictions based on facts
3. Identifying missing information needed for complete analysis
4. Building relations between nodes (facts, predictions, missing info)

IMPORTANT RULES:
- Only create nodes for facts that are relevant to government/state strategic planning
- Ignore trivial or irrelevant facts
- Create predictions when facts suggest future outcomes
- Identify critical missing information when facts create gaps in understanding
- Build relations to show causality and dependencies
- Use proper relation types: derived_from, supports, contradicts, requires, suggests
- When done, call finish_analysis

Think step by step and be thorough."""
    
    def _get_tools(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_fact_node",
                    "description": "Create a node for an important fact relevant to government strategic analysis. Only use for significant facts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string", "description": "The fact statement"},
                            "importance": {"type": "string", "enum": ["low", "medium", "high"], "description": "Importance level"},
                            "metadata": {"type": "object", "description": "Additional metadata (category, period, etc.)"}
                        },
                        "required": ["value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_prediction_node",
                    "description": "Create a prediction node based on analyzed facts. Use when facts suggest future outcomes.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string", "description": "The prediction statement"},
                            "confidence_level": {"type": "string", "enum": ["low", "medium", "high"], "description": "Confidence in this prediction"},
                            "timeframe": {"type": "string", "description": "When this prediction applies (e.g., '12 months', 'Q1 2024')"},
                            "metadata": {"type": "object", "description": "Additional metadata"}
                        },
                        "required": ["value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_missing_info_node",
                    "description": "Identify critical missing information needed for complete analysis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string", "description": "Description of missing information"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority of obtaining this info"},
                            "needed_for": {"type": "string", "description": "What analysis this info is needed for"},
                            "metadata": {"type": "object", "description": "Additional metadata"}
                        },
                        "required": ["value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_relation",
                    "description": "Create a relation between two nodes to show causality, support, contradiction, or dependency.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_node_id": {"type": "string", "description": "ID of source node"},
                            "target_node_id": {"type": "string", "description": "ID of target node"},
                            "relation_type": {
                                "type": "string", 
                                "enum": ["derived_from", "supports", "contradicts", "requires", "suggests"],
                                "description": "Type of relation"
                            },
                            "confidence": {"type": "number", "description": "Confidence 0-1", "minimum": 0, "maximum": 1},
                            "reasoning": {"type": "string", "description": "Why this relation exists"},
                            "metadata": {"type": "object", "description": "Additional metadata"}
                        },
                        "required": ["source_node_id", "target_node_id", "relation_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "finish_analysis",
                    "description": "Call when analysis is complete and all relevant nodes and relations have been created.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string", "description": "Brief summary of the analysis"}
                        },
                        "required": ["summary"]
                    }
                }
            }
        ]
