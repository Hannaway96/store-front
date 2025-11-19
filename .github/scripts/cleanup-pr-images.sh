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

# Check token format (Docker Hub access tokens start with 'dckr_pat_')
if [[ ! "${DOCKERHUB_TOKEN}" =~ ^dckr_pat_ ]]; then
  echo "⚠ Warning: Token doesn't appear to be a Docker Hub access token"
  echo "  Expected format: dckr_pat_..."
  echo "  Your token starts with: ${DOCKERHUB_TOKEN:0:10}..."
  echo "  If this is a password, you need to create an access token instead"
  echo ""
fi

# Verify authentication and repository access
echo "Verifying Docker Hub authentication..."
AUTH_TEST=$(curl -s -w "\n%{http_code}" -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
  "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/")
AUTH_CODE=$(echo "$AUTH_TEST" | tail -n1)
AUTH_BODY=$(echo "$AUTH_TEST" | sed '$d')

if [ "$AUTH_CODE" != "200" ]; then
  echo "✗ Authentication failed! Cannot access repository."
  echo "  HTTP Code: ${AUTH_CODE}"
  echo "  Response: ${AUTH_BODY}"
  echo ""
  echo "Troubleshooting:"
  echo "  1. Verify DOCKERHUB_USER is correct: ${DOCKERHUB_USER}"
  echo "  2. Verify DOCKERHUB_TOKEN is a valid access token (starts with 'dckr_pat_')"
  echo "  3. Token must have 'Read', 'Write', and 'Delete' permissions"
  echo "  4. Repository must exist: ${DOCKERHUB_USER}/${REPOSITORY}"
  echo "  5. Token must be for the same account as DOCKERHUB_USER"
  exit 1
fi

echo "✓ Authentication successful - can access repository"

# Test if we can perform a write operation (check permissions)
echo "Testing token permissions..."
PERM_TEST=$(curl -s -w "\n%{http_code}" -X GET \
  -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
  "https://hub.docker.com/v2/users/${DOCKERHUB_USER}/")
PERM_CODE=$(echo "$PERM_TEST" | tail -n1)

if [ "$PERM_CODE" != "200" ]; then
  echo "⚠ Warning: Token may not have sufficient permissions (HTTP ${PERM_CODE})"
  echo "  Continuing anyway, but deletions may fail..."
fi

# Function to delete a tag
delete_tag() {
  local TAG=$1
  echo "Deleting tag: ${TAG}"
  
  # Try Bearer token authentication first (some Docker Hub endpoints require this)
  RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE \
    -H "Authorization: Bearer ${DOCKERHUB_TOKEN}" \
    -H "Accept: application/json" \
    "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/${TAG}/" 2>&1)
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  # If Bearer token fails with 401, try basic auth as fallback
  if [ "$HTTP_CODE" = "401" ]; then
    echo "  Trying basic authentication..."
    RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE \
      -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
      -H "Accept: application/json" \
      "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/${TAG}/" 2>&1)
  fi
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "204" ]; then
    echo "  ✓ Deleted ${TAG}"
    return 0
  elif [ "$HTTP_CODE" = "401" ]; then
    echo "  ✗ Authentication failed (HTTP 401)"
    echo "  Full response: ${RESPONSE_BODY}"
    echo ""
    echo "  Common causes:"
    echo "    - Token is not an access token (should start with 'dckr_pat_')"
    echo "    - Token was created without 'Delete' permission"
    echo "    - Token belongs to a different account than DOCKERHUB_USER"
    echo "    - Token has expired or been revoked"
    return 1
  elif [ "$HTTP_CODE" = "403" ]; then
    echo "  ✗ Permission denied (HTTP 403)"
    echo "  Full response: ${RESPONSE_BODY}"
    echo "  Error: Token doesn't have delete permissions for this repository"
    return 1
  else
    echo "  ✗ Failed to delete ${TAG} (HTTP ${HTTP_CODE})"
    echo "  Full response: ${RESPONSE_BODY}"
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

# Exit with error code if any deletions failed
if [ "$FAILED" -gt 0 ]; then
  echo ""
  echo "✗ Cleanup completed with errors. Some tags could not be deleted."
  exit 1
fi

echo "✓ Cleanup completed successfully"
exit 0

