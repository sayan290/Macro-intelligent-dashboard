#!/bin/bash
echo "Initializing database..."
docker compose exec backend alembic upgrade head
echo "Database initialized."
