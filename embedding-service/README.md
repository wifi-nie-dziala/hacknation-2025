# Embedding Service

Serwis do generowania embedingów z sentence-transformers.

## Model
- **paraphrase-multilingual-MiniLM-L12-v2**
- 384 wymiarów
- Multilingual (PL, EN + 50 innych języków)
- CPU-friendly (~120MB)
- Dobry na podobieństwo semantyczne

## API

### Health Check
```bash
GET http://localhost:5001/health
```

### Generate Embeddings
```bash
POST http://localhost:5001/embed
Content-Type: application/json

{
  "texts": ["tekst 1", "tekst 2", ...]
}
```

Response:
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "count": 2,
  "dimension": 384
}
```

## Test

```bash
# Build and run
docker-compose up -d embeddings

# Test
cd embedding-service
pip install requests numpy
python test_embeddings.py
```

## Standalone (bez dockera)

```bash
cd embedding-service
pip install -r requirements.txt
python app.py

# W innym terminalu
python test_embeddings.py
```

## Użycie w kodzie

```python
import requests

texts = ["AI zmienia świat", "Artificial intelligence"]
response = requests.post('http://localhost:5001/embed', json={'texts': texts})
embeddings = response.json()['embeddings']
```
