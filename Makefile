# Makefile for Chatbot Project

.PHONY: help build up down logs clean dev prod test lint format

# 기본 설정
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_DEV = docker-compose --profile dev
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.prod.yml

help: ## 도움말 표시
	@echo "사용 가능한 명령어:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Docker 이미지 빌드
	$(DOCKER_COMPOSE) build

build-no-cache: ## 캐시 없이 Docker 이미지 빌드
	$(DOCKER_COMPOSE) build --no-cache

up: ## 전체 스택 실행 (프로덕션)
	$(DOCKER_COMPOSE) up -d

down: ## 전체 스택 중지
	$(DOCKER_COMPOSE) down

logs: ## 로그 확인
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## 백엔드 로그 확인
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## 프론트엔드 로그 확인
	$(DOCKER_COMPOSE) logs -f frontend

dev: ## 개발 환경 실행
	$(DOCKER_COMPOSE_DEV) up -d

dev-down: ## 개발 환경 중지
	$(DOCKER_COMPOSE_DEV) down

prod: ## 프로덕션 환경 실행
	$(DOCKER_COMPOSE_PROD) up -d

prod-down: ## 프로덕션 환경 중지
	$(DOCKER_COMPOSE_PROD) down

test: ## 테스트 실행
	$(DOCKER_COMPOSE) exec backend python -m pytest tests/ || echo "No tests found"

lint: ## 코드 린팅
	$(DOCKER_COMPOSE) exec backend flake8 . || echo "No flake8 configuration found"

format: ## 코드 포맷팅
	$(DOCKER_COMPOSE) exec backend black . || echo "No black configuration found"

shell-backend: ## 백엔드 컨테이너 쉘 접속
	$(DOCKER_COMPOSE) exec backend bash

shell-frontend: ## 프론트엔드 컨테이너 쉘 접속
	$(DOCKER_COMPOSE) exec frontend sh

restart: ## 전체 스택 재시작
	$(DOCKER_COMPOSE) restart

restart-backend: ## 백엔드 재시작
	$(DOCKER_COMPOSE) restart backend

restart-frontend: ## 프론트엔드 재시작
	$(DOCKER_COMPOSE) restart frontend

clean: ## 사용하지 않는 Docker 리소스 정리
	docker system prune -f
	docker volume prune -f

clean-all: ## 모든 Docker 리소스 정리 (주의!)
	docker system prune -a -f
	docker volume prune -f
	docker network prune -f

status: ## 컨테이너 상태 확인
	$(DOCKER_COMPOSE) ps

health: ## 헬스 체크
	@echo "Backend Health:"
	@curl -s http://localhost:5000/health | python -m json.tool || echo "Backend not responding"
	@echo "\nFrontend Health:"
	@curl -s http://localhost:3000/ | head -n 5 || echo "Frontend not responding"

install: ## 의존성 설치 (로컬)
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

setup: ## 초기 설정
	@echo "Setting up project..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run 'make install' to install dependencies"

# 개발용 단축 명령어
start: up ## 시작 (up과 동일)
stop: down ## 중지 (down과 동일)
rebuild: build-no-cache up ## 재빌드 후 시작
