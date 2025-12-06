.PHONY: help build up down logs clean restart status health

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services (always rebuilds backend)
	docker-compose up -d --build backend
	docker-compose up -d

up-cpu: ## Start all services (CPU-only version, always rebuilds backend)
	docker-compose -f docker-compose.cpu.yml up -d --build backend
	docker-compose -f docker-compose.cpu.yml up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

logs-database: ## View database logs
	docker-compose logs -f database

logs-llm-en: ## View English LLM logs
	docker-compose logs -f llm-en

logs-llm-pl: ## View Polish LLM logs
	docker-compose logs -f llm-pl

clean: ## Stop services and remove volumes (⚠️  deletes all data)
	docker-compose down -v
	docker system prune -f

restart: ## Restart all services
	docker-compose restart

status: ## Show status of all services
	docker-compose ps

health: ## Check health of all services
	@echo "Checking backend health..."
	@curl -s http://localhost:8080/health || echo "Backend not responding"
	@echo ""
	@echo "Checking frontend..."
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend is up" || echo "Frontend not responding"
	@echo ""
	@echo "Checking database..."
	@docker-compose exec -T database pg_isready -U postgres || echo "Database not responding"

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/sh

shell-database: ## Open PostgreSQL shell
	docker-compose exec database psql -U postgres -d hacknation

rebuild: ## Rebuild and restart all services
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
