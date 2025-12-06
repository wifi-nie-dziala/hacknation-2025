# Running Backend Locally

## Quick Start

```bash
docker-compose up -d database
cd backend
./run_local.sh
```

This will:
1. Start database in Docker
2. Install all Python dependencies
3. Set up the database (create tables + add dummy data)
4. Start Flask on http://localhost:8080

This creates:
- `processing_jobs` and `processing_items` tables
- Dummy data for FE development:
  - Job `11111111-1111-1111-1111-111111111111` (pending)
  - Job `22222222-2222-2222-2222-222222222222` (processing)
  - Job `33333333-3333-3333-3333-333333333333` (completed)
  - Job `44444444-4444-4444-4444-444444444444` (failed)

