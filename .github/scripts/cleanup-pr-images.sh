#!/bin/bash
set -euo pipefail

# Cleanup Docker Hub images for a specific PR
# Usage: cleanup-pr-images.sh <pr_number>
#   pr_number: The pull request number

PR_NUM=${1:-}

if [ -z "$PR_NUM" ]; then
  echo "Error: PR number is required"
  echo "Usage: cleanup-pr-images.sh <pr_number>"
  exit 1
fi

# Required environment variables
: "${DOCKERHUB_USER:?DOCKERHUB_USER environment variable is required}"
: "${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN environment variable is required}"
: "${REPOSITORY:?REPOSITORY environment variable is required}"

echo "Cleaning up images for PR #${PR_NUM}..."

# Function to delete a tag
delete_tag() {
  local TAG=$1
  echo "Deleting tag: ${TAG}"
  RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE \
    -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
    "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/${TAG}/")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "204" ]; then
    echo "  ✓ Deleted ${TAG}"
    return 0
  else
    echo "  ✗ Failed to delete ${TAG} (HTTP ${HTTP_CODE})"
    return 1
  fi
}

# Find all tags for this PR
TAGS=$(curl -s -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
  "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/?page_size=100" \
  | jq -r ".results[] | select(.name | startswith(\"api-pr-${PR_NUM}-\") or startswith(\"frontend-pr-${PR_NUM}-\")) | .name")

if [ -z "$TAGS" ]; then
  echo "No images found for PR #${PR_NUM}"
  exit 0
fi

DELETED=0
FAILED=0

while IFS= read -r TAG; do
  if [ -n "$TAG" ]; then
    if delete_tag "$TAG"; then
      DELETED=$((DELETED + 1))
    else
      FAILED=$((FAILED + 1))
    fi
  fi
done <<< "$TAGS"

# Also delete build cache tags for this PR
CACHE_TAGS=$(curl -s -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
  "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/?page_size=100" \
  | jq -r ".results[] | select(.name | endswith(\"-pr-${PR_NUM}-buildcache\")) | .name")

while IFS= read -r CACHE_TAG; do
  if [ -n "$CACHE_TAG" ]; then
    if delete_tag "$CACHE_TAG"; then
      DELETED=$((DELETED + 1))
    else
      FAILED=$((FAILED + 1))
    fi
  fi
done <<< "$CACHE_TAGS"

echo ""
echo "Cleanup summary:"
echo "  Deleted: ${DELETED} tags"
echo "  Failed: ${FAILED} tags"

