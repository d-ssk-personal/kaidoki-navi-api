.PHONY: help install install-dev test test-unit test-integration test-coverage clean lint format

help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 本番用の依存関係をインストール
	pip install -r requirements.txt

install-dev: ## 開発用の依存関係をインストール
	pip install -r requirements-dev.txt

test: ## 全てのテストを実行
	pytest

test-unit: ## ユニットテストのみ実行
	pytest -m unit

test-integration: ## 統合テストのみ実行
	pytest -m integration

test-coverage: ## カバレッジレポート付きでテストを実行
	pytest --cov=src --cov-report=html --cov-report=term

test-watch: ## テストを監視モードで実行
	pytest-watch

lint: ## コードの静的解析を実行
	flake8 src tests
	mypy src

format: ## コードフォーマットを実行
	black src tests
	isort src tests

clean: ## キャッシュファイルを削除
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '.coverage' -delete
	rm -rf .pytest_cache htmlcov .mypy_cache .coverage coverage.xml

docker-up: ## Dockerコンテナを起動
	./scripts/start-local.sh

docker-down: ## Dockerコンテナを停止
	docker-compose down

sam-local: ## SAM Localを起動
	sam local start-api --env-vars env.json --docker-network lambda-local

build: ## SAMアプリケーションをビルド
	sam build

deploy: ## AWSにデプロイ
	./scripts/deploy.sh

destroy: ## AWSリソースを削除
	./scripts/destroy.sh
