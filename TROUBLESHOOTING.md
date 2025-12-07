# Troubleshooting Guide

This guide helps you resolve common issues when running HackNation 2025.

## Table of Contents
- [Services Won't Start](#services-wont-start)
- [Port Conflicts](#port-conflicts)
- [LLM Issues](#llm-issues)
- [Database Connection Issues](#database-connection-issues)
- [Frontend/Backend Communication Issues](#frontendbackend-communication-issues)
- [Performance Issues](#performance-issues)
- [Docker Issues](#docker-issues)

---

## Services Won't Start

### Symptom
Running `docker-compose up` fails or containers keep restarting.

### Solutions

1. **Check Docker daemon is running:**
   ```bash
   docker ps
   ```
   If this fails, start Docker Desktop or the Docker daemon.

2. **Check logs for specific service:**
   ```bash
   docker-compose logs [service-name]
   # Example: docker-compose logs backend
   ```

3. **Verify all images can be pulled:**
   ```bash
   docker-compose pull
   ```

4. **Check system resources:**
   - Ensure you have at least 8GB of free RAM
   - Ensure you have at least 20GB of free disk space
   ```bash
   docker system df
   ```

5. **Clean and restart:**
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up -d
   ```

---

## Port Conflicts

### Symptom
Error message like: `Bind for 0.0.0.0:3000 failed: port is already allocated`

### Solutions

1. **Check which process is using the port:**
   ```bash
   # Linux/Mac
   lsof -i :3000
   # Windows
   netstat -ano | findstr :3000
   ```

2. **Stop the conflicting process or change ports in docker-compose.yml:**
   ```yaml
   services:
     frontend:
       ports:
         - "3001:80"  # Changed from 3000 to 3001
   ```

3. **Common port mappings to modify:**
   - Frontend: `3000:80` → `YOUR_PORT:80`
   - Backend: `5000:5000` → `YOUR_PORT:5000`
   - Database: `5432:5432` → `YOUR_PORT:5432`
   - LLM-EN: `11434:11434` → `YOUR_PORT:11434`
   - LLM-PL: `11435:11434` → `YOUR_PORT:11434`

---

## LLM Issues

### Symptom 1: LLM requests timeout or take extremely long

**Solutions:**

1. **First request is always slow** (model loading):
   - Initial request can take 30-60 seconds
   - Subsequent requests are faster
   - This is normal behavior

2. **Increase timeout if needed:**
   - Adjust timeout in backend/app.py if needed
   - Consider using smaller/faster models

3. **Check service logs:**
   ```bash
   docker-compose logs -f backend
   ```

### Symptom 2: LLM models not downloading

**Solutions:**

1. **Check internet connection:**
   ```bash
   docker-compose exec llm-en curl -I https://ollama.ai
   ```

2. **Manually pull models:**
   ```bash
   docker-compose exec llm-en ollama pull llama2
   docker-compose exec llm-pl ollama pull llama2
   ```

3. **Check available disk space:**
   ```bash
   docker system df
   ```

### Symptom 3: Out of memory errors

**Solutions:**

1. **Increase Docker memory limit:**
   - Docker Desktop: Settings → Resources → Memory → Increase to 8GB+

2. **Run only one LLM at a time:**
   - Comment out one LLM service in docker-compose.yml
   - Modify backend to use only one model

---

## Database Connection Issues

### Symptom
Backend logs show database connection errors.

**Solutions:**

1. **Wait for database to be ready:**
   ```bash
   docker-compose exec database pg_isready -U postgres
   ```

2. **Check database logs:**
   ```bash
   docker-compose logs database
   ```
   Look for: "database system is ready to accept connections"

3. **Verify pgvector extension:**
   ```bash
   docker-compose exec database psql -U postgres -d hacknation -c "SELECT * FROM pg_extension WHERE extname='vector';"
   ```

4. **Recreate database:**
   ```bash
   docker-compose down
   docker volume rm hacknation-postgres-data
   docker-compose up database
   ```

5. **Check network connectivity:**
   ```bash
   docker-compose exec backend ping database
   ```

---

## Frontend/Backend Communication Issues

### Symptom
Frontend cannot reach backend API.

**Solutions:**

1. **Verify backend is healthy:**
   ```bash
   curl http://localhost:5000/health
   ```
   Should return: `{"status": "healthy", "service": "backend"}`

2. **Check CORS settings:**
   - Backend has CORS enabled in `backend/app.py`
   - Verify `CORS(app)` is present

3. **Check API URL in frontend:**
   - Ensure `VITE_API_URL` in `.env` points to correct backend
   - Default: `http://localhost:5000`

4. **Check browser console:**
   - Open browser DevTools (F12)
   - Look for CORS or network errors

5. **Verify network:**
   ```bash
   docker network inspect hacknation-network
   ```
   All services should be listed.

---

## Performance Issues

### Symptom
Application is slow or unresponsive.

**Solutions:**

1. **Check resource usage:**
   ```bash
   docker stats
   ```

2. **Limit resource usage per container:**
   Add to docker-compose.yml:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

3. **Use GPU acceleration:**
   - Switch to GPU compose file
   - Ensure NVIDIA drivers installed

4. **Optimize PostgreSQL:**
   - Increase shared_buffers
   - Tune work_mem
   - Add indexes to frequently queried columns

---

## Docker Issues

### Symptom 1: Docker daemon not responding

**Solutions:**

1. **Restart Docker:**
   - Docker Desktop: Quit and restart
   - Linux: `sudo systemctl restart docker`

2. **Check Docker status:**
   ```bash
   docker info
   ```

### Symptom 2: Disk space issues

**Solutions:**

1. **Clean up Docker:**
   ```bash
   docker system prune -a --volumes
   ```
   ⚠️ WARNING: This removes all unused containers, networks, images, and volumes!

2. **Remove specific volumes:**
   ```bash
   docker volume ls
   docker volume rm VOLUME_NAME
   ```

### Symptom 3: Network issues

**Solutions:**

1. **Recreate network:**
   ```bash
   docker-compose down
   docker network rm hacknation-network
   docker-compose up
   ```

2. **Check network exists:**
   ```bash
   docker network ls | grep hacknation
   ```

---

## Still Having Issues?

If none of these solutions work:

1. **Collect diagnostic information:**
   ```bash
   docker-compose ps > status.txt
   docker-compose logs > logs.txt
   docker system info > docker-info.txt
   ```

2. **Create an issue on GitHub** with:
   - Description of the problem
   - Steps to reproduce
   - Error messages
   - Docker version: `docker --version`
   - OS information
   - Diagnostic files

3. **Check existing issues:**
   - Search GitHub issues for similar problems
   - Check if there's already a solution

---

## Useful Commands Reference

```bash
# View all services status
docker-compose ps

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Rebuild a service
docker-compose up -d --build backend

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Check resource usage
docker stats

# Check disk usage
docker system df

# Access a container shell
docker-compose exec backend /bin/sh

# Access database shell
docker-compose exec database psql -U postgres -d hacknation

# Check health of a service
docker inspect hacknation-backend | grep -A 10 Health
```

---

Need more help? Check the [README](README.md) or create an issue on GitHub.
