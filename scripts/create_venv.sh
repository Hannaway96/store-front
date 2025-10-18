#!/usr/bin/env bash
set -e

VENV_DIR="../.venv"

# Colours
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

# Check if .venv already exists
if [ -d "$VENV_DIR" ]; then
  echo -e "${YELLOW}Virtual environment already exists — skipping creation.${NC}"
else
  echo -e "${GREEN}Creating Python virtual environment...${NC}"
  python3 -m venv "$VENV_DIR"
fi

# Activate the venv
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
if [ -f "../app/backend/requirements.txt" ]; then
  echo -e "${GREEN}Installing requirements.txt...${NC}"
  pip install -r ../app/backend/requirements.txt
else
  echo -e "${YELLOW}No requirements.txt found.${NC}"
fi

# Install dev requirements if present
if [ -f "../app/backend/requirements.dev.txt" ]; then
  echo -e "${GREEN}Installing requirements.dev.txt...${NC}"
  pip install -r ../app/backend/requirements.dev.txt
else
  echo -e "${YELLOW}No requirements.dev.txt found.${NC}"
fi

echo -e "${GREEN}Virtual environment setup complete.${NC}"
