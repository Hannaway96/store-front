FROM python:3.13-slim AS base
LABEL maintainers="Jack Hannaway & Daniel O Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COVERAGE_FILE=/tmp/.coverage

ARG DEV=true

WORKDIR /app

# Copy pyproject.toml and uv.lock for build cache efficiency and reproducibility
COPY pyproject.toml uv.lock /app/

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
    if [ "$DEV" = "true" ]; then \
    uv pip install --python /opt/venv/bin/python -e ".[dev]"; \
    else \
    uv pip install --python /opt/venv/bin/python .; \
    fi; \
    # Remove build deps and clean up
    apt-get purge -y --auto-remove \
    build-essential libpq-dev libjpeg-dev zlib1g-dev libpng-dev libtiff-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev; \
    rm -rf /var/lib/apt/lists/* /root/.cache /tmp/*; \
    # Create user and directories
    useradd --create-home --shell /usr/sbin/nologin --uid 1000 django-user; \
    mkdir -p /vol/web/media /vol/web/static /tmp; \
    chown -R django-user:django-user /vol /app /opt/venv; \
    chmod -R 755 /vol; \
    chmod 1777 /tmp

# Copy Source code
COPY --chown=django-user:django-user . /app/

# Ensure /app is writable for coverage files
RUN chmod -R u+w /app

USER django-user

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000
# Default dev command (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]