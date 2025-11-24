.PHONY: help setup docker-up docker-down docker-logs test install-backend install-frontend

help:
	@echo "Available commands:"
	@echo "  make setup              - Set up environment files"
	@echo "  make docker-up          - Start all services with Docker"
	@echo "  make docker-down        - Stop all services"
	@echo "  make docker-logs        - View Docker logs"
	@echo "  make test               - Run tests"
	@echo "  make install-backend    - Install backend dependencies"
	@echo "  make install-frontend   - Install frontend dependencies"
	@echo "  make init-db            - Initialize database tables"
	@echo "  make seed-misconceptions - Seed misconceptions database"

setup:
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "Created backend/.env - please edit with your API keys"; \
	fi

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	cd backend && pytest ../tests/ -v

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && source ~/.nvm/nvm.sh && npm install

init-db:
	cd backend && python scripts/init_db.py

seed-misconceptions:
	cd backend && python scripts/seed_misconceptions.py


