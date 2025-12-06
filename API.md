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

### 3. Get Job Details
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

# Get all results
curl http://localhost:8080/api/results

# Get specific job details (replace with actual UUID)
curl http://localhost:8080/api/jobs/YOUR-JOB-UUID
```

