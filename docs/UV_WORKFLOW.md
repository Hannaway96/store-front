# UV Day-to-Day Workflow Guide

This guide covers everything you need to know for daily Python package management with UV.

## Table of Contents

- [Initial Setup](#initial-setup)
- [Daily Operations](#daily-operations)
- [Adding Dependencies](#adding-dependencies)
- [Updating Dependencies](#updating-dependencies)
- [Removing Dependencies](#removing-dependencies)
- [Working with Virtual Environments](#working-with-virtual-environments)
- [Lock Files](#lock-files)
- [Common Commands Cheat Sheet](#common-commands-cheat-sheet)

## Initial Setup

### Install UV

If you haven't installed UV yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on macOS with Homebrew:
```bash
brew install uv
```

### Generate Lock File (First Time)

After setting up your `pyproject.toml`, generate a lock file for reproducible builds:

```bash
cd app/backend
uv lock
```

This creates `uv.lock` which pins exact versions of all dependencies (including transitive ones). **Commit this file to git** for reproducible builds.

## Daily Operations

### Setting Up Your Development Environment

**Option 1: Using the setup script (recommended)**
```bash
cd scripts
bash create_venv.sh
```

**Option 2: Manual setup**
```bash
cd app/backend
uv venv                    # Create virtual environment
source .venv/bin/activate  # Activate it (Linux/Mac)
# or
.venv\Scripts\activate     # Windows

# --no-install-project: Don't install the project itself (Django app, not a package)
# --active: Use the currently active virtual environment (if venv is not in current dir)
uv sync --extra dev --no-install-project --active  # Install all dependencies including dev
```

**Note**: If your virtual environment is in a different directory than `pyproject.toml`, use the `--active` flag to tell UV to use the currently active virtual environment (via `VIRTUAL_ENV`).

### Installing Dependencies

#### Adding a New Production Dependency

**Old way (pip):**
```bash
pip install django-cors-headers
pip freeze > requirements.txt  # Manual update
```

**New way (UV):**
```bash
uv add django-cors-headers
```

This automatically:
- Adds the package to `pyproject.toml` under `[project.dependencies]`
- Updates `uv.lock` with the exact version
- Installs it in your current environment

#### Adding a New Development Dependency

**Old way (pip):**
```bash
pip install black
# Manually add to requirements.dev.txt
```

**New way (UV):**
```bash
uv add --dev black
# or
uv add --extra dev black
```

This adds it to `[project.optional-dependencies.dev]` in `pyproject.toml`.

#### Adding Multiple Dependencies

```bash
uv add django-cors-headers requests
uv add --dev black ruff mypy
```

#### Adding with Version Constraints

```bash
uv add "django>=5.1,<6.0"
uv add "pytest==8.3.3"
```

### Updating Dependencies

#### Update a Specific Package

**Old way (pip):**
```bash
pip install --upgrade django
pip freeze > requirements.txt  # Manual update
```

**New way (UV):**
```bash
uv add --upgrade django
```

#### Update All Dependencies

**Old way (pip):**
```bash
pip install --upgrade -r requirements.txt
```

**New way (UV):**
```bash
uv sync --upgrade --no-install-project
```

**Note**: For Django projects, always include `--no-install-project` to avoid trying to install the project as a package.

This updates all packages to their latest compatible versions (respecting version constraints in `pyproject.toml`).

#### Update and Regenerate Lock File

```bash
uv lock --upgrade
```

This updates the lock file without installing packages (useful for CI/CD).

### Removing Dependencies

**Old way (pip):**
```bash
pip uninstall package-name
# Manually remove from requirements.txt
```

**New way (UV):**
```bash
uv remove package-name
```

This automatically:
- Removes from `pyproject.toml`
- Updates `uv.lock`
- Uninstalls from your environment

To remove a dev dependency:
```bash
uv remove --dev package-name
```

### Working with Virtual Environments

#### Create a New Virtual Environment

```bash
uv venv                    # Creates .venv in current directory
uv venv myenv             # Creates myenv directory
uv venv --python 3.13     # Specify Python version
```

#### Activate Virtual Environment

```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows
```

#### Install Dependencies in Virtual Environment

```bash
uv sync --no-install-project                    # Install production dependencies
uv sync --extra dev --no-install-project        # Install with dev dependencies
```

**Note**: 
- For Django projects, always use `--no-install-project` since Django apps aren't meant to be installed as packages.
- If your virtual environment is not in the same directory as `pyproject.toml`, add `--active` to use the currently active venv: `uv sync --extra dev --no-install-project --active`

#### Run Commands in Virtual Environment (Without Activating)

```bash
uv run python manage.py migrate
uv run pytest
uv run black .
```

This is convenient - UV automatically uses the virtual environment.

#### Deactivate Virtual Environment

```bash
deactivate
```

### Lock Files

#### What is `uv.lock`?

`uv.lock` is a lockfile that pins exact versions of all dependencies (including transitive dependencies). It ensures reproducible builds across different machines and environments.

#### Generate/Update Lock File

```bash
uv lock                  # Generate/update lock file
uv lock --upgrade        # Update all packages to latest compatible versions
```

#### Using Lock File for Reproducible Installs

```bash
uv sync --frozen          # Install exactly what's in uv.lock (no updates)
```

This is what Docker uses for production builds.

#### Should I Commit `uv.lock`?

**Yes!** Always commit `uv.lock` to git. It ensures:
- Everyone gets the same dependency versions
- CI/CD builds are reproducible
- Production deployments are consistent

## Common Commands Cheat Sheet

### Package Management

| Task | Old (pip) | New (UV) |
|------|-----------|----------|
| Install package | `pip install pkg` | `uv add pkg` |
| Install dev package | `pip install pkg` + manual edit | `uv add --dev pkg` |
| Update package | `pip install --upgrade pkg` | `uv add --upgrade pkg` |
| Remove package | `pip uninstall pkg` + manual edit | `uv remove pkg` |
| Update all | `pip install --upgrade -r req.txt` | `uv sync --upgrade` |
| List packages | `pip list` | `uv pip list` |
| Show package info | `pip show pkg` | `uv pip show pkg` |

### Environment Management

| Task | Old | New (UV) |
|------|-----|----------|
| Create venv | `python -m venv .venv` | `uv venv` |
| Install deps | `pip install -r req.txt` | `uv sync --no-install-project` |
| Install with dev | `pip install -r req-dev.txt` | `uv sync --extra dev --no-install-project` |
| Run command | `python script.py` | `uv run script.py` |

### Lock File Management

| Task | Command |
|------|---------|
| Generate lock | `uv lock` |
| Update lock | `uv lock --upgrade` |
| Install from lock | `uv sync --frozen --no-install-project` |

## Workflow Examples

### Starting a New Feature

```bash
# 1. Ensure you're up to date
cd app/backend
uv sync --upgrade --no-install-project

# 2. Add any new dependencies you need
uv add new-package-name

# 3. Work on your feature
uv run python manage.py runserver
```

### Before Committing

```bash
# 1. Update lock file if you added dependencies
uv lock

# 2. Run tests
uv run pytest

# 3. Commit both pyproject.toml and uv.lock
git add pyproject.toml uv.lock
git commit -m "Add new feature with dependencies"
```

### Updating Dependencies

```bash
# 1. Update all dependencies to latest compatible versions
uv sync --upgrade --no-install-project

# 2. Test your application
uv run pytest
uv run python manage.py test

# 3. Update lock file
uv lock

# 4. Commit changes
git add pyproject.toml uv.lock
git commit -m "Update dependencies"
```

### Adding a New Dev Tool

```bash
# Add the tool
uv add --dev ruff

# It's automatically added to pyproject.toml and installed
# Update lock file
uv lock

# Use it
uv run ruff check .
```

## Tips & Best Practices

1. **Always use `uv add` instead of manually editing `pyproject.toml`** - It keeps everything in sync

2. **Commit `uv.lock`** - Essential for reproducible builds

3. **Use `uv sync --no-install-project` instead of `uv pip install`** - It's faster and respects your lock file (use `--no-install-project` for Django apps)

4. **Use `uv run` for one-off commands** - No need to activate the venv

5. **Run `uv lock` after adding dependencies** - Keeps your lock file up to date

6. **Use `--frozen` in CI/CD** - Ensures exact same versions as your lock file

7. **Update dependencies regularly** - Run `uv sync --upgrade --no-install-project` weekly/monthly

## Troubleshooting

### Lock file is out of sync

```bash
uv lock  # Regenerate it
```

### Need to see what would change

```bash
uv lock --upgrade-package django  # See what would update
```

### Clear UV cache

```bash
uv cache clean
```

### Reinstall everything

```bash
rm -rf .venv uv.lock
uv venv
uv sync --extra dev --no-install-project
uv lock
```

## Migration from pip/requirements.txt

If you're migrating from `requirements.txt`:

1. Your `pyproject.toml` already has dependencies defined
2. Generate lock file: `uv lock`
3. Start using `uv add` for new packages
4. You can keep `requirements.txt` for compatibility, but `pyproject.toml` is the source of truth
5. To export requirements.txt from pyproject.toml: `uv pip compile pyproject.toml -o requirements.txt`

## Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)
- [PEP 621 - Project metadata](https://peps.python.org/pep-0621/)

