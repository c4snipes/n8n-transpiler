.PHONY: help install sync test lint format check clean build

help:
	@echo "Targets:"
	@echo "  install   Install package + dev extras into uv-managed venv"
	@echo "  sync      Re-sync dependencies (alias for install)"
	@echo "  test      Run pytest"
	@echo "  lint      Run ruff lint check"
	@echo "  format    Run ruff format"
	@echo "  check     Lint + type-check + tests"
	@echo "  clean     Remove build artifacts"
	@echo "  build     Build sdist + wheel"

install:
	uv sync --all-extras

sync: install

test:
	uv run pytest

test-oracle:
	uv sync --extra oracle --extra dev
	uv run pytest -m oracle

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

typecheck:
	uv run mypy

check: lint typecheck test

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .mypy_cache .coverage
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

build:
	uv build
