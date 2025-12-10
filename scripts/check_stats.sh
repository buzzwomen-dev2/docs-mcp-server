#!/bin/bash
# Quick stats checker for the index

echo "📊 Index Statistics"
echo "===================="

# Elasticsearch
ES_COUNT=$(curl -s http://localhost:9200/docs_index/_count | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
echo "Elasticsearch: $ES_COUNT documents"

# Qdrant
QDRANT_COUNT=$(curl -s http://localhost:6333/collections/docs_collection | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['points_count'])")
echo "Qdrant:        $QDRANT_COUNT vectors"

# Metadata cache
if [ -f .index/chunks_metadata.pkl ]; then
    CACHE_SIZE=$(python3 -c "import pickle; data=pickle.load(open('.index/chunks_metadata.pkl','rb')); print(len(data))")
    echo "Metadata:      $CACHE_SIZE chunks"
fi

echo ""
echo "Status: Indexing in progress..." 
