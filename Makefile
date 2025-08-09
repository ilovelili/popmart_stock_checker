# Makefile

# Default product URL (override with: make run URL=https://... )
URL ?= https://www.popmart.com/jp/products/3884

.PHONY: help setup run run-python clean

help:
	@echo "Targets:"
	@echo "  setup       - Install deps and Playwright browser"
	@echo "  run         - Run stock checker (uses $(URL) by default)"
	@echo "  run-python  - Same as run, but shows the explicit python command"
	@echo "  clean       - Remove .venv and uv lock"

setup:
	uv sync
	uv run playwright install chromium

run:
	uv run python main.py $(URL)

run-python:
	@echo "Running: uv run python main.py $(URL)"
	uv run python main.py $(URL)

clean:
	rm -rf .venv uv.lock
