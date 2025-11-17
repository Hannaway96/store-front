#!/usr/bin/env bash
set -e

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Setup backend environment
setup_backend_env

# Ensure ruff is installed
ensure_ruff

echo -e "${GREEN}Formatting Python files with ruff...${NC}"
ruff format .

echo -e "${GREEN}✓ Formatting complete!${NC}"
