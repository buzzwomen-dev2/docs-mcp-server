#!/bin/bash
# Start Elasticsearch and Qdrant services using Docker Compose

echo "🚀 Starting Elasticsearch and Qdrant services..."
echo ""

# Check if docker-compose or docker compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Error: Neither 'docker-compose' nor 'docker compose' is available."
    echo "   Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Start services
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

# Wait for Elasticsearch
echo -n "Elasticsearch: "
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        echo "✅ Ready"
        break
    fi
    echo -n "."
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Timeout"
    echo "Check logs with: $DOCKER_COMPOSE logs elasticsearch"
    exit 1
fi

# Wait for Qdrant
echo -n "Qdrant:        "
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "✅ Ready"
        break
    fi
    echo -n "."
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Timeout"
    echo "Check logs with: $DOCKER_COMPOSE logs qdrant"
    exit 1
fi

echo ""
echo "✅ All services are ready!"
echo ""
echo "Service URLs:"
echo "  • Elasticsearch: http://localhost:9200"
echo "  • Qdrant:        http://localhost:6333"
echo "  • Qdrant UI:     http://localhost:6333/dashboard"
echo ""
echo "To view logs:    $DOCKER_COMPOSE logs -f"
echo "To stop:         $DOCKER_COMPOSE down"
echo "To stop & clean: $DOCKER_COMPOSE down -v"
echo ""
