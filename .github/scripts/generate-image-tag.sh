#!/bin/bash
set -euo pipefail

# Generate Docker image tag based on service, branch/PR, and commit SHA
# Usage: generate-image-tag.sh <service> [github_ref] [github_sha]
#   service: Service name (e.g., "api" or "frontend")
#   github_ref: Git reference (default: $GITHUB_REF or current branch)
#   github_sha: Git commit SHA (default: $GITHUB_SHA or current commit)
#   is_latest: Whether to build the latest image (default: false)

SERVICE=$1
GITHUB_REF=${2:-${GITHUB_REF:-}}
GITHUB_SHA=${3:-${GITHUB_SHA:-}}
IS_LATEST=${4:-${IS_LATEST:-false}}

if [ -z "$SERVICE" ]; then
  echo "Error: Service name is required"
  echo "Usage: generate-image-tag.sh <service> [github_ref] [github_sha] [is_latest]"
  exit 1
fi
# Normalize service name to lowercase
SERVICE_PREFIX=$(echo "$SERVICE" | tr '[:upper:]' '[:lower:]')

# Generate image tag
IMAGE_TAG=""

if [ "$IS_LATEST" = true ]; then
  IMAGE_TAG="${SERVICE_PREFIX}_latest"
else
  # Get current branch/ref if not provided
  if [ -z "$GITHUB_REF" ]; then
    GITHUB_REF=$(git rev-parse --symbolic-full-name HEAD 2>/dev/null || echo "refs/heads/$(git branch --show-current)")
  fi

  # Get current commit SHA if not provided
  if [ -z "$GITHUB_SHA" ]; then
    GITHUB_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
  fi

  SHORT_SHA=${GITHUB_SHA:0:7}

  # Determine branch name based on ref
  if [[ "$GITHUB_REF" =~ ^refs/pull/ ]]; then
    PR_NUM=$(echo "$GITHUB_REF" | sed 's|refs/pull/||' | sed 's|/merge||')
    IMAGE_TAG="${SERVICE_PREFIX}-pr-${PR_NUM}-${SHORT_SHA}"
  else
    BRANCH_NAME=${GITHUB_REF#refs/heads/}
    BRANCH_NAME=${BRANCH_NAME//\//-}
    IMAGE_TAG="${SERVICE_PREFIX}-${BRANCH_NAME}-${SHORT_SHA}"
  fi
fi
  
# Output tag (for GitHub Actions)
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "tag=${IMAGE_TAG}" >> "$GITHUB_OUTPUT"
fi

# Print tag to stdout
echo "$IMAGE_TAG"