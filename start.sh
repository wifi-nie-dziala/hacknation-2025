#!/bin/bash

# HackNation 2025 - Startup Script
# This script helps you get started with the application

set -e

echo "==================================="
echo "HackNation 2025 - Fact Extractor"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed."
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Ask user which version to use
echo "Which version would you like to run?"
echo "1) GPU-accelerated (requires NVIDIA GPU and nvidia-docker)"
echo "2) CPU-only (works on all systems, but slower)"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Starting with GPU acceleration..."
        COMPOSE_FILE="docker-compose.yml"
        ;;
    2)
        echo ""
        echo "Starting with CPU-only mode..."
        COMPOSE_FILE="docker-compose.cpu.yml"
        ;;
    *)
        echo "Invalid choice. Defaulting to CPU-only mode..."
        COMPOSE_FILE="docker-compose.cpu.yml"
        ;;
esac

# Start services
echo ""
echo "Starting all services..."
echo "This may take several minutes on first run (downloading models)..."
echo ""

if [ "$COMPOSE_FILE" = "docker-compose.yml" ]; then
    docker-compose up -d --build backend
    docker-compose up -d
else
    docker-compose -f docker-compose.cpu.yml up -d --build backend
    docker-compose -f docker-compose.cpu.yml up -d
fi

echo ""
echo "Waiting for services to start..."
sleep 5

# Show status
echo ""
echo "==================================="
echo "Service Status:"
echo "==================================="
if [ "$COMPOSE_FILE" = "docker-compose.yml" ]; then
    docker-compose ps
else
    docker-compose -f docker-compose.cpu.yml ps
fi

echo ""
echo "==================================="
echo "Application URLs:"
echo "==================================="
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8080"
echo "Database:  localhost:5432"
echo "LLM (EN):  http://localhost:11434"
echo "LLM (PL):  http://localhost:11435"
echo ""

echo "==================================="
echo "Useful Commands:"
echo "==================================="
echo "View logs:           docker-compose logs -f"
echo "Stop services:       docker-compose down"
echo "Restart services:    docker-compose restart"
echo ""

echo "✅ Setup complete! Opening browser..."
echo ""

# Try to open browser (works on most systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 &> /dev/null || true
elif command -v open &> /dev/null; then
    open http://localhost:3000 &> /dev/null || true
fi

echo "If your browser didn't open automatically, visit:"
echo "http://localhost:3000"
