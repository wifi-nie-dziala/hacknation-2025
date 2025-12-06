# LLM-Based Multi-Step Reasoning Pipeline

System z LLM (Ollama) który pracuje w krokach z tool calling do budowania grafu wiedzy.

## Flow

1. **Input** → Text/PDF/URL konwertowane do markdown
2. **Fact Extraction** → LLM wyłuskuje fakty
3. **Reasoning** → LLM z tool calling analizuje fakty i buduje graf:
   - Tworzy węzły: `fact`, `prediction`, `missing_information`
   - Buduje relacje: `derived_from`, `supports`, `contradicts`, `requires`, `suggests`
   - Ignoruje nieistotne fakty
   - Sam decyduje kiedy skończyć (`finish_analysis`)
4. **Scenarios** → Generuje 4 scenariusze (12m/36m × positive/negative) z concept maps

## Services

### ReasoningService
- `analyze_facts_for_job(job_uuid)` - Multi-step LLM reasoning z tool calling
- Tools:
  - `create_fact_node` - tylko istotne fakty
  - `create_prediction_node` - predykcje z faktów
  - `create_missing_info_node` - braki w danych
  - `create_relation` - relacje między węzłami
  - `finish_analysis` - kończy analizę

### ScenarioService
- `generate_scenarios(job_uuid)` - 4 scenariusze strategiczne
- Każdy scenariusz:
  - description
  - concept_map (nodes + edges z causality)

## API

```bash
# Submit z full pipeline
POST /api/submit
{
  "items": [...],
  "processing": {
    "enable_fact_extraction": true,
    "enable_reasoning": true,
    "enable_scenarios": true
  }
}

# Get scenarios
GET /api/jobs/{uuid}/scenarios

# Get nodes (facts/predictions/missing_info)
GET /api/jobs/{uuid}/nodes?type=prediction

# Get relations
GET /api/nodes/{node_id}/relations?direction=outgoing
```

## Database

- `processing_jobs.results` - JSONB z scenarios + summary
- `nodes` - fact/prediction/missing_information
- `node_relations` - grafy powiązań z confidence

## Config

Używa Ollama z `config.py`:
- `OLLAMA_HOST`
- `OLLAMA_PORT`
- `OLLAMA_MODEL`
