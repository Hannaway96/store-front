#!/usr/bin/env bash
set -e

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Setup backend environment
setup_backend_env

# Ensure ruff is installed
ensure_ruff

echo -e "${GREEN}Running ruff linter...${NC}"
if ruff check .; then
  echo -e "${GREEN}✓ Linting passed!${NC}"
else
  echo -e "${RED}✗ Linting failed. Please fix the errors above.${NC}"
  exit 1
fi
