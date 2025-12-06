# API Documentation

## Endpoints

### 1. Submit Processing Job
**POST** `/api/submit`

Submit a job for processing with optional scraping and fact extraction.

**Request:**
```json
{
  "items": [
    {
      "type": "text|link",
      "content": "content or URL",
      "wage": 100.00
    }
  ],
  "processing": {
    "enable_scraping": true,
    "enable_fact_extraction": true,
    "language": "en"
  }
}
```

**Response:**
```json
{
  "job_uuid": "uuid-string"
}
```

### 2. Get All Jobs and Facts
**GET** `/api/results`

Retrieve all processing jobs and extracted facts.

**Response:**
```json
{
  "jobs": [
    {
      "job_uuid": "uuid",
      "status": "pending|processing|completed|failed",
      "created_at": "ISO timestamp",
      "completed_at": "ISO timestamp or null"
    }
  ],
  "facts": [
    {
      "id": 1,
      "fact": "extracted fact text",
      "language": "en",
      "created_at": "ISO timestamp"
    }
  ]
}
```

### 3. Get All Jobs with Full Associations
**GET** `/api/jobs`

Get all processing jobs with complete associated data including items, steps, scraped data, and extracted facts.

**Query Parameters:**
- `limit` (optional): Maximum number of jobs to return (default: 100)

**Response:**
```json
{
  "count": 4,
  "jobs": [
    {
      "job_uuid": "uuid",
      "status": "completed",
      "created_at": "ISO timestamp",
      "updated_at": "ISO timestamp",
      "completed_at": "ISO timestamp or null",
      "error_message": "error text or null",
      "total_items": 3,
      "completed_items": 3,
      "failed_items": 0,
      "items": [
        {
          "id": 1,
          "type": "text|link|file",
          "content": "...",
          "wage": 100.00,
          "status": "completed",
          "processed_content": "...",
          "error_message": null
        }
      ],
      "steps": [
        {
          "id": 1,
          "step_number": 1,
          "step_type": "scraping|extraction|validation|embedding",
          "status": "completed",
          "input_data": {},
          "output_data": {},
          "metadata": {},
          "created_at": "ISO timestamp",
          "completed_at": "ISO timestamp"
        }
      ],
      "scraped_data": [
        {
          "id": 1,
          "url": "https://example.com",
          "content": "scraped text",
          "content_type": "text/html",
          "status": "completed",
          "metadata": {},
          "created_at": "ISO timestamp"
        }
      ],
      "extracted_facts": [
        {
          "id": 1,
          "fact": "extracted fact text",
          "source_type": "llm_extraction",
          "source_content": "...",
          "confidence": 0.95,
          "is_validated": true,
          "language": "en",
          "metadata": {},
          "created_at": "ISO timestamp"
        }
      ]
    }
  ]
}
```

### 4. Get Job Details
**GET** `/api/jobs/{job_uuid}`

Get detailed information about a specific job including items, steps, and extracted facts.

**Response:**
```json
{
  "job": {
    "job_uuid": "uuid",
    "status": "completed",
    "created_at": "ISO timestamp",
    "items": [
      {
        "id": 1,
        "type": "text",
        "content": "...",
        "status": "completed"
      }
    ]
  },
  "steps": [
    {
      "step_number": 1,
      "step_type": "scraping|extraction|validation",
      "status": "completed",
      "created_at": "ISO timestamp"
    }
  ],
  "facts": [
    {
      "id": 1,
      "fact": "extracted fact",
      "confidence": 0.95,
      "language": "en"
    }
  ]
}
```

## Quick Start

```bash
# Start services
make start

# Submit a job
curl -X POST http://localhost:8080/api/submit \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"type": "text", "content": "AI is cool", "wage": 50}],
    "processing": {"enable_fact_extraction": true, "language": "en"}
  }'

# Get all results (legacy)
curl http://localhost:8080/api/results

# Get all jobs with full associations
curl http://localhost:8080/api/jobs

# Get all jobs with limit
curl http://localhost:8080/api/jobs?limit=10

# Get specific job details (replace with actual UUID)
curl http://localhost:8080/api/jobs/{job_uuid}
```

