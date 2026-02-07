.PHONY: help build install man clean test dev check format lint

# Default target
help:
	@echo "pycheckit - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  help       - Show this help message"
	@echo "  .venv      - Create virtual environment and install dependencies"
	@echo "  build      - Build the distributable package with uv"
	@echo "  install    - Install the package using uv"
	@echo "  dev        - Install package in development mode"
	@echo "  clean      - Remove build artifacts and caches"
	@echo "  test       - Run tests"
	@echo "  check      - Run all checks (format, lint, test)"
	@echo "  format     - Format code with black"
	@echo "  lint       - Run linters (ruff, mypy)"

# Create virtual environment and install dependencies
.venv:
	@echo "Creating virtual environment and installing dependencies..."
	uv sync --extra dev

# Build the distributable package
build: .venv clean
	@echo "Building package..."
	uv build 

# Install the package
install:
	@echo "Installing package..."
	uv pip install .

# Install in development mode
dev:
	@echo "Installing package in development mode..."
	python3 -m pip install -e .

man:
	@echo 'generating manpages...'
	@$(MAKE) -C man man

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@$(MAKE) -C man clean

# Run tests
test:
	@echo "Running tests..."
	python3 -m pytest -v testing/

# Format code
format:
	@echo "Formatting code with black..."
	python3 -m black src/

# Lint code
lint:
	@echo "Running ruff..."
	python3 -m ruff check src/
	@echo "Running mypy..."
	python3 -m mypy src/

# Run all checks
check: format lint test
	@echo "All checks passed!"

