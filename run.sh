#!/bin/bash

echo "Building and starting SDS Chemical Inventory System..."
echo "==========================================="

docker compose down -v 2>/dev/null || docker-compose down -v 2>/dev/null || true

echo "Building Docker images..."
docker compose build || docker-compose build

echo "Starting services..."
docker compose up -d || docker-compose up -d

echo "Waiting for API to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo ""
        echo "==========================================="
        echo "✅ API is ready and available at http://localhost:8000"
        echo "📚 API Documentation: http://localhost:8000/docs"
        echo "==========================================="
        echo ""
        echo "To view logs: docker compose logs -f"
        echo "To stop services: docker compose down"
        exit 0
    fi
    
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

echo ""
echo "❌ API failed to start. Check logs with: docker compose logs"
exit 1