---

## Node System API

### 5. Create Node
**POST** `/api/nodes`

Create a new knowledge graph node.

**Request:**
```json
{
  "type": "fact|prediction|missing_information",
  "value": "node text value",
  "job_uuid": "optional-job-uuid",
  "metadata": {
    "category": "financial",
    "source": "analysis"
  }
}
```

**Response:**
```json
{
  "node": {
    "id": 1,
    "type": "fact",
    "value": "Q4 revenue was $5.2M",
    "job_id": 123,
    "metadata": {"category": "financial"},
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp"
  }
}
```

### 6. Get Node
**GET** `/api/nodes/{node_id}`

Get a specific node by ID.

**Response:**
```json
{
  "node": {
    "id": 1,
    "type": "fact",
    "value": "Q4 revenue was $5.2M",
    "job_id": 123,
    "metadata": {},
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp"
  }
}
```

### 7. Get Nodes by Job
**GET** `/api/jobs/{job_uuid}/nodes?type={type}`

Get all nodes associated with a job.

**Query Parameters:**
- `type` (optional): Filter by node type (`fact`, `prediction`, `missing_information`)

**Response:**
```json
{
  "nodes": [
    {
      "id": 1,
      "type": "fact",
      "value": "Revenue increased 15%",
      "job_id": 123,
      "metadata": {},
      "created_at": "ISO timestamp"
    }
  ],
  "count": 1
}
```

### 8. Create Node Relation
**POST** `/api/node-relations`

Create a relationship between two nodes.

**Request:**
```json
{
  "source_node_id": 1,
  "target_node_id": 2,
  "relation_type": "derived_from|supports|contradicts|requires|suggests",
  "confidence": 0.95,
  "metadata": {
    "reasoning": "Based on Q4 financial data"
  }
}
```

**Relation Types:**
- `derived_from`: Target was derived from source
- `supports`: Target supports source
- `contradicts`: Target contradicts source  
- `requires`: Target requires source
- `suggests`: Target suggests source

**Response:**
```json
{
  "relation_id": 1
}
```

### 9. Get Node Relations
**GET** `/api/nodes/{node_id}/relations?direction={direction}`

Get all relations for a specific node.

**Query Parameters:**
- `direction` (optional): `incoming`, `outgoing`, or `both` (default: `both`)

**Response:**
```json
{
  "relations": [
    {
      "id": 1,
      "source_node_id": 1,
      "target_node_id": 2,
      "relation_type": "supports",
      "confidence": 0.95,
      "metadata": {},
      "created_at": "ISO timestamp",
      "related_node_type": "prediction",
      "related_node_value": "Q1 will exceed $6M"
    }
  ],
  "count": 1
}
```

## Node System Examples

```bash
# Create a fact node
curl -X POST http://localhost:8080/api/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fact",
    "value": "Q4 revenue was $5.2M",
    "job_uuid": "11111111-1111-1111-1111-111111111111"
  }'

# Create a prediction node
curl -X POST http://localhost:8080/api/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "type": "prediction", 
    "value": "Q1 revenue will likely exceed $6M"
  }'

# Link nodes with a relation
curl -X POST http://localhost:8080/api/node-relations \
  -H "Content-Type: application/json" \
  -d '{
    "source_node_id": 1,
    "target_node_id": 2,
    "relation_type": "supports",
    "confidence": 0.85
  }'

# Get all nodes for a job
curl http://localhost:8080/api/jobs/{job_uuid}/nodes

# Get only fact nodes
curl http://localhost:8080/api/jobs/{job_uuid}/nodes?type=fact

# Get all relations for a node
curl http://localhost:8080/api/nodes/1/relations

# Get only outgoing relations
curl http://localhost:8080/api/nodes/1/relations?direction=outgoing
curl http://localhost:8080/api/jobs/YOUR-JOB-UUID
```

