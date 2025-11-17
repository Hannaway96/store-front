#!/usr/bin/env bash
set -e

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Setup backend environment
setup_backend_env

# Ensure ruff is installed
ensure_ruff

echo -e "${GREEN}Running ruff linter with auto-fix...${NC}"
ruff check --fix .

echo -e "${GREEN}✓ Linting and auto-fix complete!${NC}"
