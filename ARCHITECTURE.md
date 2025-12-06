# Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HackNation 2025 Architecture                  │
└─────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │   Browser    │
                              └──────┬───────┘
                                     │ HTTP
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
          ┌─────────────────┐              ┌─────────────────┐
          │   Frontend      │              │   Backend       │
          │   (React +      │              │   (Flask +      │
          │    Nginx)       │◄────────────►│   Gunicorn)     │
          │   Port: 3000    │   REST API   │   Port: 5000    │
          └─────────────────┘              └────────┬────────┘
                                                    │
                                                    │
                    ┌───────────────────────────────┼─────────────┐
                    │                               │             │
                    ▼                               ▼             ▼
          ┌─────────────────┐           ┌──────────────┐  ┌──────────────┐
          │   PostgreSQL +  │           │   Ollama     │  │   Ollama     │
          │    pgvector     │           │   (English)  │  │   (Polish)   │
          │   Port: 5432    │           │   Port:11434 │  │  Port: 11435 │
          └─────────────────┘           └──────────────┘  └──────────────┘
                    │
                    │
                    ▼
          ┌─────────────────┐
          │  Vector Storage │
          │  (Embeddings)   │
          └─────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                     Docker Network: hacknation-network               │
│  All containers communicate through this shared bridge network       │
└─────────────────────────────────────────────────────────────────────┘

Data Flow:
1. User interacts with React frontend (port 3000)
2. Frontend calls Flask backend API (port 5000)
3. Backend:
   - Stores/retrieves facts from PostgreSQL with pgvector
   - Sends English text to LLM-EN for fact extraction
   - Sends Polish text to LLM-PL for fact extraction
   - Uses vector similarity search for finding related facts
4. Results are returned to frontend and displayed to user

Persistent Volumes:
- hacknation-postgres-data: Database storage
- hacknation-ollama-en-data: English LLM model storage
- hacknation-ollama-pl-data: Polish LLM model storage
