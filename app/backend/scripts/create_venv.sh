#!/usr/bin/env bash
set -e

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Ensure UV is installed
ensure_uv

# Change to backend directory
cd_to_backend

# Check if .venv already exists
if [ -d ".venv" ]; then
  echo -e "${YELLOW}Virtual environment already exists — skipping creation.${NC}"
else
  echo -e "${GREEN}Creating Python virtual environment with UV in app/backend/.venv...${NC}"
  uv venv
fi

# Activate the venv
source .venv/bin/activate

# Install dependencies using UV sync (preferred method with pyproject.toml)
if [ -f "pyproject.toml" ]; then
  echo -e "${GREEN}Installing dependencies from pyproject.toml with UV sync...${NC}"
  # No need for --no-install-project or --active since we removed [build-system] from pyproject.toml
  # and the venv is in the same directory as pyproject.toml
  uv sync --extra dev
else
  echo -e "${YELLOW}No pyproject.toml found, falling back to requirements.txt...${NC}"
  # Fallback to requirements.txt if pyproject.toml doesn't exist
  if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}Installing requirements.txt with UV...${NC}"
    uv pip install -r requirements.txt
  fi
  
  if [ -f "requirements.dev.txt" ] && [ -s "requirements.dev.txt" ]; then
    echo -e "${GREEN}Installing requirements.dev.txt with UV...${NC}"
    uv pip install -r requirements.dev.txt
  fi
fi

echo -e "${GREEN}Virtual environment setup complete.${NC}"
