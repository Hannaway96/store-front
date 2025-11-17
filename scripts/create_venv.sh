#!/usr/bin/env bash
set -e

VENV_DIR="../.venv"

# Colours
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
  echo -e "${YELLOW}UV is not installed. Installing UV...${NC}"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check if .venv already exists
if [ -d "$VENV_DIR" ]; then
  echo -e "${YELLOW}Virtual environment already exists — skipping creation.${NC}"
else
  echo -e "${GREEN}Creating Python virtual environment with UV...${NC}"
  uv venv "$VENV_DIR"
fi

# Activate the venv
source "$VENV_DIR/bin/activate"

# Install dependencies using UV sync (preferred method with pyproject.toml)
if [ -f "../app/backend/pyproject.toml" ]; then
  echo -e "${GREEN}Installing dependencies from pyproject.toml with UV sync...${NC}"
  cd ../app/backend
  # --no-install-project: Don't install the project itself (Django app, not a package)
  # --active: Use the currently active virtual environment (set by VIRTUAL_ENV)
  uv sync --extra dev --no-install-project --active
  cd ../../scripts
else
  echo -e "${YELLOW}No pyproject.toml found, falling back to requirements.txt...${NC}"
  # Fallback to requirements.txt if pyproject.toml doesn't exist
  if [ -f "../app/backend/requirements.txt" ]; then
    echo -e "${GREEN}Installing requirements.txt with UV...${NC}"
    uv pip install -r ../app/backend/requirements.txt
  fi
  
  if [ -f "../app/backend/requirements.dev.txt" ] && [ -s "../app/backend/requirements.dev.txt" ]; then
    echo -e "${GREEN}Installing requirements.dev.txt with UV...${NC}"
    uv pip install -r ../app/backend/requirements.dev.txt
  fi
fi

echo -e "${GREEN}Virtual environment setup complete.${NC}"
