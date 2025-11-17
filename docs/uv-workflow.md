# UV Workflow Guide

Quick reference for using UV (fast Python package manager) in this project.

## Quick Start

### Initial Setup

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup virtual environment and install dependencies
./app/backend/scripts/create_venv.sh
```

This script will:
- Install UV if needed
- Create a virtual environment in `app/backend/.venv`
- Install all dependencies (including dev tools like Ruff and pytest)

## Common Tasks

### Adding Dependencies

```bash
cd app/backend

# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name

# Update lock file
uv lock
```

### Updating Dependencies

```bash
cd app/backend

# Update all dependencies
uv sync --upgrade

# Update lock file
uv lock
```

### Removing Dependencies

```bash
cd app/backend
uv remove package-name
uv lock
```

### Running Commands

```bash
cd app/backend

# Run Django commands
uv run python manage.py migrate
uv run python manage.py runserver

# Run tests
uv run pytest

# Run linting/formatting
./scripts/lint.sh
./scripts/format.sh
./scripts/lint-fix.sh
```

## Lock File

The `uv.lock` file ensures reproducible builds. **Always commit it to git.**

- Generate/update: `uv lock`
- Install from lock: `uv sync --frozen` (used in CI/CD)

## Development Scripts

Located in `app/backend/scripts/`:

- `create_venv.sh` - Setup virtual environment
- `lint.sh` - Check for linting issues
- `format.sh` - Format code with Ruff
- `lint-fix.sh` - Auto-fix linting issues

## Tips

1. Use `uv add` instead of manually editing `pyproject.toml`
2. Always run `uv lock` after adding/removing dependencies
3. Use `uv run` to execute commands without activating venv
4. Commit both `pyproject.toml` and `uv.lock` together

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
