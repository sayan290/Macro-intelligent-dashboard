#!/bin/bash
set -e

echo "🧠 Macro Intelligence Dashboard Setup"
echo "======================================"

# Copy env file
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ Created .env from .env.example"
fi

# Build and start
echo "🐳 Building containers..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo "⏳ Waiting for database..."
sleep 10

echo "📊 Running migrations..."
docker compose exec -T backend alembic upgrade head

echo "🤖 Downloading AI models..."
docker compose exec -T ollama ollama pull deepseek-r1:7b || echo "⚠️ AI model download skipped"
docker compose exec -T ollama ollama pull nomic-embed-text || echo "⚠️ Embedding model download skipped"

echo ""
echo "✅ Setup complete!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API Docs:  http://localhost:8080/docs"
echo "📖 Read README.md for more info"
