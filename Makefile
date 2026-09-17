DOCKER = sudo docker compose

.PHONY: help setup start stop restart logs clean seed models

help:
	@echo "Macro Intelligence Dashboard"
	@echo "============================"
	@echo "make setup    - First-time setup"
	@echo "make start    - Start all services"
	@echo "make stop     - Stop all services"
	@echo "make restart  - Restart all services"
	@echo "make logs     - View logs"
	@echo "make clean    - Remove all data"
	@echo "make seed     - Seed initial data"
	@echo "make models   - Download AI models"
	@echo "make migrate  - Run database migrations"

setup:
	cp -n .env.example .env || true
	$(DOCKER) build
	$(DOCKER) up -d postgres redis
	sleep 5
	$(DOCKER) up -d
	@echo "Waiting for services to initialize..."
	sleep 10
	$(DOCKER) exec backend alembic upgrade head || echo "Migration skipped (DB may not be ready)"
	@echo "Setup complete! Visit http://localhost:3000"

start:
	$(DOCKER) up -d

stop:
	$(DOCKER) down

restart:
	$(DOCKER) restart

logs:
	$(DOCKER) logs -f

clean:
	$(DOCKER) down -v

seed:
	$(DOCKER) exec backend python -m scripts.seed_data

models:
	$(DOCKER) exec ollama ollama pull deepseek-r1:7b
	$(DOCKER) exec ollama ollama pull nomic-embed-text

migrate:
	$(DOCKER) exec backend alembic upgrade head