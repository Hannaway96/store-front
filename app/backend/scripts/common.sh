#!/usr/bin/env bash
# Common functions and variables for backend scripts

# Color definitions
readonly GREEN="\033[0;32m"
readonly YELLOW="\033[1;33m"
readonly RED="\033[0;31m"
readonly NC="\033[0m"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Backend directory is one level up from scripts/
readonly BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Ensure UV is installed
ensure_uv() {
  if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV is not installed. Installing UV...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
  fi
}

# Change to backend directory
cd_to_backend() {
  cd "$BACKEND_DIR" || exit 1
}

# Ensure virtual environment exists and activate it
ensure_venv() {
  cd_to_backend
  
  if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Please run scripts/create_venv.sh first.${NC}"
    exit 1
  fi
  
  source .venv/bin/activate
}

# Ensure ruff is installed
ensure_ruff() {
  if ! command -v ruff &> /dev/null; then
    echo -e "${YELLOW}Ruff is not installed. Installing ruff...${NC}"
    uv sync --extra dev
  fi
}

# Setup backend environment (change directory and activate venv)
setup_backend_env() {
  cd_to_backend
  ensure_venv
}

