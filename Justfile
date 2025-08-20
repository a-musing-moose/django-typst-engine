@_default:
    @just --list

# Remove all generated files
clean:
    rm -rf dist

# Build the library
build: clean
    uv build


# Static analysis
lint:
    uv run ruff format --check src
    uv run ruff check src

# Check types make sense
typecheck:
    uv run mypy src

# Run the test suite
test:
    uv run pytest --cov=django_typst --cov-report=term

# Apply autoformatters
format:
    uv run ruff format src
    uv run ruff check --select I --fix src
