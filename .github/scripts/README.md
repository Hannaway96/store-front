# GitHub Actions Scripts

These scripts are used by GitHub Actions workflows but can also be run locally.

## Prerequisites

- `bash` (version 4+)
- `curl`
- `jq`
- `git` (for `generate-image-tag.sh`)

## Scripts

### `generate-image-tag.sh`

Generates a Docker image tag based on service name, branch/PR, and commit SHA.

**Usage:**
```bash
./generate-image-tag.sh <service> [github_ref] [github_sha]
```

**Examples:**
```bash
# In GitHub Actions (uses GITHUB_REF and GITHUB_SHA automatically)
./generate-image-tag.sh api

# Locally (uses current git branch and commit)
./generate-image-tag.sh frontend

# With explicit values
./generate-image-tag.sh api refs/pull/123/merge abc1234
```

**Output:** Prints the generated tag to stdout (e.g., `api-pr-123-abc1234`)

---

### `cleanup-docker-images.sh`

Cleans up old Docker Hub images, keeping only the most recent N images per service.

**Usage:**
```bash
./cleanup-docker-images.sh [keep_recent] [dry_run]
```

**Environment Variables:**
- `DOCKERHUB_USER` (required): Docker Hub username
- `DOCKERHUB_TOKEN` (required): Docker Hub access token
- `REPOSITORY` (required): Repository name (e.g., `store-front`)

**Arguments:**
- `keep_recent` (optional): Number of recent images to keep per service (default: 10)
- `dry_run` (optional): `true` or `false` (default: `true`)

**Examples:**
```bash
# Dry run (preview what would be deleted)
export DOCKERHUB_USER=your-username
export DOCKERHUB_TOKEN=your-token
export REPOSITORY=store-front
./cleanup-docker-images.sh 10 true

# Actually delete old images (keep 5 most recent)
./cleanup-docker-images.sh 5 false
```

---

### `cleanup-pr-images.sh`

Deletes all Docker Hub images for a specific pull request.

**Usage:**
```bash
./cleanup-pr-images.sh <pr_number>
```

**Environment Variables:**
- `DOCKERHUB_USER` (required): Docker Hub username
- `DOCKERHUB_TOKEN` (required): Docker Hub access token
- `REPOSITORY` (required): Repository name (e.g., `store-front`)

**Examples:**
```bash
export DOCKERHUB_USER=your-username
export DOCKERHUB_TOKEN=your-token
export REPOSITORY=store-front
./cleanup-pr-images.sh 123
```

---

## Local Usage Examples

### Generate a tag for local testing
```bash
cd /path/to/store-front
./.github/scripts/generate-image-tag.sh api
# Output: api-main-abc1234
```

### Clean up old images locally
```bash
export DOCKERHUB_USER=hannaway96
export DOCKERHUB_TOKEN=your-token-here
export REPOSITORY=store-front

# Preview what would be deleted
./.github/scripts/cleanup-docker-images.sh 10 true

# Actually delete (keep 10 most recent)
./.github/scripts/cleanup-docker-images.sh 10 false
```

### Clean up a specific PR's images
```bash
export DOCKERHUB_USER=hannaway96
export DOCKERHUB_TOKEN=your-token-here
export REPOSITORY=store-front
./.github/scripts/cleanup-pr-images.sh 42
```

