# HackNation 2025 - AI Fact Extractor Monorepo

A full-stack application for extracting facts from text using AI models, supporting both English and Polish languages. The application uses React.js for the frontend, Flask for the backend, PostgreSQL with pgvector for vector storage, and Ollama LLM models for fact extraction.

## 🏗️ Architecture

This is a monorepo containing:

- **Frontend**: React.js application with Vite
- **Backend**: Flask (Python) REST API
- **Database**: PostgreSQL with pgvector extension for vector storage
- **LLM Models**: Two Ollama instances (one for English, one for Polish)

All services are containerized with Docker and communicate through a shared Docker network.

## 📋 Prerequisites

Before running this project, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git**
- At least **8GB of free RAM** (LLM models are memory-intensive)
- At least **20GB of free disk space** (for Docker images and LLM models)

### Optional (for better performance):
- NVIDIA GPU with CUDA support (for GPU acceleration)
- NVIDIA Container Toolkit installed

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/wifi-nie-dziala/hacknation-2025.git
cd hacknation-2025
```

### 2. Choose Your Docker Compose File

**For systems with NVIDIA GPU:**
```bash
docker-compose up -d
```

**For CPU-only systems:**
```bash
docker-compose -f docker-compose.cpu.yml up -d
```

### 3. Wait for Services to Initialize

The first startup will take several minutes as Docker needs to:
- Pull all container images
- Download LLM models (llama2, ~4GB each)
- Initialize the database
- Build the frontend and backend

You can monitor the progress:
```bash
docker-compose logs -f
```

### 4. Access the Application

Once all services are running:

- **Frontend (React)**: http://localhost:3000
- **Backend (Flask API)**: http://localhost:5000
- **Database (PostgreSQL)**: localhost:5432
- **LLM English**: http://localhost:11434
- **LLM Polish**: http://localhost:11435

## 📁 Project Structure

```
hacknation-2025/
├── frontend/               # React.js frontend
│   ├── src/
│   │   ├── App.jsx        # Main application component
│   │   ├── App.css        # Application styles
│   │   └── ...
│   ├── Dockerfile         # Frontend Docker configuration
│   ├── nginx.conf         # Nginx configuration for production
│   └── package.json       # Node.js dependencies
│
├── backend/               # Flask backend
│   ├── app.py            # Main Flask application
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Backend Docker configuration
│
├── database/             # Database configuration
│   └── init.sql         # Database initialization script
│
├── docker-compose.yml           # Main Docker Compose (with GPU support)
├── docker-compose.cpu.yml       # CPU-only Docker Compose
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

#### Backend (Flask)
The backend uses the following environment variables (set in docker-compose.yml):

- `DB_HOST`: Database hostname (default: `database`)
- `DB_PORT`: Database port (default: `5432`)
- `DB_NAME`: Database name (default: `hacknation`)
- `DB_USER`: Database user (default: `postgres`)
- `DB_PASSWORD`: Database password (default: `postgres`)
- `LLM_EN_HOST`: English LLM hostname (default: `llm-en`)
- `LLM_EN_PORT`: English LLM port (default: `11434`)
- `LLM_PL_HOST`: Polish LLM hostname (default: `llm-pl`)
- `LLM_PL_PORT`: Polish LLM port (default: `11434`)

#### Frontend (React)
- `VITE_API_URL`: Backend API URL (default: `http://localhost:5000`)

To customize, create a `.env` file in the frontend directory based on `.env.example`.

## 🛠️ Development

### Running Individual Services

#### Frontend (Local Development)
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at http://localhost:5173

#### Backend (Local Development)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
The backend will be available at http://localhost:5000

#### Database Only
```bash
docker-compose up database
```

### Stopping Services

Stop all services:
```bash
docker-compose down
```

Stop and remove volumes (⚠️ This will delete all data):
```bash
docker-compose down -v
```

## 📊 API Endpoints

### Backend API

- **GET /health** - Health check
  ```bash
  curl http://localhost:5000/health
  ```

- **POST /api/extract-facts-en** - Extract facts from English text
  ```bash
  curl -X POST http://localhost:5000/api/extract-facts-en \
    -H "Content-Type: application/json" \
    -d '{"text": "Your English text here"}'
  ```

- **POST /api/extract-facts-pl** - Extract facts from Polish text
  ```bash
  curl -X POST http://localhost:5000/api/extract-facts-pl \
    -H "Content-Type: application/json" \
    -d '{"text": "Twój polski tekst tutaj"}'
  ```

- **GET /api/facts** - Get all stored facts
  ```bash
  curl http://localhost:5000/api/facts
  ```

- **POST /api/facts** - Store a fact
  ```bash
  curl -X POST http://localhost:5000/api/facts \
    -H "Content-Type: application/json" \
    -d '{"fact": "Your fact", "language": "en"}'
  ```

- **POST /api/search** - Search for similar facts using vector similarity
  ```bash
  curl -X POST http://localhost:5000/api/search \
    -H "Content-Type: application/json" \
    -d '{"embedding": [0.1, 0.2, ...], "limit": 10}'
  ```

## 🐳 Docker Network

All services communicate through the `hacknation-network` Docker bridge network. This allows:

- Backend to connect to Database using hostname `database`
- Backend to connect to LLMs using hostnames `llm-en` and `llm-pl`
- Frontend to connect to Backend (via host machine port mapping)

## 💾 Data Persistence

The following Docker volumes are used for data persistence:

- `hacknation-postgres-data` - PostgreSQL database data
- `hacknation-ollama-en-data` - English LLM model data
- `hacknation-ollama-pl-data` - Polish LLM model data

Data persists between container restarts unless you explicitly remove volumes with `docker-compose down -v`.

## 🧪 Testing the Setup

1. **Check all services are running:**
   ```bash
   docker-compose ps
   ```
   All services should show status "Up" or "Up (healthy)"

2. **Test the backend health:**
   ```bash
   curl http://localhost:5000/health
   ```
   Should return: `{"status": "healthy", "service": "backend"}`

3. **Test the frontend:**
   Open http://localhost:3000 in your browser

4. **Test fact extraction:**
   - Enter some text in the frontend
   - Select language (English or Polish)
   - Click "Extract Facts"
   - The AI should process and extract facts

## ⚠️ Troubleshooting

### LLM models are slow or timing out
- LLM models require significant resources
- First request may take 30-60 seconds while the model loads
- For CPU-only systems, responses can take 1-2 minutes
- Consider using a GPU for better performance

### Database connection errors
```bash
docker-compose logs database
```
Wait for the message: "database system is ready to accept connections"

### Port already in use
If ports 3000, 5000, 5432, 11434, or 11435 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "NEW_PORT:CONTAINER_PORT"
```

### Out of memory errors
- Ensure you have at least 8GB of free RAM
- Reduce the number of running services
- Consider closing other applications

### Checking logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
docker-compose logs -f llm-en
docker-compose logs -f llm-pl
```

## 🔄 Updating

To update the application:

```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🧹 Cleanup

Remove all containers, networks, and volumes:

```bash
docker-compose down -v
docker system prune -a
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please create an issue on the GitHub repository.

---

Built with ❤️ for HackNation 2025