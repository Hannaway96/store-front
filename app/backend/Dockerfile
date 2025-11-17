FROM python:3.13-slim AS base
LABEL maintainers="Jack Hannaway & Daniel O Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNUMBERBUFFERED=1

ARG DEV=true

WORKDIR /app

# Copy pyproject.toml for build cache efficiency
# Note: uv.lock is optional - if you want reproducible builds, generate it locally
# with `uv lock` and it will be copied with the source code later
COPY pyproject.toml /app/pyproject.toml

# We:
# 1) Install runtime libs needed by some Python requirements
# 2) Install UV package manager
# 3) Temporarily install build deps to compile anything lacking wheels
# 4) Install Python dependencies using UV sync
# 5) Remove build deps to keep the image lean
# 6) Create non-root user and static/media dirs with permissions
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    # Runtime Libraries
    libpq5 libjpeg62-turbo zlib1g libpng16-16 libtiff6 libfreetype6 liblcms2-2 libwebp7 libopenjp2-7 curl; \
    apt-get install -y --no-install-recommends \
    # Build dependencies (purged later)
    build-essential libpq-dev libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev; \
    # Install UV
    pip install --no-cache-dir uv; \
    # Install Python Dependencies using UV sync
    # --no-install-project: Don't install the project itself (Django app, not a package)
    cd /app; \
    if [ "$DEV" = "true" ]; then \
    uv sync --system --extra dev --no-install-project; \
    else \
    uv sync --no-dev --system --no-install-project; \
    fi; \
    apt-get purge -y --auto-remove \
    build-essential libpq-dev libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev; \
    # Clean up all dependency caches
    rm -rf /var/lib/apt/lists/* /root/.cache /tmp/*; \
    # Create user for the container
    useradd --create-home --shell /usr/sbin/nologin --uid 1000 django-user; \
    # Create media and static assets directories for django storage
    mkdir -p /vol/web/media /vol/web/static; \
    # Give ownership of dirs to container user
    chown -R django-user:django-user /vol; \
    chmod -R 755 /vol

# Copy Source code
COPY . ./app
# Give user ownership of app
RUN chown -R django-user:django-user /app
# Set current user in container
USER django-user

EXPOSE 8000
# Default dev command (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]