FROM python:3.13-slim AS base
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COVERAGE_FILE=/tmp/.coverage

ARG PRODUCTION=true

WORKDIR /app

# Create user and directories first
RUN set -eux; \
    useradd --create-home --shell /usr/sbin/nologin --uid 1000 django-user; \
    mkdir -p /vol/web/media /vol/web/static; \
    chmod -R 755 /vol; \
    chmod 1777 /tmp

# Ensure /app is owned by django-user (must run as root)
RUN chown -R django-user:django-user /app

# Copy dependency files first for better layer caching
COPY --chown=django-user:django-user pyproject.toml uv.lock /app/

# Install runtime libs, build deps, UV, and Python dependencies
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    # Runtime Libraries
    libpq5 libjpeg62-turbo zlib1g libpng16-16 libtiff6 libfreetype6 liblcms2-2 libwebp7 libopenjp2-7 curl \
    # Build dependencies (purged later)
    build-essential libpq-dev libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev; \
    # Install UV as standalone binary
    curl -LsSf https://astral.sh/uv/install.sh | sh; \
    export PATH="/root/.local/bin:$PATH"; \
    # Create venv in /opt/venv (outside /app so it persists when /app is mounted as volume)
    mkdir -p /opt; \
    uv venv /opt/venv; \
    # Install Python dependencies using uv pip install
    if [ "$PRODUCTION" = "false" ]; then \
    uv pip install --python /opt/venv/bin/python -e ".[dev]"; \
    else \
    uv pip install --python /opt/venv/bin/python .; \
    fi; \
    # Remove build deps and clean up
    apt-get purge -y --auto-remove \
    build-essential libpq-dev libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev; \
    rm -rf /var/lib/apt/lists/* /root/.cache /tmp/*; \
    # Ensure ownership of installed packages, venv, and volumes
    chown -R django-user:django-user /opt/venv /app /vol

# Copy source code
COPY --chown=django-user:django-user . /app/

# Switch to non-root user
USER django-user

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000
# Default dev command (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]