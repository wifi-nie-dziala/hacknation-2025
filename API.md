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
curl http://localhost:8080/api/jobs/YOUR-JOB-UUID
```

