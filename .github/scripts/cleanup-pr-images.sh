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

API_BASE="https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}"

echo "Cleaning up images for PR #${PR_NUM}..."

# Authenticate with Docker Hub API v2 to get JWT token
# REQUIRED: All Docker Hub API operations require JWT token authentication
# With 2FA enabled, use access token as password in login request
# Pattern: Login -> Get JWT -> Use JWT in Authorization header for all API calls
echo "Authenticating with Docker Hub..."
JWT_TOKEN=$(curl -s -H "Content-Type: application/json" -X POST \
  -d "{\"username\": \"${DOCKERHUB_USER}\", \"password\": \"${DOCKERHUB_TOKEN}\"}" \
  https://hub.docker.com/v2/users/login/ | jq -r .token)

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
  
  response=$(curl -s -w "\n%{http_code}" -X DELETE \
    -H "Authorization: JWT ${JWT_TOKEN}" \
    -H "Accept: application/json" \
    "${API_BASE}/tags/${tag}/" 2>&1)
  
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
  
  tags=$(curl -s -H "Authorization: JWT ${JWT_TOKEN}" \
    "${API_BASE}/tags/?page_size=100" \
    | jq -r ".results[] | select(.name | ${pattern}) | .name")
  
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
find_and_delete_tags "startswith(\"api-pr-${PR_NUM}-\") or startswith(\"frontend-pr-${PR_NUM}-\")"

# Delete build cache tags (*-pr-123-buildcache)
echo "Deleting build cache tags..."
find_and_delete_tags "endswith(\"-pr-${PR_NUM}-buildcache\")"

echo "✓ Cleanup completed"
exit 0
