set dotenv-load := true
set dotenv-filename := ".env"
set export := true

HERE := justfile_directory()
VERSION := `awk -F\" '/^version/{print $2}' pyproject.toml`
PYTHON_VERSIONS := `awk -F'[^0-9]+' '/requires-python/{for(i=$3;i<$5;)printf(i-$3?" ":"")$2"."i++}' pyproject.toml`

@_default:
    @just --list

# Remove all generated files
[group('Build')]
clean:
    rm -rf dist
    rm -rf site

# Build the library
[group('Build')]
build: clean
    uv build

# Build docs
[group('Build')]
build-docs: clean
    uv run zensical build


# Static analysis
[group('QA')]
lint:
    uv run ruff format --check src
    uv run ruff check src

# Check types make sense
[group('QA')]
typecheck:
    uv run mypy src

# Run the test suite
[group('QA')]
test:
    uv run pytest --cov=django_typst --cov-report=term

# Run QA tooling
[group('QA')]
check: lint typecheck test

# Apply autoformatters
[group('QA')]
format:
    uv run ruff format src
    uv run ruff check --select I --fix src


# Print the current version of the project
[group('Release')]
version:
    @echo "Current version is {{ VERSION }}"

# Tag the current version in git and push to GitHub
[group('Release')]
tag:
    echo "Tagging version v{{ VERSION }}"
    git tag -a v{{ VERSION }} -m "Creating version v{{ VERSION }}"
    git push origin v{{ VERSION }}
