FROM python:3.13-slim AS base
LABEL maintainers="Jack Hannaway & Daniel O Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNUMBERBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

ARG DEV=true

WORKDIR /app

# Copy requirements first for build cache efficiency
COPY requirements.txt /tmp/requirements.txt
# Optional dev requirements file; OK if missing
COPY requirements.dev.txt /tmp/requirements.dev.txt

# We:
# 1) Install runtime libs needed by some Python requirements
# 2) Temporarily install build deps to compile anything lacking wheels
# 3) Create a venv and install (dev) deps into it
# 4) Remove build deps to keep the image lean
# 5) Create non-root user and static/media dirs with permissions
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    # Runime Libraries
    libpq5 \
    libjpeg62-turbo zlib1g libpng16-16 libtiff6 libfreetype6 liblcms2-2 libwebp7 libopenjp2-7 \
    curl; \
    apt-get install -y --no-install-recommends \
    # Build dependencies (purged later)
    build-essential libpq-dev \
    libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev; \
    # Install Python Dependencies
    pip install --upgrade pip; \
    pip install -r /tmp/requirements.txt && \
    # Install dev requirements
    if [ "$DEV" = "true" ] && [ -f /tmp/requirements.dev.txt ]; then \
    pip install -r /tmp/requirements.dev.txt; \
    fi; \
    apt-get purge -y --auto-remove \
    build-essential libpq-dev \
    libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev; \
    # Clean up all dependency caches
    rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/*; \
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