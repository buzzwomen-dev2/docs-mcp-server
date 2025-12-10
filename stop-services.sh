#!/bin/bash
# Stop Elasticsearch and Qdrant services

echo "🛑 Stopping services..."

# Check if docker-compose or docker compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Error: Neither 'docker-compose' nor 'docker compose' is available."
    exit 1
fi

# Stop services
$DOCKER_COMPOSE down

echo "✅ Services stopped"
echo ""
echo "Note: Data is preserved in Docker volumes."
echo "To remove data as well, run: $DOCKER_COMPOSE down -v"
