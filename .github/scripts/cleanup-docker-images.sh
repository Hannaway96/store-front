#!/bin/bash
set -euo pipefail

# Cleanup old Docker Hub images
# Usage: cleanup-docker-images.sh [keep_recent] [dry_run]
#   keep_recent: Number of recent images to keep per service (default: 10)
#   dry_run: "true" or "false" (default: "true")

KEEP_RECENT=${1:-10}
DRY_RUN=${2:-true}

# Required environment variables
: "${DOCKERHUB_USER:?DOCKERHUB_USER environment variable is required}"
: "${DOCKERHUB_TOKEN:?DOCKERHUB_TOKEN environment variable is required}"
: "${REPOSITORY:?REPOSITORY environment variable is required}"

# Function to cleanup tags for a service prefix
cleanup_service() {
  local SERVICE_PREFIX=$1
  echo "Cleaning up ${SERVICE_PREFIX} images..."
  
  # Get all tags for this service prefix
  TAGS=$(curl -s -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
    "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/?page_size=100" \
    | jq -r ".results[] | select(.name | startswith(\"${SERVICE_PREFIX}-\")) | .name" \
    | sort -r)
  
  if [ -z "$TAGS" ]; then
    echo "No ${SERVICE_PREFIX} tags found"
    return
  fi
  
  # Count total tags
  TAG_COUNT=$(echo "$TAGS" | wc -l)
  echo "Found ${TAG_COUNT} ${SERVICE_PREFIX} tags"
  
  # Keep only the most recent KEEP_RECENT tags
  KEEP_TAGS=$(echo "$TAGS" | head -n ${KEEP_RECENT})
  DELETE_TAGS=$(echo "$TAGS" | tail -n +$((KEEP_RECENT + 1)))
  
  DELETE_COUNT=$(echo "$DELETE_TAGS" | grep -c . || echo "0")
  
  if [ "$DELETE_COUNT" -eq 0 ]; then
    echo "No ${SERVICE_PREFIX} tags to delete (keeping ${TAG_COUNT} tags)"
    return
  fi
  
  echo "Keeping ${KEEP_RECENT} recent ${SERVICE_PREFIX} tags:"
  echo "$KEEP_TAGS" | sed 's/^/  - /'
  echo ""
  echo "Would delete ${DELETE_COUNT} old ${SERVICE_PREFIX} tags:"
  echo "$DELETE_TAGS" | sed 's/^/  - /'
  echo ""
  
  if [ "$DRY_RUN" = "true" ]; then
    echo "DRY RUN: Skipping deletion"
    return
  fi
  
  # Delete old tags
  DELETED=0
  FAILED=0
  while IFS= read -r TAG; do
    if [ -n "$TAG" ]; then
      echo "Deleting ${SERVICE_PREFIX} tag: ${TAG}"
      RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE \
        -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
        "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/${TAG}/")
      
      HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
      RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')
      
      if [ "$HTTP_CODE" = "204" ]; then
        DELETED=$((DELETED + 1))
        echo "  ✓ Deleted ${TAG}"
      elif [ "$HTTP_CODE" = "401" ]; then
        FAILED=$((FAILED + 1))
        echo "  ✗ Authentication failed (HTTP 401)"
        echo "  Error: Check that your DOCKERHUB_TOKEN has delete permissions"
      elif [ "$HTTP_CODE" = "403" ]; then
        FAILED=$((FAILED + 1))
        echo "  ✗ Permission denied (HTTP 403)"
        echo "  Error: Your token doesn't have delete permissions for this repository"
      else
        FAILED=$((FAILED + 1))
        echo "  ✗ Failed to delete ${TAG} (HTTP ${HTTP_CODE})"
      fi
    fi
  done <<< "$DELETE_TAGS"
  
  echo "Deleted ${DELETED} ${SERVICE_PREFIX} tags, ${FAILED} failed"
}

# Cleanup build cache tags
cleanup_cache() {
  echo "Cleaning up build cache tags..."
  
  CACHE_TAGS=$(curl -s -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
    "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/?page_size=100" \
    | jq -r ".results[] | select(.name | endswith(\"-buildcache\")) | .name" \
    | sort -r)
  
  if [ -z "$CACHE_TAGS" ]; then
    echo "No build cache tags found"
    return
  fi
  
  CACHE_COUNT=$(echo "$CACHE_TAGS" | wc -l)
  echo "Found ${CACHE_COUNT} build cache tags"
  
  # Keep only the most recent KEEP_RECENT cache tags
  KEEP_CACHE=$(echo "$CACHE_TAGS" | head -n ${KEEP_RECENT})
  DELETE_CACHE=$(echo "$CACHE_TAGS" | tail -n +$((KEEP_RECENT + 1)))
  
  DELETE_CACHE_COUNT=$(echo "$DELETE_CACHE" | grep -c . || echo "0")
  
  if [ "$DELETE_CACHE_COUNT" -eq 0 ]; then
    echo "No build cache tags to delete"
    return
  fi
  
  echo "Would delete ${DELETE_CACHE_COUNT} old build cache tags"
  
  if [ "$DRY_RUN" = "true" ]; then
    echo "DRY RUN: Skipping cache deletion"
    return
  fi
  
  DELETED=0
  FAILED=0
  while IFS= read -r CACHE_TAG; do
    if [ -n "$CACHE_TAG" ]; then
      RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE \
        -u "${DOCKERHUB_USER}:${DOCKERHUB_TOKEN}" \
        "https://hub.docker.com/v2/repositories/${DOCKERHUB_USER}/${REPOSITORY}/tags/${CACHE_TAG}/")
      
      HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
      
      if [ "$HTTP_CODE" = "204" ]; then
        DELETED=$((DELETED + 1))
      elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        FAILED=$((FAILED + 1))
        echo "  ✗ Permission error (HTTP ${HTTP_CODE}) - check token has delete permissions"
      else
        FAILED=$((FAILED + 1))
      fi
    fi
  done <<< "$DELETE_CACHE"
  
  echo "Deleted ${DELETED} build cache tags, ${FAILED} failed"
}

# Cleanup each service
cleanup_service "api"
cleanup_service "frontend"
cleanup_cache

echo ""
echo "Cleanup completed!"

