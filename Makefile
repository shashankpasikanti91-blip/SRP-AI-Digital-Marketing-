.PHONY: help dev build up down logs migrate seed test lint format clean worker beat flower

# ── Colours ────────────────────────────────────────────────────────────────────
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RESET  := \033[0m

help: ## Show this help
	@echo ""
	@echo "$(CYAN)SRP Marketing OS$(RESET) — Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ── Setup ──────────────────────────────────────────────────────────────────────
setup: ## First-time setup: copy .env.example and install dependencies
	@[ -f .env ] || (cp .env.example .env && echo "$(YELLOW)⚠  .env created — please fill in your API keys$(RESET)")
	@echo "$(GREEN)✓  Setup complete$(RESET)"

# ── Development ────────────────────────────────────────────────────────────────
dev: ## Start all services in dev mode (hot-reload)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-bg: ## Start all services in dev mode (background)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-backend: ## Start only backend + DB + Redis (no frontend)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up db redis backend celery-worker

# ── Production ─────────────────────────────────────────────────────────────────
build: ## Build all Docker images
	docker compose build

up: ## Start all production services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Tail logs for all services
	docker compose logs -f

logs-backend: ## Tail backend logs only
	docker compose logs -f backend

logs-worker: ## Tail Celery worker logs only
	docker compose logs -f celery-worker

# ── Database ───────────────────────────────────────────────────────────────────
migrate: ## Run Alembic migrations (upgrade head)
	docker compose run --rm backend alembic upgrade head

migrate-down: ## Rollback last migration
	docker compose run --rm backend alembic downgrade -1

migrate-history: ## Show migration history
	docker compose run --rm backend alembic history --verbose

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add column foo")
	docker compose run --rm backend alembic revision --autogenerate -m "$(MSG)"

db-shell: ## Open a psql shell
	docker compose exec db psql -U $${POSTGRES_USER:-srp} -d $${POSTGRES_DB:-srp_marketing}

# ── Workers ────────────────────────────────────────────────────────────────────
worker: ## Start Celery worker (dev)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up celery-worker

beat: ## Start Celery beat scheduler (dev)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up celery-beat

flower: ## Open Flower monitoring UI (dev)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up flower
	@echo "$(CYAN)Flower available at http://localhost:5555$(RESET)"

# ── Testing ────────────────────────────────────────────────────────────────────
test: ## Run backend tests
	docker compose run --rm backend pytest -v --tb=short

test-cov: ## Run tests with coverage report
	docker compose run --rm backend pytest --cov=app --cov-report=html --cov-report=term-missing

# ── Code Quality ───────────────────────────────────────────────────────────────
lint: ## Run ruff linter
	docker compose run --rm backend ruff check app/

format: ## Format code with ruff + isort
	docker compose run --rm backend ruff format app/
	docker compose run --rm backend ruff check --fix app/

typecheck: ## Run mypy type checks
	docker compose run --rm backend mypy app/ --ignore-missing-imports

# ── Frontend ───────────────────────────────────────────────────────────────────
frontend-install: ## Install frontend npm dependencies
	cd frontend && npm install

frontend-dev: ## Start frontend dev server locally (without Docker)
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	cd frontend && npm run build

frontend-preview: ## Preview production build locally
	cd frontend && npm run preview

# ── Utilities ──────────────────────────────────────────────────────────────────
shell-backend: ## Open a bash shell in the backend container
	docker compose exec backend bash

redis-shell: ## Open a Redis CLI shell
	docker compose exec redis redis-cli -a $${REDIS_PASSWORD:-redis_secret}

clean: ## Remove all containers, volumes, and build cache
	docker compose down -v --remove-orphans
	docker system prune -f

clean-all: clean ## Remove everything including images
	docker system prune -af

ps: ## Show running containers
	docker compose ps
