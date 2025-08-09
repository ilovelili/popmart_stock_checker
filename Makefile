# Makefile

# Default product URL (override with: make run URL=https://... )
URL ?= https://www.popmart.com/jp/products/3884
IMAGE_NAME := popmart-stock-checker

.PHONY: help setup run run-python clean docker-build docker-run docker-run-url

help:
	@echo "Targets:"
	@echo "  setup             - Install deps and Playwright browser locally"
	@echo "  run               - Run stock checker locally (uses $(URL) by default)"
	@echo "  run-python        - Same as run, but shows the explicit python command"
	@echo "  docker-build      - Build the Docker image ($(IMAGE_NAME))"
	@echo "  docker-run        - Run the Docker image using default URL"
	@echo "  docker-run-url    - Run the Docker image with a custom URL (make docker-run-url URL=...)"
	@echo "  clean             - Remove .venv and uv lock"

setup:
	uv sync
	uv run playwright install chromium

run:
	uv run python main.py $(URL)

run-python:
	@echo "Running: uv run python main.py $(URL)"
	uv run python main.py $(URL)

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run --rm $(IMAGE_NAME)

docker-run-url:
	docker run --rm $(IMAGE_NAME) uv run python main.py $(URL)

clean:
	rm -rf .venv uv.lock
