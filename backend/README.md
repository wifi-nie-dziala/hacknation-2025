# Backend Service

## Quick Start

```bash
# Start all services (recommended)
docker-compose up -d

# Or use the main start script
./start.sh
```

This will:
1. Start database, backend, frontend, and embeddings services
2. Initialize database with sample data
3. Backend available at http://localhost:8080
4. Health check: http://localhost:8080/health

## Sample Data

The database is automatically initialized with dummy jobs:
- Job `11111111-1111-1111-1111-111111111111` (pending)
- Job `22222222-2222-2222-2222-222222222222` (processing) - with steps and facts
- Job `33333333-3333-3333-3333-333333333333` (completed) - with full data
- Job `44444444-4444-4444-4444-444444444444` (failed)

## Development

### View Logs
```bash
docker logs hacknation-backend -f
```

### Restart Backend Only
```bash
docker-compose restart backend
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build backend
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/submit` - Submit processing job
- `GET /api/jobs` - Get all jobs with full data
- `GET /api/jobs/<uuid>` - Get specific job details

See [API.md](../API.md) for full documentation.

