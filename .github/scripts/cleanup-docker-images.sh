#!/bin/bash
set -euo pipefail

# Cleanup old Docker Hub images
# Usage: cleanup-docker-images.sh [keep_recent] [dry_run]

KEEP_RECENT=${1:-10}
DRY_RUN=${2:-true}

: "${DOCKERHUB_USER:?DOCKERHUB_USER environment variable is required}"
: "${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN environment variable is required}"
: "${REPOSITORY:?REPOSITORY environment variable is required}"

API_BASE="https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}"

# Delete a tag using Docker Hub API v2
# With 2FA enabled, use access token as password in basic auth
delete_tag() {
  local tag=$1
  local response http_code
  
  response=$(curl -s -w "\n%{http_code}" -X DELETE \
    -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
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

# Cleanup tags for a service prefix
cleanup_service() {
  local prefix=$1
  local tags keep_tags delete_tags deleted=0 failed=0
  
  echo "Cleaning up ${prefix} images..."
  
  tags=$(curl -s -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
    "${API_BASE}/tags/?page_size=100" \
    | jq -r ".results[] | select(.name | startswith(\"${prefix}-\")) | .name" \
    | sort -r)
  
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

# Cleanup build cache tags
cleanup_cache() {
  local cache_tags keep_cache delete_cache deleted=0 failed=0
  
  echo "Cleaning up build cache tags..."
  
  cache_tags=$(curl -s -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
    "${API_BASE}/tags/?page_size=100" \
    | jq -r ".results[] | select(.name | endswith(\"-buildcache\")) | .name" \
    | sort -r)
  
  if [ -z "$cache_tags" ]; then
    echo "No build cache tags found"
    return 0
  fi
  
  keep_cache=$(echo "$cache_tags" | head -n ${KEEP_RECENT})
  delete_cache=$(echo "$cache_tags" | tail -n +$((KEEP_RECENT + 1)))
  
  if [ -z "$delete_cache" ]; then
    echo "No build cache tags to delete"
    return 0
  fi
  
  echo "Would delete $(echo "$delete_cache" | wc -l) old build cache tags"
  
  if [ "$DRY_RUN" = "true" ]; then
    echo "DRY RUN: Skipping cache deletion"
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
