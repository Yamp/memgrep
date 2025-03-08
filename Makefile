# MemGrep Makefile
# This Makefile simplifies common development tasks

.PHONY: setup setup-dev run test build clean verify-telegram lint format help

# Default target
help:
	@echo "MemGrep Makefile"
	@echo "----------------"
	@echo "Available targets:"
	@echo "  setup       - Install production dependencies"
	@echo "  setup-dev   - Install development dependencies"
	@echo "  run         - Run the API server"
	@echo "  test        - Run tests"
	@echo "  build       - Build Docker image"
	@echo "  clean       - Clean up resources"
	@echo "  verify-telegram - Verify Telegram API functionality"
	@echo "  lint        - Run linters"
	@echo "  format      - Format code"

# Setup production dependencies
setup:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt
	pip install -r requirements.cv.txt

# Setup development dependencies
setup-dev: setup
	@echo "Installing development dependencies..."
	pip install pytest pytest-cov black ruff mypy

# Run the API server
run:
	@echo "Starting the API server..."
	python scripts/start_api.py

# Run tests
test:
	@echo "Running tests..."
	pytest

# Build Docker image
build:
	@echo "Building Docker image..."
	docker build -t memgrep:latest .

# Clean up resources
clean:
	@echo "Cleaning up resources..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Verify Telegram API functionality
verify-telegram:
	@echo "Verifying Telegram API functionality..."
	python scripts/verify_telegram_api.py

# Run linters
lint:
	@echo "Running linters..."
	ruff check .
	mypy .

# Format code
format:
	@echo "Formatting code..."
	black .
	ruff check --fix .