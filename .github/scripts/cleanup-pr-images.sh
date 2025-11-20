#!/bin/bash
set -euo pipefail

# Cleanup Docker Hub images for a specific PR
# Usage: cleanup-pr-images.sh <pr_number>

PR_NUM=${1:-}
if [ -z "$PR_NUM" ]; then
  echo "Error: PR number is required"
  echo "Usage: cleanup-pr-images.sh <pr_number>"
  exit 1
fi

: "${DOCKERHUB_USER:?DOCKERHUB_USER environment variable is required}"
: "${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN environment variable is required}"
: "${REPOSITORY:?REPOSITORY environment variable is required}"

DOCKERHUB_URL="https://hub.docker.com/v2"
LOGIN_URL="${DOCKERHUB_URL}/users/login/"
REPO_URL="${DOCKERHUB_URL}/repositories/${DOCKERHUB_USER}/${REPOSITORY}"

TAGS_URL="${REPO_URL}/tags/?page_size=100"

echo "Cleaning up images for PR #${PR_NUM}..."

# Authenticate with Docker Hub API v2 to get JWT token
# REQUIRED: All Docker Hub API operations require JWT token authentication
# With 2FA enabled, use access token as password in login request
# Pattern: Login -> Get JWT -> Use JWT in Authorization header for all API calls
echo "Authenticating with Docker Hub..."
JWT_TOKEN=$(
  curl -s "${LOGIN_URL}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${DOCKERHUB_USER}\", \"password\": \"${DOCKERHUB_TOKEN}\"}" \
    | jq -r .token
)

if [ -z "$JWT_TOKEN" ] || [ "$JWT_TOKEN" = "null" ]; then
  echo "✗ Failed to authenticate with Docker Hub"
  echo "  Check that DOCKERHUB_USER and DOCKERHUB_TOKEN are correct"
  exit 1
fi

echo "✓ Authentication successful"

# Delete a tag using JWT token (must authenticate first)
delete_tag() {
  local tag=$1
  local response http_code
  
  response=$(
    curl -s "${REPO_URL}/tags/${tag}/" \
      -X DELETE \
      -H "Authorization: JWT ${JWT_TOKEN}" \
      -H "Accept: application/json" \
      -w "\n%{http_code}" \
      2>&1
  )
  
  http_code=$(echo "$response" | tail -n1)
  
  if [ "$http_code" = "204" ]; then
    echo "  ✓ Deleted ${tag}"
    return 0
  else
    echo "  ✗ Failed to delete ${tag} (HTTP ${http_code})"
    return 1
  fi
}

# Find and delete PR tags
find_and_delete_tags() {
  local pattern=$1
  local tags deleted=0 failed=0
  
  tags=$(
    curl -s "${TAGS_URL}" \
      -H "Authorization: JWT ${JWT_TOKEN}" \
      | jq -r ".results[] | select(.name | ${pattern}) | .name"
  )
  
  if [ -z "$tags" ]; then
    return 0
  fi
  
  while IFS= read -r tag; do
    [ -z "$tag" ] && continue
    if delete_tag "$tag"; then
      deleted=$((deleted + 1))
    else
      failed=$((failed + 1))
    fi
  done <<< "$tags"
  
  echo "  Summary: ${deleted} deleted, ${failed} failed"
  return $failed
}

# Delete service tags (api-pr-123-* and frontend-pr-123-*)
echo "Deleting service tags..."
SERVICE_TAG_PATTERN="startswith(\"api-pr-${PR_NUM}-\") or startswith(\"frontend-pr-${PR_NUM}-\")"
find_and_delete_tags "${SERVICE_TAG_PATTERN}"

# Delete build cache tags (*-pr-123-buildcache)
echo "Deleting build cache tags..."
CACHE_TAG_PATTERN="endswith(\"-pr-${PR_NUM}-buildcache\")"
find_and_delete_tags "${CACHE_TAG_PATTERN}"

echo "✓ Cleanup completed"
exit 0
