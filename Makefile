# Makefile

# Default product URL (override with: make run URL=https://... )
URL ?= https://www.popmart.com/jp/products/3884
IMAGE_NAME := popmart-stock-checker

.PHONY: help setup run run-python debug test-email clean docker-build docker-run docker-run-url

help:
	@echo "Targets:"
	@echo "  setup             - Install deps and Playwright browser locally"
	@echo "  run               - Run stock checker locally (uses $(URL) by default)"
	@echo "  run-python        - Same as run, but shows the explicit python command"
	@echo "  debug             - Debug page content to see what buttons/text are found"
	@echo "  test-email        - Test email sending configuration"
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

debug:
	uv run python debug.py $(URL)

test-email:
	uv run python test_email.py

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run --rm \
		-e USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
		-e RETRY_WAIT_MS=2000 \
		$(IMAGE_NAME)

docker-run-url:
	docker run --rm $(IMAGE_NAME) uv run python main.py $(URL)

clean:
	rm -rf .venv uv.lock
