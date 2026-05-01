.PHONY: help build up down logs clean backend frontend test

# Detect Docker Compose command (v1 or v2)
COMPOSE_CMD := $(shell command -v docker-compose 2> /dev/null)
ifndef COMPOSE_CMD
	COMPOSE_CMD := docker compose
endif

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker containers
	$(COMPOSE_CMD) build

up: ## Start all services
	$(COMPOSE_CMD) up -d

down: ## Stop all services
	$(COMPOSE_CMD) down

logs: ## View logs from all services
	$(COMPOSE_CMD) logs -f

logs-backend: ## View backend logs
	$(COMPOSE_CMD) logs -f backend

logs-frontend: ## View frontend logs
	$(COMPOSE_CMD) logs -f frontend

restart: ## Restart all services
	$(COMPOSE_CMD) restart

clean: ## Remove all containers, volumes, and images
	$(COMPOSE_CMD) down -v --rmi local

ps: ## Show running containers
	$(COMPOSE_CMD) ps

backend: ## Run backend locally
	cd backend && uvicorn app.main:app --reload --port 8000

frontend: ## Run frontend locally
	cd frontend && npm run dev

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

refresh: ## Trigger cache refresh
	curl -X POST http://localhost:8000/api/refresh

health: ## Check API health
	curl http://localhost:8000/api/health

test-backend: ## Run backend tests
	cd backend && pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test

setup: ## Initial setup (install dependencies)
	@echo "Installing backend dependencies..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Setup complete! Don't forget to set VITE_MAPBOX_TOKEN in frontend/.env"

