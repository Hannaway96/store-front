#!/bin/bash
set -euo pipefail

# Cleanup old Docker Hub images
# Usage: cleanup-docker-images.sh [keep_recent] [dry_run]

KEEP_RECENT=${1:-10}
DRY_RUN=${2:-true}

: "${DOCKERHUB_USER:?DOCKERHUB_USER environment variable is required}"
: "${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN environment variable is required}"
: "${REPOSITORY:?REPOSITORY environment variable is required}"


DOCKERHUB_URL="https://hub.docker.com/v2"
LOGIN_URL="${DOCKERHUB_URL}/users/login/"
REPO_URL="${DOCKERHUB_URL}/repositories/${DOCKERHUB_USER}/${REPOSITORY}"
TAGS_URL="${REPO_URL}/tags/?page_size=100"
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

# Cleanup tags for a service prefix
cleanup_service() {
  local prefix=$1
  local tags keep_tags delete_tags deleted=0 failed=0
  
  echo "Cleaning up ${prefix} images..."
  
  tags=$(
    curl -s "${TAGS_URL}" \
      -H "Authorization: JWT ${JWT_TOKEN}" \
      | jq -r ".results[] | select(.name | startswith(\"${prefix}-\")) | .name" \
      | sort -r
  )
  
  if [ -z "$tags" ]; then
    echo "No ${prefix} tags found"
    return 0
  fi
  
  keep_tags=$(echo "$tags" | head -n ${KEEP_RECENT})
  delete_tags=$(echo "$tags" | tail -n +$((KEEP_RECENT + 1)))
  
  if [ -z "$delete_tags" ]; then
    echo "No ${prefix} tags to delete (keeping $(echo "$tags" | wc -l) tags)"
    return 0
  fi
  
  echo "Keeping ${KEEP_RECENT} recent tags, deleting $(echo "$delete_tags" | wc -l) old tags"
  
  if [ "$DRY_RUN" = "true" ]; then
    echo "DRY RUN: Would delete:"
    echo "$delete_tags" | sed 's/^/  - /'
    return 0
  fi
  
  while IFS= read -r tag; do
    [ -z "$tag" ] && continue
    if delete_tag "$tag"; then
      deleted=$((deleted + 1))
    else
      failed=$((failed + 1))
    fi
  done <<< "$delete_tags"
  
  echo "  Summary: ${deleted} deleted, ${failed} failed"
  return $failed
}

# Cleanup build cache tags (keep fewer than regular images)
cleanup_cache() {
  local cache_tags keep_cache delete_cache deleted=0 failed=0
  # Keep fewer build cache tags (3 instead of KEEP_RECENT) to reduce storage
  local keep_cache_count=3
  
  echo "Cleaning up build cache tags (keeping ${keep_cache_count} most recent)..."
  
  cache_tags=$(
    curl -s "${TAGS_URL}" \
      -H "Authorization: JWT ${JWT_TOKEN}" \
      | jq -r ".results[] | select(.name | endswith(\"-buildcache\")) | .name" \
      | sort -r
  )
  
  if [ -z "$cache_tags" ]; then
    echo "No build cache tags found"
    return 0
  fi
  
  keep_cache=$(echo "$cache_tags" | head -n ${keep_cache_count})
  delete_cache=$(echo "$cache_tags" | tail -n +$((keep_cache_count + 1)))
  
  if [ -z "$delete_cache" ]; then
    echo "No build cache tags to delete (keeping $(echo "$cache_tags" | wc -l) tags)"
    return 0
  fi
  
  echo "Keeping ${keep_cache_count} recent cache tags, deleting $(echo "$delete_cache" | wc -l) old cache tags"
  
  if [ "$DRY_RUN" = "true" ]; then
    echo "DRY RUN: Would delete:"
    echo "$delete_cache" | sed 's/^/  - /'
    return 0
  fi
  
  while IFS= read -r tag; do
    [ -z "$tag" ] && continue
    if delete_tag "$tag"; then
      deleted=$((deleted + 1))
    else
      failed=$((failed + 1))
    fi
  done <<< "$delete_cache"
  
  echo "  Summary: ${deleted} deleted, ${failed} failed"
  return $failed
}

# Run cleanup operations
failed=0
cleanup_service "api" || failed=$((failed + 1))
cleanup_service "frontend" || failed=$((failed + 1))
cleanup_cache || failed=$((failed + 1))

if [ $failed -gt 0 ]; then
  echo "✗ Cleanup completed with errors"
  exit 1
fi

echo "✓ Cleanup completed successfully"
exit 0
