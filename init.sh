#!/bin/bash

# Expense Tracker Application - Setup Script
# This script sets up the development environment and starts all services

set -e

echo "======================================"
echo "Expense Tracker - Environment Setup"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker to proceed."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose to proceed."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check if in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "Services are now running:"
echo "  - Frontend (React):  http://localhost:3000"
echo "  - Backend (FastAPI): http://localhost:8000"
echo "  - API Docs:          http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Rebuild:      docker-compose build --no-cache"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Register a new account"
echo "  3. Start tracking your expenses!"
echo ""
