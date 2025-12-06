# Quick Start Guide

This guide will help you get the HackNation 2025 application running in just a few minutes.

## Prerequisites Check

Before starting, make sure you have:

- [ ] Docker installed (20.10+)
- [ ] Docker Compose installed (2.0+)
- [ ] At least 8GB free RAM
- [ ] At least 20GB free disk space
- [ ] Internet connection (for downloading images and models)

## Option 1: Using the Start Script (Easiest)

1. Open a terminal in the project directory
2. Run the start script:
   ```bash
   ./start.sh
   ```
3. Follow the prompts to choose GPU or CPU mode
4. Wait for services to start (5-10 minutes first time)
5. The application will open in your browser automatically

## Option 2: Using Docker Compose (Manual)

### For GPU systems:
```bash
docker-compose up -d
```

### For CPU-only systems:
```bash
docker-compose -f docker-compose.cpu.yml up -d
```

### Monitor startup progress:
```bash
docker-compose logs -f
```

Wait until you see messages indicating all services are ready.

## Option 3: Using Make (For developers)

```bash
# View all available commands
make help

# Start services (GPU)
make up

# Start services (CPU)
make up-cpu

# View logs
make logs

# Check status
make status
```

## Accessing the Application

Once all services are running:

1. **Frontend (UI)**: Open http://localhost:3000 in your browser
2. **Backend API**: http://localhost:5000/health should return `{"status": "healthy"}`

## First Use

1. Open the frontend at http://localhost:3000
2. Click "Check Backend Health" to verify the backend is running
3. Enter some text in English or Polish
4. Select the language
5. Click "Extract Facts"
6. Wait for the AI to process (may take 30-60 seconds on first request)
7. Review the extracted facts
8. Optionally save them to the database

## Troubleshooting

### Services not starting?
```bash
# Check what's running
docker-compose ps

# Check logs for errors
docker-compose logs
```

### LLM models taking too long?
- First request loads the model into memory (30-60 seconds)
- Subsequent requests are faster
- CPU mode is slower than GPU mode

### Port conflicts?
Edit `docker-compose.yml` and change the port mappings:
```yaml
ports:
  - "NEW_PORT:CONTAINER_PORT"
```

### Need to reset everything?
```bash
# Stop and remove everything
docker-compose down -v

# Remove all Docker data (⚠️ WARNING: removes all Docker data)
docker system prune -a -f
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check the [API documentation](README.md#-api-endpoints) for backend endpoints
- Explore the code in `frontend/`, `backend/`, and `database/` directories

## Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker ps`
3. Ensure ports are not in use: `netstat -tulpn | grep -E '3000|5000|5432|11434|11435'`
4. Create an issue on GitHub with error details

---

Happy hacking! 🚀
