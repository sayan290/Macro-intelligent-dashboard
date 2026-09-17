#!/bin/bash
echo "Downloading AI models..."
docker compose exec ollama ollama pull deepseek-r1:7b
docker compose exec ollama ollama pull nomic-embed-text
echo "Models downloaded."